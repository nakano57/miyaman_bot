from requests_oauthlib import OAuth1Session
import sys
import json
import time

from miyajson import Miyajson
import config


class MiyaTwi():

    mj = Miyajson()

    # 死神がいっこもツイートしていないせいでこれだとフォロワーを取得できない
    user_timeline = "https://api.twitter.com/1.1/statuses/user_timeline.json"  # タイムライン取得エンドポイント
    limit = "https://api.twitter.com/1.1/application/rate_limit_status.json"
    show_user = "https://api.twitter.com/1.1/users/show.json"
    fav_list = "https://api.twitter.com/1.1/favorites/list.json"

    CK = config.CONSUMER_KEY
    CS = config.CONSUMER_SECRET
    AT = config.ACCESS_TOKEN
    ATS = config.ACCESS_TOKEN_SECRET

    def __init__(self, modelNo):
        self.twitter = OAuth1Session(
            self.CK, self.CS, self.AT, self.ATS)  # 認証処理

        self.my_model_no = modelNo

    def get_latest_tweets(self,  screen_name, idx, count):

        params = {
            'count': count,
            'screen_name': screen_name,
            'exclude_replies': 'false'
        }

        res = self.twitter.get(self.user_timeline, params=params)

        message = []
        id = 0
        provisional_str = config.PROV_STR if idx >= config.PROVISIONAL_LINE and self.my_model_no == 2 else ''

        # 死神だけは何も返ってこない
        if res.text == '':
            print(res.text)

        if res.status_code == 200:  # 正常通信出来た場合
            timelines = json.loads(res.text)  # レスポンスからタイムラインリストを取得

            if count == 1 and timelines:  # 初回かつ死神以外
                statuses_count = timelines[0]['user']['statuses_count']
                n = statuses_count - self.mj.get_statuses_count(idx)
                self.mj.set_statuses_count(idx, statuses_count)

                if n > 1:
                    message, id = self.get_latest_tweets(
                        screen_name, idx, n)
                    message.reverse()
                    return message, id

            for line in timelines:  # タイムラインリストをループ処理

                message.append('{2}https://twitter.com/{0}/status/{1}'.format(
                    screen_name, line['id_str'], provisional_str))
                if id == 0:
                    id = line['id']

        else:  # 正常通信出来なかった場合
            print('正常通信出来なかった場合: get_latest_tweets')
            message = "Failed: %d" % res.status_code
            id = -1

        return message, id

    def get_limit(self):
        res = self.twitter.get(self.limit)

        ret = 0

        if res.status_code == 200:  # 正常通信出来た場合
            limits = json.loads(res.text)  # レスポンスからタイムラインリストを取得
            ret = limits["resources"]["statuses"]["/statuses/user_timeline"]["reset"]
            print(time.time()-ret)
        else:  # 正常通信出来なかった場合
            message = "Failed: %d" % res.status_code

        return ret

    def get_followings(self, screen_name):
        params = {
            'screen_name': screen_name,
        }
        res = self.twitter.get(self.show_user, params=params)

        ret = 0
        fav = 0
        name = ''
        profimg = ''
        bannerimg = ''

        if res.status_code == 200:  # 正常通信出来た場合
            following = json.loads(res.text)  # レスポンスからタイムラインリストを取得
            ret = following["friends_count"]
            name = following["name"]
            fav = following["favourites_count"]

            if 'profile_image_url_https' in following:
                profimg = following['profile_image_url_https'].replace('_normal.', '.')
            if 'profile_banner_url' in following:
                bannerimg = following['profile_banner_url']

        else:  # 正常通信出来なかった場合
            print('正常通信出来なかった場合: get_followings')
            ret = -1

        return ret, name, fav, profimg, bannerimg

    def get_fav_tweet(self, screen_name):
        params = {
            'screen_name': screen_name,
            'count': 1
        }
        res = self.twitter.get(self.fav_list, params=params)

        message = ''
        id = 0

        if res.status_code == 200:  # 正常通信出来た場合
            timelines = json.loads(res.text)  # レスポンスからタイムラインリストを取得
            for line in timelines:  # タイムラインリストをループ処理
                message += 'https://twitter.com/{0}/status/{1}'.format(
                    screen_name, line['id_str'])
                id = line['id']

        else:  # 正常通信出来なかった場合
            message = "Failed: %d" % res.status_code
            id = -1

        return message, id

    def my_round(self, val, digit=0):
        p = 10 ** digit
        return (val * p * 2 + 1) // 2 / p
