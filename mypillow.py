from io import BytesIO
import requests
import re
import os
from httpx import AsyncClient
from typing import List,Tuple
from PIL import ImageDraw, Image, ImageChops, ImageFont
from math import sin,cos,pi
class myDraw(ImageDraw.ImageDraw):
    def __init__(self,im) -> None:
        super().__init__(im)
    @classmethod
    async def avatar(cls, bg: Image.Image, qid: str = None, avatar_url: str = None, center: Tuple[int, int] = [562, 267]):
        """头像"""
        qava_url = "http://q1.qlogo.cn/g?b=qq&nk={qid}&s=140"
        if avatar_url is not None:
            try:
                no = re.search(r'\d{3,}',avatar_url).group()
            except:
                no = re.search(r"[a-zA-Z]{1,}\d{2}",avatar_url).group()
            a_url = avatar_url.split(no)[0] + no + '.png'
        else:
            a_url = qava_url.format(qid=qid)
        pic_data = await cls._GetNetPic(url=a_url)
        with Image.open(os.path.join(os.path.dirname(__file__),"assets/404.png")) as img_404:
            if ImageChops.difference(img_404,Image.open(pic_data)).getbbox() is None:
                pic_data = await cls._GetNetPic(url=qava_url.format(qid=qid))
        with Image.open(pic_data) as pic:
            pic = cls.ImgResize(pic,256/pic.width).convert("RGBA")
            with Image.new(mode="RGBA",size=bg.size,color="#ece5d8") as im:
                im.alpha_composite(pic, dest=(
                    int(center[0]-0.5*pic.width), int(center[1]-0.5*pic.height)))
                im.alpha_composite(bg)
                return im
    @staticmethod
    def get_font(font: str = "65", size: int = 36):
        font = str(font)
        font_path_65 = os.path.join(os.path.dirname(
            __file__), f"assets/font/HYWenHei-65W.ttf")
        font_path_85 = os.path.join(os.path.dirname(
            __file__), f"assets/font/HYWenHei-85W.ttf")
        font_path_sara = os.path.join(os.path.dirname(
            __file__), f"assets/font/sarasa-ui-sc-semibold.ttf")   # hywh缺字
        if font == '65':
            font_path = font_path_65
        elif font == '85':
            font_path = font_path_85
        elif font == 's':
            font_path = font_path_sara
        return ImageFont.truetype(font_path, size)

    @staticmethod
    def radar(origin_image:Image.Image,data:List[float],center:Tuple[float,float],radius:float):
        """雷达图,求出各点坐标,调用ImageDraw.polygon"""
        # origin_image = bg
        # 新建工作图片
        im = Image.new("RGBA",size=origin_image.size,color=(255,255,255,0))
        dr = ImageDraw.Draw(im)
        zero_x,zero_y = center
        sides = len(data)
        angel = 2*pi / sides
        angles = [angel*n for n in range(sides)]
        hypotenuse = [n*radius/100 for n in data]
        coordinates = []
        for i,hy in enumerate(hypotenuse):
            x = zero_x + hy*sin(angles[i])
            y = zero_y - hy*cos(angles[i])
            coordinates.append((x,y))
        dr.polygon(xy=coordinates,fill=(0,192,255,190))
        size = 4
        for point in coordinates:
            x,y=point
            dr.ellipse(xy=(x-size,y-size,x+size,y+size),fill="white",outline=(0,192,255))
        # 粘贴到目标图片
        origin_image.alpha_composite(im)
        return origin_image
    @staticmethod
    async def _GetNetPic(url:str):
        if url.startswith("http://q1.qlogo.cn/"):
            async with AsyncClient() as aiorequests:
                resp = await aiorequests.get(url)
                return BytesIO(await resp.content)
        image_type,img_name = url.split("/")[-2:]
        ASSETS_PATH = os.path.join(os.path.dirname(__file__),'assets')
        image_type_path = os.path.join(ASSETS_PATH,image_type)
        if not os.path.exists(image_type_path):
            os.makedirs(image_type_path)
        else:
            ex_image = os.listdir(image_type_path)
            if img_name in ex_image:
                return os.path.join(image_type_path,img_name)
        async with AsyncClient() as aiorequests:
            resp = await aiorequests.get(url)
        data = resp.content
        with open(os.path.join(image_type_path,img_name),mode="wb") as im:
            im.write(data)
            im.close()
        return BytesIO(data)
    @staticmethod
    def ImgResize(im:Image.Image,coe:float=None,weight:int=None,height:int=None):
        """等比例缩放"""
        if coe is not None:
            return im.resize((int(length * coe) for length in im.size) )
        elif weight is not None:
            coe = weight/im.size[0]
            return im.resize((int(weight),int(im.size[1]*coe)))
        elif height is not None:
            coe = height/im.size[1]
            return im.resize((int(im.size[0]*coe),int(height)))
    @staticmethod
    def ring(data: Tuple[int], radius: int = 120):
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