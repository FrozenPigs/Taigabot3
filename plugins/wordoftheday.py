# Standard Libs
from asyncio import create_task

# First Party
from core import hook
from util import iterable, request

# Third Party
from bs4 import BeautifulSoup

# word of the day plugin by ine (2020)


@hook.hook('command', ['wordoftheday'])
async def wordoftheday(bot, msg):
    html = request.get('https://www.merriam-webster.com/word-of-the-day')
    soup = BeautifulSoup(html)

    word = soup.find('div', attrs={'class': 'word-and-pronunciation'}).find('h1').text
    paragraphs = soup.find('div', attrs={'class': 'wod-definition-container'}).find_all('p')

    definitions = []

    for paragraph in iterable.limit(4, paragraphs):
        definitions.append(paragraph.text.strip())

    output = u"The word of the day is \x02{}\x02: {}".format(word, '; '.join(definitions))

    if len(output) > 320:
        output = output[:320] + '... More at https://www.merriam-webster.com/word-of-the-day'

    create_task(bot.send_privmsg([msg.target], output))
