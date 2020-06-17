# Standard Libs
from asyncio import create_task

# First Party
from core import hook
from util import messaging, request

# urban dictionary plugin by ine (2020)

base_url = 'https://api.urbandictionary.com/v0/define?term='


def clean_text(text):
    return messaging.compress_whitespace(text.replace('[', '').replace(']', ''))


def search(input):
    json = request.get_json(base_url + request.urlencode(input))

    if json is None or "error" in json or "errors" in json:
        return ["the server fucked up"]

    data = []
    for item in json['list']:
        definition = item['definition']
        word = item['word']
        example = item['example']
        votes_up = item['thumbs_up']
        votes_down = item['thumbs_down']

        output = '\x02' + word + '\x02 '

        try:
            votes = int(votes_up) - int(votes_down)
            if votes > 0:
                votes = '+' + str(votes)
        except:
            votes = 0

        if votes != 0:
            output = output + '(' + str(votes) + ') '

        output = output + clean_text(definition)

        if example:
            output = output + ' \x02Example:\x02 ' + clean_text(example)

        data.append(output)

    return data


@hook.hook('command', ['u', 'ud', 'nig', 'ebonics', 'urban', 'urbandict', 'urbandictionary'])
async def urban(bot, msg):
    "urban <phrase> -- Looks up <phrase> on urbandictionary.com."

    inp = msg.message
    results = search(inp)

    # always return just the first one
    for result in results:
        create_task(bot.send_privmsg([msg.target], f'[ud] {result}'))
        return

    create_task(bot.send_privmsg([msg.target], '[ud] Not found'))
