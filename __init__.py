import json
import random
import time
import hashlib
import requests
import os

from rich import print,print_json

mhyVersion = '2.19.1'

class Config(object):
    @staticmethod
    def load_config() -> dict:
        with open(os.path.join(os.path.dirname(__file__),f"config.json")) as f:
            CONFIG = json.load(f)
            f.close()
        return CONFIG

    def __init__(self) -> None:
        super().__init__()
        con = Config.load_config()
        self.cookies = con["cookies"]

config = Config()
cookies = config.cookies

def md5(text):
    md5 = hashlib.md5()
    md5.update(text.encode())
    return md5.hexdigest()

def DSGet(q="", b=None):
    if b:
        br = json.dumps(b)
    else:
        br = ""
    s = "xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs"
    t = str(int(time.time()))
    r = str(random.randint(100000, 200000))
    c = md5("salt=" + s + "&t=" + t + "&r=" + r + "&b=" + br + "&q=" + q)
    return t + "," + r + "," + c

def get_info(server:str="bb01",uid:str="112854881"):
    """详见url.json"""
    item = "oldAbyssReport"
    req = requests.get(
        url=f"https://api-takumi-record.mihoyo.com/game_record/app/honkai3rd/api/{item}?server={server}&role_id={uid}",
        headers={
            'DS': DSGet("role_id=" + uid + "&server=" + server),
            'x-rpc-app_version': mhyVersion,
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.11.1',
            'x-rpc-client_type': '5',
            'Referer': 'https://webstatic.mihoyo.com/',
            "Cookie": cookies})
    data = json.loads(req.text)
    with open(os.path.join(os.path.dirname(__file__),f"./dist/{item}.json"),'w',encoding='utf8') as f:
        json.dump(data,f,indent=4,ensure_ascii=False)
        f.close()
    return data

if __name__ == '__main__':
    abyss = get_info(server="hun01",uid="147828091")
    print_json(data=abyss,ensure_ascii=False)
