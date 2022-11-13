from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from ..abstract.metadata import Metadata


@dataclass
class Count(Metadata):
    current: int
    max: int


@dataclass
class Summary(Metadata):
    name: str
    description: str | None


@dataclass
class MuteInfo(Metadata):
    muted: bool
    duration: timedelta


@dataclass
class BanInfo(Metadata):
    banned: bool
    duration: timedelta


@dataclass
class Privilege(Metadata):
    available: bool
    effective: bool


@dataclass
class Nick(Metadata):
    name: str
    nickname: str
    badge: str | None


@dataclass
class Reason(Metadata):
    content: str


@dataclass
class Comment(Metadata):
    content: str


@dataclass
class QuestionItem:
    id: str
    content: str


@dataclass
class Questions(Metadata):
    items: list[QuestionItem]


@dataclass
class AnswerItem:
    id: str
    content: str


@dataclass
class Answers(Metadata):
    items: list[AnswerItem]
