"""Uils for dealing with time."""
import time
import sched
import asyncio
from typing import Callable, Tuple, Dict, Any


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
