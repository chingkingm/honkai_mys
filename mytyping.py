# pylint: disable=no-name-in-module
# pylint: disable=no-self-argument
from pydantic import BaseModel
from typing import Optional
class _favorite_character(BaseModel):
    id:str
    name:str
    star:int
    avatar_background_path:str
    icon_path:str
    background_path:str
    large_background_path:str
class WeeklyReport(BaseModel):
    favorite_character:_favorite_character
    gold_income:int
    gold_expenditure:int
    active_day_number:int
    online_hours:int
    expended_physical_power:int
    main_line_expended_physical_power_percentage:int
class _role(BaseModel):
    AvatarUrl:str
    nickname:str
    region:str
    level:int
    role_id:str
class _abyss(BaseModel):
    level:Optional[int]
    cup_number:Optional[int]
    level_of_quantum:Optional[str]
    level_of_ow:Optional[str]
class _stats(BaseModel):
    active_day_number:int
    suit_number:int
    stigmata_number:int
    armor_number:int
    sss_armor_number:int
    battle_field_ranking_percentage:str
    new_abyss:Optional[_abyss]
    old_abyss:Optional[_abyss]
    weapon_number:int
    god_war_max_punish_level: int
    god_war_extra_item_number: int
    god_war_max_challenge_score: int
    god_war_max_challenge_level: int
    god_war_max_level_avatar_number:int
    battle_field_area:int
    battle_field_score:int
    abyss_score:int
    battle_field_rank:int
class _preference(BaseModel):
    abyss:int
    main_line:int
    battle_field: int
    open_world: int
    community: int
    comprehensive_score: int
    comprehensive_rating: str
    god_war: int
    is_god_war_unlock: bool
class Index(BaseModel):
    role:_role
    stats:_stats
    preference:_preference