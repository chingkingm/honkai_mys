import re
import sys

from hoshino import HoshinoBot, MessageSegment, Service, get_bot
from hoshino.typing import CQEvent

from .modules.database import DB
from .modules.image_handle import (DrawCharacter, DrawFinance, DrawIndex,
                                   ItemTrans)
from .modules.mytyping import Index
from .modules.query import Finance, GetInfo, InfoError
from .modules.util import NotBindError

_help = """
[bh#uid服务器]：查询角色卡片
[bhv#uid服务器]：查询拥有的女武神
[bhf]：查询手账
"""
_bot = get_bot()
sv = Service(
    "崩坏3角色卡片", enable_on_default=True, visible=True, bundle="崩坏3", help_=_help
)


def handle_id(ev: CQEvent):
    msg = ev.message.extract_plain_text().strip()
    qid = str(ev.user_id)
    for mes in ev.message:
        if mes.type == "at":
            qid = mes.data["qq"]
    region_db = DB("uid.sqlite", tablename="uid_region")
    qid_db = DB("uid.sqlite", tablename="qid_uid")
    role_id = re.search(r"\d{1,}", msg)
    region_name = re.search(r"\D{1,}\d?", msg)
    if re.search(r"[mM][yY][sS]|米游社", msg):
        spider = GetInfo(mysid=role_id.group())
        region_id, role_id = spider.mys2role(spider.getrole)
    elif role_id is None:
        try:
            role_id = qid_db.get_uid_by_qid(qid)
            region_id = region_db.get_region(role_id)
        except KeyError:
            raise InfoError(
                "请在原有指令后面输入游戏uid及服务器,只需要输入一次就会记住下次直接使用bh#获取就好\n例如:bh#100074751官服"
            )
    elif role_id is not None and region_name is None:
        region_id = region_db.get_region(role_id.group())
        if not region_id:
            raise InfoError(
                f"{role_id.group()}为首次查询,请输入服务器名称.如:bh#100074751官服")
    else:
        try:
            region_id = ItemTrans.server2id(region_name.group())
        except InfoError as e:
            raise InfoError(str(e))
        now_region_id = region_db.get_region(role_id.group())
        if now_region_id is not None and now_region_id != region_id:
            raise InfoError(
                f"服务器信息与uid不匹配,可联系管理员修改."
            )  # 输入的服务器与数据库中保存的不一致，可手动delete该条数据
    role_id = role_id if isinstance(role_id, str) else role_id.group()
    return role_id, region_id, qid


@sv.on_prefix("bh#")
async def bh3_player_card(bot: HoshinoBot, ev: CQEvent):
    region_db = DB("uid.sqlite", tablename="uid_region")
    qid_db = DB("uid.sqlite", tablename="qid_uid")
    try:
        role_id, region_id, qid = handle_id(ev)
    except InfoError as e:
        await bot.send(ev, str(e), at_sender=True)
        return
    spider = GetInfo(server_id=region_id, role_id=role_id)
    try:
        ind = await spider.part()
    except InfoError as e:
        await bot.send(ev, str(e))
        return
    region_db.set_region(role_id, region_id)
    qid_db.set_uid_by_qid(qid, role_id)
    ind = DrawIndex(**ind)
    im = await ind.draw_card(qid)
    img = MessageSegment.image(im)
    await bot.send(ev, img)


@sv.on_prefix("bhv#")
async def bh3_chara_card(bot: HoshinoBot, ev: CQEvent):
    region_db = DB("uid.sqlite", tablename="uid_region")
    qid_db = DB("uid.sqlite", tablename="qid_uid")
    try:
        role_id, region_id, qid = handle_id(ev)
    except InfoError as e:
        await bot.send(ev, str(e), at_sender=True)
        return
    spider = GetInfo(role_id=role_id, server_id=region_id)
    try:
        _, data = await spider.fetch(spider.valkyrie)
        _, index_data = await spider.fetch(spider.index)
    except InfoError as e:
        await bot.send(ev, str(e), at_sender=True)
        return
    await bot.send(ev, MessageSegment.reply(ev.message_id) + "制图中，请稍后")
    region_db.set_region(role_id, region_id)
    qid_db.set_uid_by_qid(qid, role_id)
    index = Index(**index_data["data"])
    dr = DrawCharacter(**data["data"])
    im = await dr.draw_chara(index, qid)
    img = MessageSegment.image(im)
    await bot.send(ev, img, at_sender=True)
    return


@sv.on_prefix(("bhf", "手账", "水晶手账"))
async def show_finance(bot: HoshinoBot, ev: CQEvent):
    qid = ev.user_id
    msg = ev.message.extract_plain_text().strip()
    if msg.startswith("绑定"):
        try:
            await bot.delete_msg(message_id=ev.message_id)
            ret = ""
        except:
            ret = "请撤回！"
        await bot.send(ev, f"{ret}不支持在群内绑定，请添加bot好友后私聊绑定。", at_sender=True)
        return
    elif "?" in msg or "？" in msg:
        ret = NotBindError.msg2 if "2" in msg else NotBindError.msg
        await bot.send(ev, ret, at_sender=True)
        return
    else:
        try:
            spider = Finance(str(qid))
        except InfoError as e:
            await bot.send(ev, f"{e}", at_sender=True)
            return
    fi = await spider.get_finance()
    fid = DrawFinance(**fi)
    im = fid.draw()
    await bot.send(ev, f"{MessageSegment.image(im)}")
    return


@_bot.on_message("private")
async def bindcookie(ev: CQEvent):
    msg = ev["raw_message"]
    sid = int(ev["self_id"])
    qid = int(ev["sender"]["user_id"])
    cmd = re.match(r"(bhf|手账|水晶手账)绑定", msg)
    if not cmd:
        return
    sv.logger.info(
        f"Private Message {ev.message_id} triggered {sys._getframe().f_code.co_name}"
    )
    cookieraw: str = re.split(cmd.group(), msg)[1].strip()
    try:
        spider = Finance(qid=qid, cookieraw=cookieraw)
    except InfoError as e:
        await _bot.send_private_msg(user_id=qid, message=f"{e}", self_id=sid)
        return
    fi = await spider.get_finance()
    fid = DrawFinance(**fi)
    im = fid.draw()
    await _bot.send_private_msg(
        user_id=qid, message=MessageSegment.image(im), self_id=sid
    )
    return
