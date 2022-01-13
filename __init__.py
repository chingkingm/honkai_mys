# import sys
# sys.path.append("G:\GenshinTools\HoshinoBot")
import re

import hoshino
from hoshino import HoshinoBot, Service,MessageSegment
from hoshino.typing import CQEvent
from hoshino.util import DailyNumberLimiterInFile
from .info import GetInfo, InfoError
from .database import DB
from .mytyping import Index,WeeklyReport
from .info_card import DrawIndex,ItemTrans
lmt = DailyNumberLimiterInFile('hkmys',999)
sv = Service("崩坏3角色卡片",enable_on_default=False,visible=True)

@sv.on_prefix("bh#")
async def bh3_player_card(bot:hoshino.HoshinoBot,ev:CQEvent):
    msg = ev.message.extract_plain_text().strip()
    qid = str(ev.user_id)
    region_db = DB('uid.sqlite',tablename='uid_region')
    qid_db = DB("uid.sqlite",tablename='qid_uid')
    role_id = re.search(r"\d{1,}",msg)
    region_name = re.search(r"\D{1,}",msg)
    if re.search(r"[mM][yY][sS]|米游社",msg):
        spider = GetInfo(mysid=role_id.group())
        region_id,role_id = spider.mys2role(spider.getrole)
    elif role_id is None:
        try:
            role_id = qid_db.get_uid_by_qid(qid)
            region_id = region_db.get_region(role_id)
        except KeyError:
            await bot.send(ev,"请在原有指令后面输入游戏uid,只需要输入一次就会记住下次直接使用{comm}获取就好\n例如:{comm}105293904".format(comm='bh#'))
            return
    elif role_id is not None and region_name is None:
        region_id = region_db.get_region(role_id.group())
        if not region_id:
            await bot.send(ev,f"{role_id.group()}为首次查询,请输入服务器名称.")
            return
    else:
        try:
            region_id = ItemTrans.server2id(region_name.group())
        except KeyError as e:
            await bot.send(ev,e)
            return
        now_region_id = region_db.get_region(role_id.group())
        if  now_region_id is not None and now_region_id!= region_id:
            # region_db.set_region(role_id=role_id,region=region_id)
            await bot.send(ev,f'服务器信息与uid不匹配,可联系管理员修改.')
            return
    role_id=role_id if isinstance(role_id,str) else role_id.group()
    spider = GetInfo(server_id=region_id,role_id=role_id)
    try:
        _,ind = spider.fetch(spider.index)
    except InfoError as e:
        await bot.send(ev,e)
        return
    region_db.set_region(role_id,region_id)
    qid_db.set_uid_by_qid(qid,role_id)
    _,wee = spider.fetch(spider.weekly)
    ind = DrawIndex(**ind['data'])
    wee = WeeklyReport(**wee['data'])
    im = ind.draw_card(wee)
    img = MessageSegment.image(im)
    lmt.increase('111')
    print(lmt.get_num('111'))
    await bot.send(ev,img)
