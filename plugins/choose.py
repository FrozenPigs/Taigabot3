# Standard Libs
import random
from asyncio import create_task

# First Party
from core import hook


@hook.hook('command', ['decide', 'choose'])
async def choose(bot, msg):
    "choose <choice1>, [choice2], [choice3], ... --  Randomly picks one of the given choices."

    replacewords = {'should', 'could', '?', ' i ', ' you '}

    for word in replacewords:
        inp = ' '.join(msg.split_message[1:]).replace(word, '')

    if ':' in inp:
        inp = inp.split(':')[1]

    c = inp.split(', ')
    if len(c) == 1:
        c = inp.split(' or ')
        if len(c) == 1:
            c = ['Yes', 'No']

    create_task(bot.send_privmsg([msg.target], random.choice(c)))
