# Standard Libs
import random
import re
from asyncio import create_task

# First Party
from core import hook
from util import request

yandere_cache = []


def refresh_yandere_cache():
    "gets a page of random yande.re posts and puts them into a dictionary "
    url = 'https://yande.re/post?page=%s' % random.randint(1, 11000)
    soup = request.get_soup(url)

    for result in soup.findAll('li'):
        title = result.find('img', {'class': re.compile(r'\bpreview\b')})    #['title']
        img = result.find('a', {'class': re.compile(r'\bdirectlink\b')})    #['href']
        if img and title:
            yandere_cache.append(
                (result['id'].replace('p', ''), title['title'].split(' User')[0], img['href']))


def get_yandere_tags(inp):
    url = 'https://yande.re/post?tags=%s' % inp.replace(' ', '_')
    soup = request.get_soup(url)
    imagelist = soup.find('ul', {'id': 'post-list-posts'}).findAll('li')
    image = imagelist[random.randint(0, len(imagelist) - 1)]
    imageid = image["id"].replace('p', '')
    title = image.find('img')['title']
    src = image.find('a', {'class': 'directlink'})["href"]
    return u"\x034NSFW\x03: \x02({})\x02 {}: {}".format(imageid, title, src)


#do an initial refresh of the cache
refresh_yandere_cache()


@hook.hook('command', ['yandere'])
async def yandere(bot, msg):
    "tandere [tags] -- Yande.re -- Gets a random image from Yande.re."

    if msg.message != msg.command:
        create_task(bot.send_privmsg([msg.target], get_yandere_tags(msg.message)))
        return

    id, title, image = yandere_cache.pop()
    create_task(
        bot.send_privmsg([msg.target], f'\x034NSFW\x03: \x02({id})\x02 {title[:75]}: {image}'))
    if len(yandere_cache) < 3:
        refresh_yandere_cache()
