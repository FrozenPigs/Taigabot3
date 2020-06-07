"""Events for handling ctcp replies."""
# Standard Libs
import asyncio
import time

# First Party
from core import hook


@hook.hook('event', ['PRIVMSG'])
async def finger(bot, message):
    """Is for replying to ctcp finger messages."""
    if message.command == '\x01FINGER\x01':
        asyncio.create_task(
            bot.send_notice([message.user.nickname],
                               "\x01FINGER pls don't finger me\x01"))


@hook.hook('event', ['PRIVMSG'])
async def version(bot, message):
    """Is for replying to ctcp version messages."""
    if message.command == '\x01VERSION\x01':
        try:
            asyncio.create_task(
                bot.send_notice([message.user.nickname],
                                f'\x01VERSION TaigaBotNet Version 3.8\x01'))
        except AttributeError:
            asyncio.create_task(
                bot.send_notice([message.sent_by],
                                f'\x01VERSION TaigaBotNet Version 3.8\x01'))


@hook.hook('event', ['PRIVMSG'])
async def source(bot, message):
    """Is for replying to ctcp source messages."""
    if message.command == '\x01SOURCE\x01':
        asyncio.create_task(
            bot.send_notice([message.user.nickname], '\x01SOURCE No source yet.\x01'))


@hook.hook('event', ['PRIVMSG'])
async def userinfo(bot, message):
    """Is for replying to ctcp userinfo messages."""
    if message.command == '\x01USERINFO\x01':
        asyncio.create_task(
            bot.send_notice([message.user.nickname], '\x01USERINFO immabot\x01'))


@hook.hook('event', ['PRIVMSG'])
async def clientinfo(bot, message):
    """Is for replying to ctcp clientinfo messages."""
    if message.command == '\x01CLIENTINFO\x01':
        supported = ('ACTION CLIENTINFO FINGER PING SOURCE TIME USERINFO'
                     ' VERSION')
        asyncio.create_task(
            bot.send_notice([message.user.nickname],
                               f'\x01CLIENTINFO {supported}\x01'))


@hook.hook('event', ['PRIVMSG'])
async def ctcptime(bot, message):
    """Is for replying to ctcp time messages."""
    if message.command == '\x01TIME\x01':
        curtime = time.strftime('%A, %d. %B %Y %I:%M%p')
        asyncio.create_task(
            bot.send_notice([message.user.nickname], f'\x01TIME {curtime}\x01'))


@hook.hook('event', ['PRIVMSG'])
async def ping(bot, message):
    """Is for replying to ctcp ping messages."""
    if message.command == '\x01PING':
        ping_message = ' '.join(message.split_message[1:])
        asyncio.create_task(
            bot.send_notice([message.user.nickname], f'\x01PING {ping_message}\x01'))
