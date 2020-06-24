"""Events for handling ctcp replies."""
# Standard Libs
import asyncio
import time

# First Party
from core import hook

ctcpcache = []


@hook.hook('event', ['PRIVMSG'])
async def finger(bot, message):
    """Is for replying to ctcp finger messages."""
    if message.command == '\x01FINGER\x01':
        asyncio.create_task(
            bot.send_notice([message.nickname], "\x01FINGER pls don't finger me\x01"))


@hook.hook('event', ['PRIVMSG'])
async def ctcp_version(bot, message):
    """Is for replying to ctcp version messages."""
    if message.command == '\x01VERSION\x01':
        try:
            asyncio.create_task(
                bot.send_notice([message.nickname], f'\x01VERSION TaigaBotNet Version 3.8\x01'))
        except AttributeError:
            asyncio.create_task(
                bot.send_notice([message.sent_by], f'\x01VERSION TaigaBotNet Version 3.8\x01'))


@hook.hook('event', ['PRIVMSG'])
async def source(bot, message):
    """Is for replying to ctcp source messages."""
    if message.command == '\x01SOURCE\x01':
        asyncio.create_task(bot.send_notice([message.nickname], '\x01SOURCE No source yet.\x01'))


@hook.hook('event', ['PRIVMSG'])
async def userinfo(bot, message):
    """Is for replying to ctcp userinfo messages."""
    if message.command == '\x01USERINFO\x01':
        asyncio.create_task(bot.send_notice([message.nickname], '\x01USERINFO immabot\x01'))


@hook.hook('event', ['PRIVMSG'])
async def clientinfo(bot, message):
    """Is for replying to ctcp clientinfo messages."""
    if message.command == '\x01CLIENTINFO\x01':
        supported = ('ACTION CLIENTINFO FINGER PING SOURCE TIME USERINFO' ' VERSION')
        asyncio.create_task(bot.send_notice([message.nickname], f'\x01CLIENTINFO {supported}\x01'))


@hook.hook('event', ['PRIVMSG'])
async def ctcptime(bot, message):
    """Is for replying to ctcp time messages."""
    if message.command == '\x01TIME\x01':
        curtime = time.strftime('%A, %d. %B %Y %I:%M%p')
        asyncio.create_task(bot.send_notice([message.nickname], f'\x01TIME {curtime}\x01'))


@hook.hook('event', ['NOTICE'])
async def ctcp_ping(bot, message):
    """Is for replying to ctcp ping messages."""
    if message.command == '\x01PING':
        ping_message = ' '.join(message.split_message[1:])[0:-3]
        asyncio.create_task(bot.send_notice([message.nickname], f'\x01PING {ping_message}\x01'))


@hook.hook('event', ['*'])
async def ctcp_command_replies(bot, message):
    global ctcpcache
    if ctcpcache:
        for ctcp in ctcpcache:
            if ctcp[0] == 'VERSION':
                ctcpcache.remove(ctcp)
                msg = message.message.replace('\x01', '').replace('VERSION ', '')
                asyncio.create_task(
                    bot.send_privmsg([ctcp[2]], f'[VERSION] {message.nickname}: {msg}.'))
            elif ctcp[0] == 'PING':
                ctcpcache.remove(ctcp)
                ping_message = ' '.join(message.split_message[1:])[0:-3]
                curtime = time.time()
                diff = (curtime - float(ping_message))
                if diff <= 1:
                    asyncio.create_task(
                        bot.send_privmsg([ctcp[2]], f'[PING] {message.nickname}: {diff * 1000} ms'))
                else:
                    asyncio.create_task(
                        bot.send_privmsg([ctcp[2]], f'[PING] {message.nickname}: {diff} seconds'))


@hook.hook('command', ['pingme', 'ping'])
async def ping(bot, msg):
    "ping <nick> -- Returns ping "
    # if '.' in inp:
    #     return pingip(inp, reply)
    # else:
    inp = msg.split_message
    if not inp:
        user = msg.nickname
    else:
        user = inp[0]
    curtime = time.time()
    global ctcpcache
    ctcpcache.append(("PING", user, msg.target))
    asyncio.create_task(bot.send_privmsg([msg.nickname], f'\x01PING {curtime}\x01'))


@hook.hook('command', ['ver', 'version'])
async def version(bot, msg):
    "version <nick> -- Returns version "
    inp = msg.split_message
    if not inp:
        user = msg.nickname
    else:
        user = inp[0]
    global ctcpcache
    ctcpcache.append(("VERSION", user, msg.target))
    asyncio.create_task(bot.send_privmsg([msg.nickname], f'\x01VERSION\x01'))
