# pylint: disable=no-name-in-module
# pylint: disable=no-self-argument
import os
import yaml
 
from pydantic import BaseModel, main
from typing import List, Optional, Union

class Config(BaseModel):
    cookies:List[str]
    is_egenshin:bool
    egenshin_dir:str
    cache_dir:str
    @staticmethod
    def load_config() -> dict:
        with open(os.path.join(os.path.dirname(__file__),f"config.yaml"),mode='r',encoding='utf8') as f:
            CONFIG = yaml.load(f,Loader=yaml.FullLoader)
            f.close()
        return CONFIG

    # def __init__(self) -> None:
    #     super().__init__()
    #     con = Config.load_config()
    #     self.cookies = con["cookies"]
    # def get_cookie(self):
    #     pass
        
config = Config(**Config.load_config())
COOKIES = config.cookies[0]
class _favorite_character(BaseModel):
    id:str
    name:str
    star:int
    avatar_background_path:str
    icon_path:str
    background_path:str
    large_background_path:str
class WeeklyReport(BaseModel):
    favorite_character:Union[_favorite_character,None]
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

if __name__ == '__main__':
    con = Config(**Config.load_config())
    print(con)