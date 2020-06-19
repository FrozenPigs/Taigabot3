# Standard Libs
from asyncio import create_task

# First Party
from core import hook


@hook.hook('command', ['bots'])
async def bots(bot, msg):
    create_task(
        bot.send_privmsg([msg.target],
                         "Reporting in! [Python] See https://github.com/FrozenPigs/Taigabot3"))


@hook.hook('command', ['source'])
async def source(bot, msg):
    create_task(
        bot.send_privmsg([
            msg.target
        ], "\x02Taigabot\x02 - Fuck my shit up nigga https://github.com/FrozenPigs/Taigabot3"))
