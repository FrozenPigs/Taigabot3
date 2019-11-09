"""Events for handling ctcp replies."""
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
# Standard Libs
import asyncio
import time

# First Party
from core import hook


@hook.hook('event', ['PRIVMSG'])
async def finger(client, data):
    """Is for replying to ctcp finger messages."""
    if data.command == '\x01FINGER\x01':
        asyncio.create_task(
            client.notice(data.nickname,
                          '\x01FINGER pls don\'t finger me\x01'))


@hook.hook('event', ['PRIVMSG'])
async def version(client, data):
    """Is for replying to ctcp version messages."""
    if data.command == '\x01VERSION\x01':
        asyncio.create_task(
            client.notice(data.nickname,
                          f'\x01VERSION Paprika (rolling release)\x01'))


@hook.hook('event', ['PRIVMSG'])
async def source(client, data):
    """Is for replying to ctcp source messages."""
    if data.command == '\x01SOURCE\x01':
        asyncio.create_task(
            client.notice(data.nickname, '\x01SOURCE https://github.com/nojusr/paprika\x01'))


@hook.hook('event', ['PRIVMSG'])
async def userinfo(client, data):
    """Is for replying to ctcp userinfo messages."""
    if data.command == '\x01USERINFO\x01':
        asyncio.create_task(
            client.notice(data.nickname, '\x01USERINFO immabot\x01'))


@hook.hook('event', ['PRIVMSG'])
async def clientinfo(client, data):
    """Is for replying to ctcp clientinfo messages."""
    if data.command == '\x01CLIENTINFO\x01':
        supported = ('ACTION CLIENTINFO FINGER PING SOURCE TIME USERINFO'
                     ' VERSION')
        asyncio.create_task(
            client.notice(data.nickname, f'\x01CLIENTINFO {supported}\x01'))


@hook.hook('event', ['PRIVMSG'])
async def ctcptime(client, data):
    """Is for replying to ctcp time messages."""
    if data.command == '\x01TIME\x01':
        curtime = time.strftime('%A, %d. %B %Y %I:%M%p')
        asyncio.create_task(
            client.notice(data.nickname, f'\x01TIME {curtime}\x01'))


@hook.hook('event', ['PRIVMSG'])
async def ping(client, data):
    """Is for replying to ctcp ping messages."""
    if data.command == '\x01PING':
        message = ' '.join(data.message.split()[1:])
        asyncio.create_task(
            client.notice(data.nickname, f'\x01PING {message}'))
