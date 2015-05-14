import json

import requests
from TwitterAPI import TwitterAPI, TwitterConnectionError, TwitterRequestError


_TARGETS = "16298441,318339237,125386940,3194560656,407895022,159121042,381730775"
"""Comma delimited list of userids to follow."""


with open("CREDENTIALS.json") as f:
    credentials = json.load(f)

api = TwitterAPI(credentials["consumer-key"],
                 credentials["consumer-secret"],
                 credentials["access-token"],
                 credentials["access-token-secret"])

speakers = _TARGETS.split(',')
while True:
    try:
        i = api.request('statuses/filter', {'follow': _TARGETS}).get_iterator()
        for item in i:
            if 'text' in item:
                tweeter = item['user']['name']
                tweeter_login = item['user']['screen_name']
                tweeter_id = item['user']['id_str']
                # Ignore retweets of this content:
                if tweeter_id not in speakers:
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
