# First Party
# Standard Libs
from asyncio import create_task

from core import hook
from util import request

# Third Party
from bs4 import BeautifulSoup

# all icecast 2.4+ servers support the /status-json.xsl api
radios = {
    'r/a/dio': {
        'name': 'R/a/dio',
        'api': 'https://stream.r-a-d.io/status-json.xsl',
        'homepage': 'https://r-a-d.io/',
        'source': 'main.mp3'
    },
    'eden': {
        'name': 'Eden of the west Public Radio',
        'api': 'https://www.edenofthewest.com/radio/8000/status-json.xsl',
        'homepage': 'https://www.edenofthewest.com/',
        'source': 'radio.mp3'
    },
    'ducky': {
        'name': 'just some radio',
        'api': 'https://radio.wolowolo.com:8443/status-json.xsl',
        'homepage': 'https://radio.wolowolo.com/ducky/',
        'source': 'ducky'
    },
    'chiru': {
        'name': 'chiru.no',
        'api': 'https://chiru.no:8080/status-json.xsl',
        'homepage': 'https://chiru.no/',
        'source': 'stream.mp3',
    },
    'flippy': {
        'name': 'flippy radio',
        'api': 'https://radio.wolowolo.com:8443/status-json.xsl',
        'homepage': 'https://radio.wolowolo.com/flippy',
        'source': 'flippy'
    }
}


@hook.hook('command', ['radio'], autohelp=False)
async def radio(bot, msg):
    id = msg.message
    if id not in radios:
        response = "we dont support that radio. try one of the following: " + ", ".join(radios.keys(
        ))
        create_task(bot.send_privmsg([msg.target], response))
        return

    radio = radios[id]

    try:
        data = request.get_json(radio['api'])
    except ValueError:
        response = f"the radio {id} has some server issues right now. try again later"
        create_task(bot.send_privmsg([msg.target], response))
        return

    sources = data.get('icestats', {}).get('source', False)

    if sources is False:
        create_task(bot.send_privmsg([msg.target], f"the radio {id} is offline"))
        return

    def build_message(source):
        title = source.get('title', 'Untitled')
        listeners = source.get('listeners', 0)
        # genre = sourc.get('genre', 'unknown')
        response = (f'{id} is playing \x02{title}\x02 for {listeners}'
                    f' listeners. listen: {radio["homepage"]}')
        return response

    # the icecast api returns either one object (for one stream)
    # or a list of sources (for multiple streams available)
    if isinstance(sources, dict):
        if sources.get('listenurl', '').endswith(radio['source']):
            create_task(bot.send_privmsg([msg.target], build_message(sources)))
            return

    elif isinstance(sources, list):
        for source in sources:
            if source.get('listenurl', '').endswith(radio['source']):
                create_task(bot.send_privmsg([msg.target], build_message(source)))
                return

    # didn't find it
    create_task(bot.send_privmsg([msg.target], f"the radio {id} is offline"))


@hook.hook('command', ['aradio'], autohelp=True)
async def aradio(bot, msg):
    msg.message = 'r/a/dio'
    create_task(radio(bot, msg))


# fallback because chiru.no's api sometimes returns broken json
@hook.hook('command', ['mutantradio', 'muradio'], autohelp=True)
def muradio(bot, msg):
    "radio [url]-- Returns current mutantradio song"
    url = 'https://chiru.no:8080/status.xsl'
    page = request.get_text(url)
    soup = BeautifulSoup(page, 'lxml')
    stats = soup.find_all('td', 'streamstats')
    # for i in stats:
    #     print i
    # print stats[2], stats[4], stats[5]
    listeners = stats[2].text
    genre = stats[4].text
    # url = stats[5].text
    song = stats[6].text.strip()
    response = (f"[muradio] Playing: {song}, Genre: {genre}, Listening: {listeners},"
                " URL: https://chiru.no/")
    create_task(bot.send_privmsg([msg.target], response))
