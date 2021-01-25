#!/usr/local/bin/python3
# nohup /home/pi/ProjectColdBot/bot.py /home/pi/ProjectColdBot/dump.json >/dev/null &

import discord
import datetime
import sys
import asyncio
import time
import queue
import re
import os
import random

# config.pyを用意
import config
from miyajson import Miyajson
import miyatwi

MODEL_NO_2_ENABLE = config.MODEL_NO_2_ENABLE  # 2号くんモードにする場合は True
# 1号くん判別用 783629981548412948   [B]:756287897719668776　2号くん:791528352342212688
MODEL_NO_1_ID = 783629981548412948
MODEL_NO_2_ID = 791528352342212688

MODEL_NO_1_ENABLE = False if MODEL_NO_2_ENABLE else True
my_model_no = 1 if MODEL_NO_1_ENABLE else 2
partner_model_no = 3 - my_model_no


# ex_iine = ["aoshima_rokusen", "actress_nanano"]
ex_iine = []
# ex_follow = ["actress_nanano"]
ex_follow = []
ex_rt = []

# config.POST_CHANNEL_CONFIG = ['考察1st', 'bot用','｢reaper｣-｢unknown｣-｢i｣監視']

# メモ
# アカウント追加
# botctl add <screen_name>
#
# アカウント削除
# botctl delete <screen_name>
###

repatter1 = []
pattern_base1 = '(ロボ|ろぼ)(ット|っと)?(くん|君|クン)'
pattern_list1 = [
    ['ななかわ', 'ナナカワ！<:m_2_nanano:791168443851604008>'],
    ['りやりや', 'リヤリヤ！<:m_3_riya:791168443910848542>'],
    ['いおいお', 'イオイオ！<:m_7_iori:802890076321349632>'],
    ['(タスケテ|たすけて|助けて|救けて)', ':regional_indicator_s: :regional_indicator_t: :regional_indicator_o: :regional_indicator_p:\nオチツイテクダサイネ'],
    ['(参加).*(数|何人|何名|おしえて|教えて)', '[NO2_COUNT]'],
    # ['(ずがずが|ズガズガ)', '[NO2_MSG]ズガズガ？'],
    ['(とらとら|トラトラ)', '[NO2_MSG]トラトラ！'],
    ['(いちなな|イチナナ|なないち|ナナイチ)',
     '[NO2_MSG]<:m_2_nanano:791168443851604008> :heart: <:m_1_ichigo:791168439301439519>'],
    ['(りやしず|リヤシズ|しずりや|シズリヤ)',
     '[NO2_MSG]<:m_3_riya:791168443910848542> :heart: <:m_5_sizu:791168444418359317>'],
    ['(ひかれい|ヒカレイ|ヒカ玲|レイヒカ|玲ヒカ)',
     '[NO2_MSG]<:m_4_reiko:791168442966343680> :heart: <:m_6_hikari:791168442748764180>'],
    ['(どーなつ|ドーナツ|どーなっつ|ドーナッツ)', '[NO2_DOUGHNUT]'],
    ['(こんにちは|こんにちわ|コンニチハ|コンニチワ)', '[NO2_MSG]こんにちは'],
    ['(こんばんは|こんばんわ|今晩は|コンバンワ|コンバンハ)', '[NO2_MSG]こんばんは'],
    ['(癒して|癒やして|いやして)', '[NO2_MSG]すみません。現在未実装です'],
    ['(ココイチ)', '[NO2_MSG]:curry:'],
    ['(みやまん|MYMN|mymn|ＭＹＭＮ|ｍｙｍｎ|都まんじゅう|みやこまんじゅう)', '[NO2_MYMN]'],
    ['(ごはん|ご飯|御飯|ゴハン)', '[NO2_FOOD]'],
    ['(おやつ|オヤツ)', '[NO2_SWEETS]'],
    ['(スロット)', '[NO2_SLOT]'],
    ['(リーパー|りーぱー|Reaper|reaper|Ｒｅａｐｅｒ|ｒｅａｐｅｒ|REAPER|ＲＥＡＰＥＲ)', '[NO2_MSG]おやすみなさい！'],
    ['(返事|へんじ)', '[NO2_MSG]はい'],
    ['(行ってきます|行ってくる)', '[NO2_MSG]行ってらっしゃいませ'],
    ['(ただいま|タダイマ|もどった|戻った)', '[NO2_MSG]おかえりなさい'],

]

# <:m_1_ichigo:791168439301439519>
# <:m_2_nanano:791168443851604008>
# <:m_3_riya:791168443910848542>
# <:m_4_reiko:791168442966343680>
# <:m_5_sizu:791168444418359317>
# <:m_6_hikari:791168442748764180>

for i in pattern_list1:
    repatter1.append([re.compile(pattern_base1+'.*'+i[0]+'.*'), i[1]])

# 監視chのみで使えるコマンド
repatter_sys = []
pattern_base_sys1 = '(1号|１号)(くん|君|クン)'
pattern_base_sys2 = '(2号|２号)(くん|君|クン)'
pattern_list_sys = [
    # 1号くん
    [pattern_base_sys1 + '.*(おやすみ|オヤスミ|お休み|寝て|眠って).*', '[SLEEP]', 1, 1],
    [pattern_base_sys1 + '.*(おきて|起きて).*', '[SLEEP]', 1, 0],
    # 2号くん
    [pattern_base_sys2 + '.*(おやすみ|オヤスミ|お休み|寝て|眠って).*', '[SLEEP]', 2, 1],
    [pattern_base_sys2 + '.*(おきて|起きて).*', '[SLEEP]', 2, 0],
    [pattern_base_sys2 + '.*(働いて|仕事して).*', '[WAKE2]', 0, 0],
    [pattern_base_sys2 + '.*(おつかれ|お疲れ|休憩して|休んで).*', '[REST2]', 0, 0],
]

sleep_msg = [['オハヨウ！', 'おはようございます'], ['オヤスミ！', 'おやすみなさい']]

for i in pattern_list_sys:
    repatter_sys.append([re.compile(i[0]+'.*'), i[1], i[2], i[3]])


force_dic_write = False

if MODEL_NO_2_ENABLE:
    print('\n！！！！　2号くんモードです　！！！！\n')


class MiyaClient(discord.Client):

    mt = miyatwi.MiyaTwi(my_model_no)
    mj = Miyajson()

    iine_list = set()
    follow_list = set()
    fefteen_flag = False
    post_once = False
    q = queue.Queue()
    q2 = queue.Queue()

    # 2号くん用
    no2_msg = []
    last_send_time = time.time()

    def __init__(self):
        super().__init__()
        print(self.mj.latest_dic)

    def tweet_report(self):
        # key:数字　value:screen_name
        for user_id in self.mj.dic:
            try:
                urls, id = self.mt.get_latest_tweets(self.mj, user_id, 1)
            except Exception as e:
                print("get_latest_tweets : "+str(user_id))
                print(e)
                continue

            try:
                following, name, fav, profimg, bannerimg, screen_name = self.mt.get_show_user(
                    user_id)
            except Exception as e:
                print("get_followings : " + str(user_id))
                print(e)
                continue

            if id < 0 or following < 0:
                reset = self.mt.get_limit()
                dt = datetime.datetime.fromtimestamp(reset)

                self.q.put("[BOT] Twitterのリミット制限。一旦休憩します。（再開:{}）".format(dt))
                return abs(int(reset)-int(time.time()))

            else:

                if id != self.mj.get_id(user_id):
                    self.mj.update_count += 1

                    for i in urls:
                        if config.PROV_STR in i:
                            self.q2.put(i)
                        else:
                            self.q.put(i)

                    self.mj.set_id(user_id, id)

                if profimg != '' and profimg != self.mj.get_profile_image_url(user_id):
                    self.mj.update_count += 1

                    ss = '{0} のプロフィール画像が変更されました\n{1}'.format(
                        screen_name, profimg)
                    # print(ss)
                    self.q.put(ss)

                    self.mj.set_profile_image_url(user_id, profimg)

                if bannerimg != '' and bannerimg != self.mj.get_profile_banner_url(user_id):
                    self.mj.update_count += 1

                    ss = '{0} のヘッダー画像が変更されました\n{1}'.format(
                        screen_name, bannerimg)
                    # print(ss)
                    self.q.put(ss)

                    self.mj.set_profile_banner_url(user_id, bannerimg)

                if following != self.mj.get_following(user_id):
                    self.mj.update_count += 1
                    self.mj.follow_count += 1

                    self.follow_list.add(name)

                    bef = self.mj.get_following(user_id)

                    if not(screen_name in ex_follow):
                        self.q.put(name+"のフォロー数が"+str(bef) +
                                   "から"+str(following)+"になりました")

                    self.mj.set_following(user_id, following)

                sec = datetime.datetime.now().second
                if int(self.mt.my_round(sec, -1)/10) % 3 == 0:
                    if fav != self.mj.get_favorite(user_id):
                        self.mj.update_count += 1
                        self.mj.iine_count += 1

                        self.iine_list.add(name)

                        bef = self.mj.get_favorite(user_id)

                        if not (screen_name in ex_iine):
                            self.q.put(name+"のいいね数が"+str(bef) +
                                       "から"+str(fav)+"になりました")

                        self.mj.set_favorite(user_id, fav)
        return 0

    def regular_report(self):
        if self.mj.update_count == 0:
            self.q.put('[BOT]この15分間で各Twitterアカウントに変化はありませんでした')
        else:
            self.q.put('[BOT]この15分間で各Twitterアカウントに更新が'+str(self.mj.update_count)+'件ありました（内いいね' +
                       str(self.mj.iine_count)+'件、フォロー'+str(self.mj.follow_count)+'件）')
        self.mj.update_count = 0
        self.mj.iine_count = 0
        self.mj.follow_count = 0

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

    def alarm(self):
        dt = datetime.datetime.now()
        msg = '[BOT] '
        if dt.hour == 16 and dt.minute == 00:
            msg += '本日のツイート集計締め切り(17:00)まであと1時間です'

        if msg != '[BOT] ':
            if self.post_once == True:
                self.post_once = False
                self.q.put(msg)
        else:
            self.post_once = True

        return self.post_once

    def update_json(self):
        self.tweet_report()
        with self.q.mutex:
            self.q.queue.clear()

    async def worker(self, guild):
        global force_dic_write
        time_cnt = 0
        offline_cnt = 0
        post_channels = []
        f = False
        # print(guild.text_channels)
        for i in guild.text_channels:
            if i.name in config.POST_CHANNEL_CONFIG:
                post_channels.append(i)

        # self.q.put('[BOT]RESTART')

        print(post_channels)

        # dump.jsonが15分以上更新されてなかった時、死んでたと判断しsendせずjsonだけをアップデート
        json_update_time = os.stat(sys.argv[1]).st_mtime
        if (json_update_time - time.time())/60 > 15:
            print("json updated")
            self.update_json()

        # self.update_json()  # 強制更新したい場合用
        print('現在のサーバー参加者総数：{0}名\n'.format(guild.member_count))
        # await self.message_statistics(guild, 48)

        # メインループ
        while True:

            start = time.time()
            print("update: " + datetime.datetime.now().isoformat() +
                  " count = "+str(self.mj.update_count))

            wait = self.tweet_report()

            if MODEL_NO_2_ENABLE and (time_cnt % 6) == 0:
                if (start - self.last_send_time) > 16.5 * 60:
                    self.no2_wake('ガガガ')

                gmem = guild.get_member(MODEL_NO_1_ID)
                if gmem:
                    # print(gmem.raw_status)
                    no1_name = '1号'  # gmem.name
                    if gmem.raw_status == 'online':
                        offline_cnt = 0
                        if self.mj.sleep_mode_partner == 0:
                            if self.no2_rest():
                                # すでに休憩モードに入っているのでqueueに入れてもダメなのでsend
                                for i in post_channels:
                                    await i.send('あ、{0}が戻りましたね。休憩します'.format(no1_name))
                    else:
                        offline_cnt = offline_cnt + 1
                        if offline_cnt > 2:
                            self.no2_wake(
                                'あ、{0}が落ちましたね。引き継ぎます'.format(no1_name))
                else:
                    self.no2_wake()

            time_cnt = (time_cnt + 1) % 30000

            min = datetime.datetime.now().minute

            if (min % 15) == 0:
                if self.fefteen_flag == False:
                    self.fefteen_flag = True
                    self.regular_report()
            else:
                self.fefteen_flag = False

             # self.life_report()
            self.alarm()

            if force_dic_write or (not self.q.empty()):
                force_dic_write = False
                self.mj.dump()

            while not self.q.empty():
                for i in post_channels:
                    msg = self.q.get()
                    print(msg)
                    if self.mj.sleep_mode == 0:
                        if MODEL_NO_2_ENABLE:
                            if self.mj.send_enable == 1:
                                await i.send(msg)
                            else:
                                self.no2_msg.append(msg)
                        else:
                            await i.send(msg)
                await asyncio.sleep(0.5)
            # 暫定発言措置
            if MODEL_NO_2_ENABLE:
                while not self.q2.empty():
                    for i in post_channels:
                        msg = self.q2.get()
                        msg = msg[len(config.PROV_STR):]
                        print('[Provisional] '+msg)
                        await i.send(msg)
                        force_dic_write = True
                await asyncio.sleep(0.5)

            diff = time.time()-start
            if diff < len(self.mj.dic) or wait != 0:
                await asyncio.sleep(len(self.mj.dic)-diff+0.5+wait)

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

        # if ':m_6_hikari:' in message.content or ':m_4_reiko:' in message.content:
        #    print(message.content)
        # print(message.content)

        # 参加者からのメッセージ対応
        for r in repatter1:
            result = r[0].match(message.content)
            if result:
                if my_model_no == 1:
                    await self.no1_message(message, r[1])
                elif my_model_no == 2:
                    await self.no2_message(message, r[1])

        # ここから監視ch用
        if not str(message.channel) in config.POST_CHANNEL_CONFIG:
            return

        for r in repatter_sys:
            if r[0].match(message.content):
                await self.exec_sys_command(message, r[1], r[2], r[3])

        if my_model_no == 1 and message.author.id == MODEL_NO_2_ID:  # 2号くんの発言があった
            await self.check_partner_message(message)

        if my_model_no == 2 and message.author.id == MODEL_NO_1_ID:  # 1号くんの発言があった
            await self.check_partner_message(message)

        # アカウントの追加・削除
        commandlist = message.content.split()
        print("[BOT]" + str(commandlist))
        if "botctl" in commandlist:
            if "add" in commandlist:
                self.add_account(commandlist[2])
            elif "delete" in commandlist:
                self.delete_account(commandlist[2])

    # 相棒からのメッセージを調べる

    async def check_partner_message(self, message):
        global force_dic_write
        if message.content == sleep_msg[0][partner_model_no-1]:  # おはよう
            print('partner_sleep=0')
            if self.mj.sleep_mode_partner != 0:
                self.mj.sleep_mode_partner = 0
                force_dic_write = True
            if my_model_no == 2:
                if self.no2_rest():
                    await message.channel.send('おはようございます1号。では休憩に入ります')

        elif message.content == sleep_msg[1][partner_model_no-1]:  # おやすみ
            print('partner_sleep=1')
            if self.mj.sleep_mode_partner != 1:
                self.mj.sleep_mode_partner = 1
                force_dic_write = True
                if my_model_no == 2:
                    self.no2_wake('おやすみなさい1号。では引き継ぎます')
        else:
            if my_model_no == 2:
                if self.mj.sleep_mode_partner == 0:
                    if self.no2_rest():
                        print('休憩します')
                        no1_name = '1号'  # message.author.name
                        await message.channel.send('{0}が戻ってきたので休憩します'.format(no1_name))

    # 監視chのコマンドを実行

    async def exec_sys_command(self, message, cmd, arg1, arg2):
        print(cmd, arg1, arg2)
        if cmd == '[SLEEP]':
            await self.set_sleep_mode(message, arg1, arg2)

        elif cmd == '[REST2]':
            if self.no2_rest():
                await message.channel.send('ありがとうございます。休憩に入ります')

        elif cmd == '[WAKE2]':
            self.no2_wake('戻りました')

    # 参加者からのメッセージ対応（1号くん）

    async def no1_message(self, message, cmd):
        if '[NO2' in cmd:  # 2号くん用なので無視
            return
        elif '[NO1' in cmd:  # コマンド
            print('未実装')
        else:  # そのまま発言する
            await message.channel.send(cmd)

    # 参加者からのメッセージ対応（2号くん）

    async def no2_message(self, message, cmd):
        # print(cmd)
        # 基本的には1号くん優先なので大体は無視
        if cmd == '[NO2_COUNT]':
            await message.channel.send('現在のサーバー参加者総数は{0}名です'.format(message.guild.member_count))

        elif '[NO2_MSG]' in cmd:
            msg = cmd[len('[NO2_MSG]'):]
            await message.channel.send(msg)

        elif '[NO2_DOUGHNUT]' in cmd:
            ds = [':doughnut:', ':bagel:', ':cd:']
            di = [0, 0, 0]
            for j in range(3):
                r = random.randint(1, 100)
                di[j] = 1 if r >= 90 else 0
                di[j] = 2 if r == 55 else di[j]
            await message.channel.send('{0} {1} {2}'.format(ds[di[0]], ds[di[1]], ds[di[2]]))

        elif '[NO2_MYMN]' in cmd:
            ds = [
                '<:m_1_ichigo:791168439301439519>', '<:m_2_nanano:791168443851604008>',
                '<:m_3_riya:791168443910848542>', '<:m_4_reiko:791168442966343680>',
                '<:m_5_sizu:791168444418359317>', '<:m_6_hikari:791168442748764180>',
                '<:m_7_iori:802890076321349632>']
            random.shuffle(ds)
            await message.channel.send(ds[0] + ' ' + ds[1] + ' ' + ds[2] + ' ' + ds[3] + ' ' + ds[4] + ' ' + ds[5])

        elif '[NO2_FOOD]' in cmd:
            ds = [':apple:', ':bread:', ':rice:', ':pizza:', ':hamburger:', ':ramen:', ':sandwich:',
                  ':spaghetti:', ':meat_on_bone:', ':sushi:', ':hotdog:', ':curry:', ':rice_ball:']
            random.shuffle(ds)
            await message.channel.send('どうぞ')
            await message.channel.send(ds[0])

        elif '[NO2_SWEETS]' in cmd:
            ds = [':strawberry:' ':cake:', ':doughnut:', ':pancakes:', ':waffle:', ':dango:',
                  ':cookie:', ':custard:', ':icecream:', ':popcorn:', ':chocolate_bar:',
                  ':lollipop:', ':rice_cracker:', ':ice_cream:']
            random.shuffle(ds)
            await message.channel.send('どうぞ')
            await message.channel.send(ds[0])

        elif '[NO2_SLOT]' in cmd and not 'フルスロットル' in message.content:
            ds = [
                '<:m_1_ichigo:791168439301439519>', '<:m_2_nanano:791168443851604008>',
                '<:m_3_riya:791168443910848542>', '<:m_4_reiko:791168442966343680>',
                '<:m_5_sizu:791168444418359317>', '<:m_6_hikari:791168442748764180>',
                '<:m_7_iori:802890076321349632>']
            s1 = random.randint(0, 5)
            s2 = random.randint(0, 5)
            s3 = random.randint(0, 5)
            await message.channel.send('{0} {1} {2}'.format(ds[s1], ds[s2], ds[s3]))

    # スリープモードの変更

    async def set_sleep_mode(self, message, model_no, onoff):
        global force_dic_write
        if my_model_no != model_no:
            return

        if self.mj.sleep_mode == onoff:
            return

        self.mj.sleep_mode = onoff
        force_dic_write = True
        print('sleep_mode={0}'.format(onoff))

        if onoff == 1:
            await message.channel.send(sleep_msg[onoff][model_no-1])
        else:
            self.q.put(sleep_msg[onoff][model_no - 1])

    # 2号くんを休憩させる

    def no2_rest(self):
        global force_dic_write
        if self.mj.sleep_mode_partner != 0:
            self.q.put('いえ。1号が寝ているので続けます')
            return False
        self.last_send_time = time.time()
        self.no2_msg.clear()
        if self.mj.send_enable != 0:
            self.mj.send_enable = 0
            force_dic_write = True
            return True
        return False

    # 2号くんを休憩から戻す

    def no2_wake(self, comment=''):
        self.mj.sleep_mode = 0
        if self.mj.send_enable == 0:
            self.mj.send_enable = 1
            if comment != '':
                self.q.put(comment)
            for s in self.no2_msg:
                self.q.put(s)
            self.no2_msg.clear()
            return True
        return False

    # メッセージ統計出力

    async def message_statistics(self, guild, hours):
        msg_cnt = {}
        aftertime = datetime.datetime.utcnow() - datetime.timedelta(hours=hours)
        for c in guild.text_channels:
            # print('【{0}】 {1}'.format(c.name, c.id))
            if c.id != 780767711545786388 and c.id != 783661317834670090 and c.id != 797467852487393280:  # 参加ch  監視ch  ロボットくんch
                messages = await c.history(limit=None, after=aftertime).flatten()
                for h in messages:
                    # print('{2}({3}): {0}:{1}'.format(h.content, h.created_at, h.author.name, h.author.id))
                    msg_cnt.setdefault(str(h.author.id), 0)
                    msg_cnt[str(h.author.id)] += 1
        all_num = 0
        for ii in msg_cnt.values():
            all_num += ii
        print('直近{0}時間で、発言者数は{1}名でした。総発言数は{2}です'.format(
            hours, len(msg_cnt), all_num))

    def add_account(self, screen_name):
        res, k = self.mt.screen_name_to_id(screen_name)
        if res < 0:
            if MODEL_NO_2_ENABLE:
                self.q2.put(config.PROV_STR+"[BOT]エラーが発生しました")
            else:
                self.q.put("[BOT]エラーが発生しました")
            return -1
        print(screen_name, k)
        self.mj.add_key(k)
        self.update_json()

        if MODEL_NO_2_ENABLE:
            self.q2.put(config.PROV_STR+"[BOT]"+screen_name+"を追加しました")
        else:
            self.q.put("[BOT]"+screen_name+"を追加しました")

    def delete_account(self, screen_name):
        res, k = self.mt.screen_name_to_id(screen_name)
        if res < 0:
            if MODEL_NO_2_ENABLE:
                self.q2.put(config.PROV_STR+"[BOT]エラーが発生しました")
            else:
                self.q.put("[BOT]エラーが発生しました")
            return -1

        print(screen_name, k)
        res = self.mj.delete_key(k)
        if res < 0:
            if MODEL_NO_2_ENABLE:
                self.q2.put(config.PROV_STR+"[BOT]エラーが発生しました")
            else:
                self.q.put("[BOT]エラーが発生しました")
            return -1

        if MODEL_NO_2_ENABLE:
            self.q2.put(config.PROV_STR+"[BOT]"+screen_name+"を削除しました")
        else:
            self.q.put("[BOT]"+screen_name+"を削除しました")

    async def on_guild_unavailable(self, guild):
        print("Guild Unavailable: " + guild.name)
        self.mj.dump()
        for task in asyncio.all_tasks():
            print(task.get_name())
            if task.get_name() == guild.name:
                task.cancel()

    async def on_disconnect(self):
        print("Disconnected")
        self.mj.dump()
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
    if MODEL_NO_2_ENABLE:
        intents = discord.Intents.default()
        intents.presences = True
        intents.members = True
        client = MiyaClient(intents=intents)
    else:
        client = MiyaClient()
    client.run(config.DISCORD_TOKEN)
