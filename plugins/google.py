# Standard Libs
import re
from asyncio import create_task

# First Party
from core import hook
from util import messaging, request

API_URL = 'https://www.googleapis.com/customsearch/v1'


@hook.hook('command', ['search', 'g', 'google'], autohelp=True)
async def google(bot, msg):
    """google <query> -- Returns first google search result for <query>."""
    inp = request.urlencode(msg.message)

    url = API_URL + u'?key={}&cx={}&num=1&safe=off&q={}'
    cx = bot.full_config.api_keys['googleimage']
    search = '+'.join(inp.split())
    key = bot.full_config.api_keys['google']
    result = request.get_json(url.format(key, cx, search))['items'][0]

    title = result['title']
    content = messaging.remove_newlines(result['snippet'])
    link = result['link']

    create_task(bot.send_privmsg([msg.target], f'{link} -- \x02{title}\x02: "{content}"'))


#@hook.regex(r'^\>(.*\.(gif|jpe?g|png|tiff|bmp))$', re.I)
@hook.hook('command', ['gi', 'image'], autohelp=True)
async def image(bot, msg):
    """image <query> -- Returns the first Google Image result for <query>."""
    if '.' in msg.message:
        inp, filename = msg.message.split('.')
    else:
        inp, filetype = msg.message, None

    cx = bot.full_config.api_keys['googleimage']
    search = '+'.join(inp.split())
    key = bot.full_config.api_keys['google']

    if filetype:
        url = API_URL + u'?key={}&cx={}&searchType=image&num=1&safe=off&q={}&fileType={}'
        result = request.get_json(url.format(key, cx, search, filetype))['items'][0]['link']
    else:
        url = API_URL + u'?key={}&cx={}&searchType=image&num=1&safe=off&q={}'
        result = request.get_json(url.format(key, cx, search))['items'][0]['link']

    create_task(bot.send_privmsg([msg.target], result))
