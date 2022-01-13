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
    def set_region(self,qid,region):
        if self.get(qid):
            data = self[qid]
            data.update({"region":region})
        else:
            data = {"region":region}
        self[qid] = data
    def get_region(self,qid) -> Optional[str]:
        if self.get(qid):
            return self[qid]["region"]
        else:
            return None
