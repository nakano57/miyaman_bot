import sys
import json


# データダンプ用のjsonのwrapper
class Miyajson():
    dic_base = {0: "binarycity_i",
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

    init_json = {"ids": dic_base, "followings": dic_base,
                 "favorites": dic_base, "statuses_count": dic_base,
                 "profile_image_url": dic_base, "profile_banner_url": dic_base,
                 "display_name": dic_base, "screen_name": dic_base}

    def __init__(self) -> None:
        with open(sys.argv[1]) as f:
            try:
                self.latest_dic = json.load(f)
            except:
                self.latest_dic = Miyajson.init_json

        self.dic = list(map(int, list(self.latest_dic["ids"].keys())))

        self.update_count = self.latest_dic["flags"]["update_count"]
        self.iine_count = self.latest_dic["flags"]["iine_count"]
        self.follow_count = self.latest_dic["flags"]["follow_count"]
        self.send_enable = self.latest_dic["flags"]["send_enable"]
        self.sleep_mode = self.latest_dic["flags"]["sleep_mode"]
        self.sleep_mode_partner = self.latest_dic["flags"]["sleep_mode_partner"]

    def dump(self):
        self.latest_dic["flags"]["update_count"] = self.update_count
        self.latest_dic["flags"]["iine_count"] = self.iine_count
        self.latest_dic["flags"]["follow_count"] = self.follow_count
        self.latest_dic["flags"]["send_enable"] = self.send_enable
        self.latest_dic["flags"]["sleep_mode"] = self.sleep_mode
        self.latest_dic["flags"]["sleep_mode_partner"] = self.sleep_mode_partner
        with open(sys.argv[1], "w") as f:
            try:
                json.dump(self.latest_dic, f, indent=4)
                print("dumped")
            except Exception as e:
                print(e)

    def get_id(self, k):
        return self.latest_dic["ids"][str(k)]

    def set_id(self, k, n):
        self.latest_dic["ids"][str(k)] = n

    def get_following(self, k):
        return self.latest_dic["followings"][str(k)]

    def set_following(self, k, n):
        self.latest_dic["followings"][str(k)] = n

    def get_favorite(self, k):
        return self.latest_dic["favorites"][str(k)]

    def set_favorite(self, k, n):
        self.latest_dic["favorites"][str(k)] = n

    def get_statuses_count(self, k):
        return self.latest_dic["statuses_count"][str(k)]

    def set_statuses_count(self, k, n):
        self.latest_dic["statuses_count"][str(k)] = n

    def get_profile_image_url(self, k):
        return self.latest_dic["profile_image_url"][str(k)]

    def set_profile_image_url(self, k, n):
        self.latest_dic["profile_image_url"][str(k)] = n

    def get_profile_banner_url(self, k):
        return self.latest_dic["profile_banner_url"][str(k)]

    def set_profile_banner_url(self, k, n):
        self.latest_dic["profile_banner_url"][str(k)] = n

    def get_display_name(self, k):
        return self.latest_dic["display_name"][str(k)]

    def set_display_name(self, k, n):
        self.latest_dic["display_name"][str(k)] = n

    def get_screen_name(self, k):
        return self.latest_dic["screen_name"][str(k)]

    def set_screen_name(self, k, n):
        self.latest_dic["screen_name"][str(k)] = n

    def get_name(self, k):
        pass

    def set_name(self, k, n):
        pass

    def add_key(self, k):
        d = {str(k): 0}
        self.latest_dic["ids"].update(d)
        self.latest_dic["followings"].update(d)
        self.latest_dic["favorites"].update(d)
        self.latest_dic["statuses_count"].update(d)
        self.latest_dic["profile_image_url"].update(d)
        self.latest_dic["profile_banner_url"].update(d)
        self.latest_dic["screen_name"].update(d)
        self.latest_dic["display_name"].update(d)
        self.dump()
        self.dic = list(map(int, list(self.latest_dic["ids"].keys())))

    def delete_key(self, k):
        try:
            del self.latest_dic["ids"][str(k)]
            del self.latest_dic["followings"][str(k)]
            del self.latest_dic["favorites"][str(k)]
            del self.latest_dic["statuses_count"][str(k)]
            del self.latest_dic["profile_image_url"][str(k)]
            del self.latest_dic["profile_banner_url"][str(k)]
            del self.latest_dic["screen_name"][str(k)]
            del self.latest_dic["display_name"][str(k)]
        except Exception as e:
            print(e)
            return -1
        self.dump()
        self.dic = list(map(int, list(self.latest_dic["ids"].keys())))
        return 0
