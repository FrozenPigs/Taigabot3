# Standard Libs
import re
from asyncio import create_task

# First Party
from core import hook
from util import request

# linux kernel version plugin by ine (2020)


@hook.hook('command', ['kernel'])
async def kernel(bot, msg):
    data = request.get("https://www.kernel.org/finger_banner")
    lines = data.split('\n')

    versions = []
    old_versions = []
    for line in lines:
        info = re.match(r'^The latest ([[a-z0-9 \-\.]+) version of the Linux kernel is:\s*(.*)$',
                        line)
        if info is None:
            continue

        name = info.group(1)
        version = info.group(2)

        if 'longterm' in name:
            old_versions.append(version)
        else:
            versions.append(name + ': ' + version)

    output = 'Linux kernel versions: ' + '; '.join(versions)

    if len(old_versions) > 0:
        output = output + '. Old longterm versions: ' + ', '.join(old_versions)

    create_task(bot.send_privmsg([msg.target], output))
