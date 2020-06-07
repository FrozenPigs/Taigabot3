"""Sieves and events for preventing masshighlighting."""
# Standard Libs
import asyncio
import re

# First Party
from core import hook
from util import timeu


async def _detect_highlight(users, message):
    """Is used to detect if message is masshighlighting."""
    message = message.split(' ')
    regex = re.compile("['!?,.]")
    matches = [word for word in message[1:] if regex.sub('', word.lower()) in users]
    if len(set(matches)) > 5:
        return True
    False


@hook.hook('sieve', ['03-masshighlight-output'])
async def masshighlight_output_sieve(bot, message):
    """Is for preventing the bot from mass highligting."""
    parsed = bot.parse_message(message)
    if parsed[1] == 'PRIVMSG':
        message = parsed[-1][-1]
        if ' ' not in message:
            return message
        users = list(bot.users.keys())
        if await _detect_highlight(users, message):
            return None
    return message


@hook.hook('sieve', ['03-masshighlight-input'])
async def masshighlight_input_sieve(bot, message):
    """Is for banning users who masshighlight."""
    if ' ' not in message.message:
        return message
    users = list(bot.users.keys())
    if await _detect_highlight(users, message.message):
        asyncio.create_task(
            bot.send_kickban(
                message.target,
                message.sent_by,
                reason=('No mass'
                        'highlighting, come back in 1 minute.')))
        asyncio.create_task(timeu.asyncsched(60, bot.send_unban, (message.target, message.sent_by)))
        return None
    return message
