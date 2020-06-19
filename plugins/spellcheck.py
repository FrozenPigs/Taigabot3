# First Party
# Standard Libs
# Standard Libs
from asyncio import create_task

from core import hook

# Third Party
import enchant
from enchant.checker import SpellChecker

locale = "en_US"


@hook.hook('command', ['spell'], autohelp=True)
async def spell(bot, msg):
    """spell <word/sentence> -- Check spelling of a word or sentence."""

    if not enchant.dict_exists(locale):
        return "Could not find dictionary: {}".format(locale)

    inp = msg.message
    if len(msg.split_message) > 1:
        # input is a sentence
        chkr = SpellChecker(locale)
        chkr.set_text(inp)

        offset = 0
        for err in chkr:
            # find the location of the incorrect word
            start = err.wordpos + offset
            finish = start + len(err.word)
            # get some suggestions for it
            suggestions = err.suggest()
            s_string = '/'.join(suggestions[:3])
            s_string = "\x02{}\x02".format(s_string)
            # calculate the offset for the next word
            offset = (offset + len(s_string)) - len(err.word)
            # replace the word with the suggestions
            inp = inp[:start] + s_string + inp[finish:]
        create_task(bot.send_privmsg([msg.target], inp))
        return
    else:
        # input is a word
        dictionary = enchant.Dict(locale)
        is_correct = dictionary.check(inp)
        suggestions = dictionary.suggest(inp)
        s_string = ', '.join(suggestions[:10])
        if is_correct:
            create_task(
                bot.send_privmsg([msg.target],
                                 f'"{inp}" appears to be \x02valid\x02! (suggestions: {s_string})'))
            return
        else:
            create_task(
                bot.send_privmsg([
                    msg.target
                ], f'"{inp}" appears to be \x02invalid\x02! (suggestions: {s_string})'))
            return
