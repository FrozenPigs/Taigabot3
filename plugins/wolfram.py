# wolfram alpha plugin
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
# .wa, .calc [QUESTION]              -- ask wolfram alpha any
#                                       mathematical/statistics question
# config:
#   you need to create an appID in https://developer.wolframalpha.com/,
#   and put it in config.json like this:
#     "api_keys": {
#       "wolfram_alpha": "XXXXX-XXXXXX"
#     },

from core import hook

import asyncio
import requests

wolfram_api_url = 'https://api.wolframalpha.com/v1/result'


def _get_wa_api_key(client):
    """This function tries to get the wolfram alpha appID from config"""
    try:
        wa_key = client.bot.config['api_keys']['wolfram_alpha']
        return wa_key
    except KeyError:
        return ''


@hook.hook('command', ['wa', 'calc', 'math'])
async def wolfram(client, data):
    """
    This command interfaces with the wolfram alpha API to get
    mathematical and statistical awnsers
    """

    split = data.split_message

    wa_key = _get_wa_api_key(client)

    print(f'WOLFRAM_DEBUG: wa_key: {wa_key}')

    if wa_key == '':
        asyncio.create_task(client.message(data.target,
                            ('No WolframAlpha appID found. '
                             'Ask your nearest bot admin to '
                             'get one and add it into the config.')))
        return

    query = ' '.join(split)

    req_data = {'appid': wa_key, 'i': query, 'units': 'metric'}

    r = requests.get(wolfram_api_url, req_data)
    print(f'WOLFRAM_DEBUG: final url of request: {r.url}')
    print(f'WOLFRAM_DEBUG: response: {r}')
    print(f'WOLFRAM_DEBUG: actual awnser: {r.text}')

    if r.status_code == 200:
        asyncio.create_task(client.message(data.target, r.text))
    elif r.status_code == 501:
        asyncio.create_task(client.message(data.target,
                            ('Wolfram Alpha returned an error. '
                             'Did you phrase your question correclty?')))
    elif r.status_code == 400:
        asyncio.create_task(client.message(data.target,
                            ('Wolfram Alpha returned an error. '
                             'Did you enter a question?')))
    else:
        print(f'WOLFRAM_ERROR: response_code: {r.status_code}')
        asyncio.create_task(client.message(data.target,
                            'Unknown network error occured.'))
