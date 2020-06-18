# Standard Libs
import re
import time
from asyncio import create_task

# First Party
from core import db, hook

todo_db_ready = False


def init_todo_db(bot):
    global todo_db_ready
    db.init_table(bot.db, 'todo', ['user', 'text', 'added'], ['user', 'text'])
    todo_db_ready = True
    print('Todo Database Ready')


@hook.hook('command', ['todo'])
async def todo(bot, msg):
    "todo (add|del|list|search) args -- Manipulates your list of todos."
    if not todo_db_ready:
        init_todo_db(bot)

    parts = msg.split_message
    cmd = parts[0].lower()

    args = parts[1:]

    if cmd == 'add':
        if not len(args):
            return "no text"

        text = " ".join(args)
        db.set_row(bot.db, 'todo', (msg.nickname.lower(), text, time.strftime('%Y-%m-%d %H:%M:%S')))
        create_task(bot.send_notice([msg.nickname], "Task added!"))
        return
    elif cmd == 'get':
        if len(args):
            try:
                index = int(args[0])
            except ValueError:
                create_task(bot.send_notice([msg.nickname], "Invalid number format."))
                return
        else:
            index = 0

        row = list(reversed(db.get_row(bot.db, 'todo', 'user', msg.nickname.lower())))[index]

        if not row:
            create_task(bot.send_notice([msg.nickname], "No such entry."))
            return
        create_task(bot.send_notice([msg.nickname], f'[{index}]: {row[2]}: {row[1]}'))
    elif cmd == 'del' or cmd == 'delete' or cmd == 'remove':
        if not len(args):
            create_task(bot.send_privmsg([msg.target], "error"))
            return

        if args[0] == 'all':
            index = 'all'
            db.delete_row(bot.db, 'todo', 'user', msg.nickname.lower())
        else:
            try:
                index = int(args[0])
                row = list(reversed(db.get_row(bot.db, 'todo', 'user', msg.nickname.lower())))[index]
                db.delete_row(bot.db, 'todo', 'user', msg.nickname.lower(), ('text', row[1]))

            except ValueError:
                create_task(bot.send_notice([msg.nickname], "Invalid number."))
                return

        create_task(bot.send_notice([msg.nickname], f'Deleted {index} entries'))
    elif cmd == 'list':
        limit = 21

        if len(args):
            try:
                limit = int(args[0])
                limit = max(-1, limit)
            except ValueError:
                create_task(bot.send_notice([msg.nickname], "Invalid number."))
                return

        rows = list(reversed(db.get_row(bot.db, 'todo', 'user', msg.nickname.lower())[0:limit]))
        found = False
        for (index, row) in enumerate(rows):
            create_task(bot.send_notice([msg.nickname], f'[{index}]: {row[2]}: {row[1]}'))
            found = True

        if not found:
            create_task(bot.send_notice([msg.nickname], f'{msg.nickname} has no entries.'))
    elif cmd == 'search':
        if not len(args):
            create_task(bot.send_notice([msg.nickname], "No search query given!"))
            return
        query = " ".join(args)
        rows = db.get_row(bot.db, 'todo', 'user', msg.nickname.lower())
        found = False

        for (index, row) in enumerate(rows):
            if query in row[1]:
                create_task(bot.send_notice([msg.nickname], f'[{index}]: {row[2]}: {row[1]}'))
                found = True
        if not found:
            create_task(
                bot.send_notice([msg.nickname],
                                f'{msg.nickname} has no matching entries for: {query}'))
    else:
        create_task(bot.send_notice([msg.nickname], f'Unknown command: {cmd}'))
