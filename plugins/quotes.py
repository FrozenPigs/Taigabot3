# quotes
#
# usage:
# .qinit --- database initialization command (admin only)
# .q [nick/channel] [optional quote number] --- for fetching quotes by their
# number (or a random quote)
# .q [nick/channel] [search term] --- for fetching quotes by a search term
# .q add [nick] [quote] --- for adding quotes
# .q delete [quote number] --- for deleting quotes (you can only delete your
# own quotes)
#
# made by kelp

# TODO: make a util for hastebin
# TODO: rewrite docstrings
# TODO: Do quote deletion better
# TODO: Add min length to the search string

from typing import List
import time
import asyncio
import random
import requests

# import core db functions
from core import db, hook

# db table definition
quote_columns: List[str] = [
    'chan', 'nick', 'add_nick', 'msg', 'time', 'deleted']


def _remove_quotes(quotelist):
    """removes quotes from a quotelist where deleted == '1' """
    buf = []
    for quote in quotelist:
        if quote[5] != '1':
            buf.append(quote)

    return buf


def _parse_search(search, quotelist):
    if not search:
        search = random.randint(0, len(quotelist) - 1)
    else:
        try:
            search = int(search)
            if search > 0:
                search -= 1
        except ValueError:
            pass
    return search


def _message_or_paste(client, data, quotenums, quotelist):
    # if we have more than five quotes....
    if quotes:
        for i, quote in enumerate(quotes):
            out = f'[{quotenums[i]}/{len(quotelist)}] <{quote[1]}> {quote[3]}'
            if len(quotes) > 5:
                response = requests.post(
                    'https://hastebin.com/documents', data=out)
                if response.status_code == 200:
                    d = response.json()['key']
                    link = 'https://hastebin.com/' + str(d)
                    asyncio.create_task(client.message(data.target, link))
                else:
                    asyncio.create_task(
                        client.message(
                            data.target,
                            'Failed to upload quotes onto pastebin.'))

            else:
                asyncio.create_task(client.message(data.target, out))
    else:
        asyncio.create_task(client.message(data.target, 'No results.'))


def _display_quote(client, data, quotelist, target, search=None):
    """
    output a quote, given a tuple list of all avalable quotes, and possibly
    a number (for selection of a specific quote)
    """
    quotes = []
    quotenums = []
    quotelist = _remove_quotes(quotelist)
    search = _parse_search(search, quotelist)

    if len(quotelist) < 1:
        asyncio.create_task(
            client.message(data.target, f'I have no quotes for {target}'))
        return

    if isinstance(search, int):
        try:
            quotes.append(quotelist[search])
            if search < 0:
                quotenums.append(len(quotelist) + search + 1)
            else:
                quotenums.append(search + 1)
        except IndexError:
            asyncio.create_task(
                client.message(
                    data.target,
                    (f'I only have {str(len(quotelist))} quote(s) for'
                     f'{target}')))
    else:
        for i, value in enumerate(quotelist):
            if search in value[3]:
                quotes.append(value)
                quotenums.append(i + 1)
    _message_or_paste(client, data, quotenums, quotelist)


def _search_quotes(client, data, conn, message):
    if len(message) > 0 and len(data.message) > 0:

        if data.message[0] == '#':
            chansornicks = db.get_column(conn, 'channels', 'channel')
            quotes = db.get_row(conn, 'quotes', 'chan', message[0])
        else:
            print(message, data.message)
            if data.message[0] == '@':
                message[0] = message[0][1:]
                data.message = data.message[1:]
            print(message, data.message)
            chansornicks = db.get_column(conn, 'quotes', 'nick')
            quotes = db.get_row(conn, 'quotes', 'nick', message[0])
        argtuple = (message[0], )
        if argtuple in chansornicks:
            try:
                _display_quote(client, data, quotes, message[0], message[1])
            except IndexError:
                _display_quote(client, data, quotes, message[0], None)
        else:
            asyncio.create_task(
                client.message(data.target,
                               f'No quotes found for {message[0]}.'))


@hook.hook('command', ['qinit'], admin=True)
async def quoteinit(client, data):
    """admin only quote db table initiation hook, since trying to init
    on every quote(even though the db functions account for that) is kinda
    wasteful"""
    conn = client.bot.dbs[data.server]
    print(f'Initializing quote table in /persist/db/{data.server}.db...')
    db.init_table(conn, 'quotes', quote_columns)
    db.ccache()
    print('Initialization complete.')


@hook.hook('command', ['q'])
async def quotes(client, data):
    """main quote """
    conn = client.bot.dbs[data.server]
    message = data.split_message

    tables = db.get_table_names(conn)
    if 'quotes' not in tables:
        asyncio.create_task(
            client.message(
                data.target,
                ('Quote table uninitialized. Please ask your nearest bot'
                 'admin to run .qinit.')))

    if message[0] == 'add':
        quotedata = (data.target, message[1], data.nickname,
                     ' '.join(message[2:]), int(time.time()), '0')
        db.set_row(conn, 'quotes', quotedata)
        asyncio.create_task(client.message(data.target, 'Quote added.'))
        db.ccache()
        return
    elif message[0] == 'del':
        quotes = db.get_row(conn, 'quotes', 'nick', data.nickname)

        try:
            numarg = int(message[1])
            if numarg > 0:
                numarg -= 1
        except ValueError:
            asyncio.create_task(
                client.message(
                    data.target,
                    'You need to use a number when deleting quotes.'))
            return

        quotes = _remove_quotes(quotes)
        if len(quotes) > 0:
            try:
                # get quote to delete
                quote = quotes[numarg]
            except ValueError:
                asyncio.create_task(
                    client.message(
                        data.target,
                        f'You only have {str(len(quotes))} quote(s).'))
                return
            cur = conn.cursor()
            cur.execute("UPDATE quotes SET deleted='1' WHERE msg=? AND time=?",
                        (quote[3], quote[4]))
            del cur
            conn.commit()
            db.ccache()
            asyncio.create_task(client.message(data.target, 'Quote deleted.'))

            return
        else:
            asyncio.create_task(
                client.message(data.target, 'You have no quotes.'))
            return
    else:
        _search_quotes(client, data, conn, message)
