import asyncio
import json
import os
from datetime import datetime
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr, parseaddr
from smtplib import SMTP_SSL

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from genshinhelper import Honkai3rd
from genshinhelper.exceptions import GenshinHelperException
from nonebot import get_bot, get_driver, on_regex, require
from nonebot.adapters.onebot.v11 import GROUP, Bot, Event, MessageSegment
from nonebot.params import RegexGroup

from ..modules.database import DB
from ..modules.mytyping import config, result

sign_schedule: AsyncIOScheduler = require(
    "nonebot_plugin_apscheduler").scheduler
sign_trigger = on_regex(
    r"(开启|关闭|on|off)?\s?(?:崩坏?|bh|bbb|崩崩崩)(?:3|三)?自动签到")
SUPERUSERS = get_driver().config.superusers


def autosign(hk3: Honkai3rd, qid: str):
    sign_data = load_data()
    try:
        result_list = hk3.sign()
    except GenshinHelperException as e:
        sign_data.update(
            {qid: {"date": datetime.today().day, "status": False, "result": None}})
        return f"{e}\n自动签到失败."
    ret_list = f"〓米游社崩坏3签到〓\n####{datetime.date(datetime.today())}####\n"
    for n, res in enumerate(result_list):
        res = result(**res)
        ret = f"🎉No.{n+1}\n{res.region_name}-{res.nickname}\n今日奖励:{res.reward_name}*{res.reward_cnt}\n本月累签:{res.total_sign_day}天\n签到结果:"
        if res.status == "OK":
            ret += f"OK✨"
        else:
            ret += f"舰长,你今天已经签到过了哦👻"
        ret += "\n###############\n"
        ret_list += ret
    sign_data.update(
        {qid: {"date": datetime.today().day, "status": True, "result": ret_list}})
    save_data(sign_data)
    return ret_list.strip()


SIGN_PATH = os.path.join(os.path.dirname(__file__), "./sign_on.json")


def load_data():
    if not os.path.exists(SIGN_PATH):
        with open(SIGN_PATH, "w", encoding="utf8") as f:
            json.dump({}, f)
            return {}
    with open(SIGN_PATH, 'r', encoding="utf8") as f:
        data: dict = json.load(f)
        return data


def save_data(data):
    with open(SIGN_PATH, 'w', encoding="utf8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def check_cookie(qid: str):
    db = DB('uid.sqlite', tablename="qid_uid")
    cookie = db.get_cookie(qid)
    if not cookie:
        return f"自动签到需要绑定cookie,发送'bhf?'查看如何绑定."
    hk3 = Honkai3rd(cookie=cookie)
    try:
        role_info = hk3.roles_info
    except GenshinHelperException as e:
        return f"{e}\ncookie不可用,请重新绑定."
    if not role_info:
        return f"未找到崩坏3角色信息,请确认cookie对应账号是否已绑定崩坏3角色."
    return hk3


# @sv.on_rex(r"(开启|关闭|on|off)?\s?(?:崩坏?|bh|bbb|崩崩崩)(?:3|三)?自动签到")
@sign_trigger.handle()
async def switch_autosign(bot: Bot, ev: Event, match: tuple = RegexGroup()):
    """自动签到开关"""
    qid = ev.get_user_id()
    # cmd: str = ev['match'].group(1)
    cmd: str = match[0]
    sign_data = load_data()
    if cmd in ["off", "关闭"]:
        if not qid in sign_data:
            return
        sign_data.pop(qid)
        save_data(sign_data)
        await bot.send(ev, "已关闭.", at_sender=True)
        return
    hk3 = check_cookie(qid)
    if isinstance(hk3, str):
        await bot.send(ev, hk3, at_sender=True)
        return
    result = autosign(hk3, qid)
    await send_notice(qid, result, bot)
    if cmd:
        await bot.send(ev, f"自动签到已开启,每日4:10或16:10执行签到.", at_sender=True)
    else:
        await bot.send(ev, f"签到完成,结果已通过私聊或邮件发送.", at_sender=True)


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf8').encode(), addr))


async def send_notice(qid: str, context: str, bot: Bot = None):
    if not bot:
        bot = get_bot()
    friend_list = await bot.get_friend_list()
    if qid in [str(friend.get("user_id")) for friend in friend_list]:
        await bot.send_private_msg(user_id=int(qid), message=MessageSegment.text(context))
        return
    user = config.username
    password = config.password
    if not user or not password:
        await bot.send_private_msg(user_id=int(SUPERUSERS[0]), message=MessageSegment.text(context))
        return
    msg = MIMEText(context, "plain", _charset="utf-8")
    msg['Subject'] = Header(f"签到结果", 'utf8').encode()
    msg['From'] = _format_addr(f"Paimon <{user}>")
    msg["To"] = _format_addr(f"{qid} <{qid}@qq.com>")
    with SMTP_SSL(host="smtp.qq.com", port=465) as smtp:
        # smtp.set_debuglevel(1)
        smtp.login(user, password)
        smtp.sendmail(user, f"{qid}@qq.com", msg=msg.as_string())


@sign_schedule.scheduled_job('cron', hour='4,16', minute='10')
async def schedule_sign():
    today = datetime.today().day
    sign_data = load_data()
    for qid in sign_data:
        await asyncio.sleep(5)
        if sign_data[qid].get("date") != today or not sign_data[qid].get("status"):
            hk3 = check_cookie(qid)
            if isinstance(hk3, Honkai3rd):
                hk3 = autosign(hk3, qid)
            await send_notice(qid, hk3)
