from typing import List,Tuple
from PIL import ImageDraw,Image
from math import sin,cos,pi
class myDraw(ImageDraw.ImageDraw):
    def __init__(self,im) -> None:
        super().__init__(im)

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
        size = 3
        for point in coordinates:
            x,y=point
            dr.ellipse(xy=(x-size,y-size,x+size,y+size),fill="white",outline=(0,192,255))
        # 粘贴到目标图片
        origin_image.paste(im,mask=im.split()[3])