import json
import yaml
import random
import time
import hashlib
from typing import Tuple
import requests
import os
import re

from rich import print,print_json
from .mytyping import COOKIES
class InfoError(Exception):
    def __init__(self, errorinfo) -> None:
        super().__init__(errorinfo)
        self.errorinfo = errorinfo
    def __str__(self) -> str:
        return self.errorinfo
    def __repr__(self) -> str:
        return self.errorinfo
class MismatchError(InfoError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
class FormatError(InfoError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
class MysApi(object):
    """用于生成api"""
    BASE = "https://api-takumi-record.mihoyo.com/game_record/app/honkai3rd/api"
    API = {
        "往事乐土": f"{BASE}/godWar?server={{serverid}}&role_id={{roleid}}",
        "我的女武神": f"{BASE}/characters?server={{serverid}}&role_id={{roleid}}",
        "数据总览": f"{BASE}/index?server={{serverid}}&role_id={{roleid}}",
        "深渊战报_超弦空间": f"{BASE}/newAbyssReport?server={{serverid}}&role_id={{roleid}}",
        "深渊战报_量子奇点": f"{BASE}/oldAbyssReport?server={{serverid}}&role_id={{roleid}}&abyss_type=1",
        "深渊战报_迪拉克之海": f"{BASE}/oldAbyssReport?server={{serverid}}&role_id={{roleid}}&abyss_type=2",
        "深渊战报_latest": f"{BASE}/latestOldAbyssReport?server={{serverid}}&role_id={{roleid}}",
        "一周成绩单": f"{BASE}/weeklyReport?server={{serverid}}&role_id={{roleid}}",
        "战场战报": f"{BASE}/battleFieldReport?server={{serverid}}&role_id={{roleid}}",
        "常用工具": f"{BASE}/tools",
        "获取自己角色": "https://api-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie?game_biz=bh3_cn",
        "获取他人角色": f"https://api-takumi-record.mihoyo.com/game_record/app/card/wapi/getGameRecordCard?uid={{mysuid}}"
    }
    
    def __init__(self,server_id,role_id,mysid=None) -> None:
        super().__init__()
        self.server = server_id
        self.uid = role_id
        if mysid is not None:
            try:
                self.mid = str(int(mysid))
                self.getrole = self.generate("获取他人角色",self.mid)
            except ValueError:
                raise ValueError(f"{mysid}\n米游社ID格式不对")
        self.godWar = self.generate("往事乐土")
        self.valkyrie = self.generate("我的女武神")
        self.index = self.generate("数据总览")
        self.newAbyss = self.generate("深渊战报_超弦空间")
        self.oldAbyss_quantum = self.generate("深渊战报_量子奇点")
        self.oldAbyss_dirac = self.generate("深渊战报_迪拉克之海")
        self.oldAbyss_lastest = self.generate("深渊战报_latest")
        self.weekly = self.generate("一周成绩单")
        self.battleField = self.generate("战场战报")
        self.getself = self.generate("获取自己角色")
        self._for_iter = [self.godWar,self.valkyrie,self.index,self.newAbyss,self.oldAbyss_quantum,self.oldAbyss_dirac,self.oldAbyss_lastest,self.weekly,self.battleField]
    def generate(self,typename:str,*ids) -> str:
        """typename:URL类型;ids:3种id"""
        url_origin = self.API[typename]
        if len(ids) == 2:
            sid = ids[0]
            rid = ids[1]
            mid = ""
        elif len(ids) == 1:
            sid = ""
            rid = ""
            mid = ids[0]
        else:
            sid = self.server
            rid = self.uid
            mid = ""
        return url_origin.format(serverid=sid, roleid=rid, mysuid=mid)
    def __iter__(self):
        return iter(self._for_iter)


class GetInfo(MysApi):
    """继承自MysApi,用于获取信息"""
    MHY_VERSION = '2.11.1'
    def __init__(self, mysid:str=None, server_id:str=None, role_id:str=None) -> None:
        """若传入mysid则server_id及role_id不生效."""
        if mysid is not None:
            try:
                mid = str(int(mysid))
            except ValueError:
                raise FormatError(f"{mysid}米游社id格式错误.")
            server_id, role_id = self.mys2role(self.generate("获取他人角色",mid))
        super().__init__(server_id, role_id,mysid)
    @classmethod
    def md5(cls,text):
        md5 = hashlib.md5()
        md5.update(text.encode())
        return md5.hexdigest()
    @classmethod
    def DSGet(cls, q="", b=None):
        if b:
            br = json.dumps(b)
        else:
            br = ""
        s = "xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs"
        t = str(int(time.time()))
        r = str(random.randint(100000, 200000))
        c = cls.md5("salt=" + s + "&t=" + t + "&r=" + r + "&b=" + br + "&q=" + q)
        return t + "," + r + "," + c

    def all(self,api:MysApi=None) -> dict:
        """获取所有信息,接受传入MysApi对象"""
        if api is None:
            api = self
        if isinstance(api,MysApi):
            info = {}
            for url in api:
                item,data = self.fetch(url)
                if item in info:
                    item += "_dirac"    # 处理2种深渊数据覆盖问题
                info.update({item:data["data"]})
            return info

    def fetch(self,url) -> Tuple[str, dict]:
        """查询，单项数据"""
        try:
            server, uid = [temp[1:] for temp in re.findall(r'=\w{2,}',url)]
        except ValueError:
            raise ValueError(f"{url}\napi格式不对")
        item = re.search(r"/\w{1,}\?",url).group()[1:-1]
        """高级区及以下的深渊查询api不可用,使用latest代替"""
        req = requests.get(
            url=url,
            headers={
                'DS': self.DSGet("role_id=" + uid + "&server=" + server),
                'x-rpc-app_version': self.MHY_VERSION,
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.11.1',
                'x-rpc-client_type': '5',
                'Referer': 'https://webstatic.mihoyo.com/',
                "Cookie": COOKIES})
        data = json.loads(req.text)

        if data["retcode"] == 1008:
            raise MismatchError("uid与服务器不匹配")
        if item == "index":
            data["data"]["role"].update({"role_id":uid}) # index添加role_id

        return item, data
    
    @classmethod
    def mys2role(cls,url) -> Tuple[str,str]:
        """通过米游社id查询游戏角色"""
        try:
            mid = re.search(r'\?\w{1,}=\d{1,}',url).group()[1:]
        except ValueError:
            raise ValueError(f"api格式不对")
        item = re.search(r"/\w{1,}\?",url).group()[1:-1]
        req = requests.get(
            url=url,
            headers={
                'DS': cls.DSGet(mid),
                'x-rpc-app_version': cls.MHY_VERSION,
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.11.1',
                'x-rpc-client_type': '5',
                'Referer': 'https://webstatic.mihoyo.com/',
                "Cookie": COOKIES})
        data = json.loads(req.text)
        for game in data["data"]["list"]:
            if game["game_id"] == 1:
                rid = game["game_role_id"]    # 游戏id
                region = game["region"]   # 渠道代码
                region_name = game["region_name"]
                #todo 自动更新region.json
                return region, rid
        raise IndexError(f"该用户没有崩坏3角色.")   


if __name__ == '__main__':
    spider = GetInfo(mysid='19846523')
    # spider = GetInfo(server_id='bb01',role_id='112854881')
    
    try:
        data = spider.all()
        # print(data)
    except InfoError as e:
        print(e)
    with open(os.path.join(os.path.dirname(__file__),f"dist/full.json"),'w',encoding='utf8') as f:
        json.dump(data,f,indent=4,ensure_ascii=False)
        f.close()
    
