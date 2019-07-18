# This is a plugin that makes the bot resistant from being kicked.
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

@hook.hook('command', ['autojoin'], gadmin=True)
async def auto_join(client, data):
    asyncio.create_task(client.message(data.target, 'WIP'))
