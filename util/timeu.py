"""Uils for dealing with time."""
# Standard Libs
import asyncio
import datetime
import sched
import time
from typing import Any, Callable, Dict, Tuple

# First Party
from util import messaging


async def asyncsched(sched_time: int,
                     func: Callable,
                     args: Tuple[Any],
                     kwargs: Dict[str, Any] = None) -> None:
    """
    Schedule func to be run in sched_time.

    Func gets called with args and kwargs and should be an async function
    """
    event = sched.scheduler(time.perf_counter, time.sleep)
    if kwargs:
        event.enter(sched_time, 1, asyncio.create_task, (func(*args, **kwargs), ))
    else:
        event.enter(sched_time, 1, asyncio.create_task, (func(*args), ))
    event.run(blocking=False)


# Copyright (c) Django Software Foundation and individual contributors.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  1. Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#
#  3. Neither the name of Django nor the names of its contributors may be used
#     to endorse or promote products derived from this software without
#     specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"AND
#ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED.IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


def timesince(d, now=None):
    """
    Takes two datetime objects and returns the time between d and now
    as a nicely formatted string, e.g. "10 minutes".  If d occurs after now,
    then "0 minutes" is returned.
    Units used are years, months, weeks, days, hours, and minutes.
    Seconds and microseconds are ignored.  Up to two adjacent units will be
    displayed.  For example, "2 weeks, 3 days" and "1 year, 3 months" are
    possible outputs, but "2 weeks, 3 hours" and "1 year, 5 days" are not.
    Adapted from http://blog.natbat.co.uk/archive/2003/Jun/14/time_since
    """
    chunks = ((60 * 60 * 24 * 365, ('year', 'years')), (60 * 60 * 24 * 30, ('month', 'months')),
              (60 * 60 * 24 * 7, ('week', 'weeks')), (60 * 60 * 24, ('day', 'days')), (60 * 60, (
                  'hour', 'hours')), (60, ('minute', 'minutes')))

    # Convert int or float (unix epoch) to datetime.datetime for comparison
    if isinstance(d, int) or isinstance(d, float):
        d = datetime.datetime.fromtimestamp(d)

    # Convert datetime.date to datetime.datetime for comparison.
    if not isinstance(d, datetime.datetime):
        d = datetime.datetime(d.year, d.month, d.day)
    if now and not isinstance(now, datetime.datetime):
        now = datetime.datetime(now.year, now.month, now.day)

    if not now:
        now = datetime.datetime.now()

    # ignore microsecond part of 'd' since we removed it from 'now'
    delta = now - (d - datetime.timedelta(0, 0, d.microsecond))
    since = delta.days * 24 * 60 * 60 + delta.seconds
    if since <= 0:
        # d is in the future compared to now, stop processing.
        return u'0 ' + 'minutes'
    for i, (seconds, name) in enumerate(chunks):
        count = since // seconds
        if count != 0:
            break

    if count == 1:
        s = '%(number)d %(type)s' % {'number': count, 'type': name[0]}
    else:
        s = '%(number)d %(type)s' % {'number': count, 'type': name[1]}

    if i + 1 < len(chunks):
        # Now get the second item
        seconds2, name2 = chunks[i + 1]
        count2 = (since - (seconds * count)) // seconds2
        if count2 != 0:
            if count2 == 1:
                s += ', %d %s' % (count2, name2[0])
            else:
                s += ', %d %s' % (count2, name2[1])
    return s


def format_time(seconds, count=3, accuracy=6, simple=False):
    """
    Takes a length of time in seconds and returns a string describing that length of time.
    This function has a number of optional arguments that can be combined:
    SIMPLE: displays the time in a simple format
    >>> format_time(SECONDS)
    1 hour, 2 minutes and 34 seconds
    >>> format_time(SECONDS, simple=True)
    1h 2m 34s
    COUNT: how many periods should be shown (default 3)
    >>> format_time(SECONDS)
    147 years, 9 months and 8 weeks
    >>> format_time(SECONDS, count=6)
    147 years, 9 months, 7 weeks, 18 hours, 12 minutes and 34 seconds
    """

    if simple:
        periods = [('c', 60 * 60 * 24 * 365 * 100), ('de', 60 * 60 * 24 * 365 * 10),
                   ('y', 60 * 60 * 24 * 365), ('m', 60 * 60 * 24 * 30), ('d', 60 * 60 * 24),
                   ('h', 60 * 60), ('m', 60), ('s', 1)]
    else:
        periods = [(('century', 'centuries'), 60 * 60 * 24 * 365 * 100),
                   (('decade', 'decades'), 60 * 60 * 24 * 365 * 10),
                   (('year', 'years'), 60 * 60 * 24 * 365), (('month', 'months'), 60 * 60 * 24 * 30),
                   (('day', 'days'), 60 * 60 * 24), (('hour', 'hours'), 60 * 60),
                   (('minute', 'minutes'), 60), (('second', 'seconds'), 1)]

    periods = periods[-accuracy:]

    strings = []
    i = 0
    for period_name, period_seconds in periods:
        if i < count:
            if seconds > period_seconds:
                period_value, seconds = divmod(seconds, period_seconds)
                i += 1
                if simple:
                    strings.append("{}{}".format(period_value, period_name))
                else:
                    if period_value == 1:
                        strings.append("{} {}".format(period_value, period_name[0]))
                    else:
                        strings.append("{} {}".format(period_value, period_name[1]))
        else:
            break

    if simple:
        return " ".join(strings)
    else:
        return messaging.get_text_list(strings, "and")
