# youtube search plugin
# author: nojusr
#
# usage:
#  .yt [SEARCH TERM]       -- search for a video on youtube.
#                             links are shortened via is.gd
#
# note: to configure this plugin you need to add a youtube api key
#       into the "api_keys" section of config.json. Example:
#       "api_keys": { "youtube": "XXXXXXXXXXXXXXXXX" }


from core import hook

import asyncio
import requests

youtube_api_url = 'https://www.googleapis.com/youtube/v3/search'

@hook.hook('command', ['yt', 'youtube'])
async def ytsearch(client, data):
    
    split = data.split_message

    try:
        yt_key = client.bot.config['api_keys']['youtube']
    except KeyError:
        asyncio.create_task(
            client.message(
                data.target,
                ('No Youtube API key found. Please create a Google '
                 'API account and add it to the config file.')))
        return
    
    req_params = {'part': 'snippet', 'key' : yt_key, 'maxResults': '1',
                  'order': 'relevance', 'q': ' '.join(split) }

    r = requests.get(youtube_api_url, req_params)
    
    if r.status_code == 403:
        asyncio.create_task(client.message(data.target,'Youtube API quota exceeded.'))
    
    if r.status_code != 200:
        print(f'YOUTUBE_DEBUG: network error: {r.status_code}')
        print(f'YOUTUBE_DEBUG: {r.text}')
        asyncio.create_task(client.message(data.target,'Network error occured.'))

    output_url = 'https://www.youtube.com/watch?v='
    
    try:
        first_item = r.json()['items'][0]
    except KeyError:
        print('YOUTUBE_DEBUG: failed to get first item in response json')
        return
    
    print(first_item)
    link = first_item['id']['videoId']
    title = first_item['snippet']['title']
    
    output = f'{output_url+link} -- {title}'
    
    asyncio.create_task(client.message(data.target, output))














