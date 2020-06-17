# Standard Libs
from asyncio import create_task

# First Party
from core import hook
from util import request

# geoip plugin by ine (2020)


@hook.hook('command', ['geoip'])
async def geoip(bot, msg):
    "geoip <host/ip> -- Gets the location of <host/ip>"

    inp = request.urlencode(msg.message)
    data = request.get_json('https://ipinfo.io/' + inp, headers={'Accept': 'application/json'})

    if data.get('error') is not None:
        if data['error'].get('title') == 'Wrong ip':
            return '[IP] That IP is not valid'
        else:
            return '[IP] Some error ocurred'

    # example for 8.8.8.8
    loc = data.get('loc')    # 37.40, -122.07
    city = data.get('city')    # Mountain View
    country = data.get('country')    # US
    region = data.get('region')    # California
    hostname = data.get('hostname')    # dns.google
    timezone = data.get('timezone')    # unreliable
    ip = data.get('ip')    # 8.8.8.8
    org = data.get('org')    # Google LLC

    create_task(bot.send_privmsg([msg.target], f'[IP] {org} - {city}, {region}, {country}'))
