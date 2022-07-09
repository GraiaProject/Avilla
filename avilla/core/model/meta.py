from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.metadata.model import Metadata, meta_field

if TYPE_CHECKING:
    from datetime import datetime, timedelta

    from avilla.core.relationship import Relationship
    from avilla.core.resource import Resource


class Mainline(Metadata):
    name: str = meta_field("mainline.name")
    description: str = meta_field("mainline.description")
    avatar: Resource = meta_field("mainline.avatar")
    max_count: int | None = meta_field("mainline.max_count")
    current_count: int | None = meta_field("mainline.current_count")

    @classmethod
    def get_default_target(cls, relationship: Relationship):
        return relationship.mainline


class Contact(Metadata):
    name: str = meta_field("contact.name")
    nickname: str = meta_field("contact.nickname")
    avatar: Resource = meta_field("contact.avatar")

    @classmethod
    def get_default_target(cls, relationship: Relationship):
        return relationship.current


class Member(Contact, Metadata):
    budget: str = meta_field("member.budget")
    muted: bool = meta_field("member.muted")
    mute_period: timedelta | None = meta_field("self.mute_period")
    grade: int = meta_field("member.grade")
    grade_name: str = meta_field("member.grade_name")
    joined_at: datetime | None = meta_field("member.joined_at")
    last_active_at: datetime | None = meta_field("member.last_active_at")

    @classmethod
    def get_default_target(cls, relationship: Relationship):
        return relationship.ctx


class Request(Metadata):
    has_question: bool = meta_field("request.has_question")

    comment: str | None = meta_field("request.comment")
    reason: str | None = meta_field("request.reason")
    questions: dict[int, str] | None = meta_field("request.questions")
    answers: dict[int, str] | None = meta_field("request.answers")

    @property
    def qa(self) -> dict[str, str] | None:
        if self.questions is None or self.answers is None:
            return None
        return {question: self.answers[index] for index, question in self.questions.items()}

    @classmethod
    def get_default_target(cls, relationship: Relationship):
        return relationship.ctx


class Self(Contact, Metadata):
    muted: bool = meta_field("self.muted")
    mute_period: timedelta | None = meta_field("self.mute_period")
    grade: int | None = meta_field("self.grade")
    grade_name: str | None = meta_field("self.grade_name")
    budget: str = meta_field("self.budget")
    joined_at: datetime | None = meta_field("self.joined_at")
    last_active_at: datetime | None = meta_field("self.last_active_at")

    @classmethod
    def get_default_target(cls, relationship: Relationship):
        return relationship.current
