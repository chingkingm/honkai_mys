import asyncio
import datetime
import hashlib
import json
import os
import random
import re
import time
from http.cookies import SimpleCookie
from operator import itemgetter
from typing import Tuple

import httpx

from .database import DB
from .mytyping import config
from .util import InfoError, NotBindError, cache

COOKIES = config.cookies[0]


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
        "获取自己角色": "https://api-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie",
        "获取他人角色": f"https://api-takumi-record.mihoyo.com/game_record/app/card/wapi/getGameRecordCard?uid={{mysuid}}",
        "上月手账": f"https://api.mihoyo.com/bh3-weekly_finance/api/getLastMonthInfo?game_biz=bh3_cn&bind_uid={{roleid}}&bind_region={{serverid}}",
        "本月手账": f"https://api.mihoyo.com/bh3-weekly_finance/api/index?game_biz=bh3_cn&bind_uid={{roleid}}&bind_region={{serverid}}",
        "水晶明细": f"https://api.mihoyo.com/bh3-weekly_finance/api/getHcoinRecords?page=1&limit=20&game_biz=bh3_cn&bind_uid={{roleid}}&bind_region={{serverid}}",
        "星石明细": f"https://api.mihoyo.com/bh3-weekly_finance/api/getStarRecords?page=1&limit=20&game_biz=bh3_cn&bind_uid={{roleid}}&bind_region={{serverid}}"
    }

    def __init__(self, server_id, role_id, mysid=None) -> None:
        super().__init__()
        self.server = server_id
        self.uid = role_id
        if mysid is not None:
            try:
                self.mid = str(int(mysid))
                self.getrole = self.generate("获取他人角色", self.mid)
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
        self._for_iter = [self.godWar, self.valkyrie, self.index, self.newAbyss, self.oldAbyss_lastest, self.weekly, self.battleField]

    def generate(self, typename: str, *ids) -> str:
        """typename:URL类型;ids:3种id"""
        #todo: change *ids to details
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

    def __init__(self, mysid: str = None, server_id: str = None, role_id: str = None) -> None:
        """若传入mysid则server_id及role_id不生效."""
        if mysid is not None:
            try:
                mid = str(int(mysid))
            except ValueError:
                raise InfoError(f"{mysid}米游社id格式错误.")
            server_id, role_id = self.mys2role(self.generate("获取他人角色", mid))
        super().__init__(server_id, role_id, mysid)

    @classmethod
    def md5(cls, text):
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

    async def all(self, api: MysApi = None) -> dict:
        """获取所有信息,接受传入MysApi对象"""
        if api is None:
            api = self
        if isinstance(api, MysApi):
            info = {}
            for url in api:
                item, data = await self.fetch(url)
                # if item in info:
                #     item += "_greedy"  # 处理2种深渊数据覆盖问题
                info.update({item: data["data"]})
            return info

    async def part(self, api: MysApi = None):
        """不查询角色,乐土等,以减少开销"""
        if api is None:
            api = self
        info = {}
        for url in api:
            if "characters" in url or "godWar" in url:
                continue
            else:
                item, data = await self.fetch(url)
                # if item in info:
                #     item += "_greedy"  # 处理2种深渊数据覆盖问题
                info.update({item: data["data"]})
        return info

    @classmethod
    def gen_header(cls, ds: str, cookie: str):
        headers = {
            'DS': cls.DSGet(ds),
            'x-rpc-app_version': cls.MHY_VERSION,
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.11.1',
            'x-rpc-client_type': '5',
            'Referer': 'https://webstatic.mihoyo.com/',
            "Cookie": cookie
        }
        return headers

    @staticmethod
    @cache(ttl=datetime.timedelta(minutes=10), arg_key='url')
    async def fetch(url, cookie=None) -> Tuple[str, dict]:
        """查询，单项数据"""
        cookie = cookie if cookie is not None else COOKIES
        try:
            server, uid = [temp[1:] for temp in re.findall(r'=[a-z0-9]{4,}', url)]
            headers = GetInfo.gen_header("role_id=" + uid + "&server=" + server, cookie)
            item = re.search(r"/\w+\?", url).group()[1:-1]
        except ValueError:
            # raise ValueError(f"{url}\napi格式不对")
            headers = GetInfo.gen_header('', cookie)
            item = url.split("/")[-1]
        """高级区及以下的深渊查询api不可用,使用latest代替"""
        async with httpx.AsyncClient() as aiorequests:
            req = await aiorequests.get(
                url=url,
                headers=headers,
            )
            data = json.loads(req.text)
        # print(data)
        retcode = data["retcode"]
        if retcode == 1008:
            raise InfoError("uid与服务器不匹配")
        elif retcode == 10102:
            raise InfoError(f"账号数据非公开,请前往米游社修改.")
        elif retcode == 10001:
            raise InfoError("登录失效,请重新登录.")
        elif retcode == 0 or retcode == -1:
            # 0:正常获取;-1:等级与深渊不匹配
            if item == "index" and "api-takumi" in url:
                data["data"]["role"].update({"role_id": uid})  # index添加role_id
            return item, data
        else:
            raise InfoError(f"{data}")

    @classmethod
    def mys2role(cls, url) -> Tuple[str, str]:
        """通过米游社id查询游戏角色"""
        try:
            mid = re.search(r'\?\w+=\d+', url).group()[1:]
        except ValueError:
            raise ValueError(f"api格式不对")
        item = re.search(r"/\w+\?", url).group()[1:-1]
        req = httpx.get(
            url=url,
            headers=cls.gen_header(mid, COOKIES)
        )
        data = json.loads(req.text)
        for game in data["data"]["list"]:
            if game["game_id"] == 1:
                rid = game["game_role_id"]  # 游戏id
                region = game["region"]  # 渠道代码
                region_name = game["region_name"]
                return region, rid
        raise IndexError(f"该用户没有崩坏3角色.")


FINANCE_CACHE = {}


class Finance(GetInfo):
    def get_role(self, all: bool = False):
        url = 'https://api-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie'
        if not all:
            url = url + "?game_biz=bh3_cn"
        resp = httpx.get(url=url, headers=self.gen_header("", self.cookie.strip()))
        retcode = resp.json()["retcode"]
        if retcode != 0:
            raise InfoError(f"{resp.json()['message']}")
        else:
            data = resp.json()["data"]["list"]
        if data:
            data.sort(key=itemgetter("level"), reverse=True)
            data = data[0]
        else:
            raise InfoError(f"{resp.text}\n当前绑定的账号没有崩坏3游戏信息")
        server_id = data["region"]
        role_id = data["game_uid"]
        FINANCE_CACHE.update({self.account_id: {"server_id": server_id, "role_id": role_id}})
        return server_id, role_id

    def __init__(self, qid: str, cookieraw: str = None) -> None:
        """初始化传入qid,调取数据库查找cookie."""
        self.db = DB("uid.sqlite", "qid_uid")
        if cookieraw is not None:
            cookietemp = SimpleCookie()
            cookietemp.load(dict(zip(['account_id', 'cookie_token'], cookieraw.split(','))))
            self.cookie = cookietemp.output(header='', sep=';').strip()
        else:
            cookie = self.db.get_cookie(qid)
            if cookie is None:
                raise InfoError(f"尚未绑定\n{NotBindError.msg}")
            self.cookie = cookie
        self.account_id = SimpleCookie(self.cookie)["account_id"].value
        if self.account_id in FINANCE_CACHE:
            server_id = FINANCE_CACHE[self.account_id]["server_id"]
            role_id = FINANCE_CACHE[self.account_id]["role_id"]
        else:
            server_id, role_id = self.get_role()
        if "cookie" not in locals():
            self.db.set_cookie(qid, self.cookie)
        super().__init__(server_id=server_id, role_id=role_id)
        self.lastfinance = self.generate("上月手账")
        self.thisfinance = self.generate("本月手账")
        self.hcoin = self.generate("水晶明细")
        self.starstone = self.generate("星石明细")
        self.finance = [self.lastfinance, self.thisfinance, self.hcoin, self.starstone]

    async def get_finance(self):
        financedata = {}
        for url in self.finance:
            item, data = await self.fetch(url, self.cookie)
            financedata.update({item: data["data"]})
        return financedata


if __name__ == '__main__':
    # spider = GetInfo(mysid='19846523')
    spider = Finance(qid="1542292829")
    # 1551044405
    # spider = GetInfo(server_id='bb01',role_id='112854881')
    try:
        data = asyncio.run(spider.get_finance())
        print(data)
    except InfoError as e:
        print(e)
    with open(os.path.join(os.path.dirname(__file__), f"dist/financech.json"), 'w', encoding='utf8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        f.close()
