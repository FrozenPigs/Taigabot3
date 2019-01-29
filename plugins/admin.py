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
        db.add_column(conn, 'channels', 'op')
        db.add_column(conn, 'channels', 'hop')
        db.add_column(conn, 'channels', 'vop')
    elif data.nickname in client.users:
        ops = db.get_cell(conn, 'channels', 'op', 'channel', data.target)[0][0]
        hops = db.get_cell(conn, 'channels', 'hop', 'channel',
                           data.target)[0][0]
        vops = db.get_cell(conn, 'channels', 'vop', 'channel',
                           data.target)[0][0]
        if ops and data.mask in ops.split():
            await client.rawmsg('MODE', data.target, '+o', f'{data.nickname}')
        elif hops and data.mask in hops.split():
            await client.rawmsg('MODE', data.target, '+h', f'{data.nickname}')
        elif vops and data.mask in vops.split():
            await client.rawmsg('MODE', data.target, '+v', f'{data.nickname}')


# if banlist not disabled check if user should be banned and ban them


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
                if len(admins) > 1:
                    db.set_cell(conn, 'channels', 'admins', ' '.join(admins),
                                'channel', data.target)
                else:
                    db.set_cell(conn, 'channels', 'admins', admins, 'channel',
                                data.target)

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
                if len(admins) > 1:
                    db.set_cell(conn, 'channels', 'admins', ' '.join(admins),
                                'channel', data.target)
                else:
                    db.set_cell(conn, 'channels', 'admins', admins, 'channel',
                                data.target)

                asyncio.create_task(
                    client.notice(data.nickname, f'Adding {mask} to admins.'))
    elif message[0] == 'list':
        asyncio.create_task(
            client.notice(data.nickname, 'admins are: ' + ', '.join(admins)))
        return


async def _non_valid_disable(plugin, data, sieves, events, commands):
    """Is for checking if the input is an actual sieve, event or command."""
    sieve = plugin not in sieves
    event = plugin not in events
    command = plugin not in commands
    is_list = plugin != 'list'

    if sieve and event and command and is_list:
        return True
    return False


async def _valid_disables(sieves, events, commands, nodisable):
    for event in list(events):
        if event in nodisable:
            events.remove(event)
    for sieve in list(sieves):
        if sieve in nodisable:
            sieves.remove(sieve)
    for command in list(commands):
        if command in nodisable:
            commands.remove(command)
    sieves = ', '.join(sieves)
    events = ', '.join(events)
    commands = ', '.join(commands)
    return sieves, events, commands


async def _disable_enable_lists(client, data, disabled, nodisable, sieves,
                                events, commands):
    """Is for displaying a list of valid disables or enables."""
    if data.command == 'disable':
        sieves, events, commands = await _valid_disables(
            sieves, events, commands, nodisable)
        if sieves != '':
            asyncio.create_task(
                client.notice(data.nickname,
                              f'Valid sieves to disable: {sieves}'))
        if events != '':
            asyncio.create_task(
                client.notice(data.nickname,
                              f'Valid events to disable: {events}'))
        if commands != '':
            asyncio.create_task(
                client.notice(data.nickname,
                              f'Valid commands to disable: {commands}'))
    else:
        if not disabled:
            asyncio.create_task(
                client.notice(data.nickname, 'Nothing disabled.'))
        else:
            if len(disabled) > 1:
                disabled = ', '.join(disabled)
            else:
                disabled = disabled[0]
            asyncio.create_task(
                client.notice(data.nickname, f'Disabled: {disabled}'))


@hook.hook('command', ['disable', 'enable'], admin=True, autohelp=True)
async def c_enable_disable(client, data):
    """
    .enable/.disable <list/commands/events/sieves> -- Lists, enables or
    disables commands, events and sieves.
    """
    event_vals = list(client.bot.plugs['event'].values())
    events = [func[0].__name__ for func in (event for event in event_vals)]
    commands = list(client.bot.plugs['command'])
    sieves = list(client.bot.plugs['sieve'])

    nodisable = client.bot.config['servers'][data.server]['no_disable']
    conn = client.bot.dbs[data.server]
    disabled = db.get_cell(conn, 'channels', 'disabled', 'channel',
                           data.target)[0][0]

    message = data.message

    if ' ' in message:
        message = message.split(' ')
    else:
        message = [message]

    if disabled and ' ' in disabled:
        disabled = disabled.split()
    else:
        if not disabled:
            disabled = []
        else:
            disabled = [disabled]

    if message[0] == 'list':
        await _disable_enable_lists(client, data, disabled, nodisable, sieves,
                                    events, commands)
        return

    for plugin in message:
        plugin = plugin.lower().strip()
        if await _non_valid_disable(plugin, data, sieves, events, commands):
            asyncio.create_task(
                client.notice(data.nickname,
                              f'{plugin} is not a sieve, command or event.'))
        elif data.command == 'enable':
            if plugin not in disabled:
                asyncio.create_task(
                    client.notice(data.nickname, f'{plugin} is not disabled.'))
            else:
                asyncio.create_task(
                    client.notice(data.nickname, f'enabling {plugin}.'))
                disabled.remove(plugin)
                await _enable_disable(client, data.target, conn, disabled,
                                      'disabled')

        elif data.command == 'disable':
            if plugin in disabled:
                asyncio.create_task(
                    client.notice(data.nickname,
                                  f'{plugin} is already disabled.'))
            elif plugin in nodisable:
                asyncio.create_task(
                    client.notice(data.nickname,
                                  f'You cannot disable {plugin}.'))
            else:
                asyncio.create_task(
                    client.notice(data.nickname, f'disabling {plugin}.'))
                disabled.append(plugin)
                await _enable_disable(client, data.target, conn, disabled,
                                      'disabled')


async def _enable_disable(client, target, conn, value, cell):
    if len(value) > 1:
        db.set_cell(conn, 'channels', cell, ' '.join(value), 'channel', target)
    else:
        if not value:
            db.set_cell(conn, 'channels', cell, '', 'channel', target)
        else:
            db.set_cell(conn, 'channels', cell, value[0], 'channel', target)


@hook.hook(
    'command', ['op', 'hop', 'vop', 'deop', 'dehop', 'devop'],
    admin=True,
    autohelp=True)
async def c_op(client, data):
    """.op [add/list] <masks/users> -- Ops masks/users and can add to autoop
    list."""
    print(data.command)
    message = data.message.replace(',', ' ')

    if ' ' in message:
        message = message.split(' ')
    else:
        message = [message]

    if data.command in ('deop', 'dehop', 'devop'):
        if data.command == 'deop':
            await client.rawmsg('MODE', data.target, '-o',
                                f'{" ".join(message)}')
        elif data.command == 'dehop':
            await client.rawmsg('MODE', data.target, '-h',
                                f'{" ".join(message)}')
        elif data.command == 'devop':
            await client.rawmsg('MODE', data.target, '-v',
                                f'{" ".join(message)}')
        return

    conn = client.bot.dbs[data.server]
    dbmasks = db.get_cell(conn, 'channels', data.command, 'channel',
                          data.target)[0][0]

    if message[0] == 'add':
        message = message[1:]
        masks = await user.parse_masks(client, conn, ' '.join(message))
        if dbmasks:
            dbmasks = dbmasks.split()
            dbmasks.extend(masks)
        else:
            if len(masks) > 1:
                dbmasks = ' '.join(masks)
            else:
                dbmasks = masks
            await _enable_disable(client, data.target, conn, dbmasks,
                                  data.command)
    elif message[0] == 'del':
        message = message[1:]
        masks = await user.parse_masks(client, conn, ' '.join(message))
        if dbmasks:
            dbmasks = dbmasks.split()
            for mask in masks:
                if mask in dbmasks:
                    dbmasks.remove(mask)
        else:
            if len(masks) > 1:
                dbmasks = ' '.join(masks)
            else:
                dbmasks = masks
            await _enable_disable(client, data.target, conn, dbmasks,
                                  data.command)
    elif message[0] == 'list':
        if dbmasks:
            asyncio.create_task(
                client.notice(data.nickname,
                              f'{data.command}s are: {dbmasks}.'))
        else:
            asyncio.create_task(
                client.notice(data.nickname, 'There are no {data.command}s.'))
        return
    if data.command == 'op':
        await client.rawmsg('MODE', data.target, '+o', f'{" ".join(message)}')
    elif data.command == 'hop':
        await client.rawmsg('MODE', data.target, '+h', f'{" ".join(message)}')
    elif data.command == 'vop':
        await client.rawmsg('MODE', data.target, '+v', f'{" ".join(message)}')


@hook.hook('command', ['topic'], admin=True, autohelp=True)
async def c_topic(client, data):
    """.topic [|] <message> -- Changes topic, adds if message starts with |."""
    if data.message[0] != '|':
        await client.set_topic(data.target, data.message)
    else:
        await client.set_topic(
            data.target, client.channels[data.target]['topic'] + data.message)


@hook.hook('command', ['mute', 'unmute'], admin=True)
async def c_mute(client, data):
    """.mute/.unmute -- Mutes or unmutes the channel."""
    if data.command == 'mute':
        await client.rawmsg("MODE", data.target, "+m")
    else:
        await client.rawmsg("MODE", data.target, "-m")


@hook.hook('command', ['lock', 'unlock'], admin=True)
async def c_lock(client, data):
    """.lock/.unlock -- Locks or unlocks the channel."""
    if data.command == 'lock':
        await client.rawmsg("MODE", data.target, "+i")
    else:
        await client.rawmsg("MODE", data.target, "-i")
