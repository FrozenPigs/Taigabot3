"""Events, sieves, and commands for channel admins."""
# Standard Libs
import asyncio

# First Party
from core import db, hook
from util import botu, timeu, user

last_invite: str = ''


@hook.hook('event', ['INVITE'])
async def invite(bot, msg):
    """Is for listening for invite events, storing it then triggering whois."""
    global last_invite
    last_invite = f'{msg.nickname} {msg.message}'
    asyncio.create_task(bot.send_whois(msg.nickname))


@hook.hook('event', ['319'])
async def whois(bot, msg):
    """
    Is for listening to whois to deal with invites.

    If the whois was the result of the invite event, check the user is op,
    owner, or hop in the channel then join.
    """

    message = msg.split_message
    global last_invite
    if last_invite:
        invite = last_invite.split()
        channel = invite[1]
        if message[0] == invite[0]:
            privilages = [f'~{channel}', f'&{channel}', f'@{channel}', f'%{channel}']
            if len([priv for priv in privilages if priv in message]) > 0:
                channels = bot.server_config.channels
                channels.append(channel)
                asyncio.create_task(
                    botu.add_to_conf(bot, msg, channel, channels, f'Joining {channel}.',
                                     f'{channel} is already in the config.'))
                asyncio.create_task(bot.send_join([channel]))


@hook.hook('init', ['init_channel_dbs'])
async def init_channel_dbs(client):
    pass
    # print('hi')
    # conn = client.bot.dbs[client.server_tag]
    # db.add_column(conn, 'channels', 'disabled')
    # db.add_column(conn, 'channels', 'ban')
    # db.add_column(conn, 'channels', 'op')
    # db.add_column(conn, 'channels', 'hop')
    # db.add_column(conn, 'channels', 'vop')


@hook.hook('event', ['JOIN'])
async def chan_join(bot, msg):
    """Is called on channel join."""
    conn = bot.db
    if msg.sent_by in bot.users:
        ops = await botu.make_list(db.get_cell(conn, 'channels', 'op', 'channel', msg.target)[0][0])
        hops = await botu.make_list(
            db.get_cell(conn, 'channels', 'hop', 'channel', msg.target)[0][0])
        vops = await botu.make_list(
            db.get_cell(conn, 'channels', 'vop', 'channel', msg.target)[0][0])
        bans = await botu.make_list(
            db.get_cell(conn, 'channels', 'ban', 'channel', msg.target)[0][0])

        if msg.sent_by in ops:
            asyncio.create_task(bot.send_mode(msg.target, '+o', f'{msg.sent_by}'))
        elif msg.sent_by in hops:
            asyncio.create_task(bot.send_mode(msg.target, '+h', f'{msg.sent_by}'))
        elif msg.sent_by in vops:
            asyncio.create_task(bot.send_mode(msg.target, '+v', f'{msg.sent_by}'))
        if msg.sent_by in bans:
            asyncio.create_task(bot.send_ban(msg.target, msg.nickname))


@hook.hook('command', ['admins'], admin=True, autohelp=True)
async def c_admins(bot, msg):
    """
    .admins [list/add/del] [user/mask] -- Lists, adds or deletes users or
    masks from admins.
    """
    message = msg.split_message
    conn = bot.db
    admins = await botu.make_list(
        db.get_cell(conn, 'channels', 'admins', 'channel', msg.target)[0][0])
    if len(message) > 1:
        masks = await user.parse_masks(bot, conn, ' '.join(message[1:]))

    if message[0] == 'del':
        for mask in masks:
            asyncio.create_task(
                botu.del_from_channels(bot, msg, conn, 'admins', mask, admins,
                                       f'Removing {mask} from admins.', f'{mask} is not an admin.'))
    elif message[0] == 'add':
        for mask in masks:
            asyncio.create_task(
                botu.add_to_channels(bot, msg, conn, 'admins', mask, admins,
                                     f'Adding {mask} to admins.', f'{mask} is already an admin.'))
    elif message[0] == 'list':
        if admins:
            asyncio.create_task(bot.send_notice([msg.nickname], f'Admins are: {", ".join(admins)}'))
        else:
            asyncio.create_task(bot.send_notice([msg.nickname], 'There are no admins.'))
        return


@hook.hook('command', ['disable', 'enable'], admin=True, autohelp=True)
async def c_enable_disable(bot, msg):
    """
    .enable/.disable <list/commands/events/sieves> -- Lists, enables or
    disables commands, events and sieves.
    """
    event_vals = list(bot.plugins['event'].values())
    events = [func[0].__name__ for func in (event for event in event_vals)]
    commands = list(bot.plugins['command'])
    sieves = list(bot.plugins['sieve'])

    nodisable = bot.server_config.no_disable
    conn = bot.db
    disabled = await botu.make_list(
        db.get_cell(conn, 'channels', 'disabled', 'channel', msg.target)[0][0])
    message = msg.split_message

    if message[0] == 'list':
        asyncio.create_task(
            botu.cmd_event_sieve_lists(bot, msg, disabled, nodisable, sieves, events, commands))
        return

    for plugin in message:
        plugin = plugin.lower().strip()
        if await botu.is_cmd_event_sieve(plugin, msg, sieves, events, commands):
            asyncio.create_task(
                bot.send_notice([msg.nickname], f'{plugin} is not a sieve, command or event.'))
        elif msg.command == 'enable':
            asyncio.create_task(
                botu.del_from_channels(bot, msg, conn, 'disabled', plugin, disabled,
                                       f'Enabling {plugin}', f'{plugin} is not disabled'))
        elif msg.command == 'disable':
            if plugin in nodisable:
                asyncio.create_task(
                    bot.send_notice([msg.nickname], f'You cannot disable {plugin}.'))
            else:
                asyncio.create_task(
                    botu.add_to_channels(bot, msg, conn, 'disabled', plugin, disabled,
                                         f'Disabling {plugin}', f'{plugin} is already disabled.'))


@hook.hook('command', ['op', 'hop', 'vop', 'deop', 'dehop', 'devop'], admin=True, autohelp=True)
async def c_op(bot, msg):
    """.deop <users>/.op [add/del/list] [users] -- Ops/deops users and can add/del
    to autoop list. Same for hop and vop."""
    message = msg.split_message
    conn = bot.db
    if msg.command[0:2] == 'de':
        asyncio.create_task(botu.usermodes(bot, msg.target, msg.command, message))
        return

    dbmasks = await botu.make_list(
        db.get_cell(conn, 'channels', msg.command, 'channel', msg.target)[0][0])

    if message[0] == 'list':
        if dbmasks:
            asyncio.create_task(
                bot.send_notice([msg.nickname], f'{msg.command}s are: {" ".join(dbmasks)}.'))
        else:
            asyncio.create_task(bot.send_notice([msg.nickname], f'There are no {msg.command}s.'))
        return

    message = message[1:]
    masks = await user.parse_masks(bot, conn, ' '.join(message))
    for mask in masks:
        if message[0] == 'add':
            asyncio.create_task(
                botu.add_to_channels(bot, msg, conn, msg.command, mask, dbmasks,
                                     f'Adding {mask} to {msg.command} list.',
                                     f'{mask} is already auto-{msg.command}ed.'))
        elif message[0] == 'del':
            asyncio.create_task(
                botu.del_from_channels(bot, msg, conn, msg.command, mask, dbmasks,
                                       f'Removing {mask} from {msg.command} list.',
                                       f'{mask} is not auto-{msg.command}ed.'))
    asyncio.create_task(botu.usermodes(bot, msg.target, msg.command, message))


@hook.hook('command', ['topic'], admin=True, autohelp=True)
async def c_topic(bot, msg):
    """.topic [|] <message> -- Changes topic, adds if message starts with |."""
    if msg.message[0] != '|':
        asyncio.create_task(bot.sent_topic(msg.target, msg.message))
    # pydle way, need new method
    # else:
    #     asyncio.create_task(
    #         msg.set_topic(msg.target, client.channels[data.target]['topic'] + data.message))


@hook.hook('command', ['mute', 'unmute'], admin=True)
async def c_mute(bot, msg):
    """.mute/.unmute -- Mutes or unmutes the channel."""
    if msg.command == 'mute':
        asyncio.create_task(bot.send_mode(msg.target, '+m'))
    else:
        asyncio.create_task(bot.send_mode(msg.target, '-m'))


@hook.hook('command', ['lock', 'unlock'], admin=True)
async def c_lock(bot, msg):
    """.lock/.unlock -- Locks or unlocks the channel."""
    if msg.command == 'lock':
        asyncio.create_task(bot.send_mode(msg.target, '+i'))
    else:
        asyncio.create_task(bot.send_mode(msg.target, '-i'))


@hook.hook('command', ['remove'], admin=True, autohelp=True)
async def c_remove(bot, msg):
    """.remove <user> -- Makes a user part from the channel."""
    asyncio.create_task(bot.send_line(f'REMOVE {msg.target} :{msg.message}'))


@hook.hook('command', ['kick'], admin=True, autohelp=True)
async def c_kick(bot, msg):
    """.kick <user> [message] -- Kicks a user from the channel."""
    reason = 'bye bye'
    message = msg.split_message
    if len(message) > 1:
        reason = message[1:]
        if len(reason) > 1:
            reason = ' '.join(reason)
        else:
            reason = reason[0]
    asyncio.create_task(bot.send_kick(msg.target, message[0], reason))


@hook.hook('command', ['ban', 'unban', 'unban', 'kickban'], admin=True, autohelp=True)
async def c_ban_unban(bot, msg):
    """.ban [add/del/list] [user] [timer]/.kickban [add/del]
       [user] [reason] [timer]/.unban [user] --
       Ban/kickban/unban the user. User can be banned for [timer].
       .unban automatically removes from ban list."""
    message = msg.split_message
    conn = bot.db
    bans = await botu.make_list(db.get_cell(conn, 'channels', 'ban', 'channel', msg.target)[0][0])
    if msg.command == 'unban':
        asyncio.create_task(bot.send_unban(msg.target, message[0]))
        asyncio.create_task(
            botu.del_from_channels(bot, msg, conn, 'ban', message[
                0], bans, f'Removing {message[0]} from bans.',
                                   f'{message[0]} is not in the ban list.'))
        return

    try:
        timer = int(message[-1])
        message = message[:-1]
    except ValueError:
        timer = 0

    if message[0] == 'del':
        message = message[1:]
        asyncio.create_task(
            botu.del_from_channels(bot, msg, conn, 'ban', message[
                0], bans, f'Removing {message[0]} from bans.',
                                   f'{message[0]} is not in the ban list.'))
    elif message[0] == 'add':
        message = message[1:]
        asyncio.create_task(
            botu.add_to_channels(bot, msg, conn, 'ban', message[
                0], bans, f'Adding {message[0]} to the bans.',
                                 f'{message[0]} is already in the ban list.'))
    elif message[0] == 'list':
        asyncio.create_task(bot.send_notice([msg.nickname], 'bans are: ' + ', '.join(bans)))
        return

    if msg.command == 'ban':
        asyncio.create_task(bot.send_ban(msg.target, message[0]))
    if msg.command == 'kickban':
        asyncio.create_task(
            bot.send_kickban(
                msg.target, message[0], reason=' '.join(message).replace(message[0], 'Git Rekt')))

    if timer:
        asyncio.create_task(timeu.asyncsched(timer, msg.send_unban, (msg.target, message[0])))
