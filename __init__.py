# import sys
# sys.path.append("G:\GenshinTools\HoshinoBot")
import asyncio
import re

import hoshino
from hoshino import HoshinoBot, MessageSegment, Service
from hoshino.typing import CQEvent

from hoshino.modules.honkai_mys.database import DB
from hoshino.modules.honkai_mys.info import GetInfo, InfoError
from hoshino.modules.honkai_mys.info_card import DrawIndex, ItemTrans, DrawCharacter

sv = Service("崩坏3角色卡片",enable_on_default=True,visible=True)
def handle_id(ev:CQEvent):
    msg = ev.message.extract_plain_text().strip()
    qid = str(ev.user_id)
    region_db = DB('uid.sqlite',tablename='uid_region')
    qid_db = DB("uid.sqlite",tablename='qid_uid')
    role_id = re.search(r"\d{1,}",msg)
    region_name = re.search(r"\D{1,}\d?",msg)
    if re.search(r"[mM][yY][sS]|米游社",msg):
        spider = GetInfo(mysid=role_id.group())
        region_id,role_id = spider.mys2role(spider.getrole)
    elif role_id is None:
        try:
            role_id = qid_db.get_uid_by_qid(qid)
            region_id = region_db.get_region(role_id)
        except KeyError:
            raise InfoError("请在原有指令后面输入游戏uid及服务器,只需要输入一次就会记住下次直接使用bh#获取就好\n例如:bh#100074751官服")
    elif role_id is not None and region_name is None:
        region_id = region_db.get_region(role_id.group())
        if not region_id:
            raise InfoError(f"{role_id.group()}为首次查询,请输入服务器名称.")
    else:
        try:
            region_id = ItemTrans.server2id(region_name.group())
        except InfoError as e:
            raise InfoError(str(e))
        now_region_id = region_db.get_region(role_id.group())
        if  now_region_id is not None and now_region_id != region_id:
            raise InfoError(f'服务器信息与uid不匹配,可联系管理员修改.')# 输入的服务器与数据库中保存的不一致，可手动delete该条数据
    role_id=role_id if isinstance(role_id,str) else role_id.group()
    return role_id,region_id,qid
@sv.on_prefix("bh#")
async def bh3_player_card(bot:HoshinoBot,ev:CQEvent):
    region_db = DB('uid.sqlite',tablename='uid_region')
    qid_db = DB("uid.sqlite",tablename='qid_uid')
    try:
        role_id,region_id,qid = handle_id(ev)
    except InfoError as e:
        await bot.send(ev,str(e),at_sender=True)
        return
    spider = GetInfo(server_id=region_id,role_id=role_id)
    try:
        ind = await spider.part()
    except InfoError as e:
        await bot.send(ev,str(e))
        return
    region_db.set_region(role_id,region_id)
    qid_db.set_uid_by_qid(qid,role_id)
    ind = DrawIndex(**ind)
    im = await ind.draw_card(qid)
    img = MessageSegment.image(im)
    await bot.send(ev,img)

@sv.on_prefix("bhv#")
async def bh3_chara_card(bot:HoshinoBot,ev:CQEvent):
    region_db = DB('uid.sqlite',tablename='uid_region')
    qid_db = DB("uid.sqlite",tablename='qid_uid')
    try:
        role_id,region_id,qid = handle_id(ev)
    except InfoError as e:
        await bot.send(ev,str(e),at_sender=True)
        return
    spider = GetInfo(role_id=role_id,server_id=region_id)
    try:
        _,data = await spider.fetch(spider.valkyrie)
    except InfoError as e:
        await bot.send(ev,str(e),at_sender=True)
        return
    region_db.set_region(role_id,region_id)
    qid_db.set_uid_by_qid(qid,role_id)
    dr = DrawCharacter(**data["data"])
    im = await dr.draw_chara()
    img = MessageSegment.image(im)
    await bot.send(ev,img,at_sender=True)
    return