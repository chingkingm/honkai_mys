"""生成图片"""
import os
import json
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
        return level[no]
    @staticmethod
    def new_abyss(no):
        """超弦空间"""
        level = ["禁忌","原罪Ⅰ","原罪Ⅱ","原罪Ⅲ","苦痛Ⅰ","苦痛Ⅱ","苦痛Ⅲ","红莲","寂灭"]
        return level[no]
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
    def server(no:str):
        """渠道代码"""
        with open(os.path.join(os.path.dirname(__file__),f"/region.json"),'r',encoding='utf8') as f:
            region = json.load(f)
            f.close()
        for server_id,alias in region.items():
            if no in alias:
                return server_id
        raise KeyError(f"找不到服务器{no}的数据")