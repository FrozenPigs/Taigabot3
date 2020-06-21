" seen.py: written by sklnd in about two beers July 2009"

# Standard Libs
import os
import re
import sys
import time
from asyncio import create_task

# First Party
from core import db, hook
from util import timeu

seen_db_ready = False


def init_seen_db(bot):
    "check to see that our db has the the seen table and return a connection."
    global seen_db_ready
    db.init_table(bot.db, 'seen', ['name', 'time', 'quote', 'chan', 'host'], ['name', 'chan'])
    seen_db_ready = True
    print('Seen Database Ready')


def findnth(source, target, n):
    num = 0
    start = -1
    while num < n:
        start = source.find(target, start + 1)
        if start == -1: return -1
        num += 1
    return start


def replacenth(source, old, new, n):
    p = findnth(source, old, n)
    if n == -1: return source
    return source[:p] + new + source[p + len(old):]


def correction(bot, msg):
    splitinput = msg.message.split("/")
    nick = msg.nickname
    num = 1
    if len(splitinput) > 3:
        if ' ' in splitinput[3]:
            nick = splitinput[3].split(' ')[1].strip()
            splitinput[3] = splitinput[3].split(' ')[0].strip()

        if len(splitinput[3]) > 2:
            nick = splitinput[3].strip()
        else:
            if 'g' in splitinput[3]:
                num = 0
            else:
                try:
                    num = int(splitinput[3].strip())
                except:
                    num = 1

    last_seen = db.get_row(bot.db, 'seen', 'name', nick.lower(), ('chan', msg.target))[0]

    if last_seen:
        splitinput = msg.message.split("/")
        find = splitinput[1]
        replace = splitinput[2]
        if find in last_seen[2]:
            if "\x01ACTION" in last_seen[2]:
                last_message = last_seen[2].replace("\x01ACTION ", "/me ").replace("\x01", "")
            else:
                last_message = last_seen[2]

            if num == 0:
                create_task(
                    bot.send_privmsg([msg.target], '<{}> {}'.format(
                        nick, last_message.replace(find, "\x02" + replace + "\x02"))))
            else:
                create_task(
                    bot.send_privmsg([msg.target], '<{}> {}'.format(
                        nick, replacenth(last_message, find, "\x02" + replace + "\x02", num))))
    else:
        if nick == msg.nickname:
            create_task(bot.send_notice([msg.nickname], "I haven't seen you say anything here yet"))
        else:
            create_task(
                bot.send_notice([msg.nickname], "I haven't seen {nick} say anything here yet"))


#ignorebots=False
@hook.hook('event', ['PRIVMSG'])
async def seen_sieve(bot, msg):
    if not seen_db_ready:
        init_seen_db(bot)

    if re.match(r'^(s|S)/.*/.*\S*$', msg.message):
        correction(bot, msg)
        return

    # keep private messages private
    if msg.target[:1] == "#":
        db.replace_row(bot.db, 'seen',
                       (msg.nickname.lower(), time.time(), msg.message, msg.target, msg.sent_by))


@hook.hook('command', ['seen'])
async def seen(bot, msg):
    "seen <nick> -- Tell when a nickname was last in active in one of this bot's channels."
    nick = msg.message.strip()

    if bot.server_config.nickname.lower() == nick.lower():
        create_task(bot.send_privmsg([msg.target], "You need to get your eyes checked."))
        return

    if nick.lower() == msg.nickname.lower():
        create_task(bot.send_privmsg([msg.target], "Have you looked in a mirror lately?"))
        return

    # #if not re.match("^[A-Za-z0-9_|.\-\]\[]*$", inp.lower()):
    # #    return "I can't look up that name, its impossible to use!"

    if not seen_db_ready:
        init_seen_db(bot)
    print(nick.lower, msg.target)
    last_seen = db.get_row(bot.db, 'seen', 'name', nick.lower(), ('chan', msg.target))
    if last_seen:
        last_seen = last_seen[0]
        reltime = timeu.timesince(last_seen[1])
        if last_seen[0] != nick.lower():    # for glob matching
            nick = last_seen[0]
        if last_seen[2][0:1] == "\x01":
            create_task(
                bot.send_privmsg([
                    msg.target
                ], f'{nick} was last seen {reltime} ago: * {nick} {last_seen[2][8:-1]}'))
        else:
            create_task(
                bot.send_privmsg([msg.target],
                                 f'{nick} was last seen {reltime} ago saying: {last_seen[2]}'))
    else:
        create_task(
            bot.send_privmsg([msg.target], f"I've never seen {nick} talking in this channel."))
