'''
Plugin which (de)cyphers a string
Doesn't cypher non-alphanumeric strings yet.
by instanceoftom
'''

# Standard Libs
from asyncio import create_task

# First Party
from core import hook

chars = "abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ "
len_chars = len(chars)


@hook.hook('command', ['cypher'])
async def cypher(bot, msg):
    "cypher <pass> <string> -- Cyphers <string> with <password>."
    inp = msg.message

    passwd = inp.split(" ")[0]
    len_passwd = len(passwd)
    inp = " ".join(inp.split(" ")[1:])

    out = ""
    passwd_index = 0
    for character in inp:
        try:
            chr_index = chars.index(character)
            passwd_chr_index = chars.index(passwd[passwd_index])

            out_chr_index = (chr_index + passwd_chr_index) % len_chars
            out_chr = chars[out_chr_index]

            out += out_chr

            passwd_index = (passwd_index + 1) % len_passwd
        except ValueError:
            out += character
            continue
    create_task(bot.send_privmsg([msg.target], out))


@hook.hook('command', ['decypher'])
async def decypher(bot, msg):
    "decypher <pass> <string> -- Decyphers <string> with <password>."
    inp = msg.message

    passwd = inp.split(" ")[0]
    len_passwd = len(passwd)
    inp = " ".join(inp.split(" ")[1:])

    passwd_index = 0
    for character in inp:
        try:
            chr_index = chars.index(character)
            passwd_index = (passwd_index + 1) % len_passwd
        except ValueError:
            continue

    passwd_index = passwd_index - 1
    reversed_message = inp[::-1]

    out = ""
    for character in reversed_message:
        try:
            chr_index = chars.index(character)
            passwd_chr_index = chars.index(passwd[passwd_index])

            out_chr_index = (chr_index - passwd_chr_index) % len_chars
            out_chr = chars[out_chr_index]

            out += out_chr

            passwd_index = (passwd_index - 1) % len_passwd
        except ValueError:
            out += character
            continue

    create_task(bot.send_privmsg([msg.target], out[::-1]))
