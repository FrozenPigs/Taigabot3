# Standard Libs
from asyncio import create_task

# First Party
from core import hook
from util import timeu


@hook.hook('command', ['remind', 'reminder'])
async def reminder(bot, msg):
    """reminder <time sec> <message> --- reminds you of <message>."""
    timer = int(msg.split_message[1])
    message = ' '.join(msg.split_message[2:])

    if timer > 0:
        create_task(
            bot.send_notice([msg.nickname], f'I will remind you of {message} in {timer} seconds.'))
        create_task(timeu.asyncsched(timer, bot.send_notice, ([msg.nickname], message)))
