# pylint: disable=no-name-in-module
# pylint: disable=no-self-argument
import os
import yaml

from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional, Union

class Config(BaseModel):
    cookies: List[str]
    is_egenshin: bool
    egenshin_dir: str
    cache_dir: str

    @staticmethod
    def load_config() -> dict:
        with open(
            os.path.join(os.path.dirname(__file__), f"config.yaml"),
            mode="r",
            encoding="utf8",
        ) as f:
            CONFIG = yaml.load(f, Loader=yaml.FullLoader)
            f.close()
        return CONFIG


config = Config(**Config.load_config())
COOKIES = config.cookies[0]


class _favorite_character(BaseModel):
    id: str
    name: str
    star: int
    avatar_background_path: str
    icon_path: str
    background_path: str
    large_background_path: str


class WeeklyReport(BaseModel):
    favorite_character: Union[_favorite_character, None]
    gold_income: int
    gold_expenditure: int
    active_day_number: int
    online_hours: int
    expended_physical_power: int
    main_line_expended_physical_power_percentage: int


class _role(BaseModel):
    AvatarUrl: str
    nickname: str
    region: str
    level: int
    role_id: str


class _abyss(BaseModel):
    level: Optional[int]
    cup_number: Optional[int]
    level_of_quantum: Optional[str]
    level_of_ow: Optional[str]


class _stats(BaseModel):
    active_day_number: int
    suit_number: int
    stigmata_number: int
    armor_number: int
    sss_armor_number: int
    battle_field_ranking_percentage: str
    new_abyss: Optional[_abyss]
    old_abyss: Optional[_abyss]
    weapon_number: int
    god_war_max_punish_level: int
    god_war_extra_item_number: int
    god_war_max_challenge_score: int
    god_war_max_challenge_level: int
    god_war_max_level_avatar_number: int
    battle_field_area: int
    battle_field_score: int
    abyss_score: int
    battle_field_rank: int


class _preference(BaseModel):
    abyss: int
    main_line: int
    battle_field: int
    open_world: int
    community: int
    comprehensive_score: int
    comprehensive_rating: str
    god_war: int
    is_god_war_unlock: bool


class Index(BaseModel):
    role: _role
    stats: _stats
    preference: _preference


class _boss(BaseModel):
    id: str
    name: str
    avatar: str


class _avatar(BaseModel):
    """角色,不含武器圣痕"""

    id: str
    name: str
    star: int
    avatar_background_path: str
    icon_path: str
    background_path: str
    large_background_path: str
    figure_path: str
    level: int
    oblique_avatar_background_path: str
    half_length_icon_path: str
    image_path: str


class _elf(BaseModel):
    id: int
    name: str
    avatar: str
    rarity: int
    star: int


class AbyssReport(BaseModel):
    score: int
    update_time_second: Optional[datetime]
    time_scond: Optional[datetime]
    area: Optional[int]
    boss: _boss
    lineup: List[_avatar]
    rank: Optional[int]
    settled_cup_number: Optional[int]
    cup_number: Optional[int]
    elf: Union[_elf,None]
    level: Union[int, str]
    settled_level: Optional[int]
    reward_type: Optional[str]
    type: Optional[str]


class Abyss(BaseModel):
    reports: List[AbyssReport]


class BattleFieldInfo(BaseModel):
    elf: Union[_elf,None]
    lineup: List[_avatar]
    boss: _boss
    score: int


class BattleFieldReport(BaseModel):
    score: int
    rank: int
    ranking_percentage: str
    area: int
    battle_infos: List[BattleFieldInfo]
    time_second:datetime

class BattleField(BaseModel):
    reports: List[BattleFieldReport]


class godWarBuff(BaseModel):
    icon: str
    number: int
    id: int


class godWarCondition(BaseModel):
    name: str
    desc: str
    difficulty: int


class godWarRecord(BaseModel):
    settle_time_second: datetime
    score: int
    punish_level: int
    level: int
    buffs: List[godWarBuff]
    conditions: List[godWarCondition]
    main_avatar: _avatar
    support_avatars: List[_avatar]
    elf: Union[_elf,None]
    extra_item_icon: str


class godWarCollection(BaseModel):
    type: str
    collected_number: int
    total_number: int


class godWarSummary(BaseModel):
    max_level_avatar_number: int
    max_support_point: int
    extra_item_number: int
    max_punish_level: int
    max_challenge_score: int
    avatar_numbers: int
    max_challenge_level: int


class godWarAvatar(BaseModel):
    avatar: _avatar
    level: int
    challenge_success_times: int
    max_challenge_score: int
    max_punish_level: int
    max_challenge_level: int


class _godWar(BaseModel):
    records: List[godWarRecord]
    collections: List[godWarCollection]
    summary: godWarSummary
    avatar_transcript: List[godWarAvatar]


class _weapon(BaseModel):
    id: int
    name: str
    max_rarity: int
    rarity: int
    icon: str


class _stigamata(BaseModel):
    id: int
    name: str
    max_rarity: int
    rarity: int
    icon: str


class Chara_chara(BaseModel):
    avatar: _avatar
    weapon: _weapon
    stigmatas: List[_stigamata]


class Chara(BaseModel):
    character: Chara_chara
    is_chosen: bool


class Character(BaseModel):
    characters: List[Chara]


class FullInfo(BaseModel):
    """all in one"""

    godWar: _godWar
    characters: Character
    index: Index
    newAbyssReport: Optional[Abyss]
    latestOldAbyssReport: Optional[Abyss]
    weeklyReport: WeeklyReport
    battleFieldReport: BattleField

