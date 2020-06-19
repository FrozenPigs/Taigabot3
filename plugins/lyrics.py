# Standard Libs
import json
from asyncio import create_task

# First Party
from core import hook

# Third Party
import requests

url = "http://www.genius.com/search?q={}"


@hook.hook('command', ['genius', 'lyrics'], autohelp=True)
async def lyrics(bot, msg):
    """lyrics <search> - Search genius.com for song lyrics"""
    base_url = "http://api.genius.com"
    headers = {'Authorization': bot.full_config.api_keys['genius']}
    search_url = base_url + "/search"
    song_title = msg.message
    params = {'q': song_title}
    response = requests.get(search_url, params=params, headers=headers)
    create_task(
        bot.send_privmsg([msg.target],
                         json.loads(response.text)['response']['hits'][0]['result']['url']))
