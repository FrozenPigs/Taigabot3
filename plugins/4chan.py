# Standard Libs
import json
import math
import re
import time
from asyncio import create_task
from collections import deque
from threading import Thread
from time import sleep

# First Party
from core import hook
from util import request

# Third Party
import requests
from bs4 import BeautifulSoup


def get_json_data(url, sleep_time=0):
    """Returns a json data object from a given url."""
    # Respect 4chan's rule of at most 1 JSON request per second
    sleep(sleep_time)
    try:
        response = requests.get(url)
        if response.status_code == 404:
            print("url {} 404".format(url))
            return None
        json_data = json.loads(response.text.encode())
        return json_data
    except Exception as e:
        print("url: {}".format(url))
        print(e)
        raise


def sanitise(string):
    """Strips a string of all non-alphanumeric characters"""
    return re.sub(r"[^a-zA-Z0-9 ]", "", string)


def get_title(url):
    soup = request.get_soup(url)

    if '#' in url:
        postid = url.split('#')[1]
        post = soup.find('div', {'id': postid})
    else:
        post = soup.find('div', {'class': 'opContainer'})
    try:
        comment = post.find('blockquote', {
            'class': 'postMessage'
        }).renderContents().strip().decode('utf-8')
    except AttributeError:
        comment = ''
    return f'{url} - {comment}'


def sprunge(data):
    sprunge_data = {"sprunge": data}
    response = requests.post("http://sprunge.us", data=sprunge_data)
    message = response.text.strip('\n')
    return message


def search_thread(results_deque, thread_num, search_specifics):
    """
    Searches every post in thread thread_num on board board for the
    string provided. Returns a list of matching post numbers.
    """
    json_url = "https://a.4cdn.org/{0}/thread/{1}.json".format(search_specifics["board"], thread_num)
    thread_json = get_json_data(json_url)

    if thread_json is not None:
        re_search = None
        for post in thread_json["posts"]:
            user_text = "".join([post[s] for s in search_specifics["sections"] if s in post.keys()])
            re_search = re.search(search_specifics["string"], user_text, re.UNICODE + re.IGNORECASE)
            if re_search is not None:
                results_deque.append("{0}#p{1}".format(thread_num, post["no"]))


def search_page(page, search_specifics):
    """Will be run by the threading module. Searches all the 
    4chan threads on a page and adds matching results to synchronised queue"""
    threads = []
    for thread in page['threads']:
        user_text = "".join([thread[s] for s in search_specifics["sections"] if s in thread.keys()])
        if re.search(search_specifics["string"], user_text, re.UNICODE + re.IGNORECASE) is not None:
            threads.append(thread["no"])
    return threads


def process_results(board, string, threads):
    """Process the resulting data of a search and present it"""
    max_num_urls_displayed = 6
    max_num_urls_fetch = 20
    board = sanitise(board)
    message = ""
    urllist = []
    post_template = "https://boards.4chan.org/{0}/thread/{1}"
    if len(threads) <= 0:
        message = "No results for {0}".format(string)
    elif len(threads) > max_num_urls_fetch:
        #message = "Too many results for {0}".format(string)
        urls = [post_template.format(board, post_num) for post_num in threads]
        #message = " ".join(urllist[:max_num_urls_displayed])
        message = sprunge('\n'.join(urls))
    else:
        urls = [post_template.format(board, post_num) for post_num in threads]
        print(urls)
        if len(urls) > max_num_urls_displayed:
            for url in urls:
                title = get_title(url)
                urllist.append(title)
            print('\n\n'.join(urllist))
            message = sprunge('\n\n'.join(urllist))
        else:
            for url in urls:
                title = get_title(url)
                urllist.append(title[:int(120)])
            message = " ".join(urllist[:max_num_urls_displayed])

    return message


@hook.hook('command', ['4chan', 'catalog'])
async def catalog(bot, msg):
    "catalog <board> <regex> -- Search all OP posts on the catalog of a board, and return matching results"
    inp = msg.split_message
    board = inp[0]
    string = (" ".join(inp[1:])).strip()

    json_url = "https://a.4cdn.org/{0}/catalog.json".format(board)
    sections = ["com", "name", "trip", "email", "sub", "filename"]
    catalog_json = get_json_data(json_url)
    search_specifics = {"sections": sections, "board": board, "string": string}

    for page in catalog_json:
        threads = search_page(page, search_specifics)
    results = process_results(board, string, threads)
    create_task(bot.send_privmsg([msg.target], results))


@hook.hook('command', ['board'])
async def board(bot, msg):
    "board <board> <regex> -- Search all the posts on a board and return matching results"
    inp = msg.split_message
    board = inp[0]
    string = (" ".join(inp[1:]))

    json_url = "https://a.4cdn.org/{0}/threads.json".format(board)
    sections = ["com", "name", "trip", "email", "sub", "filename"]
    threads_json = get_json_data(json_url)
    search_specifics = {"sections": sections, "board": board, "string": string}

    for page in threads_json:
        threads = search_page(page, search_specifics)
    results = process_results(board, string, threads)
    create_task(bot.send_privmsg([msg.target], results))


@hook.hook('command', ['bs'])
async def bs(bot, msg):
    "bs -- Returns current battlestation threads on /g/"
    msg.message = 'g battlestation'
    msg.split_message = msg.message.split()
    create_task(catalog(bot, msg))


@hook.hook('command', ['desktops'])
async def desktops(bot, msg):
    "desktop -- Returns current desktop threads on /g/"
    msg.message = 'g desktop thread'
    msg.split_message = msg.message.split()
    create_task(catalog(bot, msg))


@hook.hook('command', ['britbong'])
async def britbong(bot, msg):
    msg.message = 'pol britbong'
    msg.split_message = msg.message.split()
    create_task(catalog(bot, msg))
