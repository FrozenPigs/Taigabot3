# wolfram alpha plugin
#
# usage:
# .urban, .ud [PHRASE]              -- ask urban dictionary to
#                                      define phrase

from core import hook

import json
import re
import urllib

@hook.hook('command', ['ud', 'urban'])
async def urban(client, data):

    # sets the index for which definition to query
    definition_index = 0

    max_response_length = 400

    query = ''
    split = data.split_message
    
    # if user is specifiying a definition index specific parsing is required
    if split[-1].isnumeric():
        # query should not have last word, which indicates definition index
        query = ' '.join(split[:-1])
        definition_index = int(split[-1])
    else:
        query = ' '.join(split)

    urban_dictionary_url = "https://api.urbandictionary.com/v0/define?term="
    word_to_define = urllib.parse.quote(query)
    request_url = urban_dictionary_url + word_to_define

    try:
        definitions = urllib.request.urlopen(request_url)
    except urllib.error.HTTPError:
        asyncio.create_task(client.message(data.target, "No definitions available."))
        return

    definitions = urllib.request.urlopen(request_url)
    j_definitions = json.load(definitions)

    # try to see if request definition index is out of range
    try:
        definition_list = j_definitions["list"][definition_index]
    except IndexError:
        asyncio.create_task(client.message(data.target, "Definition index out of range."))
        return

    definition_list = j_definitions["list"][definition_index]
    definition = definition_list["definition"].replace('\n', ' ')
    definition_no_brackets = definition.replace('[', '').replace(']', '')
    print(definition_no_brackets)

    # api caps at 10 definitions
    urban_response = "[" + str(definition_index) + "/10] " + "\02" + definition_list["word"] + ": \02" + definition_no_brackets

    # trim response length as necessary
    if len(urban_response) > max_response_length:
        asyncio.create_task(client.message(data.target, urban_response[:max_response_length] + '...'))
    else:
        asyncio.create_task(client.message(data.target, urban_response))

    return
