# Standard Libs
import random
import re
import subprocess
import time
from asyncio import create_task

# First Party
from core import db, hook
from util import messaging, request

# Third Party
from bs4 import BeautifulSoup

# import time
# import urllib
# import locale
# import math
# import random

# from util import database, hook, http
# from utilities import formatting, request

# HONK HONK
actions = {
    "honk": ["honked at", "honking"],
    "pet": ["pet", "petting"],
    "diddle": ["diddled", "diddling"],
    "spank": ["spanked", "spanking"],
    "rape": ["raped", "raping"],
    "sex": ["sexed", "sexing"],
    "lick": ["licked", "licking"]
}

# def citation(db, chan, nick, reason):
#     fine = float(random.randint(1, 1500))
#     floatfine = float(str(random.random())[0:4])
#     if reason.split()[1] == 'raping':
#         fine = float(random.randint(1500, 3000))
#     if nick.lower() == 'myon':
#         fine = floatfine
#     elif nick.lower() == 'wednesday\'s mixtape':
#         fine = 1337.69
#     else:
#         fine = fine + floatfine
#     if 'buy' in reason:
#         thing = nick
#         nick = reason.split(' ')[1]
#         try:
#             totalfines = float(database.get(db, 'users', 'fines', 'nick', nick)) + fine
#         except:
#             totalfines = 0.0 + fine
#         database.set(db, 'users', 'fines', totalfines, 'nick', nick)
#         strfines = "{:,}".format(totalfines)
#         strfine = "{:,}".format(fine)
#         if '-' in strfines[0]:
#             return u"PRIVMSG {} :\x01ACTION buys {} for \x02${}\x02 {} has \x0309${}\x01".format(
#                 chan, thing, strfine, nick, strfines[1:])
#         if totalfines <= 0:
#             return u"PRIVMSG {} :\x01ACTION buys {} for \x02${}\x02 {} owes \x0309${}\x01".format(
#                 chan, thing, strfine, nick, strfines)
#         else:
#             return u"PRIVMSG {} :\x01ACTION buys {} for \x02${}\x02. {} owes \x0304${}\x02\x01".format(
#                 chan, thing, strfine, nick, strfines)
#     if 'sell' in reason:
#         thing = nick
#         nick = reason.split(' ')[1]
#         try:
#             totalfines = float(database.get(db, 'users', 'fines', 'nick', nick)) - fine
#         except:
#             totalfines = 0.0 - fine
#         database.set(db, 'users', 'fines', totalfines, 'nick', nick)
#         strfines = "{:,}".format(totalfines)
#         strfine = "{:,}".format(fine)
#         if '-' in strfines[0]:
#             return u"PRIVMSG {} :\x01ACTION sells {} for \x02${}\x02 {} has \x0309${}\x01".format(
#                 chan, thing, strfine, nick, strfines[1:])
#         if totalfines <= 0:
#             return u"PRIVMSG {} :\x01ACTION sells {} for \x02${}\x02 {} owes \x0309${}\x01".format(
#                 chan, thing, strfine, nick, strfines)
#         else:
#             return u"PRIVMSG {} :\x01ACTION sells {} for \x02${}\x02. {} owes \x0304${}\x02\x01".format(
#                 chan, thing, strfine, nick, strfines)
#     if 'shill' in reason:
#         thing = nick
#         nick = reason.split(' ')[1]
#         try:
#             totalfines = float(database.get(db, 'users', 'fines', 'nick', nick)) - fine
#         except:
#             totalfines = 0.0 - fine
#         database.set(db, 'users', 'fines', totalfines, 'nick', nick)
#         strfines = "{:,}".format(totalfines)
#         strfine = "{:,}".format(fine)
#         if '-' in strfines[0]:
#             return u"PRIVMSG {} :\x01ACTION shills {} for \x02${}\x02 {} has \x0309${}\x01".format(
#                 chan, thing, strfine, nick, strfines[1:])
#         if totalfines <= 0:
#             return u"PRIVMSG {} :\x01ACTION shills {} for \x02${}\x02 {} owes \x0309${}\x01".format(
#                 chan, thing, strfine, nick, strfines)
#         else:
#             return u"PRIVMSG {} :\x01ACTION shills {} for \x02${}\x02. {} owes \x0304${}\x02\x01".format(
#                 chan, thing, strfine, nick, strfines)
#     else:
#         try:
#             totalfines = float(database.get(db, 'users', 'fines', 'nick', nick)) + fine
#         except:
#             totalfines = 0.0 + fine
#         database.set(db, 'users', 'fines', totalfines, 'nick', nick)
#         strfines = "{:,}".format(totalfines)
#         strfine = "{:,}".format(fine)
#         if '-' in strfines[0]:
#             return u"PRIVMSG {} :\x01ACTION fines {} \x02${}\x02 {}. You have: \x0309${}\x02\x01".format(
#                 chan, nick, strfine, reason, strfines[1:])
#         if totalfines <= 0:
#             return u"PRIVMSG {} :\x01ACTION fines {} \x02${}\x02 {}. You owe: \x0304${}\x02\x01".format(
#                 chan, nick, strfine, reason, strfines)
#         else:
#             return u"PRIVMSG {} :\x01ACTION fines {} \x02${}\x02 {}. You owe: \x0304${}\x02\x01".format(
#                 chan, nick, strfine, reason, strfines)


@hook.hook('command', ['jumi', 'guts'])
async def guts(bot, msg):
    create_task(bot.send_privmsg([msg.target], 'Fuck jumi.'))


@hook.hook('command', ['plez'])
async def plez(bot, msg):
    for i in range(0, 3):
        create_task(messaging.send_action(bot, msg.target, 'disables plez'))


# @hook.command(autohelp=False)
# def bet(inp, nick=None, db=None, chan=None):
#     "bet <ammount> -- bets <ammount>"
#     inp = inp.replace(',', '').replace('$', '')
#     try:
#         money = float(database.get(db, 'users', 'fines', 'nick', nick))
#     except:
#         money = 0.0
#     if inp == "":
#         inp = "100"
#     if inp != "0":
#         inp = float('-' + inp)
#         if math.isnan(inp):
#             return
#         strinp = "{:,}".format(inp)
#         strmoney = "{:,}".format(money)
#         if inp < money or money == 0:
#             if '-' in strmoney[0]:
#                 return u"\x01ACTION You don't have enough money to bet \x02${}\x02. You have \x0309${}\x02\x01".format(
#                     strinp[1:], strmoney[1:])
#             else:
#                 return u"\x01ACTION You don't have enough money to bet \x02${}\x02. You owe \x0304${}\x02\x01".format(
#                     strinp[1:], strmoney)
#             if inp == 0:
#                 if '-' in strmoney[0]:
#                     return u"\x01ACTION You have to bet more than \x02${}\x02. You have \x0309${}\x02\x01".format(
#                         strinp[1:], strmoney[1:])
#                 else:
#                     return u"\x01ACTION You have to bet more than \x02${}\x02. You owe \x0304${}\x02\x01".format(
#                         strinp[1:], strmoney)
#         else:
#             print(inp)
#             if random.randint(1, 100) <= 50:
#                 money = money - inp
#                 strinp = "{:,}".format(inp)
#                 strmoney = "{:,}".format(money)
#                 database.set(db, 'users', 'fines', money, 'nick', nick)
#                 if '-' in strmoney[0]:
#                     return u"\x01ACTION You lose the bet and lost \x02${}\x02. You have \x0309${}\x02\x01".format(
#                         strinp[1:], strmoney[1:])
#                 else:
#                     return u"\x01ACTION You lose the bet and lost \x02${}\x02. You owe \x0304${}\x02\x01".format(
#                         strinp[1:], strmoney)
#             else:
#                 money = money + inp
#                 strinp = "{:,}".format(inp)
#                 strmoney = "{:,}".format(money)
#                 database.set(db, 'users', 'fines', money, 'nick', nick)
#                 if '-' in strmoney[0]:
#                     return u"\x01ACTION You win the bet and win \x02${}\x02. You have \x0309${}\x02\x01".format(
#                         strinp[1:], strmoney[1:])
#                 else:
#                     return u"\x01ACTION You win the bet and win \x02${}\x02. You owe \x0304${}\x02\x01".format(
#                         strinp[1:], strmoney)

# @hook.command('sell', autohelp=False)
# @hook.command('shill', autohelp=False)
# @hook.command('sex', autohelp=False)
# @hook.command('buy', autohelp=False)
# @hook.command('rape', autohelp=False)
# @hook.command('spank', autohelp=False)
# @hook.command('diddle', autohelp=False)
# @hook.command('pet', autohelp=False)
# @hook.command('lick', autohelp=False)
# @hook.command(autohelp=False)
# def honk(inp, nick=None, conn=None, chan=None, db=None, paraml=None, input=None):
#     "honk <nick> -- Honks at someone."
#     # if pm
#     if input.raw.split(' ')[2] == conn.nick:
#         chan = input.nick
#     else:
#         chan = input.raw.split(' ')[2]
#     regex = re.compile("(\x1f|\x1d|\x03[1-9]|\x02|\x16)", re.UNICODE)
#     paraml[-1] = regex.sub('', paraml[-1])
#     target = inp.strip()
#     command = paraml[-1].split(' ')[0][1:].lower()
#     thing = paraml[-1].split(' ')[1:]
#     thing = '|'.join(thing).replace('|', ' ')
#     try:
#         if thing[-1] == ' ':
#             thing = thing[0:-1]
#     except IndexError:
#         thing = input.nick
#     if command == 'sell':
#         randnum = random.randint(1, 4)
#         if len(inp) == 0:
#             if random.randint(1, 3) == 2:
#                 out = citation(db, chan, thing, 'sell {}'.format(nick))
#             else:
#                 out = u"PRIVMSG {} :\x01ACTION drops {} in a lake.\x01".format(chan, thing)
#         else:
#             if randnum == 1:
#                 out = citation(db, chan, thing, 'sell {}'.format(nick))
#             elif randnum == 2:
#                 out = citation(db, chan, thing, 'sell {}'.format(nick))
#             elif randnum == 3:
#                 out = citation(db, chan, thing, 'sell {}'.format(nick))
#             else:
#                 out = u"PRIVMSG {} :\x01ACTION drops {} in a lake.\x01".format(chan, thing)
#     elif command == 'shill':
#         randnum = random.randint(1, 4)
#         if len(inp) == 0:
#             if random.randint(1, 3) == 2:
#                 out = citation(db, chan, thing, 'shill {}'.format(nick))
#             else:
#                 fine = float(random.randint(1500, 3000))
#                 nick = input.nick
#                 try:
#                     totalfines = float(database.get(db, 'users', 'fines', 'nick', nick)) + fine
#                 except:
#                     totalfines = 0.0 + fine
#                 database.set(db, 'users', 'fines', totalfines, 'nick', nick)
#                 fine = "{:,}".format(fine)
#                 totalfines = "{:,}".format(totalfines)
#                 out = u"PRIVMSG {} :\x01ACTION fines {} \x02${}\x02 for breaking the NDA. You have: \x0309${}\x02\x01".format(
#                     chan, nick, fine, totalfines[1:])
#         else:
#             if randnum == 1:
#                 out = citation(db, chan, thing, 'shill {}'.format(nick))
#             elif randnum == 2:
#                 out = citation(db, chan, thing, 'shill {}'.format(nick))
#             elif randnum == 3:
#                 out = citation(db, chan, thing, 'shill {}'.format(nick))
#             else:
#                 fine = float(random.randint(1500, 3000))
#                 nick = input.nick
#                 try:
#                     totalfines = float(database.get(db, 'users', 'fines', 'nick', nick)) + fine
#                 except:
#                     totalfines = 0.0 + fine
#                 database.set(db, 'users', 'fines', totalfines, 'nick', nick)
#                 fine = "{:,}".format(fine)
#                 totalfines = "{:,}".format(totalfines)
#                 if totalfines[0] == "-":
#                     out = u"PRIVMSG {} :\x01ACTION fines {} \x02${}\x02 for breaking the NDA. You have: \x0309${}\x02\x01".format(
#                         chan, nick, fine, totalfines[1:])
#                 else:
#                     out = u"PRIVMSG {} :\x01ACTION fines {} \x02${}\x02 for breaking the NDA. You owe: \x0304${}\x02\x01".format(
#                         chan, nick, fine, totalfines)
#     elif command == 'buy':
#         randnum = random.randint(1, 4)
#         if len(inp) == 0:
#             if random.randint(1, 3) == 2:
#                 out = citation(db, chan, thing, 'buy {}'.format(nick))
#             else:
#                 out = u"PRIVMSG {} :\x01ACTION pisses on the floor and leaves.\x01".format(chan)
#         else:
#             if randnum == 1:
#                 out = citation(db, chan, thing, 'buy {}'.format(nick))
#             elif randnum == 2:
#                 out = citation(db, chan, thing, 'buy {}'.format(nick))
#             elif randnum == 3:
#                 out = citation(db, chan, thing, 'buy {}'.format(nick))
#             else:
#                 out = u"PRIVMSG {} :\x01ACTION pisses on the floor and leaves.\x01".format(chan)
#     else:
#         if len(inp) == 0:
#             if random.randint(1, 3) == 2:
#                 out = citation(db, chan, nick, "for {}".format(actions[command][1]))
#             else:
#                 out = u"PRIVMSG {} :\x01ACTION {}s {}\x01".format(chan, command, nick)
#         else:
#             randnum = random.randint(1, 4)
#             if randnum == 1:
#                 out = citation(db, chan, nick, "for {}".format(actions[command][1]))
#             elif randnum == 2:
#                 out = citation(db, chan, target,
#                                "for being too lewd and getting {}".format(actions[command][0]))
#             else:
#                 out = u"PRIVMSG {} :\x01ACTION {}s {}\x01".format(chan, command, target)
#     conn.send(out)

# @hook.command('give')
# @hook.command
# def donate(inp, db=None, nick=None, chan=None, conn=None, notice=None):
#     """donate <user> <money> -- Gives <money> to <user>."""
#     inp = inp.replace('$', '').replace('-', '').split(' ')
#     inp = ' '.join(inp[0:2]).split('.')[0].split()
#     user = str(' '.join(inp[0:-1]).split('.')[0])
#     donation = float(inp[-1])
#     if math.isnan(donation) or math.isinf(donation):
#         return
#     # try:
#     #     donation = inp[-1].split('.')[0] + '.' + inp[-1].split('.')[1][0:2]
#     #     print donation
#     #     donation = float(donation)
#     # except Exception as e:
#     #     print e
#     #     return
#     #if donation > 10000.00:
#     #    donation = 10000.00
#     if user.lower() == nick.lower():
#         user = 'wednesday'
#     try:
#         giver = float(database.get(db, 'users', 'fines', 'nick', nick))
#     except:
#         giver = 0.0
#     try:
#         taker = float(database.get(db, 'users', 'fines', 'nick', user))
#     except:
#         taker = 0.0
#     if donation > giver or donation < 0:
#         return
#     if str(giver)[0] == '-':
#         giver = giver + donation
#     else:
#         giver = giver - donation
#     database.set(db, 'users', 'fines', giver, 'nick', nick)
#     wednesdaywins = random.randint(1, 80)
#     if wednesdaywins == 80:
#         wednesday = float(database.get(db, 'users', 'fines', 'nick', 'wednesday'))
#         database.set(db, 'users', 'fines', wednesday - donation, 'nick', 'wednesday')
#         conn.send(u"PRIVMSG {} :\x01ACTION gives \x02${}\x02 to wednesday.\x01".format(
#             chan, donation))
#     else:
#         if giver != taker:
#             database.set(db, 'users', 'fines', taker - donation, 'nick', user)
#             database.set(db, 'users', 'fines', giver, 'nick', nick)
#         conn.send(u"PRIVMSG {} :\x01ACTION gives \x02${}\x02 to {}.\x01".format(
#             chan, donation, user))

# @hook.command('steal')
# @hook.command('rob')
# @hook.command()
# def mug(inp, db=None, nick=None, chan=None, conn=None, notice=None):
#     """mug <user> -- Takes money from <user>.."""
#     inp = inp.split()
#     user = inp[0]
#     money = float(random.randint(20, 1500))
#     try:
#         money = inp[-1].split('.')[0] + '.' + inp[-1].split('.')[1][0:2]
#         money = float(money)
#     except:
#         pass
#     try:
#         robber = float(database.get(db, 'users', 'fines', 'nick', nick))
#     except:
#         robber = 0.0
#     try:
#         victim = float(database.get(db, 'users', 'fines', 'nick', user))
#     except:
#         victim = 0.0
#     robbingfails = random.randint(1, 3)
#     if robbingfails == 2:
#         if victim != robber:
#             database.set(db, 'users', 'fines', robber + money, 'nick', nick)
#             database.set(db, 'users', 'fines', victim - money, 'nick', user)
#         conn.send(u"PRIVMSG {} :\x01ACTION {} shoots you in the foot and takes \x02${}\x02.\x01".
#                   format(chan, user, money))
#     else:
#         if robber != victim:
#             database.set(db, 'users', 'fines', victim + money, 'nick', user)
#             database.set(db, 'users', 'fines', robber - money, 'nick', nick)
#         conn.send(u"PRIVMSG {} :\x01ACTION {} shanks {} in a dark alley and takes \x02${}\x02\x01".
#                   format(chan, nick, user, money))

# @hook.command(autohelp=False)
# def owed(inp, nick=None, conn=None, chan=None, db=None):
#     """owe -- shows your total fines"""
#     if '@' in inp: nick = inp.split('@')[1].strip()
#     fines = database.get(db, 'users', 'fines', 'nick', nick)
#     if not fines: fines = 0
#     strfines = "{:,}".format(float(fines))
#     if '-' in strfines[0]:
#         return u'\x02{} has:\x02 \x0309${}'.format(nick, strfines[1:])
#     if fines <= 0:
#         return u'\x02{} owes:\x02 \x0309${}'.format(nick, strfines)
#     else:
#         return u'\x02{} owes:\x02 \x0304${}'.format(nick, strfines)


@hook.hook('command', ['pay'])
async def pay(bot, msg):
    """pay -- pay your fines"""
    create_task(
        bot.send_privmsg([msg.target], '\x02Donate to wednesdays paypal to pay the fees!\x02'))


# VENDINGMACHINE
colors = ([('red', '\x0304'), ('orange', '\x0307'), ('yellow', '\x0308'), ('green', '\x0309'),
           ('cyan', '\x0303'), ('light blue', '\x0310'), ('royal blue', '\x0312'),
           ('blue', '\x0302'), ('magenta', '\x0306'), ('pink', '\x0313'), ('maroon', '\x0305'),
           ('super shiny', '\x03')])

items = ([('pantsu', 'used pair of'), ('dragon dildo', 'slightly used'),
          ('tfwnogf tears direct from ledzeps feels', 'vial of'), ('fursuit', 'cum stained'),
          ('girlfriend', 'self-inflatable'), ('otter suit', 'lube covered slippery'),
          ('dogecoin to call someone that cares', 'worthless'),
          ('condom that doesnt fit and will never be used', 'magnum XXL'), ('loli', 'miniature'),
          ("LeDZeP to follow you around and >tfwnogf", 'emotionally unstable'),
          ('rimu job that feels like trying to start a fire with sandpaper', 'rough and tough')])


@hook.hook('command', ['vend', 'vendingmachine'])
async def vendingmachine(bot, msg):
    if msg.message != msg.command:
        nick = msg.message
    else:
        nick = msg.nickname
    colornum = random.randint(0, len(colors) - 1)
    itemnum = random.randint(0, len(items) - 1)
    create_task(
        messaging.send_action(
            bot, msg.target,
            f'dispenses one {items[itemnum][1]} {colors[colornum][1]}{colors[colornum][0]} {items[itemnum][0]}\x03 for {nick}'
        ))


# MISC
@hook.hook('command', ['daki', 'love', 'hug'])
async def hug(bot, msg):
    "hug <nick> -- hugs someone"
    if msg.message == msg.command:
        nick = msg.nickname
    else:
        nick = msg.message
    create_task(bot.send_privmsg([msg.target], f'\x02\x034♥♡❤♡♥\x03 {nick} \x034♥♡❤♡♥\x03\x02'))


@hook.hook('command', ['dab'])
async def dab(bot, msg):
    "dab <nick> -- dab on dem haters"
    if msg.message == msg.command:
        nick = msg.nickname
    else:
        nick = msg.message
    create_task(messaging.send_action(bot, msg.target, f'dabs on {nick}'))


@hook.hook('command', ['poke'])
async def poke(bot, msg):
    "poke <nick> -- pokes someone"
    if msg.message == msg.command:
        nick = msg.nickname
    else:
        nick = msg.message
    create_task(messaging.send_action(bot, msg.target, f'pokes {nick}'))


@hook.hook('command', ['nigger'])
async def nigger(bot, msg):
    "nigger <nick> -- niggers someone"
    if msg.message == msg.command:
        nick = msg.nickname
    else:
        nick = msg.message
    create_task(messaging.send_action(bot, msg.target, f'{nick} is a nigger'))


@hook.hook('command', ['kiss'])
async def kiss(bot, msg):
    "kiss <nick> -- kisses someone"
    if msg.message == msg.command:
        nick = msg.nickname
    else:
        nick = msg.message
    create_task(bot.send_privmsg([msg.target], f'(づ｡◕‿‿◕｡)づ\x02\x034。。・゜゜・。。・゜❤ {nick} ❤\x03\x02'))

# @hook.regex(r'^\[(.*)\]$')
# @hook.command(autohelp=False)
# def intensify(inp):
#     "intensify <word> -- [EXCITEMENT INTENSIFIES]"
#     try:
#         word = inp.upper()
#     except:
#         word = inp.group(1).upper()
#     return u'\x02[{} INTENSIFIES]\x02'.format(word)


@hook.hook('command', ['increase'])
async def increase(bot, msg):
    "increase"
    create_task(
        bot.send_privmsg([msg.target], '\x02[QUALITY OF CHANNEL SIGNIFICANTLY INCREASED]\x02'))


@hook.hook('command', ['decrease'])
async def decrease(bot, msg):
    "decrease"
    create_task(
        bot.send_privmsg([msg.target], '\x02[QUALITY OF CHANNEL SIGNIFICANTLY DECREASED]\x02'))


@hook.hook('command', ['shekels'])
async def shekels(bot, msg):
    "shekles"
    create_task(
        messaging.send_action(bot, msg.target, 'lays some shekels on the ground to lure the jews.'))


@hook.hook('command', ['hump'])
async def hump(bot, msg):
    "humps"
    if msg.message == msg.command:
        nick = msg.nickname
    else:
        nick = msg.message
    create_task(messaging.send_action(bot, msg.target, f'humps {nick}'))


@hook.hook('command', ['marry'], autohelp=True)
async def marry(bot, msg):
    "marrys person"
    if msg.message == msg.command:
        create_task(bot.send_notice([msg.target], marry.__doc__))
        return
    create_task(
        messaging.send_action(bot, msg.target,
                              f'pronounces {msg.nickname} and {msg.message} husbando and waifu'))


@hook.hook('command', ['pantsumap'])
async def pantsumap(bot, msg):
    create_task(bot.send_notice([msg.nickname], "Pantsumen Map: http://tinyurl.com/clx2qeg"))


@hook.hook('command', ['tits'])
async def tits(bot, msg):
    "penis <nicks> -- Analyzes Penis's"
    if msg.message == msg.command:
        nick = msg.nickname
    else:
        nick = msg.message
    create_task(
        bot.send_privmsg([msg.target], f'http://en.inkei.net/tits/{"!".join(nick.split())}'))


# TODO cache
@hook.hook('command', ['penis'])
async def penis(bot, msg):
    if msg.message == msg.command:
        nick = msg.nickname
    else:
        nick = msg.message

    inp = request.urlencode(nick)
    html = request.get('http://en.inkei.net/penis/' + nick)
    soup = BeautifulSoup(html, 'lxml')

    details = soup.find(id='elmDescCmmn')
    if details is None:
        return 'Penis: http://en.inkei.net/penis/' + nick

    details = messaging.compress_whitespace(details.text)

    details = re.sub('Penis of [a-z0-9]+ ', 'Penis: ', details)
    create_task(bot.send_privmsg([msg.target], f'{details} - http://en.inkei.net/penis/{nick}'))


@hook.hook('command', ['vagina'])
async def vagina(bot, msg):
    if msg.message == msg.command:
        nick = msg.nickname
    else:
        nick = msg.message

    inp = request.urlencode(nick)
    html = request.get('http://en.inkei.net/vagina/' + nick)
    soup = BeautifulSoup(html, 'lxml')

    details = soup.find(id='elmDescCmmn')
    if details is None:
        return 'Penis: http://en.inkei.net/vagina/' + nick

    details = messaging.compress_whitespace(details.text)

    details = re.sub('Vagina of [a-z0-9]+ ', 'Vagina: ', details)
    create_task(bot.send_privmsg([msg.target], f'{details} - http://en.inkei.net/vagina/{nick}'))


@hook.hook('command', ['anus'])
async def anus(bot, msg):
    if msg.message == msg.command:
        nick = msg.nickname
    else:
        nick = msg.message

    inp = request.urlencode(nick)
    html = request.get('http://en.inkei.net/anus/' + nick)
    soup = BeautifulSoup(html, 'lxml')

    details = soup.find(id='elmDescCmmn')
    if details is None:
        return 'Penis: http://en.inkei.net/anus/' + nick

    details = messaging.compress_whitespace(details.text)

    details = re.sub('Anus of [a-z0-9]+ ', 'Anus: ', details)
    create_task(bot.send_privmsg([msg.target], f'{details} - http://en.inkei.net/anus/{nick}'))


@hook.hook('command', ['harakiri', 'anhero', 'seppuku', 'sudoku'])
async def sudoku(bot, msg):
    "up -- Makes the bot kill you in [channel]. "\
    "If [channel] is blank the bot will op you in "\
    "the channel the command was used in."
    create_task(bot.send_privmsg([msg.target], "Sayonara bonzai-chan..."))
    create_task(bot.send_kick(msg.target, msg.nickname, "Sayonara bonzai-chan..."))


@hook.hook('command', ['akbar'])
async def akbar(bot, msg):
    "akbar - makes the bot kick itsself."
    create_task(bot.send_privmsg([msg.target], "ALLAHU AKBAR"))
    create_task(bot.send_kick(msg.target, msg.nickname, "ALLAHU AKBAR"))
    create_task(bot.send_kick(msg.target, bot.server_config.nickname, "ALLAHU AKBAR"))
    time.sleep(5)
    create_task(bot.send_join([msg.target]))


@hook.hook('command', ['storyofrincewindscat', 'storyofpomfface'], admin=True)
async def storyofpomfface(bot, msg):
    create_task(bot.send_privmsg([msg.target], ':O C==3'))
    create_task(bot.send_privmsg([msg.target], ':OC==3'))
    create_task(bot.send_privmsg([msg.target], ':O==3'))
    create_task(bot.send_privmsg([msg.target], ':O=3'))
    create_task(bot.send_privmsg([msg.target], ':O3'))
    create_task(bot.send_privmsg([msg.target], ':3'))


@hook.hook('command', ['cowsay'], autohelp=True)
async def cowsay(bot, msg):
    create_task(bot.send_privmsg([msg.target], ' ' + '_' * (len(msg.message) + 2)))
    create_task(bot.send_privmsg([msg.target], '< {0} >'.format(msg.message)))
    create_task(bot.send_privmsg([msg.target], ' ' + '-' * (len(msg.message) + 2)))
    create_task(bot.send_privmsg([msg.target], '      \\   ^__^'))
    create_task(bot.send_privmsg([msg.target], '       \\  (oo)\\_______'))
    create_task(bot.send_privmsg([msg.target], '          (__)\\       )\\/\\'))
    create_task(bot.send_privmsg([msg.target], '              ||----w |'))
    create_task(bot.send_privmsg([msg.target], '              ||     ||'))


@hook.hook('command', ['figlet'])
async def figlet(bot, msg):
    message = msg.message[:11]
    for line in subprocess.check_output(['figlet',
                                         '{0}'.format(message)]).decode('utf-8').split('\n'):
        if line != ' ' * (len(line)):
            create_task(bot.send_privmsg([msg.target], line))


# @hook.regex(r'^(same)$')
# def same(inp):
#     "same -- dont feel left out"
#     if random.randint(1, 5) == 3: return 'butts'
#     else: return 'same'

# @hook.regex(r'^(HUEHUEHUE)$')
# @hook.regex(r'^(huehuehue)$')
# def huehuehue(inp):
#     "huehuehue -- huebaru?"
#     return inp.group(0)

# @hook.regex(r'^(TETETE)$')
# @hook.regex(r'^(tetete)$')
# def tetete(inp, nick=None):
#     return 'tetete {}{}{}'.format(nick, nick, nick)

# # @hook.regex(r'^(^)$')
# # def agree(inp):
# #     return "^"

# woahs = ([('woah'), ('woah indeed'), ('woah woah woah!'), ('keep your woahs to yourself')])

# @hook.regex(r'.*([W|w]+[H|h]+[O|o]+[A|a]+).*')
# @hook.regex(r'.*([W|w]+[O|o]+[A|a]+[H|h]+).*')
# def woah(inp, nick=None):
#     if random.randint(0, 4) == 0:
#         return woahs[random.randint(0, len(woahs) - 1)].replace('woah', inp.group(1))

# @hook.regex(r'.*([L|l]+[I|i]+[N|n]+[U|u]+[X|x]).*')
# def interject(inp, nick=None):
#     if random.randint(0, 12) == 0:
#         return "I'd Just Like To Interject For A Moment. What you're referring to as Linux, is in fact, GNU/Linux, or as I've recently taken to calling it, GNU plus Linux. Linux is not an operating system unto itself, but rather another free component of a fully functioning GNU system made useful by the GNU corelibs, shell utilities and vital system components comprising a full OS as defined by POSIX. \n "
#         # \
#         # "Many computer users run a modified version of the GNU system every day, without realizing it. Through a peculiar turn of events, the version of GNU which is widely used today is often called  Linux , and many of its users are not aware that it is basically the GNU system, developed by the GNU Project. There really is a Linux, and these people are using it, but it is just a part of the system they use. \n" \
#         # "Linux is the kernel: the program in the system that allocates the machine's resources to the other programs that you run. The kernel is an essential part of an operating system, but useless by itself; it can only function in the context of a complete operating system. Linux is normally used in combination with the GNU operating system: the whole system is basically GNU with Linux added, or GNU/Linux. All the so-called  Linux  distributions are really distributions of GNU/Linux. "


@hook.hook('command', ['hack'])
async def hack(bot, msg):
    create_task(bot.send_privmsg([msg.target], 'hacking...'))


@hook.hook('command', ['pdawg'])
async def pdawg(bot, msg):
    create_task(bot.send_privmsg([msg.target], '<PDawg> i suck cocks...'))


@hook.hook('command', ['leet'])
async def leet(bot, msg):
    leet = (
        (('are', 'Are'), 'r'),
        (('ate', 'Ate'), '8'),
        (('that', 'That'), 'tht'),
        (('you', 'You'), 'j00'),
        (('two', 'too'), '2'),
        (('for', 'For'), '4'),
        (('o', 'O'), '0'),
        (('i', 'I'), '1'),
        (('e', 'E'), '3'),
        (('s', 'S'), '5'),
        (('a', 'A'), '4'),
        (('t', 'T'), '7'),
    )
    text = msg.message
    for symbols, replaceStr in leet:
        for symbol in symbols:
            text = text.replace(symbol, replaceStr)
    create_task(bot.send_privmsg([msg.target], text))


# 'is trying to steal your girl','or else Im going to fuck her in the ass tonight lil bitch!'

exercises = [
    "pushups", "handstand pushups", "squats", "curls", "dips", "crunches", "minutes of planking",
    "burpees", "jumping jacks", "minutes of vigorous fapping"
]

fitnesslevels = ["swole", "fit", "cut", "ripped", "infinity'd", "jacked"]

motivators = [
    "bitch", "you hungry skeleton", "you puny mortal", "you weak pathetic fool", "you wat wannabe"
]


@hook.hook('command', ['workout'])
async def workout(bot, msg):
    if msg.message == msg.command:
        nick = 'you'
    else:
        nick = msg.message.replace('@', '').strip()
    create_task(
        messaging.send_action(
            bot, msg.target,
            f'wants {nick} to get {random.choice(fitnesslevels)} as fuck, do {random.randint(1, 50)} {random.choice(exercises)} now {random.choice(motivators)}!'
        ))


@hook.hook('command', ['squats', 'pushups'])
async def pushups(bot, msg):
    activity = msg.command[1:]
    if msg.message == msg.command:
        nick = 'you'
    else:
        nick = msg.message.replace('@', '').strip()
    create_task(
        messaging.send_action(
            bot, msg.target,
            f'wants {nick} to get swole as fuck, do {random.randint(1, 50)} {activity} now bitch!'))


# @hook.command
# def room(inp, conn=None):
#     letters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
#     users = inp.split()
#     channel = "#rm-"

#     for i in range(1,6):
#         channel = channel + random.choice(letters)

#     conn.send("JOIN " + channel)

#     for user in users:
#         conn.send("INVITE " + user + " " + channel)


@hook.hook('command', ['madoka'])
async def madoka(bot, msg):
    create_task(
        bot.sent_privmsg([
            msg.target
        ], f'Madoka_Miku has looked at infinitys abs {random.randint(1,500)} times today.'))


@hook.hook('command', ['drink'], autohelp=True)
async def drink(bot, msg):
    """drink <drink> --- drinks drink."""
    create_task(
        bot.send_privmsg([msg.target],
                         f'Drinks {msg.message}, and it was delicious. mmmmmmmmmmmmmmmm'))


@hook.hook('command', ['fap'], autohelp=True)
async def fap(bot, msg):
    """fap <thing> --- cums on <thing>."""
    create_task(bot.send_privmsg([msg.target], f'Jerks off and cums on {msg.message}'))


# var replies = ['faggot','i ought to fuk u up m8','1v1 me','do u evn lift','ur mom','consider urself trolld','ur mom iz gay','stfu fagget','omg nub','u hax i repert u','my dad works for this site so I would be nice if I were you','ill rek u','get rekt scrub','u r gay'];

# .sue


@hook.hook('command', ['cayoot'])
async def cayoot(bot, msg):
    """cayoot [nick] --- calls [nick] cayoot."""
    if msg.message == msg.command:
        nick = msg.nickname
    else:
        nick = msg.message
    create_task(bot.send_privmsg([msg.target], f'{nick} is cayoot!'))


@hook.hook('command', ['spit'])
async def spit(bot, msg):
    """spit [nick] --- spits on [nick]."""
    if msg.message == msg.command:
        nick = msg.nickname
    else:
        nick = msg.message
    create_task(bot.send_privmsg([msg.target], f'spits on {nick} like a dirty whore'))


@hook.hook('command', ['sniff', 'huff'])
async def sniff(bot, msg):
    """sniff [nick] --- sniffs [nick]s hair."""
    if msg.message == msg.command:
        nick = msg.nickname
    else:
        nick = msg.message
    create_task(
        bot.send_privmsg([msg.target], f'huffs {nick}s hair while sat behind them on the bus.'))


# @hook.command('siid')
# @hook.command(autohelp=False)
# def sleepytime(inp, chan=None, conn=None, notice=None):
#     "kick [channel] <user> [reason] -- Makes the bot kick <user> in [channel] "\
#     "If [channel] is blank the bot will kick the <user> in "\
#     "the channel the command was used in."
#     user = 'siid'
#     out = "KICK %s %s" % (chan, user)
#     reason = "sleepytime!"
#     out = out + " :" + reason
#     notice("Attempting to kick %s from %s..." % (user, chan))
#     conn.send(out)

# @hook.command(autohelp=False,channeladminonly=True)
# def touhouradio(inp, chan=None, notice=None, bot=None):
#     "disabled -- Lists channels's disabled commands."
#     url = "http://booru.touhouradio.com/post/list/%7Bchannel%7C%23pantsumen%7D/1"
#     html = http.get_html(url)
#
#     link = html.xpath("//div[@id='main']//a/@href")[0]
#     #COMPARE TO DB
#     image = http.unquote(re.search('.+?imgurl=(.+)&imgrefurl.+', link).group(1))
#     return image


@hook.hook('command', ['lol', 'lok'])
async def lok(bot, msg):
    create_task(bot.send_privmsg([msg.target], 'lol'))
