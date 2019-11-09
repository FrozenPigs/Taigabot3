# .bots plugin
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
# author: ine
#
# usage:
# .bots, .source                    -- show some information about the bot

from core import hook

import asyncio

@hook.hook('command', ['bots'])
async def bots(client, data):
    asyncio.create_task(client.message(data.target, 'Reporting in! [Python]'))

@hook.hook('command', ['source'])
async def source(client, data):
    asyncio.create_task(client.message(data.target, '\x02paprika\x02 - Fuck my shit up nigga https://github.com/nojusr/paprika'))
