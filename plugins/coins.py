# Standard Libs
import re
from asyncio import create_task

# First Party
from core import hook
from util import request

## CONSTANTS

exchanges = {
    "blockchain": {
        "api_url": "https://blockchain.info/ticker",
        "func": lambda data: u"[Blockchain] Buy: \x0307${:,.2f}\x0f - Sell: \x0307${:,.2f}\x0f".format(data["USD"]["buy"], \
                               data["USD"]["sell"])
    },
    "mtgox": {
        "api_url": "https://mtgox.com/api/1/BTCUSD/ticker",
        "func": lambda data: u"[MtGox] Current: \x0307{}\x0f - High: \x0307{}\x0f - Low: \x0307{}\x0f - Best Ask: \x0307{}\x0f - Volume: {}".format(data['return']['last']['display'], \
                               data['return']['high']['display'], data['return']['low']['display'], data['return']['buy']['display'], \
                               data['return']['vol']['display'])
    },
    "coinbase":{
        "api_url": "https://coinbase.com/api/v1/prices/spot_rate",
        "func": lambda data: u"[Coinbase] Current: \x0307${:,.2f}\x0f".format(float(data['amount']))
    },
    "bitpay": {
        "api_url": "https://bitpay.com/api/rates",
        "func": lambda data: u"[Bitpay] Current: \x0307${:,.2f}\x0f".format(data[0]['rate'])
    },
    "bitstamp": {
        "api_url": "https://www.bitstamp.net/api/ticker/",
        "func": lambda data: u"[BitStamp] Current: \x0307${:,.2f}\x0f - High: \x0307${:,.2f}\x0f - Low: \x0307${:,.2f}\x0f - Volume: {:,.2f} BTC".format(float(data['last']), float(data['high']), float(data['low']), \
                               float(data['volume']))
    }
}

## HOOK FUNCTIONS


@hook.hook('command', ['btc', 'bitcoin'])
async def bitcoin(bot, msg):
    """bitcoin <exchange | list> -- Gets current exchange rate for bitcoins from several exchanges, default is MtGox. Supports MtGox, Blockchain, Bitpay, Coinbase and BitStamp."""

    inp = msg.message.lower()

    if inp != msg.command:
        if inp in exchanges:
            exchange = exchanges[inp]
        else:
            create_task(
                bot.send_privmsg([msg.target],
                                 f'Available exchanges: {", ".join(exchanges.keys())}'))
            return
    else:
        exchange = exchanges["mtgox"]

    data = request.get_json(exchange["api_url"])
    func = exchange["func"]
    create_task(bot.send_privmsg([msg.target], func(data)))


@hook.hook('command', ['ltc', 'litecoin'])
async def litecoin(bot, msg):
    """litecoin -- gets current exchange rate for litecoins from BTC-E"""
    data = request.get_json("https://btc-e.com/api/2/ltc_usd/ticker")
    ticker = data['ticker']
    create_task(
        bot.send_privmsg([msg.target], "Current: \x0307${:,.2f}\x0f - High: \x0307${:,.2f}\x0f"
                         " - Low: \x0307${:,.2f}\x0f - Volume: {:,.2f} LTC".format(
                             ticker['buy'], ticker['high'], ticker['low'], ticker['vol_cur'])))


@hook.hook('command', ['dogecoin', 'doge'])
async def doge(bot, msg):
    ".doge -- Returns the value of a dogecoin."
    create_task(bot.send_privmsg([msg.target], 'Error: Doge is worthless.'))
