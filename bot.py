#!/usr/bin/python3
# nohup /home/pi/ProjectColdBot/bot.py /home/pi/ProjectColdBot/dump.json >/dev/null &

import json
from requests_oauthlib import OAuth1Session
import discord
import datetime
import sys
import asyncio
import time
import schedule

# config.pyを用意
import config

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
       10: "waruichigo"
       }

#ex_iine = ["aoshima_rokusen", "actress_nanano"]
ex_iine = []
#ex_follow = ["actress_nanano"]
ex_follow = []

init_json = {"ids": dic, "followings": dic, "favorites": dic}


# post_channel_config = ['考察1st', 'bot用','｢reaper｣-｢unknown｣-｢i｣監視']
post_channel_config = ['twitter監視ch']

with open(sys.argv[1]) as f:
    try:
        latest_dic = json.load(f)
    except:
        latest_dic = init_json

    print(latest_dic)


def get_latest_tweet(screen_name):

    params = {
        'count': 1,
        'screen_name': screen_name,
        'exclude_replies': 'false'
    }
    res = twitter.get(url, params=params)

    message = ''
    id = 0

    # 死神だけは何も返ってこない
    if res.text == '':
        print(res.text)

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

    update_count = 0
    iine_count = 0
    iine_list = set()
    follow_count = 0
    follow_list = set()
    fefteen_flag = False

    async def tweet_report(self, post_channels):
        print("update: " + datetime.datetime.now().isoformat() +
              " count = "+str(self.update_count))

        for k, v in dic.items():
            text, id = get_latest_tweet(v)
            following, name, fav = get_followings(v)

            if id < 0 or following < 0:
                reset = get_limit()
                dt = datetime.datetime.fromtimestamp(reset)
                for i in post_channels:
                    await i.send("[BOT]"+text+" Twitterのリミット制限。一旦休憩します。（再開:{}）".format(dt))

                await asyncio.sleep(int(reset)-int(time.time()))

            else:
                dump_flag = False
                if id != latest_dic["ids"][str(k)]:
                    self.update_count += 1
                    dump_flag = True
                    print(text)
                    for i in post_channels:
                        await i.send(text)

                    latest_dic["ids"][str(k)] = id

                if following != latest_dic["followings"][str(k)]:
                    self.update_count += 1
                    self.follow_count += 1
                    dump_flag = True
                    self.follow_list.add(name)

                    bef = latest_dic["followings"][str(k)]

                    if not(v in ex_follow):
                        for i in post_channels:
                            await i.send(name+"のフォロー数が"+str(bef)+"から"+str(following)+"になりました")
                    print(name+" follow:"+str(following))

                    latest_dic["followings"][str(k)] = following

                sec = datetime.datetime.now().second
                if int(my_round(sec, -1)/10) % 2 == 0:
                    if fav != latest_dic["favorites"][str(k)]:
                        self.update_count += 1
                        self.iine_count += 1
                        dump_flag = True
                        self.iine_list.add(name)
                        msg = ''
                        if fav > 0:
                            msg, id = get_fav_tweet(v)

                        bef = latest_dic["favorites"][str(k)]

                        if not (v in ex_iine):
                            for i in post_channels:
                                await i.send(name+"のいいね数が"+str(bef)+"から"+str(fav)+"になりました")

                        print(name+" fav:"+str(fav))

                        latest_dic["favorites"][str(k)] = fav

                # print(dump_flag)
                if dump_flag == True:
                    with open(sys.argv[1], "w") as f:
                        try:
                            json.dump(latest_dic, f, indent=4)
                            print("dumped")
                        except Exception as e:
                            print(e)

    async def regular_report(self, post_channels):
        if self.update_count == 0:
            for i in post_channels:
                await i.send('[BOT]この15分間で各Twitterアカウントに変化はありませんでした')
        else:
            for i in post_channels:
                iine = str(self.iine_list) if len(
                    self.iine_list) != 0 else ""
                fol = str(self.follow_list) if len(
                    self.follow_list) != 0 else ""
                await i.send('[BOT]この15分間で各Twitterアカウントに更新が'+str(self.update_count)+'件ありました（内いいね'+str(self.iine_count)+'件（'+iine+'）、フォロー'+str(self.follow_count)+'件（'+fol+'））')
        self.update_count = 0
        self.iine_count = 0
        self.follow_count = 0
        self.iine_list.clear()
        self.follow_list.clear()

    async def worker(self, guild):
        post_channels = []
        # print(guild.text_channels)
        for i in guild.text_channels:
            if i.name in post_channel_config:
                post_channels.append(i)

        for i in post_channels:
            await i.send('[BOT]RESTART')

        print(post_channels)

        schedule.every(11).seconds.do(self.tweet_report, (self, post_channels))
        schedule.every().minute.at(":15").do(self.regular_report, (self, post_channels))

        while True:
            schedule.run_pending()
            await asyncio.sleep(1)

    async def on_ready(self):
        print('We have logged in as {0.user}'.format(client))

    async def on_guild_available(self, guild):
        print("Task")

        for task in asyncio.all_tasks():
            print(task.get_name())
            if task.get_name() == guild.name:
                task.cancel()
                print("Task Stop")

        print("Connected :"+guild.name)

        task = asyncio.create_task(self.worker(guild))
        task.set_name(guild.name)
        print(asyncio.all_tasks())
        # await task
        print("started")

    async def on_message(self, message):
        #print('Message from {0.author}: {0.content}'.format(message))
        if message.author == client.user:
            return

        # if message.content.startswith('$hello'):
        #     await message.channel.send('Hello!')

    async def on_guild_unavailable(self, guild):
        print("Guild Unavailable: " + guild.name)
        for task in asyncio.all_tasks():
            print(task.get_name())
            if task.get_name() == guild.name:
                task.cancel()

    async def on_disconnect(self):
        print("Disconnected")
        for task in asyncio.all_tasks():
            print(task.get_name())
            if task.get_name() in self.guilds.name:
                print(self.guilds.name)
                task.cancel()


if __name__ == '__main__':
    client = MiyaClient()
    client.run(config.DISCORD_TOKEN)
