# Standard Libs
import random
import re
from asyncio import create_task
from datetime import datetime

# First Party
from core import hook
from util import timeu

# Third Party
import tweepy

TWITTER_RE = (r"(?:(?:www.twitter.com|twitter.com)/(?:[-_a-zA-Z0-9]+)/status/)([0-9]+)", re.I)


def get_api(bot):
    consumer_key = bot.full_config.api_keys.get("twitter_consumer_key")
    consumer_secret = bot.full_config.api_keys.get("twitter_consumer_secret")

    oauth_token = bot.full_config.api_keys.get("twitter_access_token")
    oauth_secret = bot.full_config.api_keys.get("twitter_access_secret")

    if not consumer_key:
        return False

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(oauth_token, oauth_secret)

    return tweepy.API(auth)


# @hook.regex(*TWITTER_RE)
# def twitter_url(match, bot=None):
#     # Find the tweet ID from the URL
#     tweet_id = match.group(1)

#     # Get the tweet using the tweepy API
#     api = get_api(bot)
#     if not api:
#         return
#     try:
#         tweet = api.get_status(tweet_id)
#         user = tweet.user
#     except tweepy.error.TweepError:
#         return

#     # Format the return the text of the tweet
#     text = " ".join(tweet.text.split())

#     if user.verified:
#         prefix = u"\u2713"
#     else:
#         prefix = ""

#     time = timeu.timesince(tweet.created_at, datetime.utcnow())
#     return u"{}@\x02{}\x02 ({}): {} ({} ago)".format(prefix, user.screen_name, user.name, text, time)


@hook.hook('command', ['tw', 'twatter', 'twitter'], autohelp=True)
async def twitter(bot, msg):
    """twitter <user> [n] -- Gets last/[n]th tweet from <user>"""
    inp = msg.message

    api = get_api(bot)
    if not api:
        create_task(bot.send_privmsg([msg.target], "Error: No Twitter API details."))
        return

    if re.match(r'^\d+$', inp):
        # user is getting a tweet by id

        try:
            # get tweet by id
            tweet = api.get_status(inp)
        except tweepy.error.TweepError as e:
            if e[0][0]['code'] == 34:
                create_task(bot.send_privmsg([msg.target], "Could not find tweet."))
                return
            else:
                create_task(
                    bot.send_privmsg([msg.target], f'Error {e[0][0]["code"]}: {e[0][0]["message"]}'))
                return

        user = tweet.user

    elif re.match(r'^\w{1,15}$', inp) or re.match(r'^\w{1,15}\s+\d+$', inp):
        # user is getting a tweet by name

        if inp.find(' ') == -1:
            username = inp
            tweet_number = 0
        else:
            username, tweet_number = inp.split()
            tweet_number = int(tweet_number) - 1

        if tweet_number > 300:
            create_task(
                bot.send_privmsg([msg.target],
                                 "This command can only find the last \x02300\x02 tweets."))
            return

        try:
            # try to get user by username
            user = api.get_user(username)
        except tweepy.error.TweepError as e:
            if e[0][0]['code'] == 34:
                create_task(bot.send_privmsg([msg.target], "Could not find user."))
                return
            else:
                create_task(
                    bot.send_privmsg([msg.target], f'Error {e[0][0]["code"]}: {e[0][0]["message"]}'))
                return

        # get the users tweets
        user_timeline = api.user_timeline(id=user.id, count=tweet_number + 1)

        # if the timeline is empty, return an error
        if not user_timeline:
            create_task(
                bot.send_privmsg([msg.target],
                                 f"The user \x02{user.screen_name}\x02 has no tweets."))
            return
        # grab the newest tweet from the users timeline
        try:
            tweet = user_timeline[tweet_number]
        except IndexError:
            tweet_count = len(user_timeline)
            create_task(
                bot.send_privmsg([
                    msg.target
                ], f"The user \x02{user.screen_name}\x02 only has \x02{tweet_count}\x02 tweets."))
            return
    elif re.match(r'^#\w+$', inp):
        # user is searching by hashtag
        search = api.search(inp)

        if not search:
            create_task(bot.send_privmsg([msg.target], "No tweets found."))
            return

        tweet = random.choice(search)
        user = tweet.user
    else:
        # ???
        create_task(bot.send_privmsg([msg.target], "Invalid Input"))
        return

    # Format the return the text of the tweet
    text = " ".join(tweet.text.split())

    if user.verified:
        prefix = u"\u2713"
    else:
        prefix = ""

    time = timeu.timesince(tweet.created_at, datetime.utcnow())
    create_task(
        bot.send_privmsg([msg.target],
                         f"{prefix}@\x02{user.screen_name}\x02 ({user.name}): {text} ({time} ago)"))


@hook.hook('command', ['twinfo', 'twuser'])
async def twuser(bot, msg):
    """twuser <user> -- Get info on the Twitter user <user>"""
    inp = msg.message
    api = get_api(bot)
    if not api:
        create_task(bot.send_privmsg([msg.target], "Error: No Twitter API details."))
        return

    try:
        # try to get user by username
        user = api.get_user(inp)
    except tweepy.error.TweepError as e:
        if e[0][0]['code'] == 34:
            create_task(bot.send_privmsg([msg.target], "Could not find user."))
            return
        else:
            create_task(bot.send_privmsg([msg.target], "Unknown error"))
            return

    if user.verified:
        prefix = u"\u2713"
    else:
        prefix = ""

    if user.location:
        loc_str = u" is located in \x02{}\x02 and".format(user.location)
    else:
        loc_str = ""

    if user.description:
        desc_str = u" The users description is \"{}\"".format(user.description)
    else:
        desc_str = ""
    create_task(
        bot.send_privmsg([
            msg.target
        ], f"{prefix}@\x02{user.screen_name}\x02 ({user.name}){loc_str} has \x02{user.statuses_count}\x02 tweets and \x02{user.followers_count}\x02 followers.{desc_str}"
                         ))
