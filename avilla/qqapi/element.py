from __future__ import annotations

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
    custom_template_id: int | None = None
    params: dict[str, list[str]] | None = None

    def __str__(self):
        return "[$Markdown]"

    def __repr__(self):
        return f"[$Markdown:content={self.content}]"


@dataclass
class ActionPermission:
    type: int
    specify_role_ids: list[str] | None = None
    specify_user_ids: list[str] | None = None


@dataclass
class Action:
    type: int
    data: str
    permission: ActionPermission = field(default_factory=lambda: ActionPermission(0))
    reply: bool | None = None
    enter: bool | None = None
    anchor: bool | None = None
    click_limit: int | None = None
    unsupport_tips: str = "该版本暂不支持查看此消息，请升级至最新版本。"


@dataclass
class RenderData:
    label: str
    visited_label: str
    style: int


@dataclass
class Button:
    render_data: RenderData
    action: Action
    id: str | None = None


@dataclass
class Keyboard(Element):
    id: str | None = None
    content: list[list[Button]] | None = None

    def __str__(self):
        return "[$Keyboard]"

    def __repr__(self):
        return f"[$Keyboard:id={self.id};content={self.content}]"
