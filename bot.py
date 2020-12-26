#!/usr/local/bin/python3
# nohup /home/pi/ProjectColdBot/bot.py /home/pi/ProjectColdBot/dump.json >/dev/null &

import json
from requests_oauthlib import OAuth1Session
import discord
import datetime
import sys
import asyncio
import time
import queue
import re

# config.pyを用意
import config

MODEL_NO_2_ENABLE = False  # 2号くんモードにする場合はTrue

CK = config.CONSUMER_KEY
CS = config.CONSUMER_SECRET
AT = config.ACCESS_TOKEN
ATS = config.ACCESS_TOKEN_SECRET
twitter = OAuth1Session(CK, CS, AT, ATS)  # 認証処理

# 死神がいっこもツイートしていないせいでこれだとフォロワーを取得できない
url = "https://api.twitter.com/1.1/statuses/user_timeline.json"  # タイムライン取得エンドポイント
limit = "https://api.twitter.com/1.1/application/rate_limit_status.json"
show_user = "https://api.twitter.com/1.1/users/show.json"
fav_list = "https://api.twitter.com/1.1/favorites/list.json"


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

#ex_iine = ["aoshima_rokusen", "actress_nanano"]
ex_iine = []
#ex_follow = ["actress_nanano"]
ex_follow = []
ex_rt = []

init_json = {"ids": dic, "followings": dic,
             "favorites": dic, "statuses_count": dic}


# post_channel_config = ['考察1st', 'bot用','｢reaper｣-｢unknown｣-｢i｣監視']
post_channel_config = ['twitter監視ch']

pattern = '.*(タスケテ|たすけて|助けて|救けて)(ロボット|ろぼっと)(くん|君|クン).*'
repatter = re.compile(pattern)

with open(sys.argv[1]) as f:
    try:
        latest_dic = json.load(f)
    except:
        latest_dic = init_json

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


def get_limit():
    res = twitter.get(limit)
    ret = 0

    if res.status_code == 200:  # 正常通信出来た場合
        limits = json.loads(res.text)  # レスポンスからタイムラインリストを取得
        ret = limits["resources"]["statuses"]["/statuses/user_timeline"]["reset"]
        print(time.time()-ret)
    else:  # 正常通信出来なかった場合
        message = "Failed: %d" % res.status_code

    return ret


def get_followings(screen_name):
    params = {
        'screen_name': screen_name,
    }
    res = twitter.get(show_user, params=params)

    ret = 0
    fav = 0
    name = ''

    if res.status_code == 200:  # 正常通信出来た場合
        following = json.loads(res.text)  # レスポンスからタイムラインリストを取得
        ret = following["friends_count"]
        name = following["name"]
        fav = following["favourites_count"]
    else:  # 正常通信出来なかった場合
        ret = -1

    return ret, name, fav


def get_fav_tweet(screen_name):
    params = {
        'screen_name': screen_name,
        'count': 1
    }
    res = twitter.get(fav_list, params=params)

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


def my_round(val, digit=0):
    p = 10 ** digit
    return (val * p * 2 + 1) // 2 / p


class MiyaClient(discord.Client):

    # update_count = 0
    # iine_count = 0
    iine_list = set()
    # follow_count = 0
    follow_list = set()
    fefteen_flag = False
    post_once = False
    q = queue.Queue()

    def tweet_report(self):

        for k, v in dic.items():
            urls, id = get_latest_tweets(v, k, 1)
            following, name, fav = get_followings(v)

            if id < 0 or following < 0:
                reset = get_limit()
                dt = datetime.datetime.fromtimestamp(reset)

                self.q.put("[BOT] Twitterのリミット制限。一旦休憩します。（再開:{}）".format(dt))
                return abs(int(reset)-int(time.time()))

            else:

                if id != latest_dic["ids"][str(k)]:
                    latest_dic["flags"]["update_count"] += 1

                    for i in urls:
                        self.q.put(i)

                    latest_dic["ids"][str(k)] = id

                if following != latest_dic["followings"][str(k)]:
                    latest_dic["flags"]["update_count"] += 1
                    latest_dic["flags"]["follow_count"] += 1

                    self.follow_list.add(name)

                    bef = latest_dic["followings"][str(k)]

                    if not(v in ex_follow):
                        self.q.put(name+"のフォロー数が"+str(bef) +
                                   "から"+str(following)+"になりました")

                    latest_dic["followings"][str(k)] = following

                sec = datetime.datetime.now().second
                if int(my_round(sec, -1)/10) % 2 == 0:
                    if fav != latest_dic["favorites"][str(k)]:
                        latest_dic["flags"]["update_count"] += 1
                        latest_dic["flags"]["iine_count"] += 1

                        self.iine_list.add(name)

                        if fav > 0:
                            _, id = get_fav_tweet(v)

                        bef = latest_dic["favorites"][str(k)]

                        if not (v in ex_iine):
                            self.q.put(name+"のいいね数が"+str(bef) +
                                       "から"+str(fav)+"になりました")

                        latest_dic["favorites"][str(k)] = fav
        return 0

    def regular_report(self):
        if latest_dic["flags"]["update_count"] == 0:
            self.q.put('[BOT]この15分間で各Twitterアカウントに変化はありませんでした')
        else:
            self.q.put('[BOT]この15分間で各Twitterアカウントに更新が'+str(latest_dic["flags"]["update_count"])+'件ありました（内いいね' +
                       str(latest_dic["flags"]["iine_count"])+'件、フォロー'+str(latest_dic["flags"]["follow_count"])+'件）')
        latest_dic["flags"]["update_count"] = 0
        latest_dic["flags"]["iine_count"] = 0
        latest_dic["flags"]["follow_count"] = 0

    def life_report(self):
        dt = datetime.datetime.now()
        msg = '[BOT] '

        if dt.weekday() != 5 and dt.weekday() != 6:
            if dt.hour == 8 and dt.minute == 30:
                msg += '始業時刻です。おはようございます。'
            elif dt.hour == 8 and dt.minute == 40:
                msg += 'HRの時間です。'
            elif dt.hour >= 8 and dt.hour <= 12:
                if dt.minute == 50 and dt.hour != 12:
                    msg += f'{dt.hour-7}校時が開始しました。'
                elif dt.minute == 40 and dt.hour == 12:
                    msg += '4校時が終了し、昼休みになりました。'
                elif dt.minute == 40 and dt.hour != 8:
                    msg += f'{dt.hour-8}校時が終了しました。'
            elif dt.hour >= 13 and dt.hour <= 15:
                if dt.minute == 25 and dt.hour == 13:
                    msg += '昼休みが終わり、5校時が開始しました。'
                elif dt.minute == 25 and dt.hour != 15:
                    msg += f'{dt.hour-8}校時が開始しました。'
                elif dt.minute == 15 and dt.hour != 13:
                    msg += f'{dt.hour-9}校時が終了しました。'
                    if dt.weekday() != 2 and dt.weekday() != 3 and dt.hour == 15:
                        msg += '今日の授業はこれで終わりです、お疲れ様でした。'
            if dt.weekday() == 2 or dt.weekday() == 3:
                if dt.hour == 15 and dt.minute == 25:
                    msg += '7校時が開始しました。'
                elif dt.hour == 16 and dt.minute == 25:
                    msg += '7校時が終了しました。今日の授業はこれで終わりです、お疲れ様でした。'

        if msg != '[BOT] ':
            if self.post_once == True:
                self.post_once = False
                self.q.put(msg)
        else:
            self.post_once = True

        return self.post_once

    async def worker(self, guild):
        post_channels = []
        f = False
        # print(guild.text_channels)
        for i in guild.text_channels:
            if i.name in post_channel_config:
                post_channels.append(i)

        # self.q.put('[BOT]RESTART')

        print(post_channels)

        while True:

            start = time.time()
            print("update: " + datetime.datetime.now().isoformat() +
                  " count = "+str(latest_dic["flags"]["update_count"]))

            wait = self.tweet_report()

            min = datetime.datetime.now().minute

            if (min % 15) == 0:
                if self.fefteen_flag == False:
                    self.fefteen_flag = True
                    self.regular_report()
            else:
                self.fefteen_flag = False

             # self.life_report()

            if not self.q.empty():
                with open(sys.argv[1], "w") as f:
                    try:
                        json.dump(latest_dic, f, indent=4)
                        print("dumped")
                    except Exception as e:
                        print(e)

            while not self.q.empty():
                for i in post_channels:
                    msg = self.q.get()
                    print(msg)
                    if MODEL_NO_2_ENABLE != True or latest_dic["flags"]["send_enable"] == 1:
                        await i.send(msg)
                await asyncio.sleep(0.5)

            diff = time.time()-start
            if diff < len(dic):
                await asyncio.sleep(len(dic)-diff+0.5+wait)

    async def on_ready(self):
        print('We have logged in as {0.user}'.format(client))

    async def on_guild_available(self, guild):
        print("Connected :"+guild.name)
        task = asyncio.create_task(self.worker(guild))
        task.set_name(guild.name)
        print(asyncio.all_tasks())
        # await task
        print("Started")

    async def on_message(self, message):
        if message.author == client.user:
            return

        result = repatter.match(message.content)
        if result:
            await message.channel.send(':regional_indicator_s: :regional_indicator_t: :regional_indicator_o: :regional_indicator_p:\nオチツイテクダサイネ')

    async def on_guild_unavailable(self, guild):
        print("Guild Unavailable: " + guild.name)
        for task in asyncio.all_tasks():
            print(task.get_name())
            if task.get_name() == guild.name:
                task.cancel()

    async def on_disconnect(self):
        print("Disconnected")
        names = [i.name for i in self.guilds]
        for task in asyncio.all_tasks():
            print(task.get_name())
            if task.get_name() in names:
                task.cancel()
                print("Canceled: "+str(names))
        print("Stopped")

        # 接続が切れた時は潔く死んでsystemdに蘇生してもらう
        sys.exit(1)


if __name__ == '__main__':
    client = MiyaClient()
    client.run(config.DISCORD_TOKEN)
