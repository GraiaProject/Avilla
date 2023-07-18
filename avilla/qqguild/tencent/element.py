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
    template_id: int
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
