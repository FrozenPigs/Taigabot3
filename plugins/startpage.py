# startpage search
# author: nojusr
#
# usage:
# .g [SEARCH QUERY]             -- Search for something on startpage
#
# .google [SEARCH QUERY]        -- Same as above
#
# .gi [SEARCH QUERY]            -- Search for images on startpage
#
# note: all commands resemble google because startpage uses google
#       as it's backbone, but it basically acts like a proxy.



from typing import List
import asyncio
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# import core db functions
from core import db, hook

startpage_link = 'https://www.startpage.com/do/search'

@hook.hook('command', ['g', 'google', 'sp', 'startpage'])
async def startpage_search(client, data):
    split = data.split_message
    
    req_data = {'query': ' '.join(split)}

    r = requests.get(startpage_link, req_data)
    
    soup = BeautifulSoup(r.text, 'html.parser')
    
    first_result = soup.find('li', class_=['search-result','search-item'] limit=1)
    title = first_result.find('h3', class_='search-item__title').find('a')
    print(title.attrs['href'])
    link = title.attrs['href']
    print(title.text)
    body = first_result.find('p', class_='search-item__body')
    print(body.text)
    output = f'{link} -- {title.text}: \"{body.text}\"'
    
    asyncio.create_task(client.message(data.target, output))

