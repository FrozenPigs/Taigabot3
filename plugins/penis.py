"""Test penis commands."""
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


@hook.hook('command', ['penis3'], autohelp=True)
async def penis3(client, data):
    """Is used to test threadding by sleeping."""
    print('penis')
    time.sleep(30)
    asyncio.create_task(client.message(data.target, 'penis'))


@hook.hook('command', ['penis2'], admin=True)
async def penis2(client, data):
    """Is used to test threadding by sleeping."""
    print('penis')
    time.sleep(30)
    asyncio.create_task(client.message(data.target, 'penis'))


@hook.hook('command', ['penis'], gadmin=True)
async def penis(client, data):
    """Is used to test threadding by sleeping."""
    print('penis')
    time.sleep(1)
    asyncio.create_task(client.message(data.target, 'penis'))


@hook.hook('command', ['hue1', 'hue2'])
async def hue(client, data):
    """Is used for other tests."""
    print(data)
    if data.command == 'hue2':
        print('penis')
        asyncio.create_task(client.message(data.target, 'penis'))
        return
    print('hue')
    asyncio.create_task(client.message(data.target, 'hue'))
