# Standard Libs
from asyncio import create_task

# First Party
from core import hook
from util import request

# Third Party
from bs4 import BeautifulSoup


def fetch(start, dest):
    start = request.urlencode(start)
    dest = request.urlencode(dest)
    url = "http://www.travelmath.com/flying-distance/from/{}/to/{}".format(start, dest)
    html = request.get(url)
    return html


def parse(html):
    soup = BeautifulSoup(html, 'lxml')
    query = soup.find('h1', {'class': 'main'})
    distance = soup.find('h3', {'class': 'space'})

    if query:
        query = query.get_text().strip()

    if distance:
        distance = distance.get_text().strip()

    return query, distance


@hook.hook('command', ['distance'], autohelp=True)
async def distance(bot, msg):
    "distance <start> to <end> -- Calculate the distance between 2 places."
    inp = msg.message
    if 'from ' in inp:
        inp = inp.replace('from ', '')
    start = inp.split(" to ")[0].strip()
    dest = inp.split(" to ")[1].strip()

    html = fetch(start, dest)
    query, distance = parse(html)

    if not distance:
        create_task(
            bot.send_privmsg([msg.target],
                             "Could not calculate the distance from {start} to {dest}."))
        return

    result = u"Distance: {} {}".format(query, distance)
    create_task(bot.send_privmsg([msg.target], result))
