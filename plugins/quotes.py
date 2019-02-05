#quotes
#
#usage:
# .qinit                                       --- database initialization command (admin only)
# .q [nick/channel] [optional quote number]    --- for fetching quotes
# .q add [nick] [quote]                        --- for adding quotes
# .q delete [quote number]                     --- for deleting quotes (you can only delete your own quotes)
#
#made by kelp

from typing import Optional, Dict, Any, List, Set, Union, Callable, Tuple
from dataclasses import dataclass, field
import time
import asyncio
import random
import requests

#import core db functions
from core import db

#db table definition
quote_columns: List[str] = ['chan', 'nick', 'add_nick', 'msg', 'time', 'deleted']

def remove_quotes(quotelist):
	"""removes quotes from a quotelist where deleted == '1' """
	buf = []
	for quote in quotelist:
		if quote[5] != '1':
			buf.append(quote)
			
	return buf
	
def display_quote(client, data, quotelist, target, arg):
	"""
	output a quote, given a tuple list of all avalable quotes, and possibly
	a number (for selection of a specific quote)
	"""
	
	outquotes = []
	quotenums = []
	
	if arg is None:
		"""pick a random number from the quotelist if there is no argument provided"""
		print("random numarg picked.")
		numarg = random.randint(0, len(quotelist)-1)
	else:
		try:
			if int(arg) > 0:
				numarg = int(arg)-1
			elif int(arg) < 0:
				numarg = int(arg)
			else:
				numarg = 0
		except:
			wordarg = arg
	
	
	quotelist = remove_quotes(quotelist)
	
	if len(quotelist) < 1:
		asyncio.create_task(client.message(data.target, 'I have no quotes for '+target))
		return
		
	if 'numarg' in locals():
		try:
			outquotes.append(quotelist[numarg])
			if numarg < 0:
				quotenums.append(len(quotelist)+numarg+1)
			else:
				quotenums.append(numarg+1)
		except IndexError:
			if len(quotelist) == 1:
				asyncio.create_task(client.message(data.target, 'I only have 1 quote for '+target))
			else:
				asyncio.create_task(client.message(data.target, 'I only have '+str(len(quotelist))+' quotes for '+target))
	elif 'wordarg' in locals():
		for i in range(len(quotelist)):
			quote = quotelist[i]
			if wordarg in quote[3]:
				outquotes.append(quote)
				quotenums.append(i+1)
	
	"""if we have more than five quotes...."""
	if len(outquotes) > 5:
		"""append each quote with '\n', smack it right into hastebin"""
		out = ''
		for i in range(len(outquotes)):
			print("posting...")
			quote = outquotes[i]
			out += '['+str(quotenums[i])+'/'+str(len(quotelist))+']'
			out += ' <'+quote[1]+'> '+quote[3]+'\n'
			
		response = requests.post('https://hastebin.com/documents', data=out)
		if response.status_code == 200:
			d = response.json()['key']
			link = 'https://hastebin.com/'+str(d)
			asyncio.create_task(client.message(data.target, link))
		else:
			asyncio.create_task(client.message(data.target, 'Failed to upload quotes onto pastebin.'))
	
	else:
		"""if not, send each quote as a seperate message"""
		for i in range(len(outquotes)):
			quote = outquotes[i]
			out = '['+str(quotenums[i])+'/'+str(len(quotelist))+']'
			out += ' <'+quote[1]+'> '+quote[3]
			asyncio.create_task(client.message(data.target, out))
	


@hook.hook('command', ['qinit'], admin=True)
async def quoteinit(client, data):
	"""admin only quote db table initiation hook, since trying to init
	on every quote(even though the db functions account for that) is kinda wasteful"""
	conn = client.bot.dbs[data.server]
	print ('Initializing quote table in /persist/db/'+data.server+'.db...')
	db.init_table(conn, 'quotes', quote_columns)
	db.ccache()
	print ('Initialization complete.')

@hook.hook('command', ['q'])
async def quotes(client, data):
	"""main quote hook""" 
	conn = client.bot.dbs[data.server]
	split = data.message.split()
	
	tables = db.get_table_names(conn)
	if 'quotes' not in tables:
		asyncio.create_task(client.message(data.target, 'Quote table uninitialized. Please ask your nearest bot admin to run .qinit.'))
	
	"""TODO: fix weird ass edgecase with users when a nick that corresponds to a command"""
	
	if len(split) > 1:
		if split[0] == 'add':
			quote = split.copy()
			nick = quote[1]
			
			"""remove the 'add', and the nickname from the message"""
			
			quote.pop(0)
			quote.pop(0)
			
			quote = ' '.join(quote)
			quotedata = (data.target, nick, data.nickname, quote, int(time.time()), '0',)
			db.set_row(conn, 'quotes', quotedata)
			asyncio.create_task(client.message(data.target, 'Quote added.'))
			db.ccache()
			return
			
		elif split[0] == 'delete':
			nickquotes = db.get_row(conn, 'quotes', 'nick', data.nickname)
			if int(split[1]):
				if int(split[1]) > 0:
					numarg = int(split[1])-1
				elif int(split[1]) < 0:
					numarg = int(split[1])
				else:
					numarg = 0
					
			nickquotes = remove_quotes(nickquotes)
			if len(nickquotes) > 0:
				try:
					"""get quote to delete"""
					quote = nickquotes[numarg] 
				except:
					if len(nickquotes) == 1:
						asyncio.create_task(client.message(data.target, 'You only have 1 quote.'))
					else:
						asyncio.create_task(client.message(data.target, 'You only have '+str(len(nickquotes))+' quote(s).'))
					return
				
				"""gotta do custom query since i couldn't find anything in db.py that suits my needs.
				i'm using both the time and the quote itself because it's the quickest sure way to know that that quote is unique
				afaik it's very unlikely that the bot is fast enough to process two or more inputs within a second
				"""
				
				cur = conn.cursor()
				cur.execute("UPDATE quotes SET deleted='1' WHERE msg=? AND time=?", (quote[3], quote[4]))
				del cur
				conn.commit()
				db.ccache()
				asyncio.create_task(client.message(data.target, 'Quote deleted.'))
				
				return
			else:
				asyncio.create_task(client.message(data.target, 'You have no quotes.'))
				return
	
	if len(split) > 0 and len(data.message) > 0:
		argtuple = split[0], 
		
		"""convert split[0] (we now know that it needs to be compared with a db) into a tuple, since we get db results in a tuple"""
		
		if data.message[0] == '#':
			channels = db.get_column(conn, 'channels', 'channel')
			
			if argtuple in channels:
				chanquotes = db.get_row(conn, 'quotes', 'chan', split[0])
				try:
					display_quote(client, data, chanquotes, split[0], split[1])
				except:
					display_quote(client, data, chanquotes, split[0], None)
				
			else:
				asyncio.create_task(client.message(data.target, 'No quotes found for '+split[0]+'.'))
		else:
			users = db.get_column(conn, 'quotes', 'nick')
			
			if argtuple in users:
				nickquotes = db.get_row(conn, 'quotes', 'nick', split[0])
				try:
					display_quote(client, data, nickquotes, split[0], split[1])
				except:
					display_quote(client, data, nickquotes, split[0], None)
			else:
				asyncio.create_task(client.message(data.target, 'No quotes found for '+split[0]+'.'))

