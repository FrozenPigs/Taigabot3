"""Sieves and commands for global and channel ignores."""
# Standard Libs
import asyncio

# First Party
from core import db, hook
from util import user


@hook.hook('sieve', ['01-ignore-input'])
async def ignore_sieve(bot, msg):
    """Is for ignoring messages from globally or channel ignored users."""
    if not msg.user:
        return msg
    if not msg.target:
        return msg
    if msg.user.userhost in bot.server_config.no_ignore:
        return msg

    if msg.user.global_admin:
        return msg
    if msg.user.global_ignored:
        return None

    if msg.target[0] == '#' and msg.raw_command != 'JOIN':
        if msg.user.chan_admin:
            return msg
        if msg.target in msg.user.chan_ignored:
            if msg.user.chan_ignored[msg.target]:
                return None

    if msg.user.nickname.lower().endswith('bot'):
        return None
    return msg


async def _parse_masks(client, data, conn, message):
    masks = await user.parse_masks(client, conn, message)
    bot_mask = await user.get_mask(client, conn, client.nickname)
    if data.command in {'gignore', 'ignore'}:
        no_ignore = client.bot.config['servers'][data.server]['no_ignore']
        for mask in masks:
            no_ignore.append(bot_mask)
            if mask in no_ignore:
                if data.command == 'gignore':
                    asyncio.create_task(client.notice(data.nickname, f'I cannot gignore {mask}.'))
                else:
                    asyncio.create_task(client.notice(data.nickname, f'I cannot ignore {mask}.'))
                masks.remove(mask)
    return masks


@hook.hook('command', ['gignore', 'gunignore'], gadmin=True, autohelp=True)
async def g_un_gignore(client, data):
    """
    .gunignore/.gignore <list/user/mask> -- Gignores or gunignores a list of
    users or lists gignored users.
    """
    conn = client.bot.dbs[data.server]
    message = data.message.replace(',', ' ')
    masks = await _parse_masks(client, data, conn, message)
    message = message.split(' ')

    if not len(masks) and message[0] != 'list':
        asyncio.create_task(client.notice(data.nickname, f'No valid users or masks.'))
        doc = ' '.join(g_un_gignore.__doc__.split())
        asyncio.create_task(client.notice(data.nickname, f'{doc}'))
        return

    ignored = client.bot.config['servers'][data.server]['ignored']
    if message[0] == 'list':
        if len(ignored) > 0:
            asyncio.create_task(
                client.notice(data.nickname, f'Gignored users: {", ".join(ignored)}'))
        else:
            asyncio.create_task(client.notice(data.nickname, f'No users gignored.'))
        return

    for mask in masks:
        if data.command == 'gignore':
            if mask in ignored:
                asyncio.create_task(client.notice(data.nickname, f'{mask} is already gignored.'))
            else:
                asyncio.create_task(client.notice(data.nickname, f'gignoring {mask}.'))
                ignored.append(mask)
        elif data.command == 'gunignore':
            if mask in ignored:
                asyncio.create_task(client.notice(data.nickname, f'{mask} is gunignored.'))
                ignored.remove(mask)
            else:
                asyncio.create_task(client.notice(data.nickname, f'{mask} is not gignored.'))


@hook.hook('command', ['ignore', 'unignore'], admin=True, autohelp=True)
async def c_un_ignore(client, data):
    """
    .unignore/.ignore <list/user/mask> -- Unignores or ignores a list of users,
    or lists ignored users.
    """
    conn = client.bot.dbs[data.server]
    message = data.message.replace(',', ' ')
    masks = await _parse_masks(client, data, conn, message)

    if not len(masks) and message.split(' ')[0] != 'list':
        doc = ' '.join(c_un_ignore.__doc__.split())
        asyncio.create_task(client.notice(data.nickname, f'{doc}'))
        asyncio.create_task(client.notice(data.nickname, f'No valid users or masks.'))
        return

    ignored = db.get_cell(conn, 'channels', 'ignored', 'channel', data.target)[0][0]
    if not ignored:
        ignored = ''

    if message.split(' ')[0] == 'list':
        if len(ignored) > 0:
            asyncio.create_task(client.notice(data.nickname, f'Ignored users: {ignored}'))
        else:
            asyncio.create_task(client.notice(data.nickname, f'No users ignored.'))
        return

    for mask in masks:
        if data.command == 'unignore':
            if mask in ignored:
                asyncio.create_task(
                    client.notice(data.nickname, f'{mask} is unignored in {data.target}.'))
                ignored = ignored.replace(mask, '').strip()
            else:
                asyncio.create_task(
                    client.notice(data.nickname, f'{mask} is not ignored in {data.target}.'))
                return
        elif data.command == 'ignore':
            if mask in ignored:
                asyncio.create_task(
                    client.notice(data.nickname, f'{mask} is already ignored in {data.target}.'))
                return
            else:
                asyncio.create_task(
                    client.notice(data.nickname, f'ignoring {mask} in {data.target}.'))
                ignored += mask + ' '

    db.set_cell(conn, 'channels', 'ignored', ignored, 'channel', data.target)
