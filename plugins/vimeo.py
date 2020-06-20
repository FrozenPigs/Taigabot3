# Standard Libs
import re
from asyncio import create_task

# First Party
from core import hook
from util import request, timeu

# vimeo info plugin by ine (2020)
# the v2 api is deprecated and only does simple public video information
# new one is at https://api.vimeo.com/videos/{id} but needs a key


def get_info(id):
    info = request.get_json('http://vimeo.com/api/v2/video/' + id + '.json')

    if not info or len(info) == 0:
        return

    title = info[0]['title']
    print(info)
    length = timeu.format_time(info[0]["duration"], simple=True)
    try:
        likes = format(info[0]['stats_number_of_likes'], ',d')
    except KeyError:
        likes = 'Unknown'
    try:
        views = format(info[0]['stats_number_of_plays'], ',d')
    except KeyError:
        views = 'Unknown'
    uploader = info[0]['user_name']
    upload_date = info[0]['upload_date']

    output = []
    output.append('\x02' + title + '\x02')
    output.append('length \x02' + length + '\x02')
    output.append(likes + ' likes')
    output.append(views + ' views')
    output.append('\x02' + uploader + '\x02 on ' + upload_date)

    return ' - '.join(output)


@hook.hook('regex', [
    r'https?://vimeo\.com/([0-9]+)/?', r'https?://player\.vimeo\.com/video/([0-9]+)'
])
async def vimeo_url(bot, msg):
    """<vimeo url> -- automatically returns information on the Vimeo video at <url>"""
    match = re.search(r'([0-9]+)', msg.message).group(1)
    print(match)
    output = get_info(match)

    if not output:
        return

    create_task(bot.send_privmsg([msg.target], output))
