# Standard Libs
import asyncio
import random
import sqlite3
import time

# First Party
from core import hook
# import messaging from utils, so that i could into action (i.e /me in irssi)
from util import messaging

#kelp's assembly of homages to shitbot, which doesen't work due to changes
#in bython ;-;


@hook.hook('command', ['morr'])    #morr dispenser
async def morrr(bot, message):
    out = 'hands '
    if message.message == message.command:
        out += message.user.nickname
    else:
        out = ' '.join(message.split_message[1:])
    out += ' a nice butterbrod with '
    out += str(random.randint(2, 8))
    out += ' slices of that norwegian goodness on it.'
    out = f'\x01ACTION {out}\x01'
    asyncio.create_task(bot.send_privmsg([message.target], out))


@hook.hook('command', ['s8ball'])    #shitty version of 8ball
async def sball(bot, message):
    out = 'your dumb ass didn\'t even ask a question'
    if message.message != message.command:
        choices = [
            "not today, ho", "ask Kali_", "ask your friendly neighbourhood cat", "i dont know",
            "yeh", "no", "nope", "yes, but only if you're gay", "ask shitbot", "maybe",
            "ask the same thing 12 seconds later", "probably",
            "if you have the need to ask that, then you might as well kill yourself",
            "ask your gay cat", "yes, but you will end up a soyboy in a vape shop",
            "that was a stupid question", "only if its ironic", "there is no good awnser to this one",
            "no thats gay", "ask adrift", "so we have a smartass, eh?"
        ]
        awnser = random.choice(choices)
        out = 'says... '
        out += awnser
        out = f'\x01ACTION {out}\x01'
    asyncio.create_task(bot.send_privmsg([message.target], out))