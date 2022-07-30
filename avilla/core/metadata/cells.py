from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from .model import Metadata, meta_field


class Count(Metadata):
    current: int = meta_field("count.current")
    max: int | None = meta_field("count.max")


class Summary(Metadata):
    name: str = meta_field("summary.name")
    description: str | None = meta_field("summary.description")


class MuteInfo(Metadata):
    muted: bool = meta_field("mute.muted")
    duration: timedelta = meta_field("mute.duration")


class BanInfo(Metadata):
    banned: bool = meta_field("ban.banned")
    duration: timedelta = meta_field("ban.duration")


class Privilege(Metadata):
    available: bool = meta_field("privilege.available")
    effective: bool = meta_field("privilege.effective")


class Nick(Metadata):
    name: str = meta_field("nick.name")
    nickname: str = meta_field("nick.nickname")
    badge: str | None = meta_field("nick.badge")


class Reason(Metadata):
    content: str = meta_field("reason")


class Comment(Metadata):
    content: str = meta_field("comment")


@dataclass
class QuestionItem:
    id: str
    content: str


class Questions(Metadata):
    items: list[QuestionItem] = meta_field("questions")


@dataclass
class AnswerItem:
    id: str
    content: str


class Answers(Metadata):
    items: list[AnswerItem] = meta_field("answers")
