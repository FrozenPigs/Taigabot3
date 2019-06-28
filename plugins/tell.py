#tells
#author: nojusr
#
#usage:
# .tell [user] [message]     -- send a message to an offline user.
#                               message will be shown to them once
#                               said user connects to the server.
#
# .showtells                 -- shows all seen messages sent to you
#                               within the last 24 hours and all unseen
#                               messages sent to you within the last week
#
#note: read messages are deleted within 24 hours,
#      unread messages are deleted within a week
#
#note: once a message is read, it is still displayed for 24 hours

from typing import List
import time
import dateutil.relativedelta
from datetime import datetime
import asyncio


#import core functions
from core import db
from core import hook

#db table definition
tell_columns: List[str] = ['nick', 'add_nick', 'msg', 'time', 'seen', 'seen_time']

#config values
unseen_tell_timeout = 604800 #equals to a week
seen_tell_timeout = 86400 #equals to a day

async def _check_if_recipient_online(client, recipient):
    """ Is used to check if a user is currently online on the server """
    whois = None
    try:
        whois = await client.whois(recipient)
        return True
    except:
        return False


def _set_tell_seen(conn, tell):
    """ Is used to set a tell's status to seen """
    if tell[4] == '1':
        return

    cur = conn.cursor()
    cur.execute("UPDATE tells SET seen='1', seen_time=? WHERE msg=? AND time=?", ( str(int(time.time())), tell[2], tell[3] )   )
    del cur
    conn.commit()
    db.ccache()

def _delete_tell(conn, tell):
    """ Is used to delete tells """
    cur = conn.cursor()
    cur.execute('DELETE FROM tells WHERE msg=? AND time=? AND seen_time=?',(tell[2], tell[3], tell[5]))
    conn.commit()
    db.ccache()


def _get_time_since_tell_send(tell):
    """
       Is used to get a human readable representation of the time since
       the message was sent.
    """
    print(tell)
    tell_time_sent = int(tell[3])

    current_time = int(time.time())

    dt1 = datetime.fromtimestamp(tell_time_sent)
    dt2 = datetime.fromtimestamp(current_time)
    rd = dateutil.relativedelta.relativedelta (dt2, dt1)

    out = ''

    if rd.days == 1:
        out += f'{rd.days} day, '
    elif rd.days != 0:
        out += f'{rd.days} days, '


    if rd.hours == 1:
        out += f'{rd.hours} hour, '
    elif rd.hours != 0:
        out += f'{rd.hours} hours, '


    if rd.minutes == 1:
        out += f'{rd.minutes} minute and '
    elif rd.minutes != 0:
        out += f'{rd.minutes} minutes and '


    if rd.seconds == 1:
        out += f'{rd.seconds} second ago'
    elif rd.seconds != 0:
        out += f'{rd.seconds} seconds ago'
    elif current_time - tell_time_sent == 0:
        out = 'just now'


    return out

def _send_tell_notice(client, recipient, tell):
    relative_time = _get_time_since_tell_send(tell)
    asyncio.create_task( client.notice(recipient,
        f'{tell[1]} sent you a message {relative_time}:\n {tell[2]}'))

def _get_tell_time(elem):
    """ Tiny helper function used to sort tells """
    return int(elem[3])

def _show_user_latest_tell(client, conn, recipient):
    """is used to send the recipient their newest tell/message """
    tells = db.get_row(conn, 'tells', 'nick', recipient)

    # small sanity check
    if len(tells) < 1:
        return

    # sort and get the newest tell
    tells.sort(key=_get_tell_time, reverse=True)
    tell = tells[0]

    _set_tell_seen(conn, tell)

    # get relative time since tell was sent in human readable format
    relative_time = _get_time_since_tell_send(tell)

    asyncio.create_task( client.notice(recipient,
        f'{tell[1]} sent you a message {relative_time}:\n {tell[2]}'))


def _show_user_recent_tells(client, conn, recipient, show_only_unseen):
    tells = db.get_row(conn, 'tells', 'nick', recipient)

    # small sanity check
    if len(tells) < 1:
        if show_only_unseen == False:
            asyncio.create_task( client.notice(recipient,
                'You have no pending tells.'))
        return

    # sort tells
    tells.sort(key=_get_tell_time, reverse=True)

    if show_only_unseen == True:
        asyncio.create_task(client.notice(recipient, f'You have new tells!'))
        for tell in tells:
            if str(tell[4]) == '0':
                _set_tell_seen(conn, tell)
                _send_tell_notice(client, recipient, tell)

    else:
        for tell in tells:
                _set_tell_seen(conn, tell)
                _send_tell_notice(client, recipient, tell)



@hook.hook('init', ['tell_garbage_collector'])
async def tellgc(client):
    """ Looks for and deletes old tells every 10 miuntes """
    conn = client.bot.dbs[client.server_tag]
    print ('Starting tell garbage collector...')
    while client.connected == True:
        print('Deleting old tells...')
        current_time = int(time.time())

        all_tells = db.get_table(conn, 'tells')
        print(all_tells)
        for tell in all_tells:
            print (f'TELL_DEBUG: seen: {tell[4]}, diff of send time {current_time - int(tell[3])}, diff of seen time {current_time - int(tell[5])}')
            if str(tell[4]) == '1' and (current_time - int(tell[5])) > seen_tell_timeout:
                print('TELL_DEBUG: deleting tell due to seen timeout')
                _delete_tell(conn, tell)
            if str(tell[4]) == '0' and (current_time - int(tell[3])) > unseen_tell_timeout:
                print('TELL_DEBUG: deleting tell due to unseen timeout')
                _delete_tell(conn, tell)
        print('Done.')
        await asyncio.sleep(600)

@hook.hook('init', ['tellinit'])
async def inittell(client):
    conn = client.bot.dbs[client.server_tag]
    print (f'Initializing tell table in /persist/db/{client.server_tag}.db...')
    db.init_table(conn, 'tells', tell_columns)
    db.ccache()
    print ('Tell initialization complete.')

@hook.hook('command', ['tell'])
async def tell(client, data):
    conn = client.bot.dbs[data.server]
    split = data.split_message

    tables = db.get_table_names(conn)
    if 'tells' not in tables:
        asyncio.create_task(client.message(data.target, 'Tell table uninitialized, ask your nearest bot admin to restart the bot.'))

    if len(split) > 1:
        recipient = split[0]
        message = ' '.join(split[1:])
    else:
        return

    print('TELL_DEBUG: adding new tell to db')
    telldata = (recipient, data.nickname, message, int(time.time()), '0', '0')
    print(f'TELL_DEBUG: telldata: {telldata}')
    db.set_row(conn, 'tells', telldata)
    db.ccache()
    print('TELL_DEBUG: tell added.')

    usrchk = await _check_if_recipient_online(client,recipient)

    asyncio.create_task(client.notice(data.nickname, 'Your message will be sent.'))

    if usrchk == True:
        _show_user_latest_tell(client, conn, recipient)

@hook.hook('command', ['showtells'])
async def showtells(client, data):
    conn = client.bot.dbs[data.server]
    _show_user_recent_tells(client, conn, data.nickname, False)

@hook.hook('event', ['JOIN'])
async def onconnectshowtells(client, data):
    conn = client.bot.dbs[data.server]
    _show_user_recent_tells(client, conn, data.nickname, True)
