# Standard Libs
import asyncio
from sqlite3 import Connection
from typing import Any, List

# First Party
from core import data, db


async def add_to_channels(client: Any, data: data.ParsedRaw, conn: Connection,
                          column: str, adding: str, existing: List[str],
                          added_msg: str, already_msg: str):
    if adding in existing:
        asyncio.create_task(client.notice(data.nickname, already_msg))
    else:
        existing.append(adding)
        if len(existing) > 1:
            db.set_cell(conn, 'channels', column, ' '.join(existing),
                        'channel', data.target)
        else:
            print(existing)
            db.set_cell(conn, 'channels', column, existing[0], 'channel',
                        data.target)

        asyncio.create_task(client.notice(data.nickname, added_msg))


async def del_from_channels(
        client: Any, data: data.ParsedRaw, conn: Connection, column: str,
        removing: str, existing: List[str], removed_msg: str, notin_msg: str):
    if removing in existing:
        existing.remove(removing)
        if len(existing) > 1:
            db.set_cell(conn, 'channels', column, ' '.join(existing),
                        'channel', data.target)
        else:
            if not existing:
                db.set_cell(conn, 'channels', column, '', 'channel',
                            data.target)
            else:
                db.set_cell(conn, 'channels', column, existing, 'channel',
                            data.target)

        asyncio.create_task(client.notice(data.nickname, removed_msg))
    else:
        asyncio.create_task(client.notice(data.nickname, notin_msg))


async def make_list(value):
    if not value:
        return []
    if ' ' in value:
        return value.split()
    else:
        return [value]


async def usermodes(client, target, command, users):
    prefix = '+'
    if command[0:2] == 'de':
        prefix = '-'
        command = command[2:]
    if command == 'op':
        await client.rawmsg('MODE', target, f'{prefix}o', f'users')
    elif command == 'hop':
        await client.rawmsg('MODE', target, f'{prefix}h', f'{users}')
    elif command == 'vop':
        await client.rawmsg('MODE', target, f'{prefix}v', f'{users}')


async def _enable_disable(client, target, conn, value, cell):
    if len(value) > 1:
        db.set_cell(conn, 'channels', cell, ' '.join(value), 'channel', target)
    else:
        if not value:
            db.set_cell(conn, 'channels', cell, '', 'channel', target)
        else:
            db.set_cell(conn, 'channels', cell, value[0], 'channel', target)


async def is_cmd_event_sieve(plugin, data, sieves, events, commands):
    """Is for checking if the input is an actual sieve, event or command."""
    sieve = plugin not in sieves
    event = plugin not in events
    command = plugin not in commands
    is_list = plugin != 'list'

    if sieve and event and command and is_list:
        return True
    return False


async def valid_cmd_event_sieve(sieves, events, commands, nodisable):
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


async def cmd_event_sieve_lists(client, data, disabled, nodisable, sieves,
                                events, commands):
    """Is for displaying a list of valid disables or enables."""
    if data.command == 'disable':
        sieves, events, commands = await valid_cmd_event_sieve(
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
