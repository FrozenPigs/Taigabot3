# Standard Libs
import random
import re
from asyncio import create_task

# First Party
from core import hook

# Written by Scaevolus, updated by Lukeroge and ine

whitespace_re = re.compile(r'\s+')
valid_diceroll = r'^([+-]?(?:\d+|\d*d(?:\d+|F))(?:[+-](?:\d+|\d*d(?:\d+|F)))*)( .+)?$'
valid_diceroll_re = re.compile(valid_diceroll, re.I)
sign_re = re.compile(r'[+-]?(?:\d*d)?(?:\d+|F)', re.I)
split_re = re.compile(r'([\d+-]*)d?(F|\d*)', re.I)


def nrolls(count, n):
    "roll an n-sided die count times"
    if n == "F":
        return [random.randint(-1, 1) for x in range(min(count, 100))]
    if n < 2:    # it's a coin
        if count < 100:
            return [random.randint(0, 1) for x in range(count)]
        else:    # fake it
            return [int(random.normalvariate(0.5 * count, (0.75 * count) ** 0.5))]
    else:
        if count < 100:
            return [random.randint(1, n) for x in range(count)]
        else:    # fake it
            return [
                int(
                    random.normalvariate(0.5 * (1 + n) * count, ((
                        (n + 1) * (2 * n + 1) / 6.0 - (0.5 * (1 + n)) ** 2) * count) ** 0.5))
            ]


@hook.hook('command', ['roll', 'dice'])
async def dice(bot, msg):
    "dice <diceroll> -- Simulates dicerolls. Example: '2d20-d5+4' = roll 2 D20s, subtract 1D5, add 4"
    inp = msg.message

    if "d" not in inp:
        create_task(bot.send_privmsg([msg.target], 'that doesnt look like a dice'))
        return

    validity = valid_diceroll_re.match(inp)

    if validity is None:
        create_task(bot.send_privmsg([msg.target], 'that isnt a dice'))
        return

    spec = whitespace_re.sub('', inp)
    if not valid_diceroll_re.match(spec):
        create_task(bot.send_privmsg([msg.target], "Invalid diceroll"))
        return

    groups = sign_re.findall(spec)
    total = 0
    rolls = []

    for roll in groups:
        count, side = split_re.match(roll).groups()
        count = int(count) if count not in " +-" else 1
        if side.upper() == "F":    # fudge dice are basically 1d3-2
            for fudge in nrolls(count, "F"):
                if fudge == 1:
                    rolls.append("\x033+\x0F")
                elif fudge == -1:
                    rolls.append("\x034-\x0F")
                else:
                    rolls.append("0")
                total += fudge
        elif side == "":
            total += count
        else:
            side = int(side)
            if side > 10000000:
                create_task(
                    bot.send_privmsg([msg.target], 'i cant make a dice with that many faces :('))
                return
            try:
                if count > 0:
                    dice = nrolls(count, side)
                    rolls += map(str, dice)
                    total += sum(dice)
                else:
                    dice = nrolls(-count, side)
                    rolls += [str(-x) for x in dice]
                    total -= sum(dice)
            except OverflowError:
                create_task(
                    bot.send_privmsg([msg.target], "Thanks for overflowing a float, jerk >:["))
                return

    if len(rolls) == 1:
        create_task(bot.send_privmsg([msg.target], f"Rolled {total}"))
    else:
        # show details for multiple dice
        create_task(bot.send_privmsg([msg.target], "Rolled {total} [{', '.join(rolls)}]"))
