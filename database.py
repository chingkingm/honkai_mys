import json
import os
import sqlite3

from typing import Optional
from sqlitedict import SqliteDict
from .mytyping import config
class DB(SqliteDict):
    cahce_dir = config.cache_dir
    def __init__(self, filename=None, tablename='unnamed', flag='c', autocommit=True, journal_mode="DELETE", encode=json.dumps, decode=json.loads):
        filename = os.path.join(os.path.dirname(__file__),self.cahce_dir,filename)
        super().__init__(filename=filename, tablename=tablename, flag=flag, autocommit=autocommit, journal_mode=journal_mode, encode=encode, decode=decode)   
    def set_region(self,role_id,region):
        if self.get(role_id):
            data = self[role_id]
            data.update({"region":region})
        else:
            data = {"region":region}
        self[role_id] = data
    def get_region(self,role_id) -> Optional[str]:
        if self.get(role_id):
            return self[role_id]["region"]
        else:
            return None
    def get_uid_by_qid(self,qid:str):
        """获取上次查询的uid"""
        return self[qid]["role_id"]
    def set_uid_by_qid(self,qid:str,uid:str):
        self[qid] = {"role_id":uid}