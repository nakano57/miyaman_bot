import sys
import json


class Miyajson():
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

    init_json = {"ids": dic, "followings": dic,
                 "favorites": dic, "statuses_count": dic,
                 "profile_image_url": dic, "profile_banner_url": dic}

    def __init__(self) -> None:
        with open(sys.argv[1]) as f:
            try:
                self.latest_dic = json.load(f)
            except:
                self.latest_dic = Miyajson.init_json

    def dump(self):
        pass

    def get_id(self, k):
        return self.latest_dic["ids"][str(k)]

    def set_id(self, k, n):
        self.latest_dic["ids"][str(k)] = n

    def get_following(self, k, n):
        pass

    def set_following(self, k, n):
        pass

    def get_favorite(self, k, n):
        pass

    def set_favorite(self, k, n):
        pass

    def get_statuses_count(self, k, n):
        pass

    def set_statuses_count(self, k, n):
        pass

    def get_profile_image_url(self, k, n):
        pass

    def set_profile_banner_url(self, k, n):
        pass
