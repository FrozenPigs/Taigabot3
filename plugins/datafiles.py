# -*- coding: utf-8 -*-

# Standard Libs
import json
import random
from asyncio import create_task
from random import randint

# First Party
#from util import hook, text, textgen
from core import hook
from util import messaging, textgen

color_codes = {"<r>": "\x02\x0305", "<g>": "\x02\x0303", "<y>": "\x02"}

with open("plugins/data/smileys.txt") as f:
    smileys = [line.strip() for line in f.readlines() if not line.startswith("//")]

with open("plugins/data/potato.txt") as f:
    potatoes = [line.strip() for line in f.readlines() if not line.startswith("//")]

with open("plugins/data/8ball_responses.txt") as f:
    responses = [line.strip() for line in f.readlines() if not line.startswith("//")]

with open("plugins/data/larts.txt") as f:
    larts = [line.strip() for line in f.readlines() if not line.startswith("//")]

with open("plugins/data/insults.txt") as f:
    insults = [line.strip() for line in f.readlines() if not line.startswith("//")]

with open("plugins/data/flirts.txt") as f:
    flirts = [line.strip() for line in f.readlines() if not line.startswith("//")]

with open("plugins/data/yiffs.txt") as f:
    yiffs = [line.strip() for line in f.readlines() if not line.startswith("//")]

with open("plugins/data/lewd.txt") as f:
    lewds = [line.strip() for line in f.readlines() if not line.startswith("//")]

with open("plugins/data/slogans.txt") as f:
    slogans = [line.strip() for line in f.readlines() if not line.startswith("//")]

def get_generator(_json, variables):
    data = json.loads(_json)
    return textgen.TextGenerator(data["templates"], data["parts"], variables=variables)


def send_phrase(bot, msg, actions):
    target = ' '.join(msg.split_message[1:])
    bot_nick = bot.server_config.nickname

    if target.lower() == bot_nick.lower() or target.lower() == "itself":
        target = msg.nickname

    values = {"user": target, "nick": bot_nick, "channel": msg.target, "yiffer": msg.nickname}
    phrase = random.choice(actions)
    create_task(messaging.send_action(bot, msg.target, phrase.format(**values)))


@hook.hook('command', ['smiley'], autohelp=False)
async def smiley(bot, msg):
    create_task(bot.send_privmsg([msg.target], smileys[random.randint(0, len(smileys) - 1)]))


@hook.hook('command', ['potato'], autohelp=True)
def potato(bot, msg):
    "potato <user> - Makes <user> a tasty little potato."
    user = ' '.join(msg.split_message[1:])
    method = random.choice(['bakes', 'fries', 'boils', 'roasts'])
    flavor = random.choice([
        'tasty', 'delectable', 'delicious', 'yummy', 'toothsome', 'scrumptious', 'luscious'
    ])
    size = random.choice(['small', 'little', 'mid-sized', 'medium-sized', 'large', 'gigantic'])
    potato_type = random.choice(potatoes)
    side_dish = random.choice([
        'side salad', 'dollop of sour cream', 'piece of chicken', 'bowl of shredded bacon'
    ])

    create_task(
        messaging.send_action(
            bot, msg.target, f'{method} a {flavor} {size} {potato_type} potato for'
            f' {user} and serves it with a small {side_dish}!'))


@hook.hook('command', ['8ball', 'eightball'], autohelp=True)
async def eightball(bot, msg):
    """8ball <question> -- The all knowing magic eight ball,
    =in electronic form. Ask and it shall be answered!"""
    magic = messaging.multiword_replace(random.choice(responses), color_codes)
    create_task(messaging.send_action(bot, msg.target, f'shakes the magic 8 ball... {magic}'))


@hook.hook('command', ['lart'])
async def lart(bot, msg):
    """lart <user> -- LARTs <user>."""
    send_phrase(bot, msg, larts)


@hook.hook('command', ['insult'])
async def insult(bot, msg):
    """insult <user> -- Makes the bot insult <user>."""
    send_phrase(bot, msg, insults)


@hook.hook('command', ['flirt'])
async def flirt(bot, msg):
    """flirt <user> -- Makes the bot flirt <user>."""
    send_phrase(bot, msg, flirts)


@hook.hook('command', ['yiff'])
async def yiff(bot, msg):
    """yiff <user> -- yiffs <user>."""
    send_phrase(bot, msg, yiffs)


@hook.hook('command', ['lewd'])
async def lewd(bot, msg):
    """lewd <user> -- lewd <user>."""
    if len(msg.split_message) == 1:
        create_task(bot.send_privmsg([msg.target], 'ヽ(◔ ◡ ◔)ノ.･ﾟ*｡･+☆LEWD☆'))
    else:
        send_phrase(bot, msg, lewds)


@hook.hook('command', ['kill'])
async def kill(bot, msg):
    """kill <user> -- Makes the bot kill <user>."""
    target = ' '.join(msg.split_message[1:])
    bot_nick = bot.server_config.nickname

    if ' ' in target:
        bot.send_notice([msg.target], 'Invalid username!')
        return

    # if the user is trying to make the bot kill itself, kill them
    if target.lower() == bot_nick.lower() or target.lower() == "itself":
        target = msg.nickname

    variables = {"user": target}

    with open("plugins/data/kills.json") as f:
        generator = get_generator(f.read(), variables)

    # act out the message
    create_task(messaging.send_action(bot, msg.target, generator.generate_string()))

@hook.hook('command', ['slap'])
async def slap(bot, msg):
    """slap <user> -- Makes the bot slap <user>."""
    target = ' '.join(msg.split_message[1:])
    bot_nick = bot.server_config.nickname

    if ' ' in target:
        bot.send_notice([msg.target], 'Invalid username!')
        return

    # if the user is trying to make the bot slap itself, slap them
    if target.lower() == bot_nick.lower() or target.lower() == "itself":
        target = msg.nickname

    variables = {"user": target}

    with open("plugins/data/slaps.json") as f:
        generator = get_generator(f.read(), variables)

    # act out the message
    create_task(messaging.send_action(bot, msg.target, generator.generate_string()))

@hook.hook('command', ['slogan'])
async def slogan(bot, msg):
    """slogan <word> -- Makes a slogan for <word>."""
    out = random.choice(slogans)
    inp = ' '.join(msg.split_message[1:])
    if inp.lower() and out.startswith("<text>"):
        inp = ' '.join([s[0].upper() + s[1:] for s in inp.split(' ')])

    create_task(bot.send_privmsg([msg.target], out.replace('<text>', inp)))

def get_filename(bot, msg, action):
    # if 'loli' in action: action = 'lolis'
    if 'insult' in action: action = 'insults'
    elif 'kek' in action: action = 'keks'
    elif 'flirt' in action: action = 'flirts'
    elif 'moist' in action: action = 'moists'
    elif 'lewd' in action: action = 'lewd'
    elif 'qt' in action: action = 'qts'
    elif 'urmom' in action: action = 'urmom'
    elif 'honry' in action: action = 'old'
    elif 'old' in action: action = 'old'
    elif 'fortune' in action: action = 'fortunes'
    elif 'slogan' in action: action = 'slogans'
    elif 'troll' in action: action = 'trolls'
    elif 'gain' in action: action = 'gainz'
    elif 'nsfw' in action: action = 'nsfw'
    else:
        bot.send_notice([msg.target], 'Invalid action')
        return
    return action

@hook.hook('command', ['add'], admin=True)
async def add(bot, msg):
    """add <type> <data> -- appends <data> to <type>.txt"""
    action = msg.split_message[1]
    text = ' '.join(msg.split_message[2:]).replace(action, '').strip()
    action = get_filename(bot, msg, action)

    with open('plugins/data/{}.txt'.format(action), 'a') as file:
        file.write(u'{}\n'.format(text))

        create_task(bot.send_notice([msg.target], '{} added.'.format(action)))
        file.close()

def process_text(bot, msg, name):
    # if not inp or inp is int:
    if 'add' in msg.message:
        add(bot, msg)
    else:
        inp = ' '.join(msg.split_message[1:])
        with open("plugins/data/{}.txt".format(name)) as file:
            lines = [line.strip() for line in file.readlines() if not line.startswith("//")]
        linecount = len(lines) - 1

        if inp and inp.isdigit(): num = int(inp) - 1
        else: num = randint(0, linecount)

        if num > linecount or num < 0:
            return "Theres nothing there baka"

        reply = '\x02[{}/{}]\x02 {}'.format(num + 1, linecount + 1, lines[num])

        file.close()
        lines = []
        return reply

@hook.hook('command', ['troll', 'wailord'])
async def troll(bot, msg):
    """troll -- Trolls on demand"""
    create_task(bot.send_privmsg([msg.target], process_text(bot, msg, "trolls")))

@hook.hook('command', ['fortune'])
async def fortune(bot, msg):
    """fortune -- Fortune cookies on demand."""
    create_task(bot.send_privmsg([msg.target], process_text(bot, msg, "fortunes")))

@hook.hook('command', ['kek', 'topkek'])
async def topkek(bot, msg):
    """topkek -- keks on demand."""
    create_task(bot.send_privmsg([msg.target], process_text(bot, msg, "keks")))


# @hook.command(autohelp=False)
# def loli(inp,say=None,notice=None):
#     """loli -- Returns a loli."""
#     say("\x02\x034NSFW\x03\x02 {}".format(process_text(inp,"lolis",notice)))
#     return

@hook.hook('command', ['moistcake'])
async def moistcake(bot, msg):
    "moistcake -- Moists on demand."
    create_task(bot.send_privmsg([msg.target], process_text(bot, msg, "moists")))


@hook.hook('command', ['qt'])
async def qt(bot, msg):
    """qt --  return qts."""
    create_task(bot.send_privmsg([msg.target], process_text(bot, msg, "qts")))


@hook.hook('command', ['urmom'])
async def urmom(bot, msg):
    """urmom --  return urmom."""
    create_task(bot.send_privmsg([msg.target], process_text(bot, msg, "urmom")))

@hook.hook('command', ['old', 'honry'])
async def honry(bot, msg):
    """honry --  return honry."""
    create_task(bot.send_privmsg([msg.target], process_text(bot, msg, 'old')))

@hook.hook('command', ['bender'])
async def bender(bot, msg):
    """bender -- Bender quotes."""
    benders = [
        "Bite my shiny, metal ass!", "Bite my glorious, golden ass!", "Bite my shiny, colossal ass!",
        "Bite my splintery, wooden ass!", "Lick my frozen, metal ass!",
        "Like most of life's problems, this one can be solved with bending.", "Cheese it!",
        "Well, I'm boned.", "Hey, sexy mama...wanna kill all humans?", "Oh! Your! God!",
        "He's pending for a bending!", "This is the worst kind of discrimination - the kind against me!",
        "In case of emergency, my ass can be used as a flotation device.",
        "In order to get busy at maximum efficiency, I need a girl with a big, 400-ton booty.",
        "I'm sick of shaking my booty for these fat jerks!", "Bite my red-hot glowing ass!",
        "All I know is, this gold says it was the best mission ever.", "Hey, guess what you're all accessories to.",
        "Well, I don't have anything else planned for today. Let's get drunk!",
        "Oh, no room for Bender, huh? Fine! I'll go build my own lunar lander! With blackjack and hookers! In fact, forget the lunar lander and the blackjack! Ah, screw the whole thing.",
        "I found it in the street! Like all the food I cook.",
        "I can't stand idly by while poor people get free food!",
        "Congratulations Fry, you've snagged the perfect girlfriend. Amy's rich, she's probably got other characteristics...",
        "You may need to metaphorically make a deal with the devil. By 'devil' I mean robot devil and by 'metaphorically' I mean get your coat.",
        "Boy, who knew a cooler could also make a handy wang coffin?",
        "Call me old fashioned but I like a dump to be as memorable as it is devastating.",
        "My life, and by extension everyone else's is meaningless.",
        "Do I preach to you while you're lying stoned in the gutter? No.",
        "Everybody's a jerk. You, me, this jerk.", "I hate the people that love me and they hate me.",
        "I've personalized each of your meals. Amy, you're cute, so I baked you a pony!",
        "Ahh, computer dating. It's like pimping, but you rarely have to use the phrase, 'upside your head'.",
        "Court s kinda fun when it s not my ass on the line!", "Maybe you can interface with my ass! By biting it!",
        "Well, I'll go build my own theme park! With blackjack and hookers! In fact, forget the park!",
        "  Compare your lives to mine and then kill yourself!",
        "I would give up my 8 other senses, even smision, for a sense of taste!", "Stupid anti-pimping laws!",
        "Blackmail s such an ugly word. I prefer extortion. The x makes it sound cool.",
        "Great is ok, but amazing would be great!", "The pie is ready. You guys like swarms of things, right?",
        "Fry cracked corn, and I don't care; Leela cracked corn, I still don't care; Bender cracked corn, and he is great! Take that you stupid corn!",
        "Stay away from our women. You got metal fever, baby, metal fever!",
        "If it ain't black and white, peck, scratch and bite.", "Life is hilariously cruel.",
        "Pardon me, brother. Care to donate to the anti-mugging you fund?",
        "I love this planet. I've got wealth, fame, and access to the depths of sleaze that those things bring.",
        "C'mon, it's just like making love. Y'know, left, down, rotate sixty-two degrees, engage rotors...",
        "Oh my God, I'm so excited I wish I could wet my pants.", "Argh. The laws of science be a harsh mistress.",
        "In the event of an emergency, my ass can be used as a floatation device.",
        "Hey, I got a busted ass here! I don't see anyone kissing it.",
        "I'm a fraud - a poor, lazy, sexy fraud.", "This'll show those filthy bastards who's loveable!"
    ]
    create_task(bot.send_privmsg([msg.target], random.choice(benders)))
    benders = []

@hook.hook('command', ['gains', 'gainz'])
async def gainz(bot, msg):
    """gains -- SICK GAINZ BRO"""
    create_task(bot.send_privmsg([msg.target], process_text(bot, msg, "gainz")))


@hook.hook('command', ['nsfw'])
async def nsfw(bot, msg):
    """nsfw -- Have a nice fap"""
    create_task(bot.send_privmsg([msg.target], process_text(bot, msg, "nsfw")))
