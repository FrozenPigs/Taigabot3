# Standard Libs
from asyncio import create_task

# First Party
from core import hook
from util import request

# Third Party
from bs4 import BeautifulSoup

# us debt plugin by ine (2020)


def parse(html):
    soup = BeautifulSoup(html, 'lxml')
    query = soup.find(id='debtDisplay')

    if query is None:
        return "unknown"
    else:
        return "$" + query.text


@hook.hook('command', ['debt'])
async def debt(bot, msg):
    """debt -- returns the us national debt"""

    url = "https://commodity.com/debt-clock/us/"
    html = request.get(url)
    debt = parse(html)

    create_task(bot.send_privmsg([msg.target], f'Current US Debt: \x02{debt}\x02'))
