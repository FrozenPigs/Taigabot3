" tell.py: written by sklnd in July 2009"
"       2010.01.25 - modified by Scaevolus"

# Standard Libs
import re
import time
from asyncio import create_task

# First Party
from core import db, hook
from util import timeu

db_ready = False


def db_init(bot):
    "check to see that our db has the tell table and return a dbection."
    print('hi there')
    global db_ready
    conn = bot.db
    db.init_table(conn, 'tell', ['user_to', 'user_from', 'message', 'chan', 'time'], [
        'user_to', 'message'
    ])
    db_ready = True
    print('Tell Database Ready')


@hook.hook('event', ['PRIVMSG'])
async def tellinput(bot, msg):
    if 'showtells' in msg.message.lower():
        return

    if not db_ready: db_init(bot)

    tells = db.get_row(bot.db, 'tell', 'user_to', msg.nickname)

    if tells:
        _, user_from, message, chan, sent_time = tells[0]
        past = timeu.timesince(sent_time)

        create_task(
            bot.send_notice([msg.nickname],
                            f'{user_from} sent you a message {past} ago from {chan}: {message}'))
        if len(tells) > 1:
            prefix = db.get_cell(bot.db, 'channels', 'commandprefix', 'channel', msg.target)[0][0]
            print(prefix)
            create_task(
                bot.send_notice([msg.nickname],
                                f'({len(tells) - 1} more, {prefix}showtells to view)'))
        db.delete_row(bot.db, 'tell', 'user_to', msg.nickname, ('message', message))


@hook.hook('command', ['showtells'])
async def showtells(bot, msg):
    "showtells -- View all pending tell messages (sent in a notice)."

    if not db_ready: db_init(bot)

    tells = db.get_row(bot.db, 'tell', 'user_to', msg.nickname)

    if not tells:
        create_task(bot.send_notice([msg.nickname], "You have no pending tells."))
        return

    for tell_line in tells:
        _, user_from, message, chan, sent_time = tell_line
        past = timeu.timesince(sent_time)
        create_task(
            bot.send_notice([msg.nickname],
                            f'{user_from} sent you a message {past} ago from {chan}: {message}'))
    db.delete_row(bot.db, 'tell', 'user_to', msg.nickname)


@hook.hook('command', ['ask', 'tell'], autohelp=True)
async def tell(bot, msg):
    "tell <nick> <message> -- Relay <message> to <nick> when <nick> is around."
    query = msg.message.split(' ', 1)

    if len(query) != 2:
        create_task(bot.send_notice([msg.nickname], tell.__doc__))
        return

    user_to = query[0].lower()
    message = query[1]
    user_from = msg.nickname

    if msg.target.lower() == user_from.lower():
        chan = 'a pm'
    else:
        chan = msg.target

    if user_to == 'me':
        user_to = user_from.lower()

    if user_to.lower() == bot.server_config.nickname.lower():
        # user is looking for us, being a smartass
        create_task(bot.send_notice([msg.nickname], "Thanks for the message, %s!" % user_from))
        return

    if not re.match("^([A-Za-z0-9_.|`\^\-\[\]])+$", user_to.lower()):
        create_task(bot.send_notice([msg.nickname], "I cant send a message to that user!"))
        return

    if not db_ready:
        db_init(bot)

    rows = db.get_row(bot.db, 'tell', 'user_to', user_to)
    if len(rows) >= 10:
        create_task(bot.send_notice([msg.nickname], "That person has too many messages queued."))
        return

    set_row = db.set_row(bot.db, 'tell', (user_to, user_from, message, chan, time.time()))
    if set_row is None:
        create_task(bot.send_notice([msg.nickname], "Message has already been queued."))
        return

    create_task(bot.send_notice([msg.nickname], "Your message will be sent!"))
