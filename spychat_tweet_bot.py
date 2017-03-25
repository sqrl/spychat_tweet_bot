import json

import requests
from TwitterAPI import TwitterAPI, TwitterConnectionError, TwitterRequestError


_TARGETS = {
    '@TriciaLockwood': 299820130,
    '@dril': 16298441,
    '@ActualPerson084': 318339237,
    '@arealliveghost': 407895022,
    '@tomfriedman': 59157393,
    '@_FloridaMan': 1122192223,
    '@SeinfeldToday': 1000262514,
    '@famouscrab': 385412164,
    '@KingRainhead': 142733065,
    '@leyawn': 49708023,
    '@RichardDawkins': 15143478,
    '@RoboRosewater': 3242711672,
    '@greenlightgold': 795510488,
    '@erowidrecruiter': 2999876456,
    '@hedgehogdays':  1714874952,
    '@_fox_bot': 2930505258,
    '@cybershell': 28955214,
    '@mikefossey': 1960031863,
    '@wutanggoku': 119145557,
    '@getfiscal': 24254680,
    '@pisspiggranddad': 445330799,
}

with open("CREDENTIALS.json") as f:
    credentials = json.load(f)

api = TwitterAPI(credentials["consumer-key"],
                 credentials["consumer-secret"],
                 credentials["access-token"],
                 credentials["access-token-secret"])

while True:
    try:
        i = api.request('statuses/filter', {'follow': ",".join(map(str, _TARGETS.values()))}).get_iterator()
        for item in i:
            if 'text' in item:
                tweeter = item['user']['name']
                tweeter_login = item['user']['screen_name']
                tweeter_id = item['user']['id_str']
                # Ignore retweets of this content:
                if tweeter_id not in map(str, _TARGETS.values()):
                    continue
                # Ignore retweets by the users.
                if 'retweeted_status' in item:
                    continue
                if 'in_reply_to_screen_name' in item and item['in_reply_to_screen_name']:
                    continue
                # Curious cat is spammy, so ignore those:
                if 'source' in item and 'curiouscat.me' in item['source']:
                    continue
                tweet_url = u"https://twitter.com/{}/status/{}".format(tweeter_login, item['id_str'])

                payload = {"text": u"{}: <{}>".format(tweeter, tweet_url),
                           "username": "Tweet Spy",
                           "icon_emoji": ":rat:"}
                r = requests.post(credentials["slack-webhook-url"],
                                  data={'payload': json.dumps(payload)})
            elif 'disconnect' in item:
                event = item['disconnect']
                if event['code'] in [2,5,6,7]:
                    # something needs to be fixed before re-connecting
                    raise Exception(event['reason'])
                else:
                    # temporary interruption, re-try request
                    break
    except TwitterRequestError as e:
        if e.status_code < 500:
            # something needs to be fixed before re-connecting
            raise
        else:
            # temporary interruption, re-try request
            pass
    except TwitterConnectionError:
        # temporary interruption, re-try request
        pass
