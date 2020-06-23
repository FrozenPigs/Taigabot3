# Standard Libs
import re
import urllib
from asyncio import create_task

# First Party
from core import hook
from util import messaging, request

# Third Party
import requests
from bs4 import BeautifulSoup
from lxml import html

#from urlparse import urlparse

MAX_LENGTH = 200
trimlength = 320

IGNORED_HOSTS = [
    '.onion',
    'localhost',
    # these are handled by their respective plugin
    # more info on some other file
    'youtube.com',    # handled by youtube plugin
    'youtu.be',
    'music.youtube.com',
    'vimeo.com',
    'player.vimeo.com',
    'newegg.com',
    'amazon.com',
    # 'reddit.com',
    'hulu.com',
    'imdb.com',
    'soundcloud.com',
    'spotify.com',
    'twitch.tv',
    'twitter.com',

    # handled on mediawiki.py
    'en.wikipedia.org',
    'encyclopediadramatica.wiki',
]

# 'http' + s optional + ':// ' + anything + '.' + anything
LINK_RE = (r'(https?://\S+\.\S*)', re.I)


@hook.hook('regex', [LINK_RE])
async def process_url(bot, msg):
    url = re.match(re.compile(*LINK_RE), msg.message).group(1)
    parsed = urllib.parse.urlparse(url)
    # parsed contains scheme, netloc, path, params, query, fragment

    # skip unwanted hosts
    # most of them are handled somewhere else anyway
    for ignored in IGNORED_HOSTS:
        if ignored in parsed.netloc:
            return

    result = unmatched_url(url, parsed)
    if result:
        create_task(bot.send_privmsg([msg.target], result))


user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138'
headers = {'User-Agent': user_agent}


def parse_html(stream):
    data = ''
    for chunk in stream.iter_content(chunk_size=256):
        data = data + chunk.decode('utf-8')

        if len(data) > (1024 * 12):    # use only first 12 KiB
            break

    # try to quickly grab the content between <title> and </title>
    # should match most cases, if not just fall back to lxml
    if '<title>' in data and '</title>' in data:
        try:
            quick_title = data[data.find('<title>') + 7:data.find('</title>')]
            return quick_title.strip()
        except Exception as e:
            print(e)
            pass

    parser = html.fromstring(data)

    # try to use the <title> tag first
    title = parser.xpath('//title/text()')
    if not title:
        # fall back to <h1> elements
        title = parser.xpath('//h1/text()')

    if title:
        if type(title) is list and len(title) > 0:
            return title[0].strip()

        elif type(title) is str:
            return title.strip()

    # page definitely has no title
    return 'Untitled'


def unmatched_url(url, parsed):
    # fetch, and hide all errors from the output
    try:
        req = requests.get(url, headers=headers, allow_redirects=True, stream=True, timeout=8)
    except Exception as e:
        print('[!] WARNING couldnt fetch url')
        print(e)
        return None

    # parsing
    domain = parsed.netloc
    content_type = req.headers.get('Content-Type', '')
    size = req.headers.get('Content-Length', 0)
    output = ['[URL]']

    if 'html' in content_type:
        try:
            title = parse_html(req)
        except Exception as e:
            print('[!] WARNING the url caused a parser error')
            print(e)
            title = 'Untitled'

        # TODO handle titles with html entities
        if '&' in title and ';' in title:
            # pls fix
            title = title.replace('&quot;', '"')

        # fucking cloudflare
        if 'Attention Required! | Cloudflare' in title:
            return None

        output.append(title)

    else:
        # very common mime types
        if 'image/' in content_type:
            output.append(content_type.replace('image/', '') + ' image,')
        elif 'video/' in content_type:
            output.append(content_type.replace('video/', '') + ' video,')
        elif 'text/' in content_type:
            output.append('text file,')
        elif 'application/octet-stream' == content_type:
            output.append('binary file,')
        elif 'audio/' in content_type:
            output.append('audio file,')

        # other mime types
        elif 'application/vnd.' in content_type:
            output.append('unknown binary file,')
        elif 'font/' in content_type:
            output.append('font,')

        # i dunno
        else:
            output.append(content_type + ' file,')

        try:
            size = int(size)
        except TypeError:
            size = 0

        # some pages send exactly 503 or 513 bytes of empty padding as an
        # internet explorer 5 and 6 workaround, but since that browser is
        # super dead this should probably be removed.
        # more at https://stackoverflow.com/a/11544049/4301778
        if size in [0, 503, 513]:
            output.append('unknown size')
        else:
            output.append('size: ' + messaging.filesize(size))

    # output formatting
    output = ' '.join(output)

    if len(output) > MAX_LENGTH:
        output = output[:MAX_LENGTH] + '...'

    # add domain to the end
    output = "{} ({})".format(output, domain)

    # show error codes if they appear
    if req.status_code >= 400 and req.status_code < 600:
        output = '{} (error {})'.format(output, req.status_code)

    return output
