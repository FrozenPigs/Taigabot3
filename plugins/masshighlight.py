"""Sieves and events for preventing masshighlighting."""
# Standard Libs
import re
import sched
import time
import asyncio

# First Party
from core import hook


async def _detect_highlight(users, message):
    """Is used to detect if message is masshighlighting."""
    message = message.split(' ')
    r = re.compile('[\'!?,.]')
    matches = [
        word for word in message[1:] if r.sub('', word.lower()) in users]
    if len(set(matches)) > 5:
        return True
    False


async def _start_sched(client, target, nick):
    s = sched.scheduler(time.perf_counter, time.sleep)
    s.enter(60, 1, asyncio.create_task, (client.unban(target, nick), ))
    s.run()


@hook.hook('sieve', ['03-masshighlight-output'])
async def masshighlight_output_sieve(client, server, command, args, kwargs):
    """Is for preventing the bot from mass highligting"""
    if command == 'PRIVMSG':
        message = args[1]
        if ' ' not in message:
            return command, args, kwargs
        users = list(client.users.keys())
        if await _detect_highlight(users, message):
            return None, args, kwargs
    return command, args, kwargs


@hook.hook('sieve', ['03-masshighlight-input'])
async def masshighlight_input_sieve(client, data):
    """Is for banning users who masshighlight."""
    if ' ' not in data.message:
        return data
    users = list(client.users.keys())
    if await _detect_highlight(users, data.message):
        asyncio.create_task(
            client.kickban(
                data.target,
                data.nickname,
                reason=('No mass'
                        'highlighting, come back in 1 minute.')))
        asyncio.create_task(_start_sched(client, data.target, data.nickname))
        return None
    return data
