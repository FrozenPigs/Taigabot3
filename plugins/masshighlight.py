"""Sieves and events for preventing masshighlighting."""
# Standard Libs
import asyncio
import re

# First Party
from core import hook
from util import timeu


async def _detect_highlight(users, msg):
    """Is used to detect if message is masshighlighting."""
    msg = msg.split(' ')
    regex = re.compile("['!?,.]")
    matches = [
        word for word in msg[1:] if regex.sub('', word.lower()) in users
    ]
    if len(set(matches)) > 5:
        return True
    False


@hook.hook('sieve', ['03-masshighlight-output'])
async def masshighlight_output_sieve(bot, msg):
    """Is for preventing the bot from mass highligting."""
    parsed = await bot.parse_message(msg)
    if parsed[1] == 'PRIVMSG':
        msg = parsed[-1][-1]
        if ' ' not in msg:
            return msg
        users = list(bot.users.keys())
        if await _detect_highlight(users, msg):
            return None
    return msg


@hook.hook('sieve', ['03-masshighlight-input'])
async def masshighlight_input_sieve(bot, msg):
    """Is for banning users who masshighlight."""
    if ' ' not in msg.message:
        return msg
    users = list(bot.users.keys())
    if await _detect_highlight(users, msg.message):
        asyncio.create_task(
            bot.send_kickban(
                msg.target,
                msg.sent_by,
                reason=('No mass'
                        'highlighting, come back in 1 minute.')))
        asyncio.create_task(
            timeu.asyncsched(60, bot.send_unban, (msg.target, msg.sent_by)))
        return None
    return msg
