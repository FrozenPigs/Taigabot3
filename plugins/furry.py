# Standard Libs
import random
from asyncio import create_task

# First Party
from core import hook
from util import request

# furry booru plugin by ararouge (2020)

cache = []
lastsearch = ''


def refresh_furry_cache(inp):
    print("[+] refreshing furry cache")

    global cache
    global lastsearch
    cache = []
    search = inp

    # these are special search queries in the booru
    for word in ['explicit', 'safe', 'nsfw', 'sfw']:
        search = search.replace(word, 'rating:' + word)

    lastsearch = search

    if inp == '':
        postjson = request.get_json('http://e621.net/posts.json?limit=10')
    else:
        postjson = request.get_json('http://e621.net/posts.json?limit=10&tags={}'.format(
            request.urlencode(search)))
    posts = postjson["posts"]

    for i in range(len(posts)):
        post = posts[i]
        id = post["id"]
        score = post["score"]["total"]
        url = post["file"]["url"]
        rating = post["rating"]
        tags = ", ".join(post["tags"]["general"])
        cache.append((id, score, url, rating, tags))

    random.shuffle(cache)


@hook.hook('command', ['e621', 'furry'])
async def furry(bot, msg):
    global lastsearch
    global cache

    inp = msg.message.lower()
    if inp == msg.command:
        inp = ''

    if inp not in lastsearch or len(cache) < 2:
        refresh_furry_cache(inp)

    lastsearch = inp

    if len(cache) == 0:
        return 'No Results'

    id, score, url, rating, tags = cache.pop()

    if rating == 'e':
        rating = "\x02\x034NSFW\x03\x02"
    elif rating == 'q':
        rating = "\x02Questionable\x02"
    elif rating == 's':
        rating = "\x02\x033Safe\x03\x02"

    create_task(
        bot.send_privmsg([msg.target],
                         f'\x02[{id}]\x02 Score: \x02{score}\x02 - Rating: {rating} - {url}')
