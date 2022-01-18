# import sys
# sys.path.append("G:\GenshinTools\HoshinoBot")
import asyncio
import re

import hoshino
from hoshino import HoshinoBot, MessageSegment, Service
from hoshino.typing import CQEvent

from .database import DB
from .info import GetInfo, InfoError
from .info_card import DrawIndex, ItemTrans

sv = Service("崩坏3角色卡片",enable_on_default=True,visible=True)

@sv.on_prefix("bh#")
async def bh3_player_card(bot:HoshinoBot,ev:CQEvent):
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
            await bot.send(ev,"请在原有指令后面输入游戏uid及服务器,只需要输入一次就会记住下次直接使用bh#获取就好\n例如:bh#100074751官服")
            return
    elif role_id is not None and region_name is None:
        region_id = region_db.get_region(role_id.group())
        if not region_id:
            await bot.send(ev,f"{role_id.group()}为首次查询,请输入服务器名称.")
            return
    else:
        try:
            region_id = ItemTrans.server2id(region_name.group())
        except InfoError as e:
            await bot.send(ev,str(e))
            return
        now_region_id = region_db.get_region(role_id.group())
        if  now_region_id is not None and now_region_id != region_id:
            await bot.send(ev,f'服务器信息与uid不匹配,可联系管理员修改.')# 输入的服务器与数据库中保存的不一致，可手动delete该条数据
            return
    role_id=role_id if isinstance(role_id,str) else role_id.group()
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
