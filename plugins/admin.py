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
