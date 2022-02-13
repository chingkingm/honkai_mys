import json
import os
import random
from datetime import datetime, timedelta
from shutil import copy

from apscheduler.triggers.date import DateTrigger
from loguru import logger
from hoshino import MessageSegment, get_bot
from nonebot import scheduler

# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# scheduler = AsyncIOScheduler()
game_record = {}
bot = get_bot()


class GameSession:
    @staticmethod
    def __load__(file: str = "record.json"):
        file = os.path.join(os.path.dirname(__file__), file)
        if not os.path.exists(file):
            if file.endswith("record.json"):
                with open(file, "w", encoding="utf8") as f:
                    f.write("{}")
            elif file.endswith("answer.json"):
                copy(
                    os.path.join(os.path.dirname(__file__), "answer_template.json"),
                    file,
                )
        with open(file, "r", encoding="utf8") as li:
            data = json.load(li)
        return data

    def __init__(self, gid: int) -> None:
        self.group_id = gid
        self.record = game_record.get(self.group_id, {})
        self.job_id = f"{self.group_id}_bh3_guess_voice"
        self.voice_list = self.__load__()

    async def start(self, duration: int = 30, difficulty: str = "normal"):
        """difficulty:  normal|hard"""
        if self.is_start:
            return f"游戏正在进行中"
        self.begin = datetime.now()
        self.end = self.begin + timedelta(seconds=duration)
        try:
            self.chara, vlist = random.choice(list(self.voice_list[difficulty].items()))
        except KeyError:
            return f"语音列表未生成或有错误，请先发送‘更新崩坏3语音列表’来更新"
        self.voice = random.choice(vlist)
        game_record.update(
            {self.group_id: {"chara": self.chara, "voice": self.voice, "ok": -1}}
        )
        if scheduler.get_job(job_id=self.job_id):
            scheduler.remove_job(self.job_id)
        scheduler.add_job(
            self.stop,
            trigger=DateTrigger(self.end),
            id=self.job_id,
            misfire_grace_time=60,
            coalesce=True,
            max_instances=1,
        )
        record_path = f"file:///{os.path.join(os.path.dirname(__file__),'../assets/record',self.voice['voice_path'])}"
        print(self.answer)
        await bot.send_group_msg(
            group_id=self.group_id, message=f"即将发送一段崩坏3语音，将在{duration}后公布答案。"
        )
        return f"{MessageSegment.record(record_path)}"

    @property
    def answer(self) -> list:
        self.chara = game_record[self.group_id]["chara"]
        alist = self.__load__("answer.json")
        return alist[self.chara]

    @property
    def is_start(self):
        self.record = game_record.get(self.group_id, {})
        return bool(self.record != {})

    async def stop(self):
        self.record = game_record.get(self.group_id)
        ok_player = self.record["ok"]
        if ok_player < 0:
            ret_msg = "还没有人猜中呢"
        else:
            ret_msg = f"回答正确的人：{MessageSegment.at(ok_player)}"
        ret_msg = f"正确答案是：{self.chara}\n{ret_msg}"
        await bot.send_group_msg(group_id=self.group_id, message=ret_msg)
        game_record[self.group_id] = {}

    async def check_answer(self, ans: str, qid: int):
        self.record = game_record.get(self.group_id)
        if self.record["ok"] > 0:
            return
        if ans not in self.answer:
            return
        if scheduler.get_job(self.job_id):
            scheduler.remove_job(self.job_id)
        game_record[self.group_id]["ok"] = qid
        await self.stop()
