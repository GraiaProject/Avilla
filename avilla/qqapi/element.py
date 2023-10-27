from __future__ import annotations

from dataclasses import dataclass

from avilla.core.elements import Element


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
class Reference(Element):
    message_id: str
    ignore_get_message_error: bool = False

    def __str__(self):
        return "[$Reference:id={self.message_id}]"

    def __repr__(self):
        return f"[$Reference:id={self.message_id};ignore_error={self.ignore_get_message_error}]"


@dataclass
class Markdown(Element):
    template_id: int | None = None
    content: str | None = None
    custom_template_id: int | None = None
    params: dict[str, list[str]] | None = None

    def __str__(self):
        return "[$Markdown]"

    def __repr__(self):
        return f"[$Markdown:content={self.content}]"


@dataclass
class ActionPermission:
    type: int | None = None
    specify_role_ids: list[str] | None = None
    specify_user_ids: list[str] | None = None


@dataclass
class Action:
    type: int | None = None
    permission: ActionPermission | None = None
    click_limit: int | None = None
    unsupport_tips: str | None = None
    data: str | None = None
    at_bot_show_channel_list: bool | None = None


@dataclass
class RenderData:
    label: str | None = None
    visited_label: str | None = None
    style: int | None = None


@dataclass
class Button:
    id: str | None = None
    render_data: RenderData | None = None
    action: Action | None = None


@dataclass
class Keyboard(Element):
    id: str | None = None
    content: list[list[Button]] | None = None

    def __str__(self):
        return "[$Keyboard]"

    def __repr__(self):
        return f"[$Keyboard:id={self.id};content={self.content}]"
