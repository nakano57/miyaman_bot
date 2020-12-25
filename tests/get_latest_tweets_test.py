
import json
import sys
from requests_oauthlib import OAuth1Session

# config.pyを用意
import config

CK = config.CONSUMER_KEY
CS = config.CONSUMER_SECRET
AT = config.ACCESS_TOKEN
ATS = config.ACCESS_TOKEN_SECRET
twitter = OAuth1Session(CK, CS, AT, ATS)  # 認証処理

dic = {0: "binarycity_i",
       1: "strawberry_fore",
       2: "actress_nanano",
       3: "kirakira_nanano",
       4: "riya_hoshino",
       5: "aoshima_rokusen",
       6: "iwanaga_sizu",
       7: "hikari_miyaman",
       8: "reaper_surveill",
       9: "Ft3oh35Hy51d",
       10: "waruichigo",
       11: "reiko_blueislan",
       12: "retanihoshino",
       13: "castleseven_aya"
       }


# 死神がいっこもツイートしていないせいでこれだとフォロワーを取得できない
url = "https://api.twitter.com/1.1/statuses/user_timeline.json"  # タイムライン取得エンドポイント
limit = "https://api.twitter.com/1.1/application/rate_limit_status.json"
show_user = "https://api.twitter.com/1.1/users/show.json"
fav_list = "https://api.twitter.com/1.1/favorites/list.json"


with open("/home/pi/ProjectColdBot/dump.json") as f:
    try:
        latest_dic = json.load(f)
    except:
        latest_dic = []

    print(latest_dic)


def get_latest_tweets(screen_name, idx, count):

    params = {
        'count': count,
        'screen_name': screen_name,
        'exclude_replies': 'false'
    }
    res = twitter.get(url, params=params)

    message = []
    id = 0

    # 死神だけは何も返ってこない
    if res.text == '':
        print(res.text)

    if res.status_code == 200:  # 正常通信出来た場合
        timelines = json.loads(res.text)  # レスポンスからタイムラインリストを取得

        if count == 1 and timelines:  # 初回かつ死神以外
            statuses_count = timelines[0]['user']['statuses_count']
            n = statuses_count - latest_dic["statuses_count"][str(idx)]
            latest_dic["statuses_count"][str(idx)] = statuses_count
            if n > 1:
                message, id = get_latest_tweets(screen_name, idx, n)
                message.reverse()
                return message, id

        for line in timelines:  # タイムラインリストをループ処理

            message.append('https://twitter.com/{0}/status/{1}'.format(
                screen_name, line['id_str']))
            if id == 0:
                id = line['id']

    else:  # 正常通信出来なかった場合
        message = "Failed: %d" % res.status_code
        id = -1

    return message, id


for k, v in dic.items():
    #get_latest_tweets(v, k, 1)
    print(get_latest_tweets(v, k, 1))
