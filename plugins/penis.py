"""Test penis commands."""
# Standard Libs
import asyncio
import time

# First Party
from core import hook


@hook.hook('command', ['penis3'], autohelp=True)
async def penis3(bot, message):
    """Is used to test threadding by sleeping."""
    print('penis')
    #time.sleep(5)
    asyncio.create_task(bot.send_privmsg([message.target], 'penis'))


@hook.hook('command', ['penis2'], admin=True)
async def penis2(client, data):
    """Is used to test threadding by sleeping."""
    print('penis')
    time.sleep(5)
    asyncio.create_task(client.message(data.target, 'penis'))


@hook.hook('command', ['penis'], gadmin=True)
async def penis(client, data):
    """Is used to test threadding by sleeping."""
    print('penis')
    time.sleep(1)
    asyncio.create_task(client.message(data.target, 'penis'))


@hook.hook('command', ['hue1', 'hue2'])
async def hue(client, data):
    """Is used for other tests."""
    print(data)
    if data.command == 'hue2':
        print('penis')
        asyncio.create_task(client.send_privmsg(data.target, 'penis'))
        return
    print('hue')
    asyncio.create_task(client.send_privmsg(data.target, 'hue'))
