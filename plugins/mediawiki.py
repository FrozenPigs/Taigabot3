# Standard Libs
from asyncio import create_task

# First Party
from core import hook
from util import request

# Third Party
from bs4 import BeautifulSoup

# mediawiki plugin by ine (2020)

API_QUERYPARAMS = "action=opensearch&format=json&limit=2&search="
OUTPUT_LIMIT = 240    # character limit
INSTANCES = {
    'encyclopediadramatica': {
        'name': 'Encyclopedia Dramatica',
        'search': 'https://encyclopediadramatica.wiki/api.php?' + API_QUERYPARAMS,
        'regex': r'(https?://encyclopediadramatica\.wiki/index\.php/[^ ]+)'
    },
    'wikipedia_en': {
        'name': 'Wikipedia',
        'search': 'https://en.wikipedia.org/w/api.php?' + API_QUERYPARAMS,
        'regex': r'(https?://en\.wikipedia\.org/wiki/[^ ]+)'
    },
}


def search(instance, query):
    if instance not in INSTANCES:
        return

    wiki = INSTANCES[instance]
    search = request.get_json(wiki['search'] + request.urlencode(query))

    titles = search[1]
    descriptions = search[2]
    urls = search[3]

    return (titles, descriptions, urls)


def scrape_text(url):
    html = request.get(url)
    soup = BeautifulSoup(html, 'lxml')
    title = soup.find('h1', attrs={'id': 'firstHeading'})
    body = soup.find('div', attrs={'id': 'mw-content-text'})

    if title:
        title = title.text.strip()

    if body is None:
        return "Error reading the article"

    output = []
    for paragraph in body.find_all('p'):
        text = paragraph.text.strip()
        if len(text) > 4:    # skip empty paragraphs
            output.append(text)

    output = ' '.join(output)

    return output, title


def command_wrapper(instance, inp):
    titles, descriptions, urls = search(instance, inp)

    if not titles:
        return "No results found."

    title = titles[0]
    url = urls[0]

    # `real_title` shows the article title after a
    # redirect. its generally longer than `title`
    output, real_title = scrape_text(url)

    if len(output) > OUTPUT_LIMIT:
        output = output[:OUTPUT_LIMIT] + '...'

    if title == real_title:
        return u'\x02{} -\x02 {} \x02-\x02 {}'.format(title, output, url)
    else:
        return u'\x02{} -\x02 {} \x02-\x02 {} (redirected from {})'.format(
            real_title, output, url, title)


# def url_wrapper(instance, url):
#     output, title = scrape_text(url)

#     if len(output) > OUTPUT_LIMIT:
#         output = output[:OUTPUT_LIMIT] + '...'

#     return u'\x02{} -\x02 {}'.format(title, output)

# @hook.regex(INSTANCES['encyclopediadramatica']['regex'])
# def drama_url(match):
#     url = match.group(1)
#     return url_wrapper('encyclopediadramatica', url)


@hook.hook('command', ['encyclopediadramatica', 'drama'])
async def drama(bot, msg):
    "drama <article> -- search an Encyclopedia Dramatica article"
    create_task(
        bot.send_privmsg([msg.target], command_wrapper('encyclopediadramatica', msg.message)))


# @hook.regex(INSTANCES['wikipedia_en']['regex'])
# def wikipedia_url(match):
#     url = match.group(1)
#     return url_wrapper('wikipedia_en', url)


@hook.hook('command', ['wiki', 'wikipedia'])
async def wikipedia(bot, msg):
    "wikipedia <article> -- search a wikipedia article"
    create_task(bot.send_privmsg([msg.target], command_wrapper('wikipedia_en', msg.message)))
