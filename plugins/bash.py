# Standard Libs
from asyncio import create_task

# First Party
from core import hook
from util import request

# Third Party
from bs4 import BeautifulSoup

# bash.org plugin by ine (2020)

cache = []


def refresh_cache():
    "gets a page of random bash.org quotes and puts them into a dictionary "
    print("[+] refreshing bash cache")
    html = request.get('http://bash.org/?random')
    soup = BeautifulSoup(html, 'lxml')
    quote_infos = soup.find_all('p', {'class': 'quote'})
    quotes = soup.find_all('p', {'class': 'qt'})

    num = 0
    while num < len(quotes):
        quote = quotes[num].text.replace('\n', ' ').replace('\r', ' |')
        id = quote_infos[num].contents[0].text
        votes = quote_infos[num].find('font').text
        cache.append((id, votes, quote))
        num += 1


def get_bash_quote(inp):
    try:
        inp = request.urlencode(inp)
        html = request.get('http://bash.org/?' + inp)
        soup = BeautifulSoup(html, 'lxml')
        quote_info = soup.find('p', {'class': 'quote'})
        quote = soup.find('p', {'class': 'qt'}).text.replace('\n', ' ').replace('\r', ' |')

        id = quote_info.contents[0].text
        votes = quote_info.find('font').text
        return u'\x02{}\x02 ({} votes): {}'.format(id, votes, quote)
    except Exception as e:
        print(e)
        return "No quote found."


@hook.hook('command', ['bash'])
async def bash(bot, msg):
    "bash <id> -- Gets a random quote from Bash.org, or returns a specific id."
    inp = msg.message
    if inp != msg.command:
        create_task(bot.send_privmsg([msg.target], get_bash_quote(inp)))
        return

    id, votes, text = cache.pop()
    if len(cache) < 3:
        refresh_cache()

    create_task(bot.send_privmsg([msg.target], f'\x02{id}\x02 ({votes} votes): {text}'))


refresh_cache()
