# quotes
#
# usage:
# .qinit                                       --- database initialization command (admin only)
# .q [nick/channel] [optional quote number]    --- for fetching quotes by their number (or a random quote)
# .q [nick/channel] [search term]              --- for fetching quotes by a search term
# .q add [nick] [quote]                        --- for adding quotes
# .q delete [quote number]                     --- for deleting quotes (you can only delete your own quotes)
#
# made by kelp

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


def remove_quotes(quotelist):
    """removes quotes from a quotelist where deleted == '1' """
    buf = []
    for quote in quotelist:
        if quote[5] != '1':
            buf.append(quote)

    return buf


def display_quote(client, data, quotelist, target, arg):
    """
    output a quote, given a tuple list of all avalable quotes, and possibly
    a number (for selection of a specific quote)
    """

    outquotes = []
    quotenums = []
    wordarg = None
    numarg = None

    # if not searching, pick random quote
    if not arg:
        numarg = random.randint(0, len(quotelist) - 1)
    else:
        try:
            numarg = int(arg)
            if numarg > 0:
                numarg -= 1
        except ValueError:
            wordarg = arg

    quotelist = remove_quotes(quotelist)

    if len(quotelist) < 1:
        asyncio.create_task(
            client.message(data.target, f'I have no quotes for {target}'))
        return

    print('t2')

    if numarg is not None:
        try:

            outquotes.append(quotelist[numarg])
            if numarg < 0:
                quotenums.append(len(quotelist) + numarg + 1)
            else:
                quotenums.append(numarg + 1)
        except IndexError:
            if len(quotelist) == 1:
                asyncio.create_task(
                    client.message(data.target,
                                   f'I only have 1 quote for {target}'))
            else:
                asyncio.create_task(
                    client.message(
                        data.target,
                        (f'I only have {str(len(quotelist))} quotes for'
                         f'{target}')))
    elif wordarg is not None:
        for i in range(len(quotelist)):
            quote = quotelist[i]
            if wordarg in quote[3]:
                outquotes.append(quote)
                quotenums.append(i + 1)

    # if we have more than five quotes....
    if outquotes:
        for i in range(len(outquotes)):
            quote = outquotes[i]
            out = f'[{quotenums[i]}/{len(quotelist)}] <{quote[1]}> {quote[3]}'
            if len(outquotes) > 5:
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
    """main quote hook"""
    conn = client.bot.dbs[data.server]
    split = data.message.split()

    tables = db.get_table_names(conn)
    if 'quotes' not in tables:
        asyncio.create_task(
            client.message(
                data.target,
                ('Quote table uninitialized. Please ask your nearest bot'
                 'admin to run .qinit.')))

    # TODO: fix edgecase with users when a nick that corresponds to a command

    if len(split) > 1:
        if split[0] == 'add':
            nick = split[1]

            quote = ' '.join(split[2:])
            quotedata = (data.target, nick, data.nickname, quote,
                         int(time.time()), '0',
                         )
            db.set_row(conn, 'quotes', quotedata)
            asyncio.create_task(client.message(data.target, 'Quote added.'))
            db.ccache()
            return

        elif split[0] == 'delete':
            nickquotes = db.get_row(conn, 'quotes', 'nick', data.nickname)
            numarg = None

            try:
                numarg = int(split[1])
                if numarg > 0:
                    numarg -= 1
            except ValueError:
                asyncio.create_task(
                    client.message(
                        data.target,
                        'You need to use a number when deleting quotes.'))
                return

            nickquotes = remove_quotes(nickquotes)
            if len(nickquotes) > 0:
                try:
                    # get quote to delete
                    quote = nickquotes[numarg]
                except ValueError:
                    if len(nickquotes) == 1:
                        asyncio.create_task(
                            client.message(data.target,
                                           'You only have 1 quote.'))
                    else:
                        asyncio.create_task(
                            client.message(
                                data.target,
                                (f'You only have {str(len(nickquotes))} '
                                 'quote(s).')))
                    return
                # TODO: Do quote deletion better
                cur = conn.cursor()
                cur.execute(
                    "UPDATE quotes SET deleted='1' WHERE msg=? AND time=?",
                    (quote[3], quote[4]))
                del cur
                conn.commit()
                db.ccache()
                asyncio.create_task(
                    client.message(data.target, 'Quote deleted.'))

                return
            else:
                asyncio.create_task(
                    client.message(data.target, 'You have no quotes.'))
                return

    if len(split) > 0 and len(data.message) > 0:
        argtuple = split[0],

        # convert split[0] (we now know that it needs to be compared with a db) into a tuple, since we get db results in a tuple

        if data.message[0] == '#':
            channels = db.get_column(conn, 'channels', 'channel')

            if argtuple in channels:
                chanquotes = db.get_row(conn, 'quotes', 'chan', split[0])
                try:
                    display_quote(client, data, chanquotes, split[0], split[1])
                except IndexError:
                    display_quote(client, data, chanquotes, split[0], None)

            else:
                asyncio.create_task(
                    client.message(data.target,
                                   'No quotes found for ' + split[0] + '.'))
        else:
            users = db.get_column(conn, 'quotes', 'nick')

            if argtuple in users:
                nickquotes = db.get_row(conn, 'quotes', 'nick', split[0])
                try:
                    display_quote(client, data, nickquotes, split[0], split[1])
                except IndexError:
                    display_quote(client, data, nickquotes, split[0], None)
            else:
                asyncio.create_task(
                    client.message(data.target,
                                   'No quotes found for ' + split[0] + '.'))
