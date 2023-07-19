from __future__ import annotations

from dataclasses import dataclass

from avilla.core.metadata import Metadata


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
