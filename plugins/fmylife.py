# Standard Libs
from asyncio import create_task

# First Party
from core import hook
from util import request

# Third Party
from bs4 import BeautifulSoup

# fuck my life plugin by ine (2020)

cache = []


def refresh_cache():
    print('[+] refreshing fmylife cache')
    html = request.get('https://www.fmylife.com/random')
    soup = BeautifulSoup(html, 'lxml')
    posts = soup.find_all('a', attrs={'class': 'article-link'})

    for post in posts:
        id = post['href'].split('_')[1].split('.')[0]
        text = post.text.strip()
        cache.append((id, text))


@hook.hook('command', ['fuckmylife', 'fml'])
async def fml(bot, msg):
    "fml -- Gets a random quote from fmyfife.com."

    if len(cache) < 2:
        refresh_cache()

    id, text = cache.pop()
    create_task(bot.send_privmsg([msg.target], f'(#{id}) {text}'))


refresh_cache()
