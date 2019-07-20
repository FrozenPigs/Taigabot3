"""Sieves and events for preventing masshighlighting."""
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
import re

# First Party
from core import hook
from util import timeu


async def _detect_highlight(users, message):
    """Is used to detect if message is masshighlighting."""
    message = message.split(' ')
    r = re.compile('[\'!?,.]')
    matches = [
        word for word in message[1:] if r.sub('', word.lower()) in users]
    if len(set(matches)) > 5:
        return True
    False


@hook.hook('sieve', ['03-masshighlight-output'])
async def masshighlight_output_sieve(client, server, command, args, kwargs):
    """Is for preventing the bot from mass highligting."""
    if command == 'PRIVMSG':
        message = args[1]
        if ' ' not in message:
            return command, args, kwargs
        users = list(client.users.keys())
        if await _detect_highlight(users, message):
            return None, args, kwargs
    return command, args, kwargs


@hook.hook('sieve', ['03-masshighlight-input'])
async def masshighlight_input_sieve(client, data):
    """Is for banning users who masshighlight."""
    if ' ' not in data.message:
        return data
    users = list(client.users.keys())
    if await _detect_highlight(users, data.message):
        asyncio.create_task(
            client.kickban(
                data.target,
                data.nickname,
                reason=('No mass'
                        'highlighting, come back in 1 minute.')))
        asyncio.create_task(
            timeu.asyncsched(60, client.unban,
                             (data.target, data.nickname)))
        return None
    return data
