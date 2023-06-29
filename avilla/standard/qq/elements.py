from __future__ import annotations

import json
from enum import Enum

from avilla.core.elements import Picture
from avilla.core.selector import Selector
from graia.amnesia.message.element import Element


class FlashImage(Picture):
    def __str__(self) -> str:
        return "[$FlashImage]"

    def __repr__(self) -> str:
        return f"[$FlashImage:resource={self.resource.to_selector()}]"


class Face(Element):
    fid: Selector  # id + name

    def __init__(self, fid: Selector) -> None:
        self.fid = fid

    def __str__(self) -> str:
        return f"[$Face:id={self.fid}]"


class MarketFace(Element):
    fid: Selector  # id + name

    def __init__(self, fid: Selector) -> None:
        self.fid = fid

    def __str__(self) -> str:
        return f"[$MarketFace:id={self.fid}]"


class Xml(Element):
    content: str

    def __init__(self, content: str) -> None:
        self.content = content

    def __str__(self) -> str:
        return "[Xml]"


class App(Element):
    content: str

    @classmethod
    def dump(cls, content: dict):
        return cls(json.dumps(content))

    def __init__(self, content: str) -> None:
        self.content = content

    def load(self):
        return json.loads(self.content)

    def __str__(self) -> str:
        return "[$App]"


class Json(Element):
    content: str

    @classmethod
    def dump(cls, content: dict):
        return cls(json.dumps(content))

    def __init__(self, content: str) -> None:
        self.content = content

    def load(self):
        return json.loads(self.content)

    def __str__(self) -> str:
        return "[Json]"


class PokeMethods(str, Enum):
    """戳一戳可用方法"""

    ChuoYiChuo = "ChuoYiChuo"
    """戳一戳"""

    BiXin = "BiXin"
    """比心"""

    DianZan = "DianZan"
    """点赞"""

    XinSui = "XinSui"
    """心碎"""

    LiuLiuLiu = "LiuLiuLiu"
    """666"""

    FangDaZhao = "FangDaZhao"
    """放大招"""

    BaoBeiQiu = "BaoBeiQiu"
    """宝贝球"""

    Rose = "Rose"
    """玫瑰花"""

    ZhaoHuanShu = "ZhaoHuanShu"
    """召唤术"""

    RangNiPi = "RangNiPi"
    """让你皮"""

    JeiYin = "JeiYin"
    """结印"""

    ShouLei = "ShouLei"
    """手雷"""

    GouYin = "GouYin"
    """勾引"""

    ZhuaYiXia = "ZhuaYiXia"
    """抓一下"""

    SuiPing = "SuiPing"
    """碎屏"""

    QiaoMen = "QiaoMen"
    """敲门"""

    Unknown = "Unknown"
    """未知戳一戳"""

    @classmethod
    def _missing_(cls, _) -> "PokeMethods":
        return PokeMethods.Unknown


class Poke(Element):
    name: PokeMethods

    def __init__(self, name: PokeMethods) -> None:
        self.name = name

    def __str__(self) -> str:
        return f"[$Poke:{self.name}]"


# TODO: other qq elements
