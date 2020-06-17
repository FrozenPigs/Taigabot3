# Standard Libs
import random
from asyncio import create_task

# First Party
from core import hook


@hook.hook('command', ['coin'])
async def coin(bot, msg):
    """coin [amount] -- Flips [amount] of coins."""

    if len(msg.split_message) > 1:
        try:
            amount = int(msg.split_message[1])
        except (ValueError, TypeError):
            return "Invalid input!"
    else:
        amount = 1

    if amount > 1000:
        return "thats too many coins"

    if amount == 1:
        create_task(
            bot.send_notice([msg.target],
                            f'flips a coin and gets {random.choice(["heads", "tails"])}.'))
    elif amount == 0:
        create_task(bot.send_notice([msg.target], "makes a coin flipping motion with its hands."))
    else:
        heads = int(random.normalvariate(0.5 * amount, (0.75 * amount) ** 0.5))
        tails = amount - heads
        create_task(
            bot.send_notice([msg.target],
                            f'flips {amount} coins and gets {heads} heads and {tails} tails.'))
