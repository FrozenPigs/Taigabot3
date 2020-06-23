# Standard Libs
from asyncio import create_task

# First Party
from core import db, hook

user_columns_ready = False


def add_users_columns(bot):
    global user_columns_ready
    db.add_column(bot.db, 'users', 'battlestation')
    db.add_column(bot.db, 'users', 'desktop')
    db.add_column(bot.db, 'users', 'greeting')
    db.add_column(bot.db, 'users', 'waifu')
    db.add_column(bot.db, 'users', 'husbando')
    db.add_column(bot.db, 'users', 'imouto')
    db.add_column(bot.db, 'users', 'daughteru')
    db.add_column(bot.db, 'users', 'mom')
    db.add_column(bot.db, 'users', 'dad')
    db.add_column(bot.db, 'users', 'birthday')
    db.add_column(bot.db, 'users', 'homescreen')
    db.add_column(bot.db, 'users', 'snapchat')
    db.add_column(bot.db, 'users', 'myanimelist')
    db.add_column(bot.db, 'users', 'selfie')
    db.add_column(bot.db, 'users', 'fit')
    db.add_column(bot.db, 'users', 'handwriting')
    db.add_column(bot.db, 'users', 'steam')
    user_columns_ready = True
    print('Users Database Ready')


# Battlestations
@hook.hook('command', ['bullshit', 'keyboard', 'keyb', 'bs', 'battlestation'])
async def battlestation(bot, msg):
    "battlestation <url | @ person> -- Shows a users Battlestation."
    inp = msg.message
    nick = msg.nickname
    if not user_columns_ready:
        add_users_columns(bot)
    if inp == msg.command or '@' in inp:
        if '@' in inp:
            nick = inp.split('@')[1].strip()
        try:
            result = db.get_cell(bot.db, 'users', 'battlestation', 'nick', nick)[0][0]
        except IndexError:
            result = None
        if result:
            create_task(bot.send_privmsg([msg.target], f'{nick}: {result}'))
        else:
            if '@' not in inp:
                create_task(bot.send_notice([nick], battlestation.__doc__))
                create_task(bot.send_privmsg([msg.target], f'No battlestation saved for {nick}.'))
    elif 'del' in inp:
        db.set_cell(bot.db, 'users', 'battlestation', '', 'nick', nick)
        create_task(bot.send_notice([nick], "Deleted your battlestation."))
    elif 'http' in inp:
        db.set_cell(bot.db, 'users', 'battlestation', inp.strip(), 'nick', nick)
        create_task(bot.send_notice([nick], "Saved your battlestation."))


# # Desktops
@hook.hook('command', ['desktop'])
async def desktop(bot, msg):
    "desktop <url | @ person> -- Shows a users Desktop."
    inp = msg.message
    nick = msg.nickname
    if not user_columns_ready:
        add_users_columns(bot)
    if inp == msg.command or '@' in inp:
        if '@' in inp:
            nick = inp.split('@')[1].strip()
        try:
            result = db.get_cell(bot.db, 'users', 'desktop', 'nick', nick)[0][0]
        except IndexError:
            result = None
        if result:
            create_task(bot.send_privmsg([msg.target], f'{nick}: {result}'))
        else:
            if '@' not in inp:
                create_task(bot.send_notice([nick], desktop.__doc__))
                create_task(bot.send_privmsg([msg.target], f'No desktop saved for {nick}.'))
    elif 'del' in inp:
        db.set_cell(bot.db, 'users', 'desktop', '', 'nick', nick)
        create_task(bot.send_notice([nick], "Deleted your desktop."))
    elif 'http' in inp:
        db.set_cell(bot.db, 'users', 'desktop', inp.strip(), 'nick', nick)
        create_task(bot.send_notice([nick], "Saved your desktop."))


# # Greeting
@hook.hook('command', ['intro', 'greeting'])
async def greeting(bot, msg):
    "greeting <url | @ person> -- Shows a users Greeting."
    inp = msg.message
    nick = msg.nickname
    if not user_columns_ready:
        add_users_columns(bot)
    if inp == msg.command or '@' in inp:
        if '@' in inp:
            nick = inp.split('@')[1].strip()
        try:
            result = db.get_cell(bot.db, 'users', 'greeting', 'nick', nick)[0][0]
        except IndexError:
            result = None
        if result:
            create_task(bot.send_privmsg([msg.target], f'{nick}: {result}'))
        else:
            if '@' not in inp:
                create_task(bot.send_notice([nick], greeting.__doc__))
                create_task(bot.send_privmsg([msg.target], f'No greeting saved for {nick}.'))
    elif 'del' in inp:
        db.set_cell(bot.db, 'users', 'greeting', '', 'nick', nick)
        create_task(bot.send_notice([nick], "Deleted your greeting."))
    else:
        db.set_cell(bot.db, 'users', 'greeting', inp.strip(), 'nick', nick)
        create_task(bot.send_notice([nick], "Saved your greeting."))


# # Waifu & Husbando
@hook.hook('command', ['waifu'])
async def waifu(bot, msg):
    "waifu <url | @ person> -- Shows a users Waifu."
    inp = msg.message
    nick = msg.nickname
    if not user_columns_ready:
        add_users_columns(bot)
    if inp == msg.command or '@' in inp:
        if '@' in inp:
            nick = inp.split('@')[1].strip()
        try:
            result = db.get_cell(bot.db, 'users', 'waifu', 'nick', nick)[0][0]
        except IndexError:
            result = None
        if result:
            create_task(bot.send_privmsg([msg.target], f'{nick}: {result}'))
        else:
            if '@' not in inp:
                create_task(bot.send_notice([nick], waifu.__doc__))
                create_task(bot.send_privmsg([msg.target], f'No waifu saved for {nick}.'))
    elif 'del' in inp:
        db.set_cell(bot.db, 'users', 'waifu', '', 'nick', nick)
        create_task(bot.send_notice([nick], "Deleted your waifu."))
    else:
        db.set_cell(bot.db, 'users', 'waifu', inp.strip(), 'nick', nick)
        create_task(bot.send_notice([nick], "Saved your waifu."))


@hook.hook('command', ['husbando'])
async def husbando(bot, msg):
    "husbando <url | @ person> -- Shows a users Husbando."
    inp = msg.message
    nick = msg.nickname
    if not user_columns_ready:
        add_users_columns(bot)
    if inp == msg.command or '@' in inp:
        if '@' in inp:
            nick = inp.split('@')[1].strip()
        try:
            result = db.get_cell(bot.db, 'users', 'husbando', 'nick', nick)[0][0]
        except IndexError:
            result = None
        if result:
            create_task(bot.send_privmsg([msg.target], f'{nick}: {result}'))
        else:
            if '@' not in inp:
                create_task(bot.send_notice([nick], husbando.__doc__))
                create_task(bot.send_privmsg([msg.target], f'No husbando saved for {nick}.'))
    elif 'del' in inp:
        db.set_cell(bot.db, 'users', 'husbando', '', 'nick', nick)
        create_task(bot.send_notice([nick], "Deleted your husbando."))
    else:
        db.set_cell(bot.db, 'users', 'husbando', inp.strip(), 'nick', nick)
        create_task(bot.send_notice([nick], "Saved your husbando."))


@hook.hook('command', ['imouto'])
async def imouto(bot, msg):
    "imouto <url | @ person> -- Shows a users Imouto."
    inp = msg.message
    nick = msg.nickname
    if not user_columns_ready:
        add_users_columns(bot)
    if inp == msg.command or '@' in inp:
        if '@' in inp:
            nick = inp.split('@')[1].strip()
        try:
            result = db.get_cell(bot.db, 'users', 'imouto', 'nick', nick)[0][0]
        except IndexError:
            result = None
        if result:
            create_task(bot.send_privmsg([msg.target], f'{nick}: {result}'))
        else:
            if '@' not in inp:
                create_task(bot.send_notice([nick], imouto.__doc__))
                create_task(bot.send_privmsg([msg.target], f'No imouto saved for {nick}.'))
    elif 'del' in inp:
        db.set_cell(bot.db, 'users', 'imouto', '', 'nick', nick)
        create_task(bot.send_notice([nick], "Deleted your imouto."))
    else:
        db.set_cell(bot.db, 'users', 'imouto', inp.strip(), 'nick', nick)
        create_task(bot.send_notice([nick], "Saved your imouto."))


@hook.hook('command', ['daughteru'])
async def daughteru(bot, msg):
    "daughteru <url | @ person> -- Shows a users Daughteru."
    inp = msg.message
    nick = msg.nickname
    if not user_columns_ready:
        add_users_columns(bot)
    if inp == msg.command or '@' in inp:
        if '@' in inp:
            nick = inp.split('@')[1].strip()
        try:
            result = db.get_cell(bot.db, 'users', 'daughteru', 'nick', nick)[0][0]
        except IndexError:
            result = None
        if result:
            create_task(bot.send_privmsg([msg.target], f'{nick}: {result}'))
        else:
            if '@' not in inp:
                create_task(bot.send_notice([nick], daughteru.__doc__))
                create_task(bot.send_privmsg([msg.target], f'No daughteru saved for {nick}.'))
    elif 'del' in inp:
        db.set_cell(bot.db, 'users', 'daughteru', '', 'nick', nick)
        create_task(bot.send_notice([nick], "Deleted your daughteru."))
    else:
        db.set_cell(bot.db, 'users', 'daughteru', inp.strip(), 'nick', nick)
        create_task(bot.send_notice([nick], "Saved your daughteru."))


@hook.hook('command', ['mom'])
async def mom(bot, msg):
    "mom <url | @ person> -- Shows a users Mom."
    inp = msg.message
    nick = msg.nickname
    if not user_columns_ready:
        add_users_columns(bot)
    if inp == msg.command or '@' in inp:
        if '@' in inp:
            nick = inp.split('@')[1].strip()
        try:
            result = db.get_cell(bot.db, 'users', 'mom', 'nick', nick)[0][0]
        except IndexError:
            result = None
        if result:
            create_task(bot.send_privmsg([msg.target], f'{nick}: {result}'))
        else:
            if '@' not in inp:
                create_task(bot.send_notice([nick], mom.__doc__))
                create_task(bot.send_privmsg([msg.target], f'No mom saved for {nick}.'))
    elif 'del' in inp:
        db.set_cell(bot.db, 'users', 'mom', '', 'nick', nick)
        create_task(bot.send_notice([nick], "Deleted your mom."))
    else:
        db.set_cell(bot.db, 'users', 'mom', inp.strip(), 'nick', nick)
        create_task(bot.send_notice([nick], "Saved your mom."))


@hook.hook('command', ['dad'])
async def dad(bot, msg):
    "dad <url | @ person> -- Shows a users Dad."
    inp = msg.message
    nick = msg.nickname
    if not user_columns_ready:
        add_users_columns(bot)
    if inp == msg.command or '@' in inp:
        if '@' in inp:
            nick = inp.split('@')[1].strip()
        try:
            result = db.get_cell(bot.db, 'users', 'dad', 'nick', nick)[0][0]
        except IndexError:
            result = None
        if result:
            create_task(bot.send_privmsg([msg.target], f'{nick}: {result}'))
        else:
            if '@' not in inp:
                create_task(bot.send_notice([nick], dad.__doc__))
                create_task(bot.send_privmsg([msg.target], f'No dad saved for {nick}.'))
    elif 'del' in inp:
        db.set_cell(bot.db, 'users', 'dad', '', 'nick', nick)
        create_task(bot.send_notice([nick], "Deleted your dad."))
    else:
        db.set_cell(bot.db, 'users', 'dad', inp.strip(), 'nick', nick)
        create_task(bot.send_notice([nick], "Saved your dad."))


@hook.hook('command', ['birthday'])
async def birthday(bot, msg):
    "birthday <url | @ person> -- Shows a users Birthday."
    inp = msg.message
    nick = msg.nickname
    if not user_columns_ready:
        add_users_columns(bot)
    if inp == msg.command or '@' in inp:
        if '@' in inp:
            nick = inp.split('@')[1].strip()
        try:
            result = db.get_cell(bot.db, 'users', 'birthday', 'nick', nick)[0][0]
        except IndexError:
            result = None
        if result:
            create_task(bot.send_privmsg([msg.target], f'{nick}: {result}'))
        else:
            if '@' not in inp:
                create_task(bot.send_notice([nick], birthday.__doc__))
                create_task(bot.send_privmsg([msg.target], f'No birthday saved for {nick}.'))
    elif 'del' in inp:
        db.set_cell(bot.db, 'users', 'birthday', '', 'nick', nick)
        create_task(bot.send_notice([nick], "Deleted your birthday."))
    else:
        db.set_cell(bot.db, 'users', 'birthday', inp.strip(), 'nick', nick)
        create_task(bot.send_notice([nick], "Saved your birthday."))


# @hook.command(autohelp=False)
# def horoscope(inp, db=None, notice=None, nick=None):
#     """horoscope <sign> [save] -- Get your horoscope."""
#     save = False
#     database.init(db)

#     if '@' in inp:
#         nick = inp.split('@')[1].strip()
#         sign = database.get(db, 'users', 'horoscope', 'nick', nick)
#         if not sign:
#             return "No horoscope sign stored for {}.".format(nick)
#     else:
#         sign = database.get(db, 'users', 'horoscope', 'nick', nick)
#         if not inp:
#             if not sign:
#                 notice(horoscope.__doc__)
#                 return
#         else:
#             if not sign:
#                 save = True
#             if " save" in inp:
#                 save = True
#             sign = inp.split()[0]

#     url = "https://my.horoscope.com/astrology/free-daily-horoscope-{}.html".format(sign)
#     try:
#         result = http.get_soup(url)
#         container = result.find('div', attrs={'class': 'main-horoscope'})
#         if not container:
#             return 'Could not parse the horoscope for {}.'.format(sign)

#         paragraph = container.find('p')

#         if paragraph:
#             return nick + ': ' + paragraph.text
#         else:
#             return 'Could not read the horoscope for {}.'.format(sign)

#     except Exception:
#         raise
#         return "Could not get the horoscope for {}.".format(sign)

#     if sign and save:
#         database.set(db, 'users', 'horoscope', sign, 'nick', nick)

#     return u"\x02{}\x02 {}".format(title, horoscopetxt)


@hook.hook('command', ['hs', 'home', 'homescreen'])
async def homescreen(bot, msg):
    "homescreen <url | @ person> -- Shows a users Homescreen."
    inp = msg.message
    nick = msg.nickname
    if not user_columns_ready:
        add_users_columns(bot)
    if inp == msg.command or '@' in inp:
        if '@' in inp:
            nick = inp.split('@')[1].strip()
        try:
            result = db.get_cell(bot.db, 'users', 'homescreen', 'nick', nick)[0][0]
        except IndexError:
            result = None
        if result:
            create_task(bot.send_privmsg([msg.target], f'{nick}: {result}'))
        else:
            if '@' not in inp:
                create_task(bot.send_notice([nick], homescreen.__doc__))
                create_task(bot.send_privmsg([msg.target], f'No homescreen saved for {nick}.'))
    elif 'del' in inp:
        db.set_cell(bot.db, 'users', 'homescreen', '', 'nick', nick)
        create_task(bot.send_notice([nick], "Deleted your homescreen."))
    else:
        db.set_cell(bot.db, 'users', 'homescreen', inp.strip(), 'nick', nick)
        create_task(bot.send_notice([nick], "Saved your homescreen."))


@hook.hook('command', ['sc', 'snapchat'])
async def snapchat(bot, msg):
    "snapchat <url | @ person> -- Shows a users Snapchat."
    inp = msg.message
    nick = msg.nickname
    if not user_columns_ready:
        add_users_columns(bot)
    if inp == msg.command or '@' in inp:
        if '@' in inp:
            nick = inp.split('@')[1].strip()
        try:
            result = db.get_cell(bot.db, 'users', 'snapchat', 'nick', nick)[0][0]
        except IndexError:
            result = None
        if result:
            create_task(bot.send_privmsg([msg.target], f'{nick}: {result}'))
        else:
            if '@' not in inp:
                create_task(bot.send_notice([nick], snapchat.__doc__))
                create_task(bot.send_privmsg([msg.target], f'No snapchat saved for {nick}.'))
    elif 'del' in inp:
        db.set_cell(bot.db, 'users', 'snapchat', '', 'nick', nick)
        create_task(bot.send_notice([nick], "Deleted your snapchat."))
    else:
        db.set_cell(bot.db, 'users', 'snapchat', inp.strip(), 'nick', nick)
        create_task(bot.send_notice([nick], "Saved your snapchat."))


@hook.hook('command', ['mal', 'myanimelist'])
async def myanimelist(bot, msg):
    "myanimelist <url | @ person> -- Shows a users Myanimelist."
    inp = msg.message
    nick = msg.nickname
    if not user_columns_ready:
        add_users_columns(bot)
    if inp == msg.command or '@' in inp:
        if '@' in inp:
            nick = inp.split('@')[1].strip()
        try:
            result = db.get_cell(bot.db, 'users', 'myanimelist', 'nick', nick)[0][0]
        except IndexError:
            result = None
        if result:
            create_task(bot.send_privmsg([msg.target], f'{nick}: {result}'))
        else:
            if '@' not in inp:
                create_task(bot.send_notice([nick], myanimelist.__doc__))
                create_task(bot.send_privmsg([msg.target], f'No myanimelist saved for {nick}.'))
    elif 'del' in inp:
        db.set_cell(bot.db, 'users', 'myanimelist', '', 'nick', nick)
        create_task(bot.send_notice([nick], "Deleted your myanimelist."))
    else:
        db.set_cell(bot.db, 'users', 'myanimelist', inp.strip(), 'nick', nick)
        create_task(bot.send_notice([nick], "Saved your myanimelist."))


@hook.hook('command', ['mml', 'mymangalist'])
async def mymangalist(bot, msg):
    "mymangalist <url | @ person> -- Shows a users Mymangalist."
    inp = msg.message
    nick = msg.nickname
    if not user_columns_ready:
        add_users_columns(bot)
    if inp == msg.command or '@' in inp:
        if '@' in inp:
            nick = inp.split('@')[1].strip()
        try:
            result = db.get_cell(bot.db, 'users', 'mymangalist', 'nick', nick)[0][0]
        except IndexError:
            result = None
        if result:
            create_task(bot.send_privmsg([msg.target], f'{nick}: {result}'))
        else:
            if '@' not in inp:
                create_task(bot.send_notice([nick], mymangalist.__doc__))
                create_task(bot.send_privmsg([msg.target], f'No mymangalist saved for {nick}.'))
    elif 'del' in inp:
        db.set_cell(bot.db, 'users', 'mymangalist', '', 'nick', nick)
        create_task(bot.send_notice([nick], "Deleted your mymangalist."))
    else:
        db.set_cell(bot.db, 'users', 'mymangalist', inp.strip(), 'nick', nick)
        create_task(bot.send_notice([nick], "Saved your mymangalist."))


@hook.hook('command', ['selfie'])
async def selfie(bot, msg):
    "selfie <url | @ person> -- Shows a users Selfie."
    inp = msg.message
    nick = msg.nickname
    if not user_columns_ready:
        add_users_columns(bot)
    if inp == msg.command or '@' in inp:
        if '@' in inp:
            nick = inp.split('@')[1].strip()
        try:
            result = db.get_cell(bot.db, 'users', 'selfie', 'nick', nick)[0][0]
        except IndexError:
            result = None
        if result:
            create_task(bot.send_privmsg([msg.target], f'{nick}: {result}'))
        else:
            if '@' not in inp:
                create_task(bot.send_notice([nick], selfie.__doc__))
                create_task(bot.send_privmsg([msg.target], f'No selfie saved for {nick}.'))
    elif 'del' in inp:
        db.set_cell(bot.db, 'users', 'selfie', '', 'nick', nick)
        create_task(bot.send_notice([nick], "Deleted your selfie."))
    else:
        db.set_cell(bot.db, 'users', 'selfie', inp.strip(), 'nick', nick)
        create_task(bot.send_notice([nick], "Saved your selfie."))


@hook.hook('command', ['fit'])
async def fit(bot, msg):
    "fit <url | @ person> -- Shows a users Fit."
    inp = msg.message
    nick = msg.nickname
    if not user_columns_ready:
        add_users_columns(bot)
    if inp == msg.command or '@' in inp:
        if '@' in inp:
            nick = inp.split('@')[1].strip()
        try:
            result = db.get_cell(bot.db, 'users', 'fit', 'nick', nick)[0][0]
        except IndexError:
            result = None
        if result:
            create_task(bot.send_privmsg([msg.target], f'{nick}: {result}'))
        else:
            if '@' not in inp:
                create_task(bot.send_notice([nick], fit.__doc__))
                create_task(bot.send_privmsg([msg.target], f'No fit saved for {nick}.'))
    elif 'del' in inp:
        db.set_cell(bot.db, 'users', 'fit', '', 'nick', nick)
        create_task(bot.send_notice([nick], "Deleted your fit."))
    else:
        db.set_cell(bot.db, 'users', 'fit', inp.strip(), 'nick', nick)
        create_task(bot.send_notice([nick], "Saved your fit."))


@hook.hook('command', ['hw', 'handwriting'])
async def handwriting(bot, msg):
    "handwriting <url | @ person> -- Shows a users Handwriting."
    inp = msg.message
    nick = msg.nickname
    if not user_columns_ready:
        add_users_columns(bot)
    if inp == msg.command or '@' in inp:
        if '@' in inp:
            nick = inp.split('@')[1].strip()
        try:
            result = db.get_cell(bot.db, 'users', 'handwriting', 'nick', nick)[0][0]
        except IndexError:
            result = None
        if result:
            create_task(bot.send_privmsg([msg.target], f'{nick}: {result}'))
        else:
            if '@' not in inp:
                create_task(bot.send_notice([nick], handwriting.__doc__))
                create_task(bot.send_privmsg([msg.target], f'No handwriting saved for {nick}.'))
    elif 'del' in inp:
        db.set_cell(bot.db, 'users', 'handwriting', '', 'nick', nick)
        create_task(bot.send_notice([nick], "Deleted your handwriting."))
    else:
        db.set_cell(bot.db, 'users', 'handwriting', inp.strip(), 'nick', nick)
        create_task(bot.send_notice([nick], "Saved your handwriting."))


@hook.hook('command', ['steam'])
async def steam(bot, msg):
    "steam <url | @ person> -- Shows a users Steam."
    inp = msg.message
    nick = msg.nickname
    if not user_columns_ready:
        add_users_columns(bot)
    if inp == msg.command or '@' in inp:
        if '@' in inp:
            nick = inp.split('@')[1].strip()
        try:
            result = db.get_cell(bot.db, 'users', 'steam', 'nick', nick)[0][0]
        except IndexError:
            result = None
        if result:
            create_task(bot.send_privmsg([msg.target], f'{nick}: {result}'))
        else:
            if '@' not in inp:
                create_task(bot.send_notice([nick], steam.__doc__))
                create_task(bot.send_privmsg([msg.target], f'No steam saved for {nick}.'))
    elif 'del' in inp:
        db.set_cell(bot.db, 'users', 'steam', '', 'nick', nick)
        create_task(bot.send_notice([nick], "Deleted your steam."))
    else:
        db.set_cell(bot.db, 'users', 'steam', inp.strip(), 'nick', nick)
        create_task(bot.send_notice([nick], "Saved your steam."))
