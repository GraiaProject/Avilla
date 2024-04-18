from __future__ import annotations

from typing import Literal

from avilla.core import Selector
from avilla.core.resource import Resource


class TelegramResource(Resource[bytes]):
    fild_id: str
    file_unique_id: str
    file_size: int | None

    def __init__(self, selector: Selector, file_id: str, file_unique_id: str, file_size: int | None = None):
        super().__init__(selector)
        self.file_id = file_id
        self.file_unique_id = file_unique_id
        self.file_size = file_size


class TelegramFileResource(TelegramResource):
    file_path: str | None

    def __init__(
        self,
        selector: Selector,
        file_id: str,
        file_unique_id: str,
        file_size: int | None = None,
        file_path: str | None = None,
    ):
        super().__init__(selector, file_id, file_unique_id, file_size=file_size)
        self.file_path = file_path


class TelegramPhotoResource(TelegramResource):
    width: int
    height: int

    def __init__(
        self,
        selector: Selector,
        file_id: str,
        file_unique_id: str,
        width: int,
        height: int,
        file_size: int | None = None,
    ):
        super().__init__(selector, file_id, file_unique_id, file_size=file_size)
        self.width = width
        self.height = height


class TelegramAnimationResource(TelegramResource):
    width: int
    height: int
    duration: int
    thumbnail: TelegramPhotoResource | None
    file_name: str | None
    mime_type: str | None

    def __init__(
        self,
        selector: Selector,
        file_id: str,
        file_unique_id: str,
        width: int,
        height: int,
        duration: int,
        thumbnail: TelegramPhotoResource | None = None,
        file_name: str | None = None,
        mime_type: str | None = None,
        file_size: int | None = None,
    ):
        super().__init__(selector, file_id, file_unique_id, file_size=file_size)
        self.width = width
        self.height = height
        self.duration = duration
        self.thumbnail = thumbnail
        self.file_name = file_name
        self.mime_type = mime_type


class TelegramAudioResource(TelegramResource):
    duration: int
    performer: str | None
    title: str | None
    file_name: str | None
    mime_type: str | None
    thumbnail: TelegramPhotoResource | None

    def __init__(
        self,
        selector: Selector,
        file_id: str,
        file_unique_id: str,
        duration: int,
        performer: str | None = None,
        title: str | None = None,
        file_name: str | None = None,
        mime_type: str | None = None,
        file_size: int | None = None,
        thumbnail: TelegramPhotoResource | None = None,
    ):
        super().__init__(selector, file_id, file_unique_id, file_size=file_size)
        self.duration = duration
        self.performer = performer
        self.title = title
        self.file_name = file_name
        self.mime_type = mime_type
        self.thumbnail = thumbnail


class TelegramDocumentResource(TelegramResource):
    thumbnail: TelegramPhotoResource | None
    file_name: str | None
    mime_type: str | None

    def __init__(
        self,
        selector: Selector,
        file_id: str,
        file_unique_id: str,
        thumbnail: TelegramPhotoResource | None = None,
        file_name: str | None = None,
        mime_type: str | None = None,
        file_size: int | None = None,
    ):
        super().__init__(selector, file_id, file_unique_id, file_size=file_size)
        self.thumbnail = thumbnail
        self.file_name = file_name
        self.mime_type = mime_type


class TelegramVideoResource(TelegramResource):
    width: int
    height: int
    duration: int
    thumbnail: TelegramPhotoResource | None
    file_name: str | None
    mime_type: str | None

    def __init__(
        self,
        selector: Selector,
        file_id: str,
        file_unique_id: str,
        width: int,
        height: int,
        duration: int,
        thumbnail: TelegramPhotoResource | None = None,
        file_name: str | None = None,
        mime_type: str | None = None,
        file_size: int | None = None,
    ):
        super().__init__(selector, file_id, file_unique_id, file_size=file_size)
        self.width = width
        self.height = height
        self.duration = duration
        self.thumbnail = thumbnail
        self.file_name = file_name
        self.mime_type = mime_type


class TelegramVideoNoteResource(TelegramResource):
    length: int
    duration: int
    thumbnail: TelegramPhotoResource | None

    def __init__(
        self,
        selector: Selector,
        file_id: str,
        file_unique_id: str,
        length: int,
        duration: int,
        thumbnail: TelegramPhotoResource | None = None,
        file_size: int | None = None,
    ):
        super().__init__(selector, file_id, file_unique_id, file_size=file_size)
        self.length = length
        self.duration = duration
        self.thumbnail = thumbnail


class TelegramVoiceResource(TelegramResource):
    duration: int
    mime_type: str | None

    def __init__(
        self,
        selector: Selector,
        file_id: str,
        file_unique_id: str,
        duration: int,
        mime_type: str | None = None,
        file_size: int | None = None,
    ):
        super().__init__(selector, file_id, file_unique_id, file_size=file_size)
        self.duration = duration
        self.mime_type = mime_type


class TelegramStickerResource(TelegramResource):
    type: Literal["sticker", "mask", "custom_emoji"]
    width: int
    height: int
    is_animated: bool
    is_video: bool
    thumb: TelegramPhotoResource | None
    emoji: str | None
    set_name: str | None
    premium_animation: TelegramFileResource | None
    mask_position: dict | None
    custom_emoji_id: str | None
    need_repainting: Literal[True] | None

    def __init__(
        self,
        selector: Selector,
        file_id: str,
        file_unique_id: str,
        type: Literal["sticker", "mask", "custom_emoji"],  # noqa
        width: int,
        height: int,
        is_animated: bool,
        is_video: bool,
        thumb: TelegramPhotoResource | None = None,
        emoji: str | None = None,
        set_name: str | None = None,
        premium_animation: TelegramFileResource | None = None,
        mask_position: dict | None = None,
        custom_emoji_id: str | None = None,
        need_repainting: Literal[True] | None = None,
        file_size: int | None = None,
    ):
        super().__init__(selector, file_id, file_unique_id, file_size=file_size)
        self.type = type
        self.width = width
        self.height = height
        self.is_animated = is_animated
        self.is_video = is_video
        self.thumb = thumb
        self.emoji = emoji
        self.set_name = set_name
        self.premium_animation = premium_animation
        self.mask_position = mask_position
        self.custom_emoji_id = custom_emoji_id
        self.need_repainting = need_repainting
