# source, help, and .bots script
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
# author: nojusr
#
# usage:
#  .help                 -- get help with the bot
#  .bots                 -- confirm the bot's presence in a channel
#  .source               -- get the git repository of the bot

from core import hook


@hook.hook('command', ['help'])
async def bothelp(client, data):
    out =  'You can find description and usage of every plugin '
    out += 'installed in the source at '
    out += 'https://github.com/nojusr/paprika/tree/master/plugins'
    asyncio.create_task(client.message(data.target, out))


@hook.hook('command', ['source'])
async def source(client, data):
    out = 'Here\'s my source: https://github.com/nojusr/paprika'
    asyncio.create_task(client.message(data.target, out))


@hook.hook('command', ['bots'])
async def bots(client, data):
    name = client.bot.config['servers'][data.server]['nick']
    out = f'{name} reporting in!'
    asyncio.create_task(client.message(data.target, out))
