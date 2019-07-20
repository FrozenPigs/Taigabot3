"""Uils for dealing with time."""
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
import asyncio
import sched
import time
from typing import Any, Callable, Dict, Tuple


async def asyncsched(sched_time: int,
                     func: Callable,
                     args: Tuple[Any],
                     kwargs: Dict[str, Any] = None) -> None:
    """
    Schedule func to be run in sched_time.

    Func gets called with args and kwargs and should be an async function
    """
    s = sched.scheduler(time.perf_counter, time.sleep)
    if kwargs:
        s.enter(sched_time, 1, asyncio.create_task, (func(*args, **kwargs), ))
    else:
        s.enter(sched_time, 1, asyncio.create_task, (func(*args), ))
    s.run()
