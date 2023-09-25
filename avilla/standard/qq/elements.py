from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from avilla.core.elements import Picture
from avilla.core.selector import Selector
from graia.amnesia.message import MessageChain
from graia.amnesia.message.element import Element


class FlashImage(Picture):
    def __str__(self) -> str:
        return "[$FlashImage]"

    def __repr__(self) -> str:
        return f"[$FlashImage:resource={self.resource.to_selector()}]"


@dataclass
class MarketFace(Element):
    id: str
    name: str | None = None

    def __str__(self) -> str:
        return f"[$MarketFace:id={self.id};name={self.name}]"


class Xml(Element):
    content: str

    def __init__(self, content: str) -> None:
        self.content = content

    def __str__(self) -> str:
        return "[$Xml]"


class App(Element):
    content: str

    @classmethod
    def dump(cls, content: dict):
        return cls(json.dumps(content, ensure_ascii=False))

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
        return cls(json.dumps(content, ensure_ascii=False))

    def __init__(self, content: str) -> None:
        self.content = content

    def load(self):
        return json.loads(self.content)

    def __str__(self) -> str:
        return "[$Json]"


class PokeKind(str, Enum):
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
    def _missing_(cls, _) -> "PokeKind":
        return PokeKind.Unknown


class Poke(Element):
    """戳一戳 (或称窗口抖动)

    请与 头像双击动作(Nudge) 区分
    """

    kind: PokeKind

    def __init__(self, kind: PokeKind = PokeKind.Unknown) -> None:
        self.kind = kind

    def __str__(self) -> str:
        return f"[$Poke:kind={self.kind}]"


@dataclass
class Dice(Element):
    value: int | None = None

    def __str__(self) -> str:
        return f"[$Dice:value={self.value}]"


class MusicShareKind(str, Enum):
    """音乐分享的来源。"""

    NeteaseCloudMusic = "NeteaseCloudMusic"
    """网易云音乐"""

    QQMusic = "QQMusic"
    """QQ音乐"""

    MiguMusic = "MiguMusic"
    """咪咕音乐"""

    KugouMusic = "KugouMusic"
    """酷狗音乐"""

    KuwoMusic = "KuwoMusic"
    """酷我音乐"""


@dataclass
class MusicShare(Element):
    """表示消息中音乐分享消息元素"""

    kind: MusicShareKind
    """音乐分享的来源"""

    title: str | None = None
    """音乐卡片标题"""

    content: str | None = None
    """音乐摘要"""

    url: str | None = None
    """点击卡片跳转的链接"""

    thumbnail: str | None = None
    """音乐图片链接"""

    audio: str | None = None
    """音乐链接"""

    brief: str | None = None
    """音乐简介"""

    def __str__(self) -> str:
        return f"[$MusicShare:title={self.title}]"

    def __repr__(self) -> str:
        return f"[$MusicShare:kind={self.kind};title={self.title};url={self.url}"


class GiftKind(int, Enum):
    """礼物的类型"""

    SweetWink = 0
    """甜 Wink"""

    Cocacola = 1
    """快乐肥宅水"""

    LuckyBracelet = 2
    """幸运手链"""

    Cappuccino = 3
    """卡布奇诺"""

    CatWatch = 4
    """猫咪手表"""

    FluffyGloves = 5
    """绒绒手套"""

    RainbowCandy = 6
    """彩虹糖果"""

    Strong = 7
    """坚强"""

    ConfessionMicrophone = 8
    """告白话筒"""

    HoldYourHand = 9
    """牵你的手"""

    CuteCat = 10
    """可爱猫咪"""

    MysteriousMask = 11
    """神秘面具"""

    Busy = 12
    """我超忙的"""

    LoveMask = 13
    """爱心口罩"""

    @classmethod
    def _missing_(cls, _) -> "GiftKind":
        return GiftKind.SweetWink


@dataclass
class Gift(Element):
    """表示免费礼物的消息元素"""

    kind: GiftKind
    target: Selector

    def __str__(self) -> str:
        return f"[Gift:kind={self.kind};target={self.target}]"


@dataclass
class Share(Element):
    """表示分享链接的消息元素"""

    url: str
    """分享链接的 URL"""

    title: str
    """分享链接的标题"""

    content: str | None = None
    """分享链接的内容描述"""

    thumbnail: str | None = None
    """分享链接的缩略图 URL"""

    def __str__(self) -> str:
        return f"[$Share:title={self.title}]"

    def __repr__(self) -> str:
        return f"[$Share:title={self.title};url={self.url}]"


@dataclass
class Node(Element):
    """表示转发消息的节点消息元素"""

    mid: Selector | None = None
    name: str | None = None
    uid: str | None = None
    time: datetime = field(default_factory=datetime.now)
    content: MessageChain | None = None

    def __str__(self) -> str:
        return f"[$Node:id={self.mid}]" if self.mid else f"[$Node:content={self.content}]"


@dataclass
class DisplayStrategy:
    title: str | None = None
    """卡片顶部标题"""
    brief: str | None = None
    """消息列表预览"""
    source: str | None = None
    """未知"""
    preview: list[str] | None = None
    """卡片消息预览 (只显示前 4 条)"""
    summary: str | None = None
    """卡片底部摘要"""


@dataclass
class Forward(Element):
    """表示转发消息的消息元素"""

    id: Selector | None = None
    nodes: list[Node] = field(default_factory=list)
    strategy: DisplayStrategy | None = None

    def __str__(self) -> str:
        return f"[$Forward:id={self.id}]"


# TODO: other qq elements
