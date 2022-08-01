import json
from datetime import datetime
from pathlib import Path

from genshinhelper import Honkai3rd
from genshinhelper.utils import _, nested_lookup, request


class Honkai3rd_edit(Honkai3rd):
    def __init__(self, cookie: str = None):
        super().__init__(cookie)
        self.act_id = "e202207181446311"
        self.rewards_info_url = (
            f"{self.api}/event/luna/info?lang=zh-cn&act_id={self.act_id}"
            + "&uid={}&region={}"
        )
        self.month_awards_url = (
            f"{self.api}/event/luna/home?lang=zh-cn&act_id={self.act_id}"
        )
        self._month_awards = []

    @property
    def sign_info(self):
        if not self._sign_info:
            rewards_info = self.rewards_info
            for i in rewards_info:
                self._sign_info.append(
                    {"total_sign_day": i["total_sign_day"], "is_sign": i["is_sign"]}
                )
        return self._sign_info

    @property
    def rewards_info(self):
        if not self._rewards_info:
            roles_info = self.roles_info
            for i in roles_info:
                url = self.rewards_info_url.format(i["game_uid"], i["region"])
                response = request(
                    "get", url, headers=self.headers, cookies=self.cookie
                ).json()
                self._rewards_info.append(
                    nested_lookup(response, "data", fetch_first=True)
                )
        return self._rewards_info

    @property
    def month_awards(self):
        if not self._month_awards:
            url = self.month_awards_url
            response = request(
                "get", url, headers=self.headers, cookies=self.cookie
            ).json()
            self._month_awards = nested_lookup(response, "awards", fetch_first=False)
        return self._month_awards

    def get_month_awards(self):
        awards_path = Path(__file__).parent / Path("awards.json")
        today = datetime.now()
        day1 = today.replace(day=1, hour=0, minute=0)
        if not awards_path.exists() or awards_path.stat().st_mtime < day1.timestamp():
            awards = self.month_awards
            with open(awards_path, "w", encoding="utf8") as file:
                json.dump(awards, file, indent=4, ensure_ascii=False)
            return awards
        with open(awards_path, "r", encoding="utf8") as file:
            return json.load(file)

    def sign_more(self):
        result = self.sign()
        month_awards = self.get_month_awards()
        for res in result:
            assert isinstance(res, dict)
            award = month_awards[0][res["total_sign_day"] - 1]
            res.update(award)
        return result
