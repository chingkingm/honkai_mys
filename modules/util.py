import datetime
import functools
import inspect
import json
import os

from .mytyping import config

# 一些egenshin的轮子,感谢艾琳佬


def cache(ttl=datetime.timedelta(hours=1), **kwargs):
    def wrap(func):
        cache_data = {}

        @functools.wraps(func)
        async def wrapped(*args, **kw):
            nonlocal cache_data
            bound = inspect.signature(func).bind(*args, **kw)
            bound.apply_defaults()
            ins_key = "|".join(["%s_%s" % (k, v) for k, v in bound.arguments.items()])
            default_data = {"time": None, "value": None}
            data = cache_data.get(ins_key, default_data)

            now = datetime.datetime.now()
            if not data["time"] or now - data["time"] > ttl:
                try:
                    data["value"] = await func(*args, **kw)
                    data["time"] = now
                    cache_data[ins_key] = data
                except Exception as e:
                    raise e

            return data["value"]

        return wrapped

    return wrap


class NotBindError(Exception):
    msg = """
* 这个插件需要获取账号cookie, 外泄有可能导致您的账号遭受损失, 请注意相关事项再进行绑定, 造成一切损失由用户自行承担
* 修改密码可以直接使其失效

1. 打开米游社(https://bbs.mihoyo.com/ys/)
2. 登录游戏账号
3. F12打开控制台
4. 输入以下代码运行
javascript:(()=>{_=(n)=>{for(i in(r=document.cookie.split(";"))){var arr=r[i].split("=");if(arr[0].trim()==n)return arr[1];}};c=_("cookie_token")||alert('请重新登录');m=_("account_id")+","+c;c&&confirm('确定复制到剪切板?:'+m)&&copy(m)})();
5. 复制提示的内容, 私聊发给机器人
私聊格式为
bhf绑定0000000,xxxxxxxxxxxx

其中0000000,xxxxxxxxxxxx是复制的内容

如果你想查看另外个方法可以发送 bhf?2
* 同时兼容手机端"""
    msg2 = """
如果你是PC端,浏览器需要安装tampermonkey插件(https://www.tampermonkey.net/)
如果你是手机端,可以下载油猴浏览器(http://www.youhouzi.cn/),并且在右下角打开菜单 [打开电脑模式] ,之后在[脚本管理]->[启用脚本功能]

然后打开链接安装脚本 https://greasyfork.org/scripts/435553-%E7%B1%B3%E6%B8%B8%E7%A4%BEcookie/code/%E7%B1%B3%E6%B8%B8%E7%A4%BEcookie.user.js

就可以访问米游社进行登录了
提示复制的内容可以直接私聊发给机器人

私聊格式为

bhf绑定0000000,xxxxxxxxxxxx

其中0000000,xxxxxxxxxxxx是复制的内容
    """


class InfoError(Exception):
    def __init__(self, errorinfo) -> None:
        super().__init__(errorinfo)
        self.errorinfo = errorinfo

    def __str__(self) -> str:
        return self.errorinfo

    def __repr__(self) -> str:
        return str(self.errorinfo)


class CookieNotBindError(InfoError):
    def __repr__(self) -> str:
        if config.is_egenshin:
            pass
        return super().__repr__()


class ItemTrans(object):
    """
    - 数字/字母 -> 文字
    - 文字 -> server_id"""

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def area(no):
        """分组"""
        if no is None:
            no = 0
        level = ["初级区", "中级区", "高级区", "终极区"]
        return level[no - 1]

    @staticmethod
    def abyss_type(_type):
        if _type is None:
            return "超弦空间"
        t = {"OW": "迪拉克之海", "Quantum": "量子奇点", "Greedy": "量子流形"}
        return t[_type]

    @staticmethod
    def oldAbyssLevelChange(reward_type):
        """老深渊段位变化"""
        reward = {"Degrade": "降级", "Upgrade": "晋级", "Relegation": "保级"}
        return reward[reward_type]

    @staticmethod
    def abyss_level(no):
        """通用"""
        if isinstance(no, str) and no.startswith("Unknown"):
            return f"无数据"
        level = {
            1: "禁忌",
            2: "原罪Ⅰ",
            3: "原罪Ⅱ",
            4: "原罪Ⅲ",
            5: "苦痛Ⅰ",
            6: "苦痛Ⅱ",
            7: "苦痛Ⅲ",
            8: "红莲",
            9: "寂灭",
            "A": "红莲",
            "B": "苦痛",
            "C": "原罪",
            "D": "禁忌",
        }
        return level[no]

    @staticmethod
    def server2id(no: str):
        """渠道名转渠道代码"""
        no = no.lower().strip()
        if no.endswith("服"):
            no = no[:-1]
        with open(
            os.path.join(os.path.dirname(__file__), "../region.json"),
            "r",
            encoding="utf8",
        ) as f:
            region = json.load(f)
            f.close()
        for server_id, alias in region.items():
            if no in alias["alias"] or no == alias["name"]:
                return server_id
        raise InfoError(f"找不到渠道{no}的数据,可以尝试输入账号所在的服务器,如安卓3服")

    @staticmethod
    def id2server(region_id):
        """渠道代码转渠道名"""
        with open(
            os.path.join(os.path.dirname(__file__), "../region.json"),
            "r",
            encoding="utf8",
        ) as f:
            region = json.load(f)
            f.close()
        return region[region_id]["name"]

    @staticmethod
    def rate2png(rate):
        """综合评价 -> 图片地址"""
        BASE = os.path.join(os.path.dirname(__file__), "../assets/star")
        rating_png = {"C": "a.png", "B": "s.png", "A": "ss.png", "S": "sss.png"}
        return os.path.join(BASE, rating_png[rate])

    @staticmethod
    def star(_st: int, is_elf: bool = False):
        """星级图片"""
        base = os.path.join(os.path.dirname(__file__), "../assets/star")
        if is_elf:
            num = [1, 2, 2, 3, 3, 3, 4][_st - 1]

        else:
            num = ["b", "a", "s", "ss", "sss"][_st - 1]
        return os.path.join(base, f"{num}.png")
