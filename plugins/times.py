# Standard Libs
from asyncio import create_task
from datetime import datetime

# First Party
from core import hook

# Third Party
from pytz import timezone

# ScottSteiner 2014


@hook.hook('command', ['times'])
async def times(bot, msg):
    "times -- Shows times around the world."

    default_format = "%I:%M %p %Z"
    default_separator = " | "
    default_timezones = [("Los Angeles", "America/Los_Angeles"), ("New York", "America/New_York"),
                         ("London", "Europe/London"), ("Berlin", "Europe/Berlin"),
                         ("Kiev", "Europe/Kiev"), ("Tokyo", "Asia/Tokyo")]

    out = []
    utc = datetime.now(timezone('UTC'))

    tz_zones = bot.full_config.times.get("time_zones", default_timezones)
    tz_format = bot.full_config.times.get("format", default_format)
    tz_separator = bot.full_config.times.get("separator", default_separator)

    for (location, tztext) in tz_zones:
        tzout = utc.astimezone(timezone(tztext)).strftime(tz_format)
        out.append("{} {}".format(location, tzout))

    create_task(bot.send_privmsg([msg.target], tz_separator.join(out)))
