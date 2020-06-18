"""Main file for running Taigabot."""

# Standard Libs
import asyncio
import base64
import difflib
import os
import pprint
import signal
import sys
from pathlib import Path
from sqlite3 import Connection
from ssl import SSLCertVerificationError, SSLContext
from typing import (Any, Callable, Dict, List, Optional, Set, Tuple, TypeVar,
                    Union, cast)

# First Party
from core import config, db, irc, plugins
from core.data import Config, Message, ParsedRaw, ServerConfig, User
from util import user

DBResult = Optional[List[Tuple[Optional[str], ...]]]
# Used for commands, events, and sieves
CommandFunc = TypeVar('CommandFunc')
CommandDict = Dict[str, List[CommandFunc]]


class Taigabot(irc.IRC):

    def __init__(self, config: Config, server_name: str, ssl_context: SSLContext):
        self.restarted = False
        self.ssl_context = ssl_context
        self.full_config = config
        self.server_name = server_name
        self.server_config: ServerConfig = self.full_config.servers[self.server_name]
        self.plugin_dirs: List[Path] = []
        for plugin_dir in self.full_config.plugin_dirs:
            self.plugin_dirs.append(Path(plugin_dir).resolve())

        self.plugins: Dict[str, Dict[str, Callable]] = {
            'command': {},
            'event': {},
            'init': {},
            'sieve': {}
        }
        self.plugin_mtimes: Dict[str, float] = {}
        self.plugin_mtimes, self.plugins = plugins.reload(self.plugin_dirs, self.plugin_mtimes,
                                                          self.plugins)
        self.users: Dict[str, User] = {}
        self.db: Connection = db.connect(self.full_config.db_dir, self.server_name)
        super().__init__(self.server_config)

################################################################################
#                                   MISC                                       #
################################################################################

    async def stop(self, reset: bool = False) -> None:
        """Is used to stop or restart the bot."""
        self.restarted = reset
        os.kill(os.getpid(), signal.SIGINT)

    async def nickserv(self) -> None:
        self.send_privmsg([
            self.server_config.nickserv_nick
        ], self.server_config.nickserv_command.format(self.server_config.nickname_password))

    async def start(self) -> None:    # on_connect
        try:
            await self.connect()
        except SSLCertVerificationError as err:
            print('Certificate verification failed')
            print(str(err))
            return

        await asyncio.gather(self.authenticate(), self.read_loop())

    async def authenticate(self) -> None:
        await super().authenticate()
        if 'sasl' not in self.server_config.capabilities:
            if self.server_config.nickname_password:
                await self.nickserv()

    async def connect(self) -> None:
        return await self.create_connection(self.server_config.server, self.server_config.port,
                                            self.ssl_context)

    async def _run_output_sieves(self, message: str) -> Union[None, str]:
        msg = message
        for name, funcs in self.plugins['sieve'].items():
            if name not in self.server_config.disabled and name.endswith('-output'):
                for func in funcs:
                    msg = await func(self, msg)
        return msg

    async def send_line(self, message: str) -> None:
        msg = await self._run_output_sieves(message)
        if msg:
            await super().send_line(msg)

    async def send_join(self, channels: List[str]) -> None:
        new_channels = channels
        for channel in channels:
            tmp_channel = channel
            if ' ' in channel:
                tmp_channel = channel.split()[0]
            if tmp_channel in self.server_config.no_channels:
                new_channels.remove(channel)
        if new_channels:
            await super().send_join(new_channels)
        return

    async def _userhost_from_names(self, nick: str) -> Tuple[str, str, str]:
        nickname = nick
        userhost = ''
        username = ''
        if '!' in nick:
            userhost = nick
            nickname = userhost.split('!')[0]
            username = userhost.split('!')[1].split('@')[0]
        return nickname, username, userhost

    async def _chanmodes_from_names(self, nick: str, userhost: str = '') -> Tuple[str, str, str]:
        nickname = nick
        channel_mode = '+'
        for char in nick:
            modes = {'+': 'v', '%': 'h', '@': 'o', '&': 'a', '~': 'q'}
            if char in modes.keys():
                if userhost:
                    userhost = userhost.replace(char, '')
                nickname = nickname.replace(char, '')
                channel_mode += modes[char]
        return nickname, channel_mode, userhost

    async def _chanmodes_from_chans(self, channels: List[str]) -> Tuple[Dict[str, str], List[str]]:
        channel_modes = {}
        new_channels = []
        for channel in channels:
            channel, channel_mode, host = await self._chanmodes_from_names(channel)
            if channel_mode != '+':
                channel_modes[channel] = channel_mode
            new_channels.append(channel)
        return channel_modes, new_channels

    async def check_admins(self, user: User, target: str) -> None:
        user.global_admin = user.userhost in self.server_config.admins
        db.add_column(self.db, 'channels', 'admins')
        admins = db.get_cell(self.db, 'channels', 'admins', 'channel', target)
        if admins:
            nadmins: Optional[str] = admins[0][0]
            if nadmins:
                if user.userhost in nadmins.split():
                    user.chan_admin = True
                else:
                    user.chan_admin = False

    async def check_ignored(self, user: User, target: str) -> None:
        user.global_ignored = user.userhost in self.server_config.ignored
        db.add_column(self.db, 'channels', 'ignored')
        ignores = db.get_cell(self.db, 'channels', 'ignored', 'channel', target)
        if ignores:
            nignores: Optional[str] = ignores[0][0]
            if nignores:
                if user.userhost in nignores:
                    user.chan_ignored[target] = True
        user.chan_ignored[target] = False

    async def track_users_userhost(self, userhost: str) -> None:
        if '!' in userhost:
            username_user_set = False
            if '~' in userhost:
                username_user_set = True
                userhost = userhost.replace('~', '')
            nickname = userhost.split('!')[0]
            username = userhost.split('!')[1].split('@')[0]
            if nickname not in self.users.keys():
                user = User(nickname, self)
                user.userhost = userhost
                user.username = username
                user.username_user_set = username_user_set
                self.users[nickname] = user
            elif nickname in self.users.keys():
                self.users[nickname].userhost = userhost
                self.users[nickname].username = username
                self.users[nickname].username_user_set = username_user_set

################################################################################
#                                    RPL                                       #
################################################################################

    async def rpl_353(self, message: Message) -> None:
        """NAMES."""
        users = message.split_message[2:]
        channel = message.split_message[1]
        for nick in users:
            nickname, username, userhost = await self._userhost_from_names(nick)
            nickname, chan_mode, userhost = await self._chanmodes_from_names(nickname, userhost)
            if userhost:
                await self.track_users_userhost(userhost)
                if chan_mode != '+':
                    self.users[nickname].channel_modes[channel] = chan_mode
                if channel not in self.users[nickname].channels:
                    self.users[nickname].channels.append(channel)
            else:
                user = User(nickname, self)
                if chan_mode != '+':
                    user.channel_modes[channel] = chan_mode
                user.channels.append(channel)
                self.users[nickname] = user

    async def rpl_311(self, message: Message) -> None:
        nickname = message.split_message[0]
        username = message.split_message[1]
        userhost = f'{nickname}!{username}@{message.split_message[2]}'
        await self.track_users_userhost(userhost)
        realname = ' '.join(message.split_message[4:])
        self.users[nickname].realname = realname

    async def rpl_319(self, message: Message) -> None:
        """whois channels"""
        nickname = message.split_message[0]
        channel_modes, channels = await self._chanmodes_from_chans(message.split_message[1:])
        self.users[nickname].channel_modes = channel_modes
        self.users[nickname].channels = channels

    async def rpl_307(self, message: Message) -> None:
        nickname = message.split_message[0]
        if message.message == f'{nickname} has identified for this nick':
            self.users[nickname].identified = True

    async def rpl_318(self, message: Message) -> None:
        nickname = message.split_message[0]
        self.users[nickname].whoised = True

    async def rpl_333(self, message: Message) -> None:
        userhost = message.split_message[1]
        await self.track_users_userhost(userhost)
        channel = message.split_message[0]
        nickname = userhost.split('!')[0]
        self.users[nickname].channels.append(channel)

    async def rpl_376(self, message: Message) -> None:
        channels = self.server_config.channels
        if channels:
            asyncio.create_task(self.send_join(channels))
        else:
            print('No channels to join.')

    async def rpl_PART(self, message: Message) -> None:
        userhost = message.sent_by
        await self.track_users_userhost(userhost)
        nickname = userhost.split('!')[0]
        channel = message.target
        msg = message.message
        self.users[nickname].part_message[channel] = msg
        self.users[nickname].channels.remove(channel)

    async def rpl_QUIT(self, message: Message) -> None:
        userhost = message.sent_by
        await self.track_users_userhost(userhost)
        nickname = userhost.split('!')[0]
        msg = message.message
        self.users[nickname].quit_message = msg
        self.users[nickname].whoised = False

    async def rpl_JOIN(self, message: Message) -> None:
        userhost = message.sent_by
        await self.track_users_userhost(userhost)
        nickname = userhost.split('!')[0]
        channel = message.target
        self.users[nickname].channels.append(channel)

    async def rpl_NOTICE(self, message: Message) -> None:
        userhost = message.sent_by
        await self.track_users_userhost(userhost)
        nickname = userhost.split('!')[0]
        if nickname in self.users:
            user = self.users[nickname]
            user.last_message = message.raw_message

    async def rpl_PRIVMSG(self, message: Message) -> None:
        userhost = message.sent_by
        await self.track_users_userhost(userhost)
        nickname = userhost.split('!')[0]
        self.users[nickname].last_message = message.raw_message
        if not self.users[nickname].whoised:
            self.send_whois(nickname)
        target = message.target
        await self.check_admins(self.users[nickname], target)
        await self.check_ignored(self.users[nickname], target)
        prefix = await self._get_prefix(target)
        if message.command and message.command[0] == prefix:
            asyncio.create_task(self._run_commands(message))


################################################################################
#                     SIEVES, EVENTS AND COMMANDS                              #
################################################################################

    async def _run_commands(self, message: Message) -> None:
        commands = self.plugins['command']
        command = message.command[1:]
        conn = self.db
        if not message.sent_by:
            return
        if command in commands.keys():
            for func in commands[command]:
                hook = func.__hook__[1]
                if hook['gadmin'] and not message.user.global_admin:
                    asyncio.create_task(
                        self.send_notice([message.nickname], ('You must be a gadmin to use'
                                                              ' that command')))
                    return
                if hook['admin'] and not message.user.chan_admin and not message.user.global_admin:
                    asyncio.create_task(
                        self.send_notice([message.nickname], ('You must be an admin to use'
                                                              ' that command')))
                    return
                if not len(message.message) - len(message.command) and hook['autohelp']:
                    doc: str = ' '.join(cast(str, func.__doc__).split())
                    asyncio.create_task(self.send_notice([message.nickname], f'{doc}'))
                    return
                message.message = message.message.replace(message.command + ' ', '')
                message.split_message.pop(0)
                if isinstance(message.split_message, str):
                    message.split_message = [message.split_message]
                asyncio.create_task(func(self, message))

    async def _get_prefix(self, target: str) -> str:
        default_prefix = self.server_config.command_prefix
        if not default_prefix:
            default_prefix = '.'
        if target[0] != '#':
            return default_prefix
        db_prefix = db.get_cell(self.db, 'channels', 'commandprefix', 'channel', target)
        if not db_prefix:
            prefix = default_prefix
            db.add_channel(self.db, target, prefix)
            db.set_cell(self.db, 'channels', 'commandprefix', prefix, 'channel', target)
        else:
            prefix = db_prefix[0][0]
            valid_prefixes = self.full_config.valid_command_prefixes
            if not prefix or prefix not in valid_prefixes:
                prefix = default_prefix
                db.set_cell(self.db, 'channels', 'commandprefix', prefix, 'channel', target)
        return prefix

    async def _run_input_sieves(self, privmsg) -> None:
        msg = privmsg
        for name, funcs in self.plugins['sieve'].items():
            if name not in self.server_config.disabled and name.endswith('-input'):
                for func in funcs:
                    msg = await func(self, msg)
                    if msg is None:
                        return msg
        return msg

    async def _run_inits(self) -> None:
        for name, funcs in self.plugins['init'].items():
            if name not in self.server_config.disabled:
                for func in funcs:
                    await func(self)

    async def _run_events(self, privmsg) -> None:
        events = self.plugins['event']
        if privmsg.raw_command in events:
            for func in events[privmsg.raw_command]:
                if func.__name__.lower() not in self.server_config.disabled:
                    asyncio.create_task(func(self, privmsg))
        if '*' in events:
            for func in events['*']:
                if func.__name__.lower() not in self.server_config.disabled:
                    asyncio.create_task(func(self, privmsg))

    async def read_loop(self) -> None:    # message_handler
        await self._run_inits()
        while True:
            self.plugin_mtimes, self.plugins = plugins.reload(self.plugin_dirs, self.plugin_mtimes,
                                                              self.plugins)
            try:
                raw_message = await self.read_line()
                message = Message(self, await self.parse_message(raw_message))
                await self._get_prefix(message.target)
                message = await self._run_input_sieves(message)
                if message:
                    await self._run_events(message)
                    if '!' in message.sent_by:
                        nick = message.sent_by.split('!')[0]
                    if hasattr(self, f'rpl_{message.raw_command}'):
                        rpl_handler = getattr(self, f'rpl_{message.raw_command}')
                        await rpl_handler(message)

            except asyncio.IncompleteReadError:
                if self.server_config.auto_reconnect:
                    await asyncio.sleep(self.server_config.auto_reconnect_delay)
                    try:
                        await self.connect()
                    except ConnectionResetError:
                        await self.connect()
                    asyncio.create_task(self.authenticate())
