# last.fm plugin
#
# usage:
# .np [lastfm_nickname] --- check what is playing right now for an user
# NOTE: this bot saves the last lastfm nick you used. You *really* only
# need to use this command like that once, afterwards you can just do
# .np , and the bot will remember the lastfm nick associated with your
# irc nick.
# .np @[irc_username] --- check what's playing for an another user (if
# they have their nicks saved)
#
#
# TODO:
# .compat [lastfm_nickname] [lastfm_nickname] --- get compatiblity
# between two lastfm users.
# NOTE .compat can be used like this too:
# .compat @[irc_nick] (compares your saved nick with the argument nick)
# .compat [lastfm_nick] (same as above, but with a lastfm nick)
# .compat @[irc_nick] [lastfm_nick]
# .compat [irc_nick] @[lastfm_nick]
# .compat @[irc_nick] @[irc_nick]


from typing import List
import asyncio
import requests
from datetime import datetime

# import core db functions
from core import db, hook

# db table definition
quote_columns: List[str] = [
    'irc_nick', 'lastfm_nick']

api_url = 'http://ws.audioscrobbler.com/2.0/?format=json'


def _get_lastfm_nick(conn, irc_nick):
    nicks = db.get_row(conn, 'lastfm', 'irc_nick', irc_nick)
    try:
        return nicks[0][1]
    except IndexError:
        pass


def _add_lastfm_nick(conn, irc_nick, lastfm_nick):
    nick_check = None
    nick_check = _get_lastfm_nick(conn, irc_nick)

    if nick_check is None:
        nickdata = (irc_nick, lastfm_nick)
        db.set_row(conn, 'lastfm', nickdata)
    else:
        db.set_cell(conn, 'lastfm',
                    'lastfm_nick', lastfm_nick,
                    'irc_nick', irc_nick)

    return lastfm_nick


def _pull_latest_track(api_key, lastfm_nick):
    url = api_url+f'&method=user.getrecenttracks'
    url += f'&user={lastfm_nick}&api_key={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        try:
            track = response.json()['recenttracks']['track'][0]
            return track
        except IndexError:
            pass


def _pull_track_tags(api_key, track_title, track_artist):
    url = api_url+f'&method=track.gettoptags&track={track_title}'
    url += f'&artist={track_artist}&api_key={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        try:
            tags_json = response.json()['toptags']['tag'][0:5]
        except IndexError:
            tags_json = response.json()['toptags']['tag']

        if len(tags_json) < 1:
            return 'none'

        tags = []
        for tag in tags_json:
            tags.append(tag['name'])
        tags = ', '.join(tags)
        return tags


def _get_when_played(track):
    """returns the time difference between right now and the time the
    track was played in text format"""

    """i decided to not include this in the output since the API
     is either buggy, or is reacting too slowly to changes. i.e a track
     i had just scrobbled shows up as 'played one hour ago' """
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
        return listened
    except KeyError:
        pass


def _pull_track_plays(api_key, track_title, track_artist, lastfm_nick):
    url = api_url+f'&method=track.getinfo&username={lastfm_nick}'
    url += f'&track={track_title}&artist={track_artist}'
    url += f'&api_key={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        try:
            playcount_json = response.json()['track']['userplaycount']
            return str(playcount_json)
        except:
            return 'unknown'


def _output_nowplaying(client, data, lastfm_nick,
                       title, artist,album, plays, tags):
    out = f'{lastfm_nick} is listening to "{title}" by {artist} from '
    if album == 'an unknown album':
        out += 'an unknown album'
    else:
        out += f'the album {album}'

    out += f', Play count: {plays}, Tags: {tags}.'

    asyncio.create_task(
        client.message(
            data.target, out))

    return


@hook.hook('command', ['lastfminit'], admin=True)
async def lfminit(client, data):
    """admin only table initiation hook """
    conn = client.bot.dbs[data.server]
    print(f'Initializing lastfm table in /persist/db/{data.server}.db...')
    db.init_table(conn, 'lastfm', quote_columns)
    db.ccache()
    print('Initialization complete.')


@hook.hook('command', ['np'])
async def nowplaying(client, data):
    """gets the current song that's playing."""

    conn = client.bot.dbs[data.server]
    split = data.message.split()

    try:
        api_keys = client.bot.config['api_keys']
        lastfm_key = api_keys['last_fm']
    except KeyError:
        asyncio.create_task(
            client.message(
                data.target,
                'No last.fm API key found. Please create an API account, add it\'s API key to \'api_keys\' in config.json with the tag \'last_fm\''))
        return

    # deal with getting the last.fm nickname

    lastfm_nick = None

    if len(split) > 0:
        arg = split[0]
        if arg[0] == '@':
            arg = arg[1:]
            lastfm_nick = _get_lastfm_nick(conn, arg)
        else:
            lastfm_nick = _add_lastfm_nick(conn, data.nickname, arg)

        if lastfm_nick is None:
            asyncio.create_task(
                client.message(
                    data.target,
                    'No associated last.fm nickname found.'))
            return
    else:
        lastfm_nick = _get_lastfm_nick(conn, data.nickname)

        if lastfm_nick is None:
            asyncio.create_task(
                client.message(
                    data.target,
                    'No associated last.fm nickname found.'))
            return

    track = None
    track = _pull_latest_track(lastfm_key, lastfm_nick)

    if track is None:
        asyncio.create_task(
            client.message(
                data.target,
                f'No recent tracks found for {lastfm_nick}.'))
        return

    # extract track data
    title = track['name']
    artist = track['artist']['#text']
    album = track['album']['#text']
    if album == '':
        album = 'an unknown album'

    # gather other data
    tags = _pull_track_tags(lastfm_key, title, artist)
    plays = _pull_track_plays(lastfm_key, title, artist, lastfm_nick)

    # final output
    _output_nowplaying(client, data, lastfm_nick,
                       title, artist, album, plays, tags)
