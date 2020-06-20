# Standard Libs
import random
import re
import time
import urllib
from asyncio import create_task

# First Party
from core import hook
from util import request, timeu

youtube_re = (
    r'(https?:\/\/)?(www\.)?(?:youtube.*?(?:v=|\/v\/)|youtu\\.be\/)([-_a-zA-Z0-9]{11})?(.*)', re.I)
video_id_re = r'([-_a-zA-Z0-9]{11})'

base_url = 'https://www.googleapis.com/youtube/v3/'
search_api_url = base_url + 'search?part=id,snippet'
api_url = base_url + 'videos?part=snippet,statistics,contentDetails'
video_url = "http://youtu.be/{}"


def plural(num=0, text=''):
    return "{:,} {}{}".format(num, text, "s"[num == 1:])


def get_video_description(key, video_id, bot):
    url = api_url + f'&id={request.urlencode(video_id)}&key={request.urlencode(key)}'
    print(url)
    try:
        req = request.get_json(url)
    except:
        key = bot.full_config.api_keys.get("public_google_key")
        req = request.get_json(url)

    if req.get('error'):
        return

    data = req['items'][0]

    title = filter(None, data['snippet']['title'].split(' '))
    title = ' '.join(map(lambda s: s.strip(), title))
    out = u'\x02{}\x02'.format(title)

    try:
        data['contentDetails'].get('duration')
    except KeyError:
        return out

    length = data['contentDetails']['duration']
    timelist = re.findall('(\d+[DHMS])', length)

    seconds = 0
    for t in timelist:
        t_field = int(t[:-1])
        if t[-1:] == 'D': seconds += 86400 * t_field
        elif t[-1:] == 'H': seconds += 3600 * t_field
        elif t[-1:] == 'M': seconds += 60 * t_field
        elif t[-1:] == 'S': seconds += t_field

    out += u' - length \x02{}\x02'.format(timeu.format_time(seconds, simple=True))

    try:
        data['statistics']
    except KeyError:
        return out
    stats = data['statistics']
    try:
        likes = u"\u2191{:,}".format(int(stats['likeCount']))
        dislikes = u"\u2193{:,}".format(int(stats['dislikeCount']))
        try:
            percent = 100 * float(stats['likeCount']) / (
                int(stats['likeCount']) + int(stats['dislikeCount']))
        except ZeroDivisionError:
            percent = 0
    except KeyError:
        likes = '\x0304likes disabled\x03'
        dislikes = '\x0304dislikes disabled\x03'
        percent = 0
    if percent >= 50:
        out += u' - \x0309{}\x03, \x0304{}\x03 (\x02\x0309{:.1f}\x03\x02%)'.format(
            likes, dislikes, percent)
    else:
        out += u' - \x0309{}\x03, \x0304{}\x03 (\x0304\x02{:.1f}\x02%\x03)'.format(
            likes, dislikes, percent)

    views = int(stats['viewCount'])
    out += u' - \x02{:,}\x02 {}{}'.format(views, 'view', "s"[views == 1:])

    uploader = data['snippet']['channelTitle']

    try:
        upload_time = time.strptime(data['snippet']['publishedAt'], "%Y-%m-%dT%H:%M:%S.000Z")
    except Exception as e:
        print(e)
        upload_time = time.strptime(data['snippet']['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")
    out += u' - \x02{}\x02 on \x02{}\x02'.format(uploader, time.strftime("%Y.%m.%d", upload_time))

    try:
        data['contentDetails']['contentRating']
        if data['contentDetails']['contentRating'] == {}:
            return out
    except KeyError:
        return out

    out += u' - \x034NSFW\x02'

    return out


@hook.hook('regex', [youtube_re])
async def youtube_url(bot, msg):
    key = bot.full_config.api_keys.get("google")
    match = re.search(video_id_re, msg.message).group(0)

    create_task(bot.send_privmsg([msg.target], get_video_description(key, match, bot)))


@hook.hook('command', ['hooktube', 'ht', 'yt', 'youtube'])
async def youtube(bot, msg):
    """youtube <query> -- Returns the first YouTube search result for <query>."""
    key = bot.full_config.api_keys.get("google")
    url = search_api_url + f'&type=video&key={key}&q={request.urlencode(msg.message)}'
    try:
        req = request.get_json(url)
    except:
        key = bot.full_config.api_keys.get("public_google_key")
        req = request.get_json(url)
    if 'error' in req:
        create_task(bot.send_privmsg([msg.target], 'Error performing search.'))
        return

    if req['pageInfo']['totalResults'] == 0:
        create_task(bot.send_privmsg([msg.target], 'No results found.'))
        return

    video_id = req['items'][0]['id']['videoId']
    if msg.command[1:] == 'hooktube' or msg.command[1:] == 'ht':
        create_task(
            bot.send_privmsg([msg.target],
                             get_video_description(key, video_id) + u" - " + video_url.replace(
                                 'youtu.be', 'hooktube.com', bot).format(video_id)))
    else:
        print(get_video_description(key, video_id, bot))
        create_task(
            bot.send_privmsg([msg.target],
                             get_video_description(key, video_id, bot) + " - " +
                             video_url.format(video_id)))


@hook.hook('command', ['ytime', 'youtime'])
async def youtime(bot, msg):
    """youtime <query> -- Gets the total run time of the first YouTube search result for <query>."""
    inp = msg.message
    key = bot.full_config.api_keys.get("google")
    url = search_api_url + f'&type=video&key={key}&q={request.urlencode(inp)}'
    req = request.get_json(url)

    if 'error' in req:
        create_task(bot.send_privmsg([msg.target], 'Error performing search.'))
        return

    if req['pageInfo']['totalResults'] == 0:
        create_task(bot.send_privmsg([msg.target], 'No results found.'))
        return

    video_id = req['items'][0]['id']['videoId']
    url = api_url + f'&id={request.urlencode(video_id)}&key={request.urlencode(key)}'
    req = request.get_json(url)

    data = req['items'][0]

    length = data['contentDetails']['duration']
    timelist = re.findall('(\d+[DHMS])', length)

    seconds = 0
    for t in timelist:
        t_field = int(t[:-1])
        if t[-1:] == 'D': seconds += 86400 * t_field
        elif t[-1:] == 'H': seconds += 3600 * t_field
        elif t[-1:] == 'M': seconds += 60 * t_field
        elif t[-1:] == 'S': seconds += t_field

    views = int(data['statistics']['viewCount'])
    total = int(seconds * views)

    length_text = timeu.format_time(seconds, simple=True)
    total_text = timeu.format_time(total, accuracy=8)
    create_task(
        bot.send_privmsg([
            msg.target
        ], 'The video \x02{}\x02 has a length of {} and has been viewed {:,} times for a total run time of {}!'
                         .format(data['snippet']['title'], length_text, views, total_text)))


# already broken
# ytpl_re = (r'(https?:\/\/)?(www\.)(youtube.com/playlist)(:[0-9]+)?(.*)', re.I)

# @hook.hook('regex', [ytpl_re])
# async def youtubeplaylist_url(bot, msg):
#     location = re.match(re.compile(*ytpl_re), msg.message).groups()[-1].split('=')[-1]

#     try:
#         soup = request.get_soup("https://www.youtube.com/playlist?list=" + location)
#     except Exception:
#         create_task(bot.send_privmsg([msg.target], "\x034\x02Invalid response."))
#         return

#     title = soup.find('title').text.split('-')[0].strip()
#     print(soup.find_all('a'))
#     author = soup.find('img', {'class': 'channel-header-profile-image'})['title']
#     numvideos = soup.find('ul', {'class': 'pl-header-details'}).findAll('li')[1].string
#     numvideos = re.sub("\D", "", numvideos)
#     views = soup.find('ul', {'class': 'pl-header-details'}).findAll('li')[2].string
#     views = re.sub("\D", "", views)

#     create_task(
#         bot.send_privmsg([
#             msg.target
#         ], f"\x02{title}\x02 - \x02{views}\x02 views - \x02{numvideos}\x02 videos - \x02{author}\x02"
#                          ))
