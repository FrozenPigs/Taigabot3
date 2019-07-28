#!/usr/local/bin/python3.7
# Copyright (C) 2019  Anthony DeDominic <adedomin@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Main file for running bot."""

# Standard Libs
import asyncio
import os
import signal
import sys
from sqlite3 import Connection
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, cast

# First Party
import pydle
from core import config, db, plugins
from core.data import Bot, ParsedRaw
from util import user

# TODO: Take another look at the disable code
# TODO: finish cleaning admin.py

InputSieveList = List[Callable[['Client', 'ParsedRaw'], 'ParsedRaw']]
InputSievePlugDict = Dict[str, InputSieveList]

OutputSieveList = List[
    Callable[['Client', str, str, Tuple[str, ...], Dict[str, str]],
             Tuple[str, Tuple[str, ...], Dict[str, str]]]]
OutputSievePlugDict = Dict[str, OutputSieveList]

CommandEventFunc = Callable[['Client', 'ParsedRaw'], None]
CommandEventList = List[CommandEventFunc]
CommandEventPlugsDict = Dict[str, CommandEventList]

InitFunc = Callable[['Client'], None]
InitList = List[CommandEventFunc]
InitDict = Dict[str, CommandEventList]

FuncUnion = Union[InputSieveList, OutputSieveList, CommandEventList, InitList]
AllPlugsDict = Dict[str, FuncUnion]
DBResult = Optional[List[Tuple[Optional[str], ...]]]

PydleClient = pydle.featurize(
    pydle.features.RFC1459Support, pydle.features.IRCv3Support,
    pydle.features.AccountSupport, pydle.features.CTCPSupport,
    pydle.features.ISUPPORTSupport, pydle.features.TLSSupport)


class Client(PydleClient):
    """Taigabot Client."""

    async def stop(self, reset: bool = False) -> None:
        """Is used to stop or restart the bot."""
        global restarted
        restarted = reset
        os.kill(os.getpid(), signal.SIGINT)

    async def message_handler(self, data: 'ParsedRaw') -> None:
        """
        Is used for running sieves, events and commands if applicable.

        Runs sieves before everything, then events or commands,
        depending on the information in data.
        """
        if not self.server_tag:
            return

        # get prefix before sieves to add channel to db
        if data.target:
            prefix: str = await self._get_prefix(data.target)
        gdisabled: List[Optional[str]]
        gdisabled = self.bot.config['servers'][self.server_tag]['disabled']
        ndata: Optional['ParsedRaw'] = await self._run_sieves(data, gdisabled)
        if not ndata:
            return
        data = ndata

        asyncio.create_task(self._run_events(data, gdisabled))

        if data.nickname in self.users:
            asyncio.create_task(self._update_user(data.nickname, data.mask))
        if not data.command:
            return

        if data.command[0] != prefix:
            return

        data.message = data.message.replace(data.command, '').strip()
        data.split_message.remove(data.command)
        data.command = data.command[1:]
        if data.command.lower() in gdisabled:
            #asyncio.create_task(
                #self.notice(data.nickname, f'{data.command} is gdisabled.'))
            return
        asyncio.create_task(self._run_commands(data))

    async def _update_user(self, user: str, mask: str) -> None:
        """
        Is used to update the users db information when they speak.

        Runs before sieves so ignored users are in the db.
        If user not in db, adds them, otherwise update nick,
        or mask if needed.
        """
        if user == self.nickname:
            return
        conn: Connection = self.bot.dbs[self.server_tag]

        db_mask: DBResult = db.get_cell(conn, 'users', 'mask', 'nick', user)
        db_nick: DBResult = db.get_cell(conn, 'users', 'nick', 'mask', mask)

        if not db_mask or not db_nick:
            db.add_user(conn, user, mask)
            return
        else:
            same_mask = (db_mask[0][0] == mask)
            same_nick = (db_nick[0][0] == user)
            # if mask changed
            if not same_mask and same_nick:
                db.set_cell(conn, 'users', 'mask', mask, 'nick', user)
            # if nick changed
            if same_mask and not same_nick:
                db.set_cell(conn, 'users', 'nick', user, 'mask', mask)

    async def _run_events(self, data: 'ParsedRaw',
                          gdisabled: List[Optional[str]]) -> None:
        """IS used for running all the events if not disabled."""
        events: CommandEventPlugsDict = self.bot.plugs['event']
        if data.raw_command in events:
            for func in events[data.raw_command]:
                if func.__name__.lower() not in gdisabled:
                    asyncio.create_task(func(self, data))
        if '*' in events:
            for func in events['*']:
                if func.__name__.lower() not in gdisabled:
                    asyncio.create_task(func(self, data))

    async def _run_inits(self, gdisabled: List[Optional[str]]) -> None:
        """IS used for running all the events if not disabled."""
        inits: InitDict = self.bot.plugs['init']
        for init in inits.values():
            for func in init:
                if func.__name__.lower() not in gdisabled:
                    asyncio.create_task(func(self))

    async def _run_commands(self, data: 'ParsedRaw') -> None:
        """
        Is used for running user commands if not disabled.

        commands are run if user has correct privilages,
        used correct command, and has long enough input.
        """
        commands: CommandEventPlugsDict = self.bot.plugs['command']
        conn: Connection = self.bot.dbs[self.server_tag]

        if data.mask and data.nickname:
            gadmin: bool = await user.is_gadmin(self, data.server, data.mask)
            admin: bool = await user.is_admin(self, conn, data.nickname,
                                              data.mask)
        else:
            return

        if data.command in commands:
            for func in commands[data.command]:
                hook: Dict[str, Union[List[str], bool]]
                hook = func.__hook__[1]    # type: ignore
                if hook['gadmin'] and not gadmin:
                    asyncio.create_task(
                        self.notice(data.nickname,
                                    ('You must be a gadmin to use'
                                     ' that command')))
                    return
                if hook['admin'] and not admin and not gadmin:
                    asyncio.create_task(
                        self.notice(data.nickname,
                                    ('You must be an admin to use'
                                     ' that command')))
                    return
                if not len(data.message) and hook['autohelp']:
                    doc: str = ' '.join(cast(str, func.__doc__).split())
                    asyncio.create_task(self.notice(data.nickname, f'{doc}'))
                    return
                asyncio.create_task(func(self, data))

    async def _run_sieves(
            self, data: 'ParsedRaw',
            gdisabled: List[Optional[str]]) -> Optional['ParsedRaw']:
        """
        Is used to run the sieves on the input if not disabled.

        Sieves filter data, and return None or modified data,
        if None bot takes no futher action on the input.
        """
        plugs: InputSievePlugDict = self.bot.plugs['sieve']
        for name, func_list in sorted(plugs.items()):
            if name not in gdisabled and name.endswith('-input'):
                for func in func_list:
                    data = await func(self, data)
                    if not data:
                        return data
        return data

    async def _get_prefix(self, target: str) -> str:
        """
        Is used to get or set the channel command prefix.

        Returns default for private messages.
        If channel has prefix set to non valid prefix, set it to default.
        """
        default_prefix: str
        try:
            default_prefix = self.bot.config['servers'][self.server_tag].get(
                'command_prefix', '.')
        except AttributeError:
            default_prefix = '.'

        conn: Connection = self.bot.dbs[self.server_tag]
        prefix: Optional[str]
        if target[0] == '#':
            db_prefix: DBResult = db.get_cell(
                conn, 'channels', 'commandprefix', 'channel', target)
            if not db_prefix:
                prefix = default_prefix
                db.add_channel(conn, target, prefix)
            else:
                prefix = db_prefix[0][0]
                valid_prefixes: Union[str, List[str]] = self.bot.config.get(
                    'valid_command_prefixes', '.')
                if not prefix or prefix not in valid_prefixes:
                    prefix = default_prefix
                    db.set_cell(conn, 'channels', 'commandprefix', prefix,
                                'channel', target)
        else:
            prefix = default_prefix
        return prefix

    # changing defaults
    async def join(self, channel: str, password: str = None) -> None:
        """Overwrite the join channel funcion to block channels."""
        no_join = self.bot.config['servers'][self.server_tag]['no_channels']
        if ',' in channel:
            chans = channel.split(',')
            for chan in no_join:
                if chan in chans:
                    chans.remove(chan)
            if not chans:
                return
            channel = ','.join(chans)
        else:
            for chan in no_join:
                if chan == channel:
                    return
        await super().join(channel, password)

    async def on_capability_away_notify_available(self, value: Any) -> False:
        """Disable away-notify."""
        return False

    async def on_capability_invite_notify_available(self, value: Any) -> False:
        """Disable invite-notify."""
        return False

    async def rawmsg(self, command: str, *args: str, **kwargs: str) -> None:
        """
        Is called to send data, non-disabled sieves are run first.

        self.bot is here because the first thing that happens on
        connect is sending messages.
        Sieves modify the commands, args, or kwargs, if command comes
        back None then output is not sent.
        """
        print(command, args, kwargs)
        global bot
        self.bot: 'Bot' = bot
        gdisabled: List[Optional[str]] = self.bot.config['servers'][
            self.server_tag].get('disabled', [])

        sieves: OutputSievePlugDict = self.bot.plugs['sieve']
        for name, func_list in sorted(sieves.items()):
            if name not in gdisabled and name.endswith('-output'):
                for func in func_list:
                    command, args, kwargs = await func(self, self.server_tag,
                                                       command, args, kwargs)
                    if not command:
                        return
        if not command:
            return
        await super().rawmsg(command, *args, **kwargs)

    async def on_ctcp_version(self, by: str, target: str,
                              contents: List[str]) -> None:
        """Is overwriting ctcp version to be handled by the events."""
        pass

    async def on_raw(self, message: Any) -> None:
        """Is called on raw commands, starts the message handler."""
        await super().on_raw(message)
        plugins.reload(self.bot)

        data: 'ParsedRaw' = ParsedRaw(message._raw,    # noqa: SF01
                                      self.server_tag)
        asyncio.create_task(self.message_handler(data))

    async def on_connect(self) -> None:
        """
        Is called when connection to server is successful.

        Identifies with services and joins channels.
        """
        await super().on_connect()
        # self.logger.setLevel(10)
        server_conf: Dict[str, Any] = self.bot.config['servers'][self
                                                                 .server_tag]

        passwd: str = server_conf.get('nickserv_password', '')
        nickserv: str = server_conf.get('nickserv_nick', 'nickserv')
        nickserv_command: str = server_conf.get('nickserv_command',
                                                'IDENTIFY {0}')

        if passwd != '':
            asyncio.create_task(
                self.message(nickserv, nickserv_command.format(passwd)))

        try:
            # for channel in server_conf['channels']:
            #     self.join(channel)
            asyncio.create_task(self.join(','.join(server_conf['channels'])))
        except KeyError:
            print('Warning: No channels to join.')
        gdisabled = self.bot.config['servers'][self.server_tag]['disabled']
        asyncio.create_task(self._run_inits(gdisabled))

    # were unhandled
    async def on_raw_479(self, message: Any) -> None:
        """Is called on invalid channel name."""
        pass

    async def on_raw_716(self, message: Any) -> None:
        """Is called when recieved user is +G."""
        pass

    async def on_raw_379(self, message: Any) -> None:
        """Is called when recieved whoismodes."""
        pass

    async def on_raw_378(self, message: Any) -> None:
        """Is called when recieved whoishost."""
        pass

    async def on_raw_338(self, message: Any) -> None:
        """Is called when recieved whoisactually."""
        pass


dbs: List[Connection] = []    # list of dbs for closing
restarted = False    # global, typed in stop

bot = Bot()    # global typed in rawmsg

try:
    server_configs: Dict[str, Any] = bot.config['servers']
except KeyError:
    print('No servers in config')
    sys.exit(0)

pool: pydle.client.ClientPool = pydle.ClientPool()    # type: ignore
for server_name in bot.config['servers']:
    server: Dict[str, Any] = bot.config['servers'][server_name]
    if server:
        client: Client = Client(server['nick'])
    else:
        print('Invalid server config.')
        sys.exit(0)

    bot.clients.append(client)
    pool.connect(client, server['server'], tls=True, tls_verify=False)

try:
    pool.handle_forever()
except KeyboardInterrupt:
    print('Disconnecting clients.')
    for client in bot.clients:
        pool.disconnect(client)
    print('Saving and closing dbs.')
    for conn in list(bot.dbs.values()):
        conn.commit()
        conn.close()
    print('Saving config.')
    config.save(bot)
    if restarted:
        print('Restarting.')
        args: List[str] = sys.argv[:]
        args.insert(0, sys.executable)
        os.execv(sys.executable, args)
    else:
        print('Closing.')
