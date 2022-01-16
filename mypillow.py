from io import BytesIO
import requests
import re
import os
from typing import List,Tuple
from PIL import ImageDraw,Image,ImageChops
from math import sin,cos,pi
class myDraw(ImageDraw.ImageDraw):
    def __init__(self,im) -> None:
        super().__init__(im)
    @classmethod
    def avatar(cls,bg:Image.Image,qid:str=None,avatar_url:str=None):
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
        pic_data = cls._GetNetPic(url=a_url)
        with Image.open(os.path.join(os.path.dirname(__file__),"assets/404.png")) as img_404:
            if ImageChops.difference(img_404,Image.open(pic_data)).getbbox() is None:
                pic_data = cls._GetNetPic(url=qava_url.format(qid=qid))
        with Image.open(pic_data) as pic:
            pic = cls.ImgResize(pic,256/pic.width).convert("RGBA")
            with Image.new(mode="RGBA",size=bg.size,color="#ece5d8") as im:
                im.alpha_composite(pic,dest=(int(562-0.5*pic.width),int(267-0.5*pic.height)))
                im.alpha_composite(bg)
                return im
    def endpoint(self,xy:Tuple[float,float]):
        """端点"""
        size = 3
        x,y=xy
        self.ellipse(xy=(x-size,y-size,x+size,y+size),fill="white",outline=(0,192,255))
        pass
    def radar(self,data:List[float],center:Tuple[float,float],radius:float):
        """雷达图,求出各点坐标,调用ImageDraw.polygon"""
        origin_image = self._image
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
    @staticmethod
    def _GetNetPic(url:str):
        if url.startswith("http://q1.qlogo.cn/"):
            return BytesIO(requests.get(url).content)
        image_type,img_name = url.split("/")[-2:]
        ASSETS_PATH = os.path.join(os.path.dirname(__file__),'assets')
        image_type_path = os.path.join(ASSETS_PATH,image_type)
        if not os.path.exists(image_type_path):
            os.makedirs(image_type_path)
        else:
            ex_image = os.listdir(image_type_path)
            if img_name in ex_image:
                return os.path.join(image_type_path,img_name)
        
        data = requests.get(url).content
        with open(os.path.join(image_type_path,img_name),mode="wb") as im:
            im.write(data)
            im.close()
        return BytesIO(data)
    @staticmethod
    def ImgResize(im:Image.Image,coe:float):
        """等比例缩放"""
        return im.resize((int(length * coe) for length in im.size) )
    
