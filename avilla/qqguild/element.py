from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict

from avilla.core.elements import Element


class EmbedThumbnail(TypedDict):
    url: str


class EmbedField(TypedDict):
    name: str


@dataclass
class Embed(Element):
    title: str | None = None
    prompt: str | None = None
    thumbnail: EmbedThumbnail | None = None
    fields: list[EmbedField] | None = None

    def __str__(self):
        return "[$Embed]"

    def __repr__(self):
        return f"[$Embed:title={self.title};prompt={self.prompt};thumbnail={self.thumbnail};fields={self.fields}]"


class ArkObjKv(TypedDict):
    key: str
    value: str


class ArkObj(TypedDict):
    obj_kv: list[ArkObjKv]


@dataclass
class ArkKv:
    key: str
    value: str | None = None
    obj: list[ArkObj] | None = None


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
    ignore_get_message_error: bool | None = None

    def __str__(self):
        return "[$Reference:id={self.message_id}]"

    def __repr__(self):
        return f"[$Reference:id={self.message_id};ignore_error={self.ignore_get_message_error}]"
