"""Event for logging input."""
# Copyright (C) 2019  Anthony DeDominic <adedomin@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Standard Libs
import time

# First Party
from core import hook
from util import user


@hook.hook('event', ['*'])
async def logger(client, data):
    """Is for ignoring messages from globally or channel ignored users."""
    bot = client.bot
    nolog = client.bot.config['servers'][data.server]['no_log']
    conn = client.bot.dbs[data.server]
    server = client.bot.config['servers'][data.server]['server']

    if data.nickname is not None:
        host = await user.get_mask(client, conn, data.nickname)
    else:
        host = data.nickname

    command = data.raw_command
    message = data.message
    target = data.target
    timestamp = time.strftime('%H:%M:%S')
    output = (f'<{timestamp}> <{server}> <{command}> <{host}> <{target}> '
              f'{message}')
    log_dir = bot.log_dir / data.server / time.strftime('%Y')
    raw_log_dir = log_dir / 'raw'

    if not raw_log_dir.exists():
        raw_log_dir.mkdir(parents=True)

    logfile = time.strftime('%m-%d.log')

    with (raw_log_dir / logfile).open('a') as f:
        f.write(f'[{timestamp}] {data.raw}\n')
        f.close()

    if not data.target:
        return

    log_dir = log_dir / data.target
    if data.target not in nolog:
        if not log_dir.exists():
            log_dir.mkdir(parents=True)
        with (log_dir / logfile).open('a') as f:
            f.write(timestamp + data.raw + '\n')
            f.close()
    print(output)
