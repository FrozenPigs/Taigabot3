"""Events, sieves, and commands for channel admins."""
# Standard Libs
import asyncio

# First Party
from core import db, hook
from util import user

last_invite: str = ''


@hook.hook('event', ['INVITE'])
async def invite(client, data):
    """Is for listening for invite events, storing it then triggering whois."""
    global last_invite
    last_invite = f'{data.nickname} {data.message}'
    asyncio.create_task(client.whois(data.nickname))


@hook.hook('event', ['319'])
async def whois(client, data):
    """
    Is for listening to whois to deal with invites.

    If the whois was the result of the invite event, check the user is op,
    owner, or hop in the channel then join.
    """
    split_message = data.message.split()
    global last_invite
    if last_invite:
        split_invite = last_invite.split()
        nick = split_invite[0]
        channel = split_invite[1]
        if split_message[1] == split_invite[0]:
            privilages = [
                f'~{channel}', f'&{channel}', f'@{channel}', f'%{channel}']
            if len([priv for priv in privilages if priv in split_message]) > 0:
                channels = client.bot.config['servers'][data
                                                        .server]['channels']
                if channel not in channels:
                    channels.append(channel)
                    asyncio.create_task(client.join(channel))
                    asyncio.create_task(
                        client.notice(nick, f'Joining {channel}.'))
                else:
                    asyncio.create_task(
                        client.notice(nick, f'Already in {channel}.'))


@hook.hook('event', ['JOIN'])
async def chan_join(client, data):
    """Is called on channel join."""
    conn = client.bot.dbs[data.server]
    if data.nickname == client.nickname:
        db.add_column(conn, 'channels', 'disabled')
        db.add_column(conn, 'channels', 'autoban')
        db.add_column(conn, 'channels', 'autoop')
    elif data.nickname in client.users:
        pass


# if banlist not disabled check if user should be banned and ban them
# if autoop enabled and user should be oped then op them


@hook.hook('command', ['admins'], admin=True, autohelp=True)
async def c_admins(client, data):
    """
    .admins <list/add/del> [user/mask] -- Lists, adds or deletes users or
    masks from admins.
    """
    message = data.message.replace(',', ' ')
    conn = client.bot.dbs[data.server]
    admins = db.get_cell(conn, 'channels', 'admins', 'channel',
                         data.target)[0][0]

    if ' ' in message:
        message = message.split(' ')
        masks = await user.parse_masks(client, conn, ' '.join(message[1:]))
    else:
        message = [message]

    if ' ' in admins:
        admins = admins.split()
    else:
        admins = [admins]

    if message[0] == 'del':
        for mask in masks:
            if mask in admins:
                admins.remove(mask)
                db.set_cell(conn, 'channels', 'admins', ' '.join(admins),
                            'channel', data.target)
                asyncio.create_task(
                    client.notice(data.nickname,
                                  f'Removing {mask} from gadmins.'))
            else:
                asyncio.create_task(
                    client.notice(data.nickname, f'{mask} is not a gadmin.'))
    elif message[0] == 'add':
        for mask in masks:
            if mask in admins:
                asyncio.create_task(
                    client.notice(data.nickname,
                                  f'{mask} is already a admin.'))
            else:
                admins.append(mask)
                db.set_cell(conn, 'channels', 'admins', ' '.join(admins),
                            'channel', data.target)

                asyncio.create_task(
                    client.notice(data.nickname, f'Adding {mask} to admins.'))
    elif message[0] == 'list':
        asyncio.create_task(
            client.notice(data.nickname, 'admins are: ' + ', '.join(admins)))
        return
