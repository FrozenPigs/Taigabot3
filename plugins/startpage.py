# startpage search
# Copyright (C) 2019  Anthony DeDominic <adedomin@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
is_gd_link = 'https://is.gd/create.php'

startpage_request_limit = 10


def _shorten_url(link):
    """ Is used to shorten a link via is.gd"""


    req_data = {'format': 'simple', 'url': link }
    r = requests.get(is_gd_link, req_data)
    if r.status_code == 200:
        return r.text
    else:
        print(f'SEARCH_DEBUG: is.gd fail: {r.status_code}, {r.text}')
        return f'Failed to shorten link: is.gd returned {r.status_code}'


def _get_first_result(req_data):
    """Is used to get the first text result from search"""
    r = requests.get(startpage_link, req_data)
    soup = BeautifulSoup(r.text, 'html.parser')

    first_result = soup.find('li', class_=['search-result','search-item'])

    return first_result

def _get_first_img_result(req_data):

    r = requests.get(startpage_link, req_data)
    soup = BeautifulSoup(r.text, 'html.parser')

    first_result = soup.find('li', id='image-0')


    return first_result


@hook.hook('command', ['g', 'google'])
async def startpage_search(client, data):
    split = data.split_message

    if len(split) < 1:
        return

    req_data = {'query': ' '.join(split)}


    first_result = _get_first_result(req_data)

    i = 0

    while first_result is None:
        print('SEARCH_DEBUG: failed to get first result, making another request')
        first_result = _get_first_result(req_data)
        await asyncio.sleep(0.5)
        i += 1
        if i > startpage_request_limit:
            print('SEARCH_DEBUG: req limit exceeded, returning')
            return


    title = first_result.find('h3', class_='search-item__title').find('a')
    link = title.attrs['href']

    short_link = _shorten_url(link)

    body = first_result.find('p', class_='search-item__body')
    output = f'{short_link} -- \02{title.text}:\02 \"{body.text}\"'

    asyncio.create_task(client.message(data.target, output))


@hook.hook('command', ['gi'])
async def startpage_img_search(client, data):
    split = data.split_message

    if len(split) < 1:
        return

    req_data = {'cat': 'pics', 'query': ' '.join(split)}

    first_result = _get_first_img_result(req_data)

    i = 0

    while first_result is None:
        print('SEARCH_DEBUG: failed to get first result for image, making another request')
        first_result = _get_first_img_result(req_data)
        await asyncio.sleep(0.5)
        i += 1
        if i > startpage_request_limit:
            print('SEARCH_DEBUG: req limit exceeded, returning')
            return


    a = first_result.find('a', class_='image-result__overlay-image')
    link = a.attrs['href']

    short_link = _shorten_url(link)
    asyncio.create_task(client.message(data.target, short_link))
