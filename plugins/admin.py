"""Events, sieves, and commands for channel admins."""
# First Party
import asyncio
from core import db, hook

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
