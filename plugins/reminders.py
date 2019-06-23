# plugin to save various reminders
# author: nojusr
#
# usage:
#  .reminit                      -- initialize reminder db table
#  .r [REMINDER_NAME] [MESSAGE]  -- add/append to a new reminder
#  #[REMINDER_NAME]              -- view a reminder

from typing import List
import asyncio
from datetime import datetime

# import core db functions
from core import db, hook

reminder_columns: List[str] = [
    'name', 'msg', 'time_org', 'last_updated']

max_reminder_len = 400 # maximum length of reminders

def _get_reminder_text(conn, reminder_name):
    #Finds reminder text if reminder has any
    
    out = ''
    
    rem_row = db.get_row(conn, 'reminders', 'name', reminder_name) 
    
    if len(rem_row) == 0:
        return out
    else:
        print(rem_row)
        out = rem_row[0][1]
        return out

def _create_new_reminder(conn, rem_name, rem_text):
    """Is for creating new reminders in the db"""
    rem_data = (rem_name, rem_text, str(int(time.time())), str(int(time.time())), )
    db.set_row(conn, 'reminders', rem_data)
    db.ccache();

def _append_reminder(conn, rem_name, rem_text):
    """Is for appending to old reminders in the db"""
    old_rem_text = _get_reminder_text(conn, rem_name);
    new_rem_text = f'{old_rem_text} and {rem_text}'
    
    db.set_cell(conn, 'reminders', 'msg', new_rem_text, 'name', rem_name)
    db.set_cell(conn, 'reminders', 'last_updated', str(int(time.time())), 'name', rem_name)
    db.ccache();


@hook.hook('command', ['reminit'], admin=True)
async def reminit(client, data):
    """Admin only db init hook, run once before using this plugin"""
    conn = client.bot.dbs[data.server]
    print(f'Initializing reminder database table in /persist/db/{data.server}.db...')
    db.init_table(conn, 'reminders', reminder_columns)
    db.ccache()
    print('Initialization complete.')

   

@hook.hook('command', ['r'])
async def addrem(client, data):
    """Is for adding new reminders"""
    conn = client.bot.dbs[data.server]
    split = data.message.split()
    

    tables = db.get_table_names(conn)
    if 'reminders' not in tables:
        asyncio.create_task(client.message(data.target, 'Reminder table uninitialized. Please ask your nearest bot admin to run .qinit.'))

    print ("REMINDER_DEBUG: running func")

    rem_name = split[0]
    rem_user_text = ' '.join(split[1:])
    rem_text = _get_reminder_text(conn, rem_name)    
    
    print(f'REMINDER_DEBUG: rem_name: {rem_name}, rem_user_text: {rem_user_text}, rem_text: {rem_text}')

    if rem_text == '':
        print(f'REMINDER_DEBUG: creating new reminder')
        _create_new_reminder(conn, rem_name , rem_user_text)
    else:
        print(f'REMINDER_DEBUG: appending to reminder')
        _append_reminder(conn, rem_name, rem_user_text)

    
    
