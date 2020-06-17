# Standard Libs
import time
from asyncio import create_task

# First Party
from core import hook
from util import iterable, request

# Third Party
from bs4 import BeautifulSoup

# distrowatch ranking plugin by ine (2020)

# distrowatch updates around midnight
# update cache every 2 hours
cache = ''
cache_stale = 2 * 60 * 60
last_refresh = time.time()

data_limit = 4    # how many distros per each dataset
allowed_datasets = [
    'Last 12 months',    # popularity ranking
    'Last 1 month',
    'Trending past 12 months',    # trending list
    'Trending past 1 month',
]


def refresh_cache():
    print('[+] refreshing distrowatch cache')
    output = '[DistroWatch]'

    def parse_table(data):
        global data_limit
        distro_names = []

        for distro in iterable.limit(data_limit, data):
            distro_names.append(distro.text.strip())

        return ', '.join(distro_names)

    # most popular distros in the last 12, 6 and 1 months
    html = request.get('https://distrowatch.com/dwres.php?resource=popularity')
    soup = BeautifulSoup(html, 'lxml')
    tables = soup.select('td.NewsText tr td table')

    for table in tables:
        header = table.find('th', attrs={'class': 'Invert'})
        data = table.find_all('td', attrs={'class': 'phr2'})

        # skip table if it doesn't have distro info
        if header is None or data is None:
            continue

        # skip this table if its not wanted
        header = header.text.strip()
        if header not in allowed_datasets:
            continue

        output = output + ' \x02Popular\x02 (' + header.replace('Last ', '') + '): '
        output = output + parse_table(data) + '.'

    # trending distros in the past 12, 6 and 1 months
    html = request.get('https://distrowatch.com/dwres.php?resource=trending')
    soup = BeautifulSoup(html, 'lxml')
    tables = soup.select('table table table table.News')

    for table in tables:
        header = table.find('th', attrs={'class': 'Invert'})
        data = table.parent.find_all('td', attrs={'class': 'phr2'})

        if header is None or data is None:
            continue

        # skip this table if its not wanted
        header = header.text.strip()
        if header not in allowed_datasets:
            continue

        output = output + ' \x02Trending\x02 (' + header.replace('Trending ', '') + '): '
        output = output + parse_table(data) + '.'

    global cache
    cache = output


@hook.hook('command', ['distro'])
async def distro(bot, msg):
    # update if time passed is more than cache_stale
    global last_refresh, cache_stale, cache
    now = time.time()
    if now - last_refresh > cache_stale:
        refresh_cache()
        last_refresh = now

    create_task(bot.send_privmsg([msg.target], cache))


refresh_cache()
