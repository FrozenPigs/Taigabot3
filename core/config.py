"""Load and interface with config file."""
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
import json
from typing import Any, Dict, Optional, Union


def save(bot: Any) -> None:
    """Is used to save the specified config file."""
    json.dump(bot.config, bot.config_file.open('w'), indent=2)
    return None


def load(bot: Any) -> Union[Exception, Dict[str, Any]]:
    """Is used to load the specified config file, use reload."""
    return json.load(bot.config_file.open('r'))


def reload(bot: Any) -> Optional[Exception]:
    """Is used to load/reload the config file."""
    new_mtime: float = bot.config_file.stat().st_mtime
    try:
        if bot.config_mtime != new_mtime:
            if bot.config_mtime != 0.0:
                print('<<< Config Reloaded')
            bot.config_mtime = new_mtime
            bot.config = load(bot)
    except KeyError as e:
        return e
    return None
