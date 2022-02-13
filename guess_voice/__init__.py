import json
import os
import random
import re

from hoshino import HoshinoBot, MessageSegment, Service, priv
from hoshino.typing import CQEvent
from hoshino.util import FreqLimiter

from .game import GameSession

_help = """
[崩坏3猜语音]：正常舰桥、战斗等语音
[崩坏3猜语音2/困难]：简短的语气或拟声词
"""
FN = 30
flmt = FreqLimiter(FN)
sv = Service("崩坏3猜语音", bundle="崩坏3", help_=_help)


def split_voice_by_chara(v_list: list):
    """对语音列表进行分类"""
    ret = {
        "normal": {},  # 正常语音
        "hard": {}   # 语气&拟声词
    }
    for voice in v_list:
        op_dict = ret["hard"] if "拟声词" in voice["voice_path"] else ret["normal"]
        chara = re.split("-|\(", voice["voice_name"])[0].strip()
        if re.search(r"《|【", chara):
            continue
        if not op_dict.get(chara):
            op_dict[chara] = []
        op_dict[chara].append(voice)
    return ret


def gen_voice_list(origin_path=None):
    """递归生成语音列表"""
    voice_dir = os.path.join(os.path.dirname(__file__), "../assets/record")
    if origin_path is None:
        origin_path = voice_dir
    ret_list = []
    for item in os.listdir(origin_path):
        item_path = os.path.join(origin_path, item)
        if os.path.isdir(item_path):
            ret_list.extend(gen_voice_list(item_path))
        elif item.endswith("mp3"):
            voice_path = os.path.relpath(item_path, voice_dir)
            ret_list.append({"voice_name": item, "voice_path": voice_path})
        else:
            continue
    return ret_list


@sv.on_rex(r"^(崩坏?|bh)(3|三)?猜语音")
async def guess_voice(bot: HoshinoBot, ev: CQEvent):
    msg = str(ev.message.extract_plain_text().strip())
    if re.search(r"2|困难", msg):
        difficulty = "hard"
    else:
        difficulty = "normal"
    game = GameSession(ev.group_id)
    ret = await game.start(difficulty=difficulty)
    await bot.send(ev, ret)


@sv.on_message()
async def check_answer(bot, ev: CQEvent):
    game = GameSession(ev.group_id)
    if not game.is_start:
        return
    msg = ev.message.extract_plain_text().strip()
    msg = msg.lower().replace(",", "和").replace("，", "和")
    await game.check_answer(msg, ev.user_id)


@sv.on_rex(r"^(崩坏?|bh)(3|三)?语音([^:]+)$")
async def send_voice(bot: HoshinoBot, ev: CQEvent):
    msg = ev["match"].group(3)
    uid = ev.user_id
    a_list = GameSession.__load__("answer.json")
    assert isinstance(a_list, dict)
    for k, v in a_list.items():
        if msg in v:
            if not flmt.check(uid):
                await bot.send(
                    ev,
                    f"{FN}s内只能获取一次语音，{int(flmt.left_time(uid))}s后再试。",
                    at_sender=True,
                )
                return
            try:
                v_list = GameSession.__load__()["normal"][k]
            except KeyError:
                await bot.send(ev,f"语音列表未生成或有错误，请先发送‘更新崩坏3语音列表’来更新")
            voice = random.choice(v_list)
            voice_path = f"file:///{os.path.join(os.path.dirname(__file__),'../assets/record',voice['voice_path'])}"
            await bot.send(ev, MessageSegment.record(voice_path))
            flmt.start_cd(uid)
            return
    await bot.send(ev, f"没找到【{msg}】的语音，请检查输入。", at_sender=True)


@sv.on_rex(r"^(崩坏?|bh)(3|三)?语音新增答案(\w+)[:|：](\w+)$")
async def add_answer(bot: HoshinoBot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SU):
        return
    origin = ev["match"].group(3)
    new = ev["match"].group(4)
    data = GameSession.__load__("answer.json")
    if origin not in data:
        await bot.send(ev,f"{origin}不存在。")
        return
    if new in data[origin]:
        await bot.send(ev,f"答案已存在。")
        return
    data[origin].append(new)
    with open(
        os.path.join(os.path.dirname(__file__), "answer.json"), "w", encoding="utf8"
    ) as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    await bot.send(ev, "添加完成。")


@sv.on_fullmatch("更新崩坏3语音列表")
async def update_voice_list(bot: HoshinoBot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SU):
        return
    data = gen_voice_list()
    data_dict = split_voice_by_chara(data)
    with open(
        os.path.join(os.path.dirname(__file__), "record.json"), "w", encoding="utf8"
    ) as f:
        json.dump(data_dict, f, indent=4, ensure_ascii=False)
    num_normal = sum(len(data_dict["normal"][v]) for v in data_dict["normal"])
    num_hard = sum(len(data_dict["hard"][v]) for v in data_dict["hard"])
    await bot.send(
        ev, f"崩坏3语音列表更新完成，当前共有语音{num_hard+num_normal}条，其中普通{num_normal}条，困难{num_hard}条"
    )


if __name__ == "__main__":
    data = gen_voice_list()
    with open(
        os.path.join(os.path.dirname(__file__), "record.json"), "w", encoding="utf8"
    ) as f:
        json.dump(split_voice_by_chara(data), f, indent=4, ensure_ascii=False)
