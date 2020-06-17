# Standard Libs
import time
from asyncio import create_task

# First Party
from core import hook

countdown_is_running = False
countdown_nicks = []
countdown_timeout = 20


def set_countdown_to_true():
    global countdown_is_running
    countdown_is_running = True


def set_countdown_to_false():
    global countdown_is_running
    countdown_is_running = False


@hook.hook('command', ['countdown'])
async def countdown(bot, msg):
    "countdown [seconds] [nick1 nick2 nick3] -- starts a countdown. It will begin when all the users type .ready"
    inp = msg.message

    if countdown_is_running:
        return
    else:
        set_countdown_to_true()

    global countdown_nicks
    wait_count = 1
    inp = inp.lower().replace(',', '')
    count = 6

    try:
        if inp[0][0].isdigit():
            count = int(inp.split()[0]) + 1
            countdown_nicks = inp.split()[1:]
            if count > 6:
                count = 6
        else:
            countdown_nicks = inp.split()[0:]
            count = 6
    except Exception:
        pass

    if len(inp) > 6:
        nicks = ', '.join(countdown_nicks)
        create_task(
            bot.send_notice([
                msg.target
            ], f'Countdown started! Waiting for {nicks}. Type \x02.ready\x02 when ready!'))

        # TODO fix: there can be only one countdown running per network
        # this chunk keeps the whole plugin busy
        while countdown_nicks:
            time.sleep(1)
            wait_count = int(wait_count) + 1
            if wait_count == countdown_timeout:
                set_countdown_to_false()
                create_task(bot.send_privmsg([msg.target], "Countdown expired."))

        create_task(
            bot.send_notice([msg.target], 'Ready! The countdown will begin in 2 seconds...'))
        time.sleep(2)

    for cur in range(1, count):
        create_task(bot.send_notice([msg.target], f'*** {count - cur} ***'))
        time.sleep(1)
    else:
        set_countdown_to_false()
        create_task(bot.send_privmsg([msg.target], '\x02***\x02 GO \x02***\x02'))


@hook.hook('command', ['ready'])
async def ready(bot, msg):
    "ready -- when all users are ready the countdown will begin."
    global countdown_nicks
    nicks_size_start = len(countdown_nicks)
    try:
        countdown_nicks.remove(msg.nickname.lower())
    except Exception:
        pass

    if nicks_size_start > len(countdown_nicks):
        if len(countdown_nicks) > 0:
            create_task(bot.send_notice([msg.target], f'Waiting for: {", ".join(countdown_nicks)}'))
