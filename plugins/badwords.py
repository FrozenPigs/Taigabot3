"""Events and commands for kick and banwords."""
# Standard Libs
import asyncio
import re

# First Party
from core import db, hook
from util import timeu, user


@hook.hook('sieve', ['04-censor-badwords-output'])
async def badwords_output_sieve(bot, message):
    """Is for stopping the bot saying bad words in channel."""
    parsed = bot.parse_message(message)
    if parsed[1] == 'PRIVMSG':
        channel = parsed[-1][0]
        kickwords = db.get_cell(bot.db, 'channels', 'kickwords', 'channel', channel)[0][0]
        banwords = db.get_cell(bot.db, 'channels', 'banwords', 'channel', channel)[0][0]
        split_message = parsed[-1][-1].split()
        if kickwords:
            if ' ' in kickwords:
                kickwords = kickwords.split()
            else:
                kickwords = [kickwords]
            for word in kickwords:
                if word in split_message:
                    message = message.replace(word, '[censored]').strip()
        if banwords:
            if ' ' in banwords:
                banwords = banwords.split()
            else:
                banwords = [banwords]
            for word in banwords:
                word = ' '.join(word.split(':')[0:-1])
                if word in split_message:
                    message = message.replace(word, '[censored]').strip()
    return message


@hook.hook('sieve', ['04-disallow-badwords-input'])
async def badwords_input_sieve(bot, msg):
    """Is used to block inputs from users using bad words."""
    if not msg.user:
        return msg
    admin = msg.user.chan_admin
    gadmin = msg.user.global_admin
    db.add_column(bot.db, 'channels', 'kickwords')
    db.add_column(bot.db, 'channels', 'banwords')

    if not msg.target or msg.target[0] != '#' or gadmin or admin:
        return msg

    db_prefix = db.get_cell(bot.db, 'channels', 'commandprefix', 'channel', msg.target)[0][0]
    if msg.command[0] != db_prefix:
        return msg

    kickwords = db.get_cell(bot.db, 'channels', 'kickwords', 'channel', msg.target)
    banwords = db.get_cell(bot.db, 'channels', 'banwords', 'channel', msg.target)
    if kickwords:
        kickwords = kickwords[0][0]
        for word in kickwords.split(' '):
            if word in msg.split_message:
                asyncio.create_task(
                    bot.send_notice([msg.user.nickname], (f'I cannot say {word} in'
                                                          f'{msg.target}')))
    if banwords:
        banwords = banwords[0][0]
        for word in banwords.split(' '):
            word = ' '.join(word.split(':')[0:-1])
            if word in msg.split_message:
                asyncio.create_task(
                    bot.send_notice([msg.user.nickname], (f'I cannot say {word} in'
                                                          f'{msg.target}')))
    return msg


@hook.hook('event', ['PRIVMSG'])
async def badwords(bot, msg):
    """Is an event for kicking or banning users using bad words."""
    if msg.target[0] != '#':
        return

    if msg.user.chan_admin:
        return
    if msg.user.global_admin:
        return

    kickwords = db.get_cell(bot.db, 'channels', 'kickwords', 'channel', msg.target)
    banwords = db.get_cell(bot.db, 'channels', 'banwords', 'channel', msg.target)
    if kickwords:
        kickwords = kickwords[0][0]
        for word in kickwords.split():
            if word in msg.message:
                asyncio.create_task(
                    bot.send_kick(
                        msg.target, msg.sent_by, reason=(f"You're not allowed to say {word}.")))
    if banwords:
        banwords = banwords[0][0]
        for word in banwords.split():
            word, ban_time, *_ = word.split(':')
            ban_time = int(ban_time)
            if word in msg.message:
                asyncio.create_task(
                    bot.send_kickban(
                        msg.target,
                        msg.sent_by,
                        reason=(f"You're not allowed to say {word}, banned for"
                                f' {ban_time} seconds.')))
                asyncio.create_task(
                    timeu.asyncsched(ban_time, bot.send_unban, (msg.target, msg.sent_by)))


async def _add_words(client, data, conn, words, message, ban=False):
    """Is used for adding words to the ban or kick list."""
    if ban:
        column = 'banwords'
    else:
        column = 'kickwords'

    for msg in message:
        if ban:
            if ':' in msg:
                timeless = ' '.join(msg.split(':')[0:-1])
            else:
                timeless = msg
                msg = f'{msg}:60'
        else:
            timeless = msg
        if not words:
            asyncio.create_task(client.notice(data.nickname, f'Adding {msg} to {column}'))
            db.set_cell(conn, 'channels', column, msg.strip(), 'channel', data.target)
        elif timeless in words:
            asyncio.create_task(client.notice(data.nickname, f'{msg} is already in {column}.'))
        else:
            asyncio.create_task(client.notice(data.nickname, f'Adding {msg} to {column}'))
            words = f'{words[0][0]} {msg}'.strip()
            db.set_cell(conn, 'channels', column, words, 'channel', data.target)


async def _del_words(client, data, conn, words, message, ban=False):
    """Is used for removing words to the ban or kick list."""
    if ban:
        column = 'banwords'
    else:
        column = 'kickwords'

    for msg in message:
        if ban:
            if ':' in msg:
                timeless = ' '.join(msg.split(':')[0:-1])
            else:
                timeless = msg
                msg = f'{msg}:60'
        else:
            timeless = msg
        if timeless in words:
            asyncio.create_task(client.notice(data.nickname, f'Removimg {msg} from {column}.'))
            if ban:
                regex = re.compile(r'{0}*\:[0-9]'.format(timeless))
                words = [i for i in words.split() if not regex.search(i)]
                words = ' '.join(words)
            else:
                words = words.replace(msg, '').strip()
            db.set_cell(conn, 'channels', column, words, 'channel', data.target)
        else:
            asyncio.create_task(client.notice(data.nickname, f'{msg} is not in {column}.'))


@hook.hook('command', ['badwords'], admin=True, autohelp=True)
async def c_badwords(client, data):
    """
    .badwords <list/kick/ban> [add/del] [word] -- List or add kick and ban
    words, for ban words do word:seconds or it will default to 1 minute.
    """
    kickwords = db.get_cell(client.bot.dbs[data.server], 'channels', 'kickwords', 'channel',
                            data.target)
    banwords = db.get_cell(client.bot.dbs[data.server], 'channels', 'banwords', 'channel',
                           data.target)
    if ' ' in data.message:
        message = data.message.split(' ')
    else:
        message = [data.message]

    tooshort = (len(message) < 3 and message[0] != 'list')
    if message[0] not in ['list', 'ban', 'kick'] or tooshort:
        doc = ' '.join(c_badwords.__doc__.split())
        asyncio.create_task(client.notice(data.nickname, f'{doc}'))
        return

    if message[0] == 'list':
        if not kickwords or not kickwords[0][0]:
            asyncio.create_task(client.notice(data.nickname, 'No words in kick list.'))
        else:
            asyncio.create_task(client.notice(data.nickname, f'Kickwords: {kickwords[0][0]}.'))
        if not banwords or not banwords[0][0]:
            asyncio.create_task(client.notice(data.nickname, 'No words in ban list.'))
        else:
            asyncio.create_task(client.notice(data.nickname, f'Banwords: {banwords[0][0]}.'))
        return

    if message[1] == 'add':
        if message[0] == 'ban':
            await _add_words(client, data, client.bot.dbs[data.server], banwords, message[2:], True)
        else:
            await _add_words(client, data, client.bot.dbs[data.server], kickwords, message[2:])
    elif message[1] == 'del':
        if message[0] == 'ban':
            await _del_words(
                client, data, client.bot.dbs[data.server], banwords, message[2:], ban=True)
        else:
            await _del_words(client, data, client.bot.dbs[data.server], kickwords, message[2:])
    else:
        doc = ' '.join(c_badwords.__doc__.split())
        asyncio.create_task(client.notice(data.nickname, f'{doc}'))
