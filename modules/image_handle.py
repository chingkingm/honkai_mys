import base64
import math
import os
import re
from io import BytesIO
from math import cos, pi, sin
from operator import attrgetter
from typing import List, Tuple, Union

from httpx import AsyncClient
from PIL import Image, ImageChops, ImageDraw, ImageFont

from .mytyping import (
    AbyssReport,
    BattleFieldReport,
    Character,
    FinanceInfo,
    FullInfo,
    Index,
    _stigamata,
    _weapon,
)
from .util import ItemTrans


class myDraw(ImageDraw.ImageDraw):
    def __init__(self, im) -> None:
        super().__init__(im)

    @classmethod
    async def avatar(
        cls,
        bg: Image.Image,
        qid: str = None,
        avatar_url: str = None,
        center: Tuple[int, int] = [562, 267],
    ) -> Image.Image:
        """头像"""
        qava_url = "http://q1.qlogo.cn/g?b=qq&nk={qid}&s=140"
        if avatar_url is not None:
            try:
                no = re.search(r"\d{3,}", avatar_url).group()
                a_url = avatar_url.split(no)[0] + no + ".png"
            except:
                try:
                    no = re.search(r"[a-zA-Z]{1,}\d{2}", avatar_url).group()
                    a_url = avatar_url.split(no)[0] + no + ".png"
                except:
                    a_url = "https://upload-bbs.mihoyo.com/game_record/honkai3rd/all/SpriteOutput/AvatarIcon/705.png"
        else:
            a_url = qava_url.format(qid=qid)
        pic_data = await cls.get_net_img(url=a_url)
        with Image.open(
            os.path.join(os.path.dirname(__file__), "../assets/404.png")
        ) as img_404:
            if ImageChops.difference(img_404, Image.open(pic_data)).getbbox() is None:
                pic_data = await cls.get_net_img(url=qava_url.format(qid=qid))
        with Image.open(pic_data) as pic:
            pic = cls.ImgResize(pic, 256 / pic.width).convert("RGBA")
            with Image.new(mode="RGBA", size=bg.size, color="#ece5d8") as im:
                im.alpha_composite(
                    pic,
                    dest=(
                        int(center[0] - 0.5 * pic.width),
                        int(center[1] - 0.5 * pic.height),
                    ),
                )
                im.alpha_composite(bg)
                return im

    @staticmethod
    def get_font(font: str = "65", size: int = 36) -> ImageFont.FreeTypeFont:
        font = str(font)
        font_path_65 = os.path.join(
            os.path.dirname(__file__), f"../assets/font/HYWenHei-65W.ttf"
        )
        font_path_85 = os.path.join(
            os.path.dirname(__file__), f"../assets/font/HYWenHei-85W.ttf"
        )
        font_path_sara = os.path.join(
            os.path.dirname(__file__), f"../assets/font/sarasa-ui-sc-semibold.ttf"
        )  # hywh缺字
        font_path_lxj = os.path.join(
            os.path.dirname(__file__), "../assets/font/HYLingXinTiJ.ttf"
        )
        if font == "65":
            font_path = font_path_65
        elif font == "85":
            font_path = font_path_85
        elif font == "s":
            font_path = font_path_sara
        elif font == "l":
            font_path = font_path_lxj
        return ImageFont.truetype(font_path, size)

    @staticmethod
    def radar(
        origin_image: Image.Image,
        data: List[float],
        center: Tuple[float, float],
        radius: float,
    ) -> Image.Image:
        """雷达图,求出各点坐标,调用ImageDraw.polygon"""
        # origin_image = bg
        # 新建工作图片
        im = Image.new("RGBA", size=origin_image.size, color=(255, 255, 255, 0))
        dr = ImageDraw.Draw(im)
        zero_x, zero_y = center
        sides = len(data)
        angel = 2 * pi / sides
        angles = [angel * n for n in range(sides)]
        hypotenuse = [n * radius / 100 for n in data]
        coordinates = []
        for i, hy in enumerate(hypotenuse):
            x = zero_x + hy * sin(angles[i])
            y = zero_y - hy * cos(angles[i])
            coordinates.append((x, y))
        dr.polygon(xy=coordinates, fill=(0, 192, 255, 190))
        size = 4
        for point in coordinates:
            x, y = point
            dr.ellipse(
                xy=(x - size, y - size, x + size, y + size),
                fill="white",
                outline=(0, 192, 255),
            )
        # 粘贴到目标图片
        origin_image.alpha_composite(im)
        return origin_image

    @staticmethod
    async def get_net_img(url: str) -> Union[BytesIO, str]:
        async with AsyncClient() as aiorequests:
            if url.startswith("http://q1.qlogo.cn/"):
                resp = await aiorequests.get(url)
                return BytesIO(resp.content)
            image_type, img_name = url.split("/")[-2:]
            ASSETS_PATH = os.path.join(os.path.dirname(__file__), "../assets")
            image_type_path = os.path.join(ASSETS_PATH, image_type)
            if not os.path.exists(image_type_path):
                os.makedirs(image_type_path)
            else:
                ex_image = os.listdir(image_type_path)
                if img_name in ex_image:
                    return os.path.join(image_type_path, img_name)
            resp = await aiorequests.get(url)
            data = resp.content
            with open(os.path.join(image_type_path, img_name), mode="wb") as im:
                im.write(data)
                im.close()
            return BytesIO(data)

    @staticmethod
    def ImgResize(
        im: Image.Image, coe: float = None, weight: int = None, height: int = None
    ) -> Image.Image:
        """等比例缩放"""
        if coe is not None:
            return im.resize((int(length * coe) for length in im.size))
        elif weight is not None:
            coe = weight / im.size[0]
            return im.resize((int(weight), int(im.size[1] * coe)))
        elif height is not None:
            coe = height / im.size[1]
            return im.resize((int(im.size[0] * coe), int(height)))

    @staticmethod
    def ring(data: Tuple[int], radius: int = 120) -> Image.Image:
        """画环"""
        imsize = 300
        imsize_half = 0.5 * imsize
        with Image.new("RGBA", size=[imsize, imsize]) as im:
            dr = ImageDraw.Draw(im)
            degree_start = -90
            degree_radian = 0
            colors = ["#969cf2", "#fc9208", "#57d9ad", "#ffe148"]
            # 先画饼图
            for n, d in enumerate(data):
                dr.pieslice(
                    [
                        imsize_half - radius,
                        imsize_half - radius,
                        imsize_half + radius,
                        imsize_half + radius,
                    ],
                    start=degree_start,
                    end=degree_start + d * 3.6,
                    fill=colors[n],
                )
                degree_start += d * 3.6
                degree_radian = degree_radian + d / 100 * 2 * pi
                dr.line(
                    xy=[
                        imsize_half,
                        imsize_half,
                        imsize_half + sin(degree_radian) * radius,
                        imsize_half - cos(degree_radian) * radius,
                    ],
                    fill="white",
                    width=2,
                )  # 画分割线
            # 用圆遮住中间,形成环
            dr.ellipse(
                xy=(
                    imsize_half - 0.5 * radius,
                    imsize_half - 0.5 * radius,
                    imsize_half + 0.5 * radius,
                    imsize_half + 0.5 * radius,
                ),
                fill="white",
            )
            return im

    @staticmethod
    def star(equip: Union[_stigamata, _weapon]) -> Image.Image:
        """画星星"""
        num_total = equip.max_rarity
        num_bright = equip.rarity
        im_name = f"{num_bright}_of_{num_total}.png"
        im_path = os.path.join(os.path.dirname(__file__), "../assets/star", im_name)
        if os.path.exists(im_path):
            return Image.open(im_path).convert("RGBA")
        starlist = [1] * num_bright
        num_dark = num_total - num_bright
        starlist.extend([0] * num_dark)
        star = Image.open(
            os.path.join(os.path.dirname(__file__), "../assets/star/星.png")
        )
        star_dark = Image.open(
            os.path.join(os.path.dirname(__file__), "../assets/star/灰星.png")
        )
        with Image.new(mode="RGBA", size=(216, 62), color=(0, 0, 0, 0)) as bg:
            indent = 31
            length = indent * num_total
            x = int(0.5 * (bg.size[0] - length))
            y = 14
            for n, s in enumerate(starlist):
                if s:
                    bg.alpha_composite(star, dest=(x + indent * n, y))
                else:
                    bg.alpha_composite(star_dark, dest=(x + indent * n, y))
            bg.save(im_path, format="png")
            return bg


def pic2b64(im: Image.Image, quality: int = 100) -> str:
    bio = BytesIO()
    im.save(bio, format="png", quality=quality)
    base64_str = base64.b64encode(bio.getvalue()).decode()
    im.close()
    return "base64://" + base64_str


async def draw_abyss(aby: AbyssReport) -> Image.Image:
    if aby.type == "Greedy":
        bg_path = os.path.join(os.path.dirname(__file__), "../assets/abyss_greedy.png")
    else:
        bg_path = os.path.join(os.path.dirname(__file__), "../assets/abyss.png")
    with Image.open(bg_path) as im:
        dr = myDraw(im)
        with Image.new(mode="RGBA", size=im.size) as temp:
            for n, val in enumerate(aby.lineup):
                ava_bg = dr.ImgResize(
                    Image.open(
                        await dr.get_net_img(val.avatar_background_path)
                    ).convert("RGBA"),
                    1.5,
                )
                ava_icon = dr.ImgResize(
                    Image.open(await dr.get_net_img(val.icon_path)).convert("RGBA"),
                    0.72,
                )
                temp.alpha_composite(ava_bg, dest=(45 + n * 120, 108))
                temp.alpha_composite(ava_icon, dest=(45 + n * 120, 109))
            temp.alpha_composite(im)
            img_boss = dr.ImgResize(
                Image.open(await dr.get_net_img(aby.boss.avatar)), 1.26
            )
            if aby.elf is not None:
                img_elf = Image.open(await dr.get_net_img(aby.elf.avatar))
                img_elf = dr.ImgResize(img_elf, coe=0.74)
                img_elf_star = dr.ImgResize(
                    Image.open(ItemTrans.star(aby.elf.star, 1)), 0.755
                )
                temp.alpha_composite(img_elf, dest=(415, 110))
                temp.alpha_composite(img_elf_star, dest=(408, 172))
            for n, val in enumerate(aby.lineup):
                ava_star = dr.ImgResize(Image.open(ItemTrans.star(val.star)), 0.49)
                temp.alpha_composite(ava_star, dest=(23 + n * 120, 159))
            temp.alpha_composite(img_boss, dest=(700, 76))
            im = temp.copy()
        dr = myDraw(im)
        font_wh65 = myDraw.get_font(size=24)
        font_lxj = myDraw.get_font("l", 48)
        font_lxj_s = myDraw.get_font("l", 40)
        dr.text((39, 60), text=f"{aby.boss.name}", fill="white", font=font_wh65)
        if aby.type == "Greedy":
            if aby.floor == 10:
                dr.text(
                    xy=(938, 28),
                    text=f"{aby.floor}层{aby.score:,}",
                    fill="#0f9ed8",
                    font=font_lxj_s,
                    anchor="mm",
                )
            else:
                # TODO: 缺少数据，临时处理
                dr.text(
                    xy=(938, 28),
                    text=f"{aby.floor}层",
                    fill="#0f9ed8",
                    font=font_lxj,
                    anchor="mm",
                )
        else:
            dr.text(
                (865, 28),
                text=f"{aby.score:,}",
                fill="#0f9ed8",
                font=font_lxj,
                anchor="lm",
            )
        if aby.reward_type:
            # 有reward_type表明是低级区深渊
            abylevel = aby.level
            timescond = aby.time_second
            dr.text(
                xy=(580, 28),
                text=f"{ItemTrans.oldAbyssLevelChange(aby.reward_type)}",
                fill="white",
                font=font_wh65,
                anchor="lm",
            )
        else:
            abylevel = aby.level
            timescond = aby.updated_time_second
            dr.multiline_text(
                xy=(600, 153),
                text=f"段位: {ItemTrans.abyss_level(aby.settled_level)}\n排名: {str(aby.rank)}\n杯数: {aby.cup_number}({aby.settled_cup_number:+})",
                fill="white",
                font=font_wh65,
                anchor="lm",
            )
        dr.text(
            (39, 15),
            text=f"{ItemTrans.area(aby.area)}·{ItemTrans.abyss_level(abylevel)}·{ItemTrans.abyss_type(aby.type)}",
            fill="white",
            font=font_wh65,
        )
        dr.text(
            xy=(680, 90),
            text=f"结算时间:{timescond.astimezone().date()}",
            fill="#d4c18d",
            font=font_wh65,
            anchor="rb",
        )
        return im


async def draw_battlefield(bfs: BattleFieldReport) -> List[Image.Image]:
    ret: List[Image.Image] = []
    for bf in bfs.battle_infos:
        with Image.open(
            os.path.join(os.path.dirname(__file__), "../assets/bf.png")
        ) as bg:
            dr = myDraw(bg)
            img_boss = Image.open(await dr.get_net_img(bf.boss.avatar))
            bg.alpha_composite(img_boss, dest=(42, 0))
            for n, val in enumerate(bf.lineup):
                img_val = dr.ImgResize(
                    Image.open(await dr.get_net_img(val.background_path)), 0.77
                )
                bg.alpha_composite(img_val, dest=(0, 166 + 104 * n))
                img_star = dr.ImgResize(Image.open(ItemTrans.star(val.star)), 0.455)
                bg.alpha_composite(img_star, dest=(283, 222 + 104 * n))
            if bf.elf is not None:
                img_elf = dr.ImgResize(
                    Image.open(await dr.get_net_img(bf.elf.avatar)), 0.562
                )
                bg.alpha_composite(img_elf, dest=(124, 485))
                img_star = dr.ImgResize(
                    Image.open(ItemTrans.star(bf.elf.star, 1)), 0.44
                )
                bg.alpha_composite(img_star, dest=(195, 523))
            dr.text(
                xy=(170, 133),
                text=f"{bf.score:,}",
                fill="#f1bd31",
                font=myDraw.get_font("l", 48),
                anchor="mm",
            )
            ret.append(bg)
    return ret


class DrawIndex(FullInfo):
    async def draw_card(self, qid: str = None) -> str:
        weekr = self.weeklyReport
        if self.index.preference.is_god_war_unlock:
            bg_path = os.path.join(
                os.path.dirname(__file__), f"../assets/backgroud_godwar.png"
            )
        else:
            bg_path = os.path.join(
                os.path.dirname(__file__), f"../assets/backgroud_no_godwar.png"
            )
        bg = Image.open(bg_path).convert("RGBA")
        bg = await myDraw.avatar(bg, avatar_url=self.index.role.AvatarUrl, qid=qid)
        if weekr.favorite_character is not None:
            img_fav = Image.open(
                await myDraw.get_net_img(weekr.favorite_character.large_background_path)
            )
            bg.alpha_composite(img_fav, dest=(782, 367))
        font = myDraw.get_font("s", 48)
        font_6536 = myDraw.get_font()
        font_8548 = myDraw.get_font("85", 48)
        font_6532 = myDraw.get_font(size=32)
        font_6524 = myDraw.get_font(size=24)
        draw = myDraw(bg)
        draw.text(
            (1100, 20),
            text=f"UID:{self.index.role.role_id}",
            fill="white",
            font=font_6536,
            anchor="rt",
        )
        draw.text(
            xy=(562, 562),
            text=self.index.role.nickname,
            fill=(0, 0, 0),
            font=font,
            anchor="mm",
        )
        draw.text(
            xy=(390, 675),
            text=str(self.index.role.level),
            fill=(133, 96, 61),
            font=font_8548,
            anchor="lm",
        )
        draw.text(
            xy=(641, 677),
            text=ItemTrans.id2server(self.index.role.region),
            fill=(133, 96, 61),
            font=font_8548,
            anchor="mm",
        )

        # 深渊
        if self.index.stats.old_abyss is not None:
            draw.text(
                xy=(232, 821),
                text="量子奇点",
                fill=(133, 96, 61),
                font=font_6536,
                anchor="mm",
            )
            draw.text(
                xy=(232, 885),
                text=ItemTrans.abyss_level(self.index.stats.old_abyss.level_of_quantum),
                fill=(133, 96, 61),
                font=font_6532,
                anchor="mm",
            )
            draw.line(xy=[(310, 790), (310, 917)], fill=(161, 154, 129), width=0)
            draw.text(
                xy=(410, 821),
                text="量子流形",
                fill=(133, 96, 61),
                font=font_6536,
                anchor="mm",
            )
            draw.text(
                xy=(410, 885),
                text=ItemTrans.abyss_level(self.index.stats.old_abyss.level_of_greedy),
                fill=(133, 96, 61),
                font=font_6532,
                anchor="mm",
            )
        else:
            draw.text(
                xy=(310, 821),
                text="超弦空间",
                fill=(133, 96, 61),
                font=font_6536,
                anchor="mm",
            )
            draw.text(
                xy=(232, 885),
                text=ItemTrans.abyss_level(self.index.stats.new_abyss.level),
                fill=(133, 96, 61),
                font=font_8548,
                anchor="mm",
            )
            draw.text(
                xy=(410, 885),
                text=f"{self.index.stats.new_abyss.cup_number}杯",
                fill=(133, 96, 61),
                font=font_6532,
                anchor="mm",
            )
        # 战场
        draw.text(
            xy=(790, 821),
            text=ItemTrans.area(self.index.stats.battle_field_area),
            fill=(133, 96, 61),
            font=font_6536,
            anchor="mm",
        )
        if self.index.stats.battle_field_score != 0:
            draw.text(
                xy=(697, 885),
                text=f"{self.index.stats.battle_field_score:,}",
                fill=(133, 96, 61),
                font=font_6536,
                anchor="mm",
            )
            draw.text(
                xy=(880, 885),
                text=f"{self.index.stats.battle_field_ranking_percentage}%",
                fill=(133, 96, 61),
                font=font_8548,
                anchor="mm",
            )
        else:
            draw.text(
                xy=(790, 885),
                text="无数据",
                fill=(133, 96, 61),
                font=font_6532,
                anchor="mm",
            )
        # 数据总览
        draw.text(
            xy=(465, 1190),
            text=str(self.index.stats.active_day_number),
            fill=(133, 96, 61),
            font=font_8548,
            anchor="mm",
        )
        draw.text(
            xy=(465, 1305),
            text=str(self.index.stats.armor_number),
            fill=(133, 96, 61),
            font=font_8548,
            anchor="mm",
        )
        draw.text(
            xy=(465, 1420),
            text=str(self.index.stats.weapon_number),
            fill=(133, 96, 61),
            font=font_8548,
            anchor="mm",
        )
        draw.text(
            xy=(1010, 1190),
            text=str(self.index.stats.suit_number),
            fill=(133, 96, 61),
            font=font_8548,
            anchor="mm",
        )
        draw.text(
            xy=(1010, 1305),
            text=str(self.index.stats.sss_armor_number),
            fill=(133, 96, 61),
            font=font_8548,
            anchor="mm",
        )
        draw.text(
            xy=(1010, 1420),
            text=str(self.index.stats.stigmata_number),
            fill=(133, 96, 61),
            font=font_8548,
            anchor="mm",
        )
        # 往世乐土
        if self.index.preference.is_god_war_unlock:
            draw.text(
                xy=(307, 1645),
                text=str(self.index.stats.god_war_max_support_point),
                fill=(133, 96, 61),
                font=font_8548,
                anchor="mm",
            )
            draw.text(
                xy=(809, 1645),
                text=str(self.index.stats.god_war_max_challenge_score),
                fill=(133, 96, 61),
                font=font_8548,
                anchor="mm",
            )
            draw.text(
                xy=(307, 1789),
                text=str(self.index.stats.god_war_max_level_avatar_number),
                fill=(133, 96, 61),
                font=font_8548,
                anchor="mm",
            )
            draw.text(
                xy=(809, 1789),
                text=str(self.index.stats.god_war_extra_item_number),
                fill=(133, 96, 61),
                font=font_8548,
                anchor="mm",
            )
        # 舰长偏好
        data = [
            self.index.preference.battle_field,
            self.index.preference.abyss,
            self.index.preference.god_war,
            self.index.preference.open_world,
            self.index.preference.community,
            self.index.preference.main_line,
        ]
        if self.index.preference.is_god_war_unlock:
            bg = draw.radar(bg, data=data, center=(237, 2246), radius=164)
        else:
            data.pop(2)
            bg = draw.radar(bg, data=data, center=(237, 2246), radius=177)
        draw = ImageDraw.Draw(bg)
        draw.text(
            xy=(845, 2176),
            text=str(self.index.preference.comprehensive_score),
            font=font_8548,
            fill=(133, 96, 61),
            anchor="mm",
        )
        rating_image_path = ItemTrans.rate2png(
            self.index.preference.comprehensive_rating
        )
        rating_image = Image.open(rating_image_path).convert("RGBA")
        bg.alpha_composite(rating_image, dest=(782, 2300))
        # 深渊战报
        if self.newAbyssReport is not None:
            abyss = self.newAbyssReport
        else:
            abyss = self.latestOldAbyssReport
            abyss.reports.sort(key=attrgetter("time_second"), reverse=True)
        if len(abyss.reports) == 0:
            bg.alpha_composite(
                Image.open(
                    os.path.join(os.path.dirname(__file__), "../assets/no-data.png")
                ),
                dest=(379, 2767),
            )
        for n, reports in enumerate(abyss.reports):
            abyss_card = await draw_abyss(reports)
            bg.alpha_composite(abyss_card, dest=(48, 2622 + n * 230))
            if n >= 2:
                break
        # 战场战报
        if self.battleFieldReport.reports:
            bfr = self.battleFieldReport.reports[0]
            ims = await draw_battlefield(bfr)
            for n, bfcard in enumerate(ims):
                bg.alpha_composite(bfcard, dest=(39 + 355 * n, 3542))
            draw.text(
                xy=(562, 3506),
                text=f"{ItemTrans.area(bfr.area)}\t{bfr.ranking_percentage}%\t{bfr.score:,}",
                fill=(133, 96, 61),
                font=font_6536,
                anchor="mm",
            )
            draw.text(
                xy=(1110, 3530),
                text=f"结算时间:{bfr.time_second.astimezone().date()}",
                fill="gray",
                font=font_6524,
                anchor="rb",
            )
        else:
            bg.alpha_composite(
                Image.open(
                    os.path.join(os.path.dirname(__file__), "../assets/no-data2.png")
                ),
                dest=(398, 3678),
            )
        # bg.show()

        return pic2b64(bg, quality=100)


def cal_dest(im: Image.Image, center: int) -> int:
    """计算粘贴位置"""
    size = im.size
    return int(center - 0.5 * size[0])


class DrawCharacter(Character):
    async def draw_chara(self, index: Index, qid: str = None) -> str:
        row_number = math.ceil(len(self.characters) / 3)
        card_chara = Image.new(
            mode="RGBA", size=(920, 20 + 320 * row_number), color=(236, 229, 216)
        )
        for no, valkyrie in enumerate(self.characters):
            with Image.open(
                os.path.join(os.path.dirname(__file__), "../assets/chara.png")
            ) as bg:
                blank = Image.new(mode="RGBA", size=bg.size, color=(236, 229, 216))
                md = myDraw(blank)
                img_backgroud = Image.open(
                    await md.get_net_img(
                        valkyrie.character.avatar.avatar_background_path
                    )
                )
                img_backgroud = img_backgroud.resize((190, 153))
                blank.alpha_composite(img_backgroud, dest=(46, 15))
                img_avatar = Image.open(
                    await md.get_net_img(
                        valkyrie.character.avatar.half_length_icon_path
                    )
                ).resize((172, 148))
                blank.alpha_composite(img_avatar, dest=(61, 19))
                blank.alpha_composite(bg)
                img_star = Image.open(
                    ItemTrans.star(valkyrie.character.avatar.star)
                ).resize((64, 54))
                blank.alpha_composite(img_star, dest=(48, 148))
                weapon = valkyrie.character.weapon
                bg_weapon = Image.open(
                    os.path.join(
                        os.path.dirname(__file__),
                        f"../assets/equipment_{weapon.max_rarity}.png",
                    )
                ).resize((75, 75))
                blank.alpha_composite(bg_weapon, dest=(215, 126))
                img_weapon = Image.open(await md.get_net_img(weapon.icon)).resize(
                    (72, 63)
                )
                blank.alpha_composite(img_weapon, dest=(215, 132))
                img_star = md.ImgResize(myDraw.star(weapon), height=27)
                blank.alpha_composite(img_star, dest=(cal_dest(img_star, 253), 182))
                for n, sti in enumerate(valkyrie.character.stigmatas):
                    if sti.id == 0:
                        img_none = Image.open(
                            os.path.join(
                                os.path.dirname(__file__), "../assets/equipment_0.png"
                            )
                        ).resize((75, 75))
                        blank.alpha_composite(img_none, dest=(35 + 76 * n, 223))
                    else:
                        bg_sti = Image.open(
                            os.path.join(
                                os.path.dirname(__file__),
                                f"../assets/equipment_{sti.max_rarity}.png",
                            )
                        ).resize((75, 75))
                        blank.alpha_composite(bg_sti, dest=(35 + 76 * n, 223))
                        img_sti = Image.open(await md.get_net_img(sti.icon)).resize(
                            (75, 65)
                        )
                        blank.alpha_composite(img_sti, dest=(35 + 76 * n, 228))
                        img_star = md.ImgResize(myDraw.star(sti), height=29)
                        blank.alpha_composite(
                            img_star, dest=(cal_dest(img_star, 73 + 76 * n), 279)
                        )
                # font_lxj = ImageFont.truetype(os.path.join(os.path.dirname(
                # __file__), "assets/font/HYLingXinTiJ.ttf"), size=26)
                font_lxj = myDraw.get_font("l", 26)
                md.text(
                    xy=(149, 176),
                    text=f"Lv.{valkyrie.character.avatar.level}",
                    fill="black",
                    font=font_lxj,
                    anchor="mt",
                )
                col = math.floor(no / 3)
                row = no % 3
                card_chara.alpha_composite(blank, dest=(10 + 300 * row, 10 + 320 * col))
                blank.close()
        # card_chara.show()
        img_header = Image.open(
            os.path.join(os.path.dirname(__file__), "../assets/header.png")
        ).convert("RGBA")
        img_header = await myDraw.avatar(
            img_header, qid=qid, avatar_url=index.role.AvatarUrl, center=(460, 218)
        )
        dr = myDraw(img_header)
        dr.text(
            (900, 20),
            text=f"UID: {index.role.role_id}",
            fill="white",
            font=dr.get_font(size=30),
            anchor="rt",
        )
        dr.text(
            xy=(460, 460),
            text=index.role.nickname,
            fill=(0, 0, 0),
            font=dr.get_font("s", 40),
            anchor="mm",
        )
        dr.text(
            xy=(310, 552),
            text=str(index.role.level),
            fill=(133, 96, 61),
            font=dr.get_font(85, 40),
            anchor="lm",
        )
        dr.text(
            xy=(524, 552),
            text=ItemTrans.id2server(index.role.region),
            fill=(133, 96, 61),
            font=dr.get_font(85, 40),
            anchor="mm",
        )
        dr.text(
            xy=(368, 678),
            text=str(index.stats.armor_number),
            fill=(133, 96, 61),
            font=dr.get_font(85, 40),
            anchor="mm",
        )
        dr.text(
            xy=(842, 678),
            text=str(index.stats.sss_armor_number),
            fill=(133, 96, 61),
            font=dr.get_font(85, 40),
            anchor="mm",
        )
        with Image.new(
            "RGBA",
            (card_chara.size[0], card_chara.size[1] + img_header.size[1]),
            color=(236, 229, 216),
        ) as full_im:
            # im = await myDraw.avatar(full_im, qid=qid, avatar_url=index.role.AvatarUrl)
            full_im.alpha_composite(img_header)
            full_im.alpha_composite(card_chara, (0, img_header.size[1]))
            # im.show()
        return pic2b64(full_im, 100)


class DrawFinance(FinanceInfo):
    def draw(self) -> str:
        with Image.open(
            os.path.join(os.path.dirname(__file__), "../assets/finance.png")
        ) as finance_bg:
            # 本月
            index = self.index
            dr = myDraw(finance_bg)
            font_6536 = myDraw.get_font()
            dr.text(
                xy=(375, 80),
                text=f"UID:{index.uid}",
                fill="black",
                font=font_6536,
                anchor="mm",
            )
            dr.text(
                xy=(375, 164),
                text=f"舰长的{index.month}月手账",
                fill="black",
                font=font_6536,
                anchor="mm",
            )
            dr.text(
                xy=(375, 245),
                text=f"截止至{index.date}",
                fill="black",
                font=font_6536,
                anchor="mm",
            )
            dr.text(
                xy=(161, 435),
                text=f"{index.month_hcoin}",
                fill="black",
                font=font_6536,
                anchor="lm",
            )
            dr.text(
                xy=(510, 435),
                text=f"{index.month_star:,}",
                fill="black",
                font=font_6536,
                anchor="lm",
            )
            if index.day_hcoin != 0 or index.day_star != 0:
                dr.text(
                    xy=(375, 550),
                    text=f"舰长今日已经获取{index.day_hcoin}水晶,{index.day_star}星石.",
                    fill="black",
                    font=font_6536,
                    anchor="mm",
                )
            else:
                dr.text(
                    xy=(375, 550),
                    text=f"舰长今日还没有收入哦.",
                    fill="black",
                    font=font_6536,
                    anchor="mm",
                )
            # 上月
            lastmonth = self.getLastMonthInfo
            font_6524 = myDraw.get_font(size=24)
            dr.text(
                xy=(375, 747),
                text=f"舰长的{lastmonth.month}月手账",
                fill="black",
                font=font_6536,
                anchor="mm",
            )
            dr.text(
                xy=(375, 841),
                text=f"{lastmonth.month_start.date()}至{lastmonth.month_end.date()}",
                fill="black",
                font=font_6536,
                anchor="mm",
            )
            dr.text(
                xy=(135, 1189),
                text=f"{lastmonth.month_hcoin:,}",
                fill="black",
                font=font_6524,
                anchor="lm",
            )
            dr.text(
                xy=(403, 1189),
                text=f"{lastmonth.month_star:,}",
                fill="black",
                font=font_6524,
                anchor="lm",
            )
            data = []
            for n, src in enumerate(lastmonth.group_by):
                data.append(src.percent)
                dr.text(
                    xy=(400, 940 + n * 49),
                    text=f"{src.name}",
                    fill="black",
                    font=font_6524,
                    anchor="lm",
                )
                dr.text(
                    xy=(665, 940 + n * 49),
                    text=f"{src.percent}%",
                    fill="black",
                    font=font_6524,
                    anchor="rm",
                )
            ring = dr.ring(data)
            finance_bg.alpha_composite(ring, dest=(37, 861))
            return pic2b64(finance_bg)
