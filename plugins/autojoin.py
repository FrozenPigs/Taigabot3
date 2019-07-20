# This is a plugin that makes the bot resistant from being kicked.
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
#  .autojoin add #[channel_name]      -- gadmin only command to make the
#                                        bot automatically join the
#                                        channel whenever it is kicked
#
#  .autojoin remove #[channel_name]   -- gadmin only command to stop the
#                                        bot from joining the channel.
#
#  note: the bot will not rejoin instantly in order to avoid spamming
#        the server and getting disconnected. there is a configurable
#        delay that the user can change in this plugin in order to fit
#        the IRC network's requirements.

import asyncio
import time

from core import db, hook
from util import botu, messaging, user

def _check_channel(conn, channel_name):
    """Is used to confirm a channel's existence in the db"""
    tst = db.get_row(conn, 'channels', 'channel', channel_name)
    if len(tst) < 1:
        return False
    return True

def _check_if_channel_autojoin(conn, channel_name):
    """Is used to check if a channel is set to autojoin"""
    tst = db.get_cell(conn, 'channels', 'autojoin',
                      'channel', channel_name)
    print(tst)
    if tst is None or tst[0][0] == '0':
        return False
    return True

@hook.hook('init', ['autojoininit'])
async def auto_join_init(client):
    """Is used for initializing the database for this plugin"""
    conn = client.bot.dbs[client.server_tag]
    print(('Initializing autojoin column in \'channels\''
           f' in /persist/db/{client.server_tag}.db...'))
    db.add_column(conn, 'channels', 'autojoin')
    db.ccache()
    print('Autojoin initialization complete.')


@hook.hook('command', ['autojoin'], admin=True)
async def auto_join(client, data):
    conn = client.bot.dbs[data.server]
    split = data.split_message


    if split[0] is None or split[1] is None:
        asyncio.create_task(
            client.notice(data.nickname,
            'Syntax: .autojoin [add/delete] #[channel_name]'))
        return

    command = split[0].lower()
    channel = split[1].lower()

    if channel[0] != '#':
        asyncio.create_task(
            client.notice(data.nickname,
            'Syntax: .autojoin [add/delete] #[channel_name]'))
        return
    
    print (_check_channel(conn, channel))
    
    if _check_channel(conn, channel) == False:
        asyncio.create_task(
            client.notice(data.nickname,
            'Error: channel not in database'))
        return

    if command == 'add':
        db.set_cell(conn, 'channels', 'autojoin',
                    '1', 'channel', channel)
        db.ccache()
        asyncio.create_task(
            client.notice(data.nickname,
            f'Added {channel} to autojoins.'))

    elif command == 'delete':
        db.set_cell(conn, 'channels', 'autojoin',
                    '0', 'channel', channel)
        db.ccache()
        asyncio.create_task(
            client.notice(data.nickname,
            f'Removed {channel} from autojoins.'))
    else:
        asyncio.create_task(
            client.notice(data.nickname,
            'Syntax: .autojoin [add/delete] #[channel_name]'))
        return


@hook.hook('event', ['KICK'])
async def auto_join_on_kick(client, data):
    conn = client.bot.dbs[data.server]

    if _check_if_channel_autojoin(conn, data.target) == False:
        return

    await asyncio.sleep(3)
    asyncio.create_task(client.rawmsg('JOIN', data.target))

