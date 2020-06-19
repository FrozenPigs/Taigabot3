# bible/koran plugin by ine (2020)
# First Party
# Standard Libs
# Standard Libs
# Standard Libs
# Standard Libs
# Standard Libs
# Standard Libs
# Standard Libs
from asyncio import create_task

# First Party
from core import hook
from util import messaging, request

# Third Party
from bs4 import BeautifulSoup


@hook.hook('command', ['god', 'bible'], autohelp=True)
async def bible(bot, msg):
    """bible <passage> -- gets <passage> from the Bible (ESV)"""

    API_KEY = bot.full_config.api_keys.get('english_bible', None)

    if API_KEY is None:
        create_task(bot.send_privmsg([msg.target], 'Bible error: no API key configured'))
        return

    url = "https://api.esv.org/v3/passage/text/?q=" + request.urlencode(msg.message)
    json = request.get_json(url, headers={"Authorization": "Token " + API_KEY})

    if 'detail' in json:
        create_task(bot.send_privmsg([msg.target], 'Bible error (lol): ' + json['detail']))
        return

    if 'passages' in json and len(json['passages']) == 0:
        create_task(bot.send_privmsg([msg.target], '[Bible] Not found'))
        return

    output = '[Bible]'

    if 'canonical' in json:
        output = output + ' \x02' + json['canonical'] + '\x02:'

    if 'passages' in json:
        output = output + ' ' + messaging.compress_whitespace('. '.join(json['passages']))

    if len(output) > 320:
        output = output[:320] + '...'

    create_task(bot.send_privmsg([msg.target], output))


@hook.hook('command', ['allah', 'koran'], autohelp=True)
async def koran(bot, msg):
    "koran <chapter.verse> -- gets <chapter.verse> from the Koran. it can also search any text."

    url = 'https://quod.lib.umich.edu/cgi/k/koran/koran-idx?type=simple&q1=' + request.urlencode(
        msg.message)
    html = request.get(url)
    soup = BeautifulSoup(html, 'lxml')
    query = soup.find_all('li')

    if not query or len(query) == 0:
        create_task(bot.send_privmsg([msg.target], 'No results for ' + msg.message))
        return

    output = '[Koran] '
    lines = []

    for li in query[:4]:
        lines.append(messaging.compress_whitespace(li.text))

    output = output + ' '.join(lines)

    if len(output) > 320:
        output = output[:320] + '...'

    create_task(bot.send_privmsg([msg.target], output))
