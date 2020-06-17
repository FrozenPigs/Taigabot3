# Standard Libs
from asyncio import create_task

# First Party
from core import hook
from util import request

# Third Party
from bs4 import BeautifulSoup

# w3c validator plugin by ine (2020)


@hook.hook('command', ['w3c', 'validate'])
async def validate(bot, msg):
    """validate <url> -- Runs url through the w3c markup validator."""
    inp = msg.message
    if not inp.startswith('http'):
        inp = 'https://' + inp

    url = 'https://validator.w3.org/nu/?doc=' + request.urlencode(inp)
    html = request.get(url)
    soup = BeautifulSoup(html, 'lxml')
    results = soup.find('div', attrs={'id': 'results'})

    errors = len(results.find_all('li', attrs={'class': 'error'}))
    warns = len(results.find_all('li', attrs={'class': 'warning'}))
    info = len(results.find_all('li', attrs={'class': 'info'}))

    if errors == 0 and warns == 0 and info == 0:
        create_task(bot.send_privmsg([msg.target], "[w3c] Successfully validated with no errors"))

    create_task(
        bot.send_privmsg([msg.target],
                         f'[w3c] Found {errors} errors, {warns} warnings and {info} notices.'))
