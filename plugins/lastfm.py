# Standard Libs
import time
import urllib
from asyncio import create_task
from datetime import datetime

# First Party
from core import db, hook
from util import request


@hook.hook('command', ['band'])
async def band(bot, msg):
    artist = msg.message
    api_key = bot.full_config.api_keys['lastfm']
    api_url = 'http://ws.audioscrobbler.com/2.0/?format=json&'
    params = {'method': 'artist.getInfo', 'artist': artist, 'api_key': api_key}
    response = request.get_json(api_url + urllib.parse.urlencode(params))
    plays = response['artist']['stats']['playcount']
    listeners = response['artist']['stats']['listeners']
    similar = []
    for i in response['artist']['similar']['artist']:
        similar.append(i['name'])
    similar = ", ".join(similar)
    tags = []
    for i in response['artist']['tags']['tag']:
        tags.append(i['name'])
    tags = ', '.join(tags)
    create_task(
        bot.send_privmsg([msg.target], artist + ' have ' + plays + ' plays and ' + listeners +
                         '. Similar artists include ' + similar + '. Tags: (' + tags + ').'))


@hook.hook('command', ['np', 'lastfm'])
async def lastfm(bot, msg):
    """lastfm [username|@nick] -- Displays the current/last played track."""
    api_key = bot.full_config.api_keys['lastfm']
    api_url = 'http://ws.audioscrobbler.com/2.0/?format=json&'
    save = False
    inp = msg.message
    nick = msg.nickname
    db.add_column(bot.db, 'users', 'lastfm')
    if '@' in inp:
        nick = inp.split('@')[1].strip()
        user = db.get_cell(bot.db, 'users', 'lastfm', 'nick', nick)
        if not user:
            create_task(bot.send_privmsg([msg.target], f'No lastfm user stored for {nick}.'))
            return
    else:
        user = db.get_cell(bot.db, 'users', 'lastfm', 'nick', nick)[0][0]
        if inp == msg.command or not inp:
            if user == None:
                create_task(
                    bot.send_notice([msg.nickname],
                                    f'[{msg.target}]: {msg.command[0]}{lastfm.__doc__}'))
                return
        else:
            if user == None:
                save = True
            if ' save' in inp:
                save = True
            user = inp.split()[0]

    if user == 'None':
        return
    params = {'method': 'user.getRecentTracks', 'user': user, 'limit': 1, 'api_key': api_key}
    if not api_key:
        create_task(bot.send_privmsg([msg.target], 'Error: no api key set'))
        return
    response = request.get_json(api_url + urllib.parse.urlencode(params))
    try:
        track = response['recenttracks']['track'][0]
    except IndexError:
        create_task(bot.send_notice([msg.target], '[{msg.target}] {user} has no recent tracks.'))
        return
    title = track['name']
    artist = track['artist']['#text']
    album = track['album']['#text']
    if album == '':
        album = 'Unknown Album'
    try:
        tag_params = {
            'method': 'track.getTopTags',
            'track': title,
            'artist': artist,
            'api_key': api_key
        }
        tagr = request.get_json(api_url + urllib.parse.urlencode(tag_params))
        tagr = tagr['toptags']['tag'][0:5]
        tags = []
        for i in tagr:
            tags.append(i['name'])
        tags = ', '.join(tags)
    except:
        tags = ''
    try:
        pc_params = {
            'method': 'track.getInfo',
            'track': title,
            'artist': artist,
            'username': user,
            'api_key': api_key
        }
        pc = request.get_json(api_url + urllib.parse.urlencode(pc_params))
        played = pc['track']['userplaycount']
    except:
        played = ''
    try:
        listened = datetime.strptime(track['date']['#text'], '%d %b %Y, %H:%M')
        curtime = datetime.fromtimestamp(time.time())
        curtime = datetime.strptime(str(curtime), '%Y-%m-%d %H:%M:%S.%f')
        diff = str((curtime - listened))
        listened = diff.split('.')[0]
        if listened[0:2] == '-1':
            listened = listened[8:-6] + ' seconds'
        elif listened[0] == '0':
            if listened[2:4] == '01':
                listened = listened[3:-3] + ' minute'
            elif listened[2:3] == '0':
                if listened[2:4] == '00':
                    listened = '1 minute'
                else:
                    listened = listened[3:-3] + ' minutes'
            else:
                listened = listened[2:-3] + ' minutes'
        else:
            if listened[-8:-6] == ' 1' or listened[0:2] == '1:':
                listened = listened[:-6] + ' hour'
            else:
                listened = listened[:-6] + ' hours'

        if tags:
            out = (u'{} listened to "{}" by \x02{}\x02 from the'
                   u' album \x02{}\x02 {} ago, Play Count: {}, Tags: {}'.format(
                       user, title, artist, album, listened, played, tags))
        else:
            out = (u'{} listened to "{}" by \x02{}\x02 from the'
                   u' album \x02{}\x02 {} ago, Play Count: {}.'.format(
                       user, title, artist, album, listened, played))
    except KeyError:
        if tags:
            out = (u'{} is listening to "{}" by \x02{}\x02 from the'
                   u' album \x02{}\x02, Play Count: {}, Tags: {}.'.format(
                       user, title, artist, album, played, tags))
        else:
            out = (u'{} is listening to "{}" by \x02{}\x02 from the'
                   u' album \x02{}\x02, Play Count: {}.'.format(user, title, artist, album, played))
    print(user, save)
    if user != msg.command and save:
        db.set_cell(bot.db, 'users', 'lastfm', user, 'nick', nick)
    create_task(bot.send_privmsg([msg.target], out))
