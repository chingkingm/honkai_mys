# import sys
# sys.path.append("G:\GenshinTools\HoshinoBot")
import re

import hoshino
from hoshino import HoshinoBot, Service,MessageSegment
from hoshino.typing import CQEvent
from .info import GetInfo
from .database import DB
from .mytyping import Index,WeeklyReport
from .info_card import DrawIndex,ItemTrans
sv = Service("崩坏3角色卡片",enable_on_default=False,visible=True)

@sv.on_prefix("bh#")
async def bh3_player_card(bot:hoshino.HoshinoBot,ev:CQEvent):
    msg = ev.message.extract_plain_text().strip()
    role_id = re.search(r"\d{1,}",msg).group()
    region_name = re.search(r"\D{1,}",msg).group()
    if re.search(r"[mM][yY][sS]|米游社",region_name):
        spider = GetInfo(mysid=role_id)
    else:
        try:
            region_id = ItemTrans.server2id(region_name)
        except KeyError as e:
            await bot.send(ev,e)
        region_db = DB('region.sqlite')
        if region_db.get_region(role_id) != region_id:
            region_db.set_region(qid=role_id,region=region_id)
        spider = GetInfo(server_id=region_id,role_id=role_id)
    _,ind = spider.fetch(spider.index)
    _,wee = spider.fetch(spider.weekly)
    ind = DrawIndex(**ind['data'])
    wee = WeeklyReport(**wee['data'])
    im = ind.draw_card(wee)
    img = MessageSegment.image(im)
    await bot.send(ev,img)
