"""生成图片"""
import os
import json
import base64

from rich import print,print_json
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from .mytyping import Index,WeeklyReport
from .mypillow import myDraw
class ItemTrans(object):
    """
    - 数字/字母 -> 文字
    - 文字 -> server_id"""
    def __init__(self) -> None:
        super().__init__()
    @staticmethod
    def area(no):
        """分组"""
        level = ["初级区","中级区","高级区","终极区"]
        return level[no-1]
    @staticmethod
    def new_abyss(no):
        """超弦空间"""
        level = ["禁忌","原罪Ⅰ","原罪Ⅱ","原罪Ⅲ","苦痛Ⅰ","苦痛Ⅱ","苦痛Ⅲ","红莲","寂灭"]
        return level[no-1]
    @staticmethod
    def old_abyss(no):
        """量子奇点&迪拉克之海"""
        level = {
            "A":"红莲",
            "B":"苦痛",
            "C":"原罪",
            "D":"禁忌",
        }
        return level[no]
    @staticmethod
    def server2id(no:str):
        """渠道名转渠道代码"""
        no = no.lower()
        with open(os.path.join(os.path.dirname(__file__),f"region.json"),'r',encoding='utf8') as f:
            region = json.load(f)
            f.close()
        for server_id,alias in region.items():
            if no in alias["alias"]:
                return server_id
        raise KeyError(f"找不到服务器{no}的数据")
    @staticmethod
    def id2server(region_id):
        """渠道代码转渠道名"""
        with open(os.path.join(os.path.dirname(__file__),f"region.json"),'r',encoding='utf8') as f:
            region = json.load(f)
            f.close()
        return region[region_id]["name"]
    @staticmethod
    def rate2png(rate):
        """综合评价 -> 图片地址"""
        BASE = os.path.join(os.path.dirname(__file__),r"assets/star")
        rating_png = {
            "C":"a.png",
            "B":"s.png",
            "A":"ss.png",
            "S":"sss.png"
        }
        return os.path.join(BASE,rating_png[rate])
def draw_text_center(image:Image.Image,font:ImageFont.FreeTypeFont,height:int,color=(0,0,0),text="测翻一翻试"):
    """unused!居中写字"""
    image_w,image_h = image.size
    text_size = font.getsize(text)
    draw = ImageDraw.Draw(image)
    text_condinate = int((image_w-text_size[0])/2),int(height-text_size[1]/2)
    draw.text(text_condinate,text,fill=color,font=font)
    return image

class DrawIndex(Index):

    def draw_card(self,weekr:WeeklyReport):
        if self.preference.is_god_war_unlock:
            bg_path = os.path.join(os.path.dirname(__file__),f"assets/backgroud_godwar.png")
        else:
            bg_path = os.path.join(os.path.dirname(__file__),f"assets/backgroud_no_godwar.png")
        bg = Image.open(bg_path).convert("RGBA")
        bg = myDraw.avatar(bg,avatar_url=self.role.AvatarUrl)
        favorite = Image.open(os.path.join(os.path.dirname(__file__),f"assets/backgroud_avatar/{weekr.favorite_character.large_background_path[-11:]}")).convert("RGBA")
        r,g,b,a = favorite.split()
        bg.paste(favorite,(782,367),mask=a)
        font_path_65 = os.path.join(os.path.dirname(__file__),f"assets/font/HYWenHei-65W.ttf")
        font_path_85 = os.path.join(os.path.dirname(__file__),f"assets/font/HYWenHei-85W.ttf")
        font_path_sara = os.path.join(os.path.dirname(__file__),f"assets/font/sarasa-ui-sc-semibold.ttf")   # hywh缺字
        font = ImageFont.truetype(font_path_sara,48)
        font_6536 = ImageFont.truetype(font_path_65,size=36)
        font_8548 = ImageFont.truetype(font_path_85,size=48)
        font_6532 = ImageFont.truetype(font_path_65,size=32)
        # bg = draw_text_center(bg,font,height=560,text=self.role.nickname,color=(133,96,61))
        # draw = ImageDraw.Draw(bg)
        draw = myDraw(bg)
        draw.text((1120,20),text=f'UID:{self.role.role_id}',fill='white',font=font_6536,anchor='rt')
        draw.text(xy=(562,562),text=self.role.nickname,fill=(0,0,0),font=font,anchor='mm')
        draw.text(xy=(390,647),text=str(self.role.level),fill=(133,96,61),font=font_8548)
        draw.text(xy=(600,650),text=ItemTrans.id2server(self.role.region),fill=(133,96,61),font=font_8548)
        
        # 深渊
        if self.stats.old_abyss is not None:
            draw.text(xy=(232,821),text="量子奇点",fill=(133,96,61),font=font_6536,anchor='mm')
            draw.text(xy=(232,885),text=ItemTrans.old_abyss(self.stats.old_abyss.level_of_quantum),fill=(133,96,61),font=font_6532,anchor='mm')
            draw.line(xy=[(310,790),(310,917)],fill=(161,154,129),width=0)
            draw.text(xy=(410,821),text="迪拉克之海",fill=(133,96,61),font=font_6536,anchor='mm')
            draw.text(xy=(410,885),text=ItemTrans.old_abyss(self.stats.old_abyss.level_of_ow),fill=(133,96,61),font=font_6532,anchor='mm')
        else:
            draw.text(xy=(310,821),text="超弦空间",fill=(133,96,61),font=font_6536,anchor="mm")
            draw.text(xy=(232,885),text=ItemTrans.new_abyss(self.stats.new_abyss.level),fill=(133,96,61),font=font_8548,anchor='mm')
            draw.text(xy=(410,885),text=f"{self.stats.new_abyss.cup_number}杯",fill=(133,96,61),font=font_6532,anchor='mm')
        # 战场
        draw.text(xy=(790,821),text=ItemTrans.area(self.stats.battle_field_area),fill=(133,96,61),font=font_6536,anchor='mm')
        draw.text(xy=(697,885),text=str(self.stats.battle_field_score),fill=(133,96,61),font=font_6536,anchor="mm")
        draw.text(xy=(880,885),text=f"{self.stats.battle_field_ranking_percentage}%",fill=(133,96,61),font=font_8548,anchor="mm")
        # 数据总览
        draw.text(xy=(465,1190),text=str(self.stats.active_day_number),fill=(133,96,61),font=font_8548,anchor="mm")
        draw.text(xy=(465,1305),text=str(self.stats.armor_number),fill=(133,96,61),font=font_8548,anchor="mm")
        draw.text(xy=(465,1420),text=str(self.stats.weapon_number),fill=(133,96,61),font=font_8548,anchor="mm")
        draw.text(xy=(1010,1190),text=str(self.stats.suit_number),fill=(133,96,61),font=font_8548,anchor="mm")
        draw.text(xy=(1010,1305),text=str(self.stats.sss_armor_number),fill=(133,96,61),font=font_8548,anchor="mm")
        draw.text(xy=(1010,1420),text=str(self.stats.stigmata_number),fill=(133,96,61),font=font_8548,anchor="mm")
        # 往世乐土
        if self.preference.is_god_war_unlock:
            draw.text(xy=(307,1645),text=str(self.stats.god_war_max_punish_level),fill=(133,96,61),font=font_8548,anchor="mm")
            draw.text(xy=(809,1645),text=str(self.stats.god_war_max_challenge_level)+"层"+str(self.stats.god_war_max_challenge_score),fill=(133,96,61),font=font_8548,anchor="mm")
            draw.text(xy=(307,1789),text=str(self.stats.god_war_max_level_avatar_number),fill=(133,96,61),font=font_8548,anchor="mm")
            draw.text(xy=(809,1789),text=str(self.stats.god_war_extra_item_number),fill=(133,96,61),font=font_8548,anchor="mm")
        # 舰长偏好
        data = [
            self.preference.battle_field,
            self.preference.abyss,
            self.preference.god_war,
            self.preference.open_world,
            self.preference.community,
            self.preference.main_line,
        ]
        if self.preference.is_god_war_unlock:
            draw.radar(data=data,center=(237,2246),radius=164)
        else:
            data.pop(2)
            draw.radar(data=data,center=(237,2246),radius=177)
        draw.text(xy=(845,2176),text=str(self.preference.comprehensive_score),font=font_8548,fill=(133,96,61),anchor="mm")
        rating_image_path = ItemTrans.rate2png(self.preference.comprehensive_rating)
        rating_image = Image.open(rating_image_path).convert("RGBA")
        bg.paste(rating_image,box=(782,2300),mask=rating_image.split()[3])
        # bg.show()

        bio = BytesIO()
        # data = bg.convert("RGB")
        bg.save(bio, format="png", quality=80)
        base64_str = base64.b64encode(bio.getvalue()).decode()
        bg.close()
        return "base64://" + base64_str
        bg.show()


if __name__ == '__main__':
    with open(os.path.join(os.path.dirname(__file__),f"dist/index.json"),'r',encoding='utf8') as f:
        index = json.load(f)
        f.close()
    with open(os.path.join(os.path.dirname(__file__),f"dist/weeklyReport.json"),'r',encoding='utf8') as f:
        weekly = json.load(f)
        f.close()
    di = DrawIndex(**index["data"])
    # print(di.json())
    di.draw_card(WeeklyReport(**weekly["data"]))