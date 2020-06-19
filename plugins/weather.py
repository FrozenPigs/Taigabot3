# Standard Libs
import json
from asyncio import create_task
from datetime import datetime

# First Party
from core import db, hook
from util import request

# Third Party
import pytz
from geopy.geocoders import Nominatim

location_db_ready = False


def init_location_db(bot):
    "check to see that our db has the tell table and return a dbection."
    global location_db_ready
    db.init_table(bot.db, 'location', ['location', 'latlong', 'address'], ['location'])
    location_db_ready = True
    print('Location Database Ready')


def getlocation(bot, location):
    try:
        latlong = db.get_cell(bot.db, 'location', 'latlong', 'location', location)[0][0]
        address = db.get_cell(bot.db, 'location', 'address', 'location', location)[0][0]
    except IndexError:
        latlong = None
        address = None
    if not latlong:
        locator = Nominatim(user_agent="Taiga").geocode(location)
        latlong = (locator.latitude, locator.longitude)
        address = locator.address.replace('United States of America', 'USA').replace(
            'United Kingdom', 'UK')
        db.set_row(bot.db, 'location', (location, f'{latlong[0]},{latlong[1]}', address))
    else:
        latlong = latlong.split(',')
        print(latlong)
    return latlong, address


@hook.hook('command', ['alerts', 'time', 't', 'w', 'forecast'])
async def weather(bot, msg):
    "weather/time/alerts | <location> [save] | <@ user> -- Gets weather data for <location>."
    save = True
    command = msg.command[1:]
    nick = msg.nickname
    inp = msg.message
    if not location_db_ready:
        init_location_db(bot)
    if '@' in inp:
        save = False
        nick = inp.split('@')[1].strip()
        userloc = db.get_cell(bot.db, 'users', 'location', 'nick', nick)
        latlong, address = getlocation(bot, userloc)
        if not userloc:
            create_task(
                bot.send_privmsg([msg.target], "No location stored for {}.".format(
                    nick.encode('ascii', 'ignore'))))
            return
    else:
        userloc = db.get_cell(bot.db, 'users', 'location', 'nick', nick)
        if userloc:
            latlong, address = getlocation(bot, userloc)
        if inp == msg.command:
            if userloc == 'None':
                userloc = None
            if not userloc or userloc is None:
                create_task(bot.send_notice([msg.nickname], weather.__doc__))
                return
        else:
            if " dontsave" in inp:
                inp = inp.replace(' dontsave', '')
                save = False
    if inp != msg.command and '@' not in inp:
        try:
            latlong, address = getlocation(bot, inp)
        except AttributeError:
            create_task(bot.send_notice([msg.nickname], "Could not find your location, try again."))
            create_task(bot.send_notice([msg.nickname], weather.__doc__))
            return

    if inp and save:
        db.set_cell(bot.db, 'users', 'location', inp, 'nick', nick)

    secret = bot.full_config.api_keys.get("darksky")
    baseurl = 'https://api.darksky.net/forecast/{}/{},{}?exclude=minutely,flags,hourly'.format(
        secret, latlong[0], latlong[1])
    reply = request.get_json(baseurl)
    current = reply['currently']
    daily_current = reply['daily']['data'][0]

    if command == 'forecast':
        current = reply['daily']['data'][1]
        daily_current = reply['daily']['data'][1]
    if command == 'alerts':
        output = ''
        if 'alerts' not in reply:
            create_task(bot.send_privmsg([msg.target], 'No alerts for your location.'))
            return
        else:
            for alert in reply['alerts']:
                tz = pytz.timezone(reply['timezone'])
                output += '\x02{}\x02: \x02Starts:\x02 {}, \x02Ends:\x02 {}, \x02Severity:\x02 {}'.format(
                    alert['title'].encode('utf-8'),
                    datetime.fromtimestamp(alert['time'], tz).strftime('%Y-%m-%d %H:%M:%S'),
                    datetime.fromtimestamp(alert['expires'], tz).strftime('%Y-%m-%d %H:%M:%S'),
                    alert['severity'])
                if len(reply['alerts']) > 1 and reply['alerts'].index(alert) != len(
                        reply['alerts']) - 1:
                    output += ', '
            create_task(bot.send_privmsg([msg.target], output))
            return
    elif command == 'time' or command == 't':
        tz = pytz.timezone(reply['timezone'])
        time = datetime.fromtimestamp(current['time'], tz)
        create_task(
            bot.send_privmsg([msg.target], '\x02{}\x02: {}/{}'.format(
                address, time.strftime('%Y-%m-%d %I:%M:%S %p'), time.strftime('%H:%M:%S'))))
        return
    else:
        tz = pytz.timezone(reply['timezone'])
        weather_data = {
            'place':
            address,
            'summary':
            current['summary'],
            'high_f':
            int(round(daily_current['temperatureMax'])),
            'high_c':
            int(round((daily_current['temperatureMax'] - 32) * 5 / 9)),
            'low_f':
            int(round(daily_current['temperatureMin'])),
            'low_c':
            int(round((daily_current['temperatureMin'] - 32) * 5 / 9)),
            'humidity': (str(current['humidity'])[2:] if len(str(current['humidity'])) > 3 else (
                '100' if current['humidity'] == 1 else str(current['humidity'])[2:] + '0')),
            'wind_text':
            wind_type(current['windSpeed']),
            'wind_mph':
            int(round(current['windSpeed'])),
            'wind_kph':
            int(round(current['windSpeed'] * 1.609)),
            'wind_direction':
            wind_dir(current['windBearing']),
            'pressure':
            int(round(current['pressure'])),
            'uv_index':
            current['uvIndex']
        }
        try:
            weather_data['forecast'] = daily_current['summary'][:-1]
            weather_data['sunrise'] = datetime.fromtimestamp(daily_current['sunriseTime'],
                                                             tz).strftime('%I:%M:%S %p')
            weather_data['sunset'] = datetime.fromtimestamp(daily_current['sunsetTime'],
                                                            tz).strftime('%I:%M:%S %p')

        except KeyError:
            weather_data['forecast'] = 'no forecast'
            weather_data['sunrise'] = 'no sunrise'
            weather_data['sunset'] = 'no sunset'

        if command != 'forecast':
            weather_data['temp_f'] = int(round(current['temperature']))
            weather_data['temp_c'] = int(round((current['temperature'] - 32) * 5 / 9))
            weather_data['feel_f'] = int(round(current['apparentTemperature']))
            weather_data['feel_c'] = int(round((current['apparentTemperature'] - 32) * 5 / 9, 1))
        #uv index, moon phase, cloud cover, preasure, dew point, wind gust, sunset time, sunrise time, ozone,
        # precip intencity, precip probabilyty, precip type, precip intencity max
        output = "\x02{place}\x02: {summary}, {forecast}".format(**weather_data)
        if 'temp_f' in weather_data:
            output += ', \x02Currently:\x02 {temp_c}C ({temp_f}F), \x02Feels Like:\x02 {feel_c}C ({feel_f}F)'.format(
                **weather_data)
        output += ", \x02High:\x02 {high_c}C ({high_f}F), \x02Low:\x02 {low_c}C ({low_f}F), \x02Humidity:\x02 {humidity}%, \x02Wind:\x02 {wind_text} ({wind_mph} mph/{wind_kph} kph {wind_direction}), \x02Pressure:\x02 {pressure} mb, \x02Sunrise/Sunset:\02 {sunrise}/{sunset}".format(
            **weather_data)
        if weather_data['uv_index']:
            output += ', \x02UV:\x02 {uv_index}'.format(**weather_data)
        if 'alerts' in reply:
            output += ', \x0304\x02Alerts:\x02 {} (.alerts)\x03'.format(len(reply['alerts']))
        create_task(bot.send_privmsg([msg.target], output))


def wind_dir(direction):
    if direction == 0 or direction == 360:
        return 'N'
    elif direction > 0 and direction < 90:
        return 'NE'
    elif direction == 90:
        return 'E'
    elif direction > 90 and direction < 180:
        return 'SE'
    elif direction == 180:
        return 'S'
    elif direction > 180 and direction < 270:
        return 'SW'
    elif direction == 270:
        return 'W'
    else:
        return 'NW'


def wind_type(mph):
    if mph < 1:
        return 'Calm'
    elif mph <= 3:
        return 'Light Air'
    elif mph <= 7:
        return 'Light Breeze'
    elif mph <= 12:
        return 'Gentle Breeze'
    elif mph <= 18:
        return 'Moderate Breeze'
    elif mph <= 24:
        return 'Fresh Breeze'
    elif mph <= 31:
        return 'Strong Breeze'
    elif mph <= 38:
        return 'High Wind'
    elif mph <= 46:
        return 'Gale'
    elif mph <= 54:
        return 'Strong Gale'
    elif mph <= 63:
        return 'Storm'
    elif mph <= 72:
        return 'Violent Storm'
    else:
        return 'Hurricane Force'
