from __future__ import annotations

from satori.model import (
    ArgvInteraction,
    ButtonInteraction,
    Channel,
    Event,
    Guild,
    Login,
    Member,
    MessageObject,
    Role,
    User,
)


class MessageEvent(Event):
    channel: Channel
    member: Member
    message: MessageObject
    user: User


class DirectEvent(Event):
    user: User


class GuildEvent(Event):
    guild: Guild


class GuildMemberEvent(Event):
    guild: Guild
    user: User
    member: Member


class GuildRoleEvent(Event):
    guild: Guild
    role: Role


class LoginEvent(Event):
    login: Login


class ReactionEvent(Event):
    channel: Channel
    user: User
    message: MessageObject


class ButtonInteractionEvent(Event):
    button: ButtonInteraction
    user: User
    channel: Channel


class CommandInteractionEvent(Event):
    message: MessageObject
    user: User
    channel: Channel


class ArgvInteractionEvent(Event):
    argv: ArgvInteraction
    user: User
    channel: Channel
