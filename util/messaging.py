"""Messaging and colour utils."""
# Standard Libs
import asyncio
import re
from typing import Any, Dict

colors: Dict[str, str] = {
    'white': '\x0300',
    'black': '\x0301',
    'blue': '\x0302',
    'green': '\x0303',
    'red': '\x0304',
    'brown': '\x0305',
    'purple': '\x0306',
    'orange': '\x0307',
    'yellow': '\x0308',
    'lime': '\x0309',
    'teal': '\x0310',
    'cyan': '\x0311',
    'royal': '\x0312',
    'pink': '\x0313',
    'grey': '\x0314',
    'silver': '\x0315',
    'bold': '\x02',
    'italic': '\x1D',
    'underline': '\x1F',
    'reverse': '\x16',
    'reset': '\x0F'
}


async def send_action(bot: Any, target: str, message: str) -> None:
    """Is used to do an action in a channel."""
    message = f'\x01ACTION {message}\x01'
    asyncio.create_task(bot.send_privmsg([target], message))


def multiword_replace(text, wordDic):
    """
    take a text and replace words that match a key in a dictionary with
    the associated value, return the changed text
    """
    rc = re.compile('|'.join(map(re.escape, wordDic)))

    def translate(match):
        return wordDic[match.group(0)]

    return rc.sub(translate, text)
