from __future__ import annotations

from enum import IntEnum
from dataclasses import dataclass, field

from avilla.core.elements import Element
from avilla.core.elements import Reference as _Reference


@dataclass
class Embed(Element):
    title: str
    prompt: str | None = None
    thumbnail: str | None = None
    fields: list[str] | None = None

    def __str__(self):
        return "[$Embed]"

    def __repr__(self):
        return f"[$Embed:title={self.title};prompt={self.prompt};thumbnail={self.thumbnail};fields={self.fields}]"


@dataclass
class ArkKv:
    key: str
    value: str | None = None
    obj: list[dict] | None = None


@dataclass
class Ark(Element):
    template_id: int | None = None
    kv: list[ArkKv] | None = None

    def __str__(self):
        return "[$Ark]"

    def __repr__(self):
        return f"[$Ark:template_id={self.template_id};kv={self.kv}]"


@dataclass
class Reference(_Reference):
    ignore_get_message_error: bool = False

    def __repr__(self):
        return f"[$Reference:id={self.message};ignore_error={self.ignore_get_message_error}]"


@dataclass
class Markdown(Element):
    content: str | None = None
    custom_template_id: str | None = None
    params: dict[str, list[str]] | None = None

    def __str__(self):
        return "[$Markdown]"

    def __repr__(self):
        return f"[$Markdown:content={self.content}]"


class ActionPermissionType(IntEnum):
    USER = 0
    ADMIN = 1
    ALL = 2
    ROLE = 3


@dataclass
class ActionPermission:
    type: int | ActionPermissionType
    """操作权限类型
    
    - 0 指定用户可操作
    - 1 仅管理者可操作
    - 2 所有人可操作
    - 3 指定身份组可操作（仅频道可用）
    """
    specify_role_ids: list[str] | None = None
    """有权限的用户 id 的列表"""
    specify_user_ids: list[str] | None = None
    """有权限的身份组 id 的列表（仅频道可用）"""


class ActionType(IntEnum):
    REDIRECT = 0
    CALLBACK = 1
    COMMAND = 2


@dataclass
class Action:
    type: int | ActionType
    """按钮操作类型
    
    - 设置 0 跳转按钮：http 或 小程序 客户端识别 scheme
    - 设置 1 回调按钮：回调后台接口, data 传给后台
    - 设置 2 指令按钮：自动在输入框插入 @bot data
    """
    data: str
    """操作相关的数据"""
    permission: ActionPermission = field(default_factory=lambda: ActionPermission(2))
    """操作权限"""
    reply: bool = False
    """指令按钮可用，指令是否带引用回复本消息，默认 false"""
    enter: bool = False
    """指令按钮可用，点击按钮后直接自动发送 data，默认 false"""
    anchor: int = 0
    """本字段仅在指令按钮下有效，设置后后会忽略 action.enter 配置。设置为 1 时 ，点击按钮自动唤起启手Q选图器，其他值暂无效果。"""
    unsupport_tips: str = "该版本暂不支持查看此消息，请升级至最新版本。"
    """客户端不支持本action的时候，弹出的toast文案"""


class ButtonStyle(IntEnum):
    GREY = 0
    BLUE = 1


@dataclass
class RenderData:
    label: str
    """按钮上的文字"""
    visited_label: str
    """点击后按钮上的文字"""
    style: int | ButtonStyle
    """按钮样式：0 灰色线框，1 蓝色线框"""


@dataclass
class Button:
    render_data: RenderData
    """按钮显示"""
    action: Action
    """按钮操作"""
    id: str | None = None
    """按钮ID：在一个keyboard消息内设置唯一"""


@dataclass
class Keyboard(Element):
    id: str | None = None
    """模板id"""
    content: list[list[Button]] | None = None
    """自定义内容"""

    def __str__(self):
        return "[$Keyboard]"

    def __repr__(self):
        return f"[$Keyboard:id={self.id};content={self.content}]"
