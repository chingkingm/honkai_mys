import json
import os
from typing import Optional

from sqlitedict import SqliteDict

from .mytyping import config


class DB(SqliteDict):
    cahce_dir = os.path.join(os.path.dirname(__file__), "../", config.cache_dir)

    def __init__(
        self,
        filename=None,
        tablename="unnamed",
        flag="c",
        autocommit=True,
        journal_mode="DELETE",
        encode=json.dumps,
        decode=json.loads,
    ) -> None:
        if not os.path.exists(self.cahce_dir):
            os.mkdir(self.cahce_dir)
        filename = os.path.join(
            os.path.dirname(__file__), "../", self.cahce_dir, filename
        )
        super().__init__(
            filename=filename,
            tablename=tablename,
            flag=flag,
            autocommit=autocommit,
            journal_mode=journal_mode,
            encode=encode,
            decode=decode,
        )

    def set_region(self, role_id: str, region: str) -> None:
        data = self.get(role_id, {})
        data.update({"region": region})
        self[role_id] = data

    def get_region(self, role_id: str) -> Optional[str]:
        if self.get(role_id):
            return self[role_id]["region"]
        else:
            return None

    def get_uid_by_qid(self, qid: str) -> str:
        """获取上次查询的uid"""
        return self[qid]["role_id"]

    def set_uid_by_qid(self, qid: str, uid: str) -> None:
        data = self.get(qid, {})
        data.update({"role_id": uid})
        self[qid] = data

    def get_cookie(self, qid: str) -> Optional[str]:
        try:
            cookie = self[qid]["cookie"]
        except KeyError:
            if config.is_egenshin:
                if config.egenshin_dir is None:
                    config.egenshin_dir = os.path.join(
                        os.path.dirname(__file__), "../../egenshin/data/uid.sqlite"
                    )
                edb = DB(config.egenshin_dir, tablename="unnamed")
                try:
                    cookie = edb.get(qid)["cookie"]
                except:
                    return None
            else:
                return None
        return cookie

    def set_cookie(self, qid: str, cookie: str) -> None:
        data = self.get(qid, {})
        data.update({"cookie": cookie})
        self[qid] = data
