from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from . import Cell


@dataclass
class Count(Cell):
    current: int
    max: int


@dataclass
class Summary(Cell):
    name: str
    description: str | None


@dataclass
class MuteInfo(Cell):
    muted: bool
    duration: timedelta


@dataclass
class BanInfo(Cell):
    banned: bool
    duration: timedelta


@dataclass
class Privilege(Cell):
    available: bool
    effective: bool


@dataclass
class Nick(Cell):
    name: str
    nickname: str
    badge: str | None


@dataclass
class Reason(Cell):
    content: str


@dataclass
class Comment(Cell):
    content: str


@dataclass
class QuestionItem:
    id: str
    content: str


@dataclass
class Questions(Cell):
    items: list[QuestionItem]


@dataclass
class AnswerItem:
    id: str
    content: str


@dataclass
class Answers(Cell):
    items: list[AnswerItem]
