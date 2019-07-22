"""Hooks for commands, events, sieves and exception catching."""
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
import functools
from typing import Any, Callable, Dict, List, Union

GenericPluginFunc = Callable[..., Any]
GenericWrapperFunc = Callable[[GenericPluginFunc], GenericPluginFunc]


def hook(hook_type: str,
         arg: List[str],
         admin: bool = False,
         gadmin: bool = False,
         autohelp: bool = False) -> GenericWrapperFunc:
    """Is used for command, event, and sieve hooks."""
    args: Dict[str, Union[List[str], bool]] = {}

    def decorator(func):
        @functools.wraps(func)
        def hook_wrapper(*args, **kwargs) -> GenericPluginFunc:
            return func(*args, **kwargs)

        setattr(hook_wrapper, '__hook__', [hook_type, args])
        return hook_wrapper

    args['name'] = arg
    args['admin'] = admin
    args['gadmin'] = gadmin
    args['autohelp'] = autohelp
    return decorator
