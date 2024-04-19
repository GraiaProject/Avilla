from __future__ import annotations

from typing import TYPE_CHECKING

from graia.amnesia.message import Element, Text

from avilla.core import Audio, File, Selector
from avilla.core.ryanvk.collector.application import ApplicationCollector
from avilla.standard.telegram.elements import (
    Animation,
    Picture,
    Sticker,
    Video,
    VideoNote,
)
from avilla.telegram.capability import TelegramCapability
from avilla.telegram.resource import (
    TelegramAnimationResource,
    TelegramAudioResource,
    TelegramDocumentResource,
    TelegramFileResource,
    TelegramPhotoResource,
    TelegramStickerResource,
    TelegramVideoNoteResource,
    TelegramVideoResource,
    TelegramVoiceResource,
)
from graia.ryanvk import OptionalAccess

if TYPE_CHECKING:
    from avilla.core.context import Context
    from avilla.telegram.account import TelegramAccount


class TelegramMessageDeserializePerform((m := ApplicationCollector())._):
    m.namespace = "avilla.protocol/telegram::message"
    m.identify = "deserialize"

    context: OptionalAccess[Context] = OptionalAccess()
    account: OptionalAccess[TelegramAccount] = OptionalAccess()

    # LINK: https://github.com/microsoft/pyright/issues/5409

    @m.entity(TelegramCapability.deserialize_element, raw_element="text")
    async def text(self, raw_element: dict) -> list[Element]:
        return [Text(raw_element["text"])]

    @staticmethod
    async def extract_entities(text: str, entities: list[dict]) -> list[Element]:
        # See: https://core.telegram.org/api/entities#entity-length

        ignored_keys = {"type", "offset", "length"}
        result = []
        encoded = text.encode("utf-16be")
        remaining = encoded
        offset = 0
        for entity in entities:
            start = (entity["offset"] - offset) * 2
            end = (entity["offset"] - offset + entity["length"]) * 2
            if left := remaining[:start]:
                result.append(Text(left.decode("utf-16be")))
            text_entity = Text(remaining[start:end].decode("utf-16be"), style=entity["type"])
            for _k, _v in {k: v for k, v in entity.items() if k not in ignored_keys}.items():
                setattr(text_entity, _k, _v)
            result.append(text_entity)
            remaining = remaining[end:]
            offset = entity["offset"] + entity["length"]
        if remaining:
            result.append(Text(remaining.decode("utf-16be")))
        return result

    @m.entity(TelegramCapability.deserialize_element, raw_element="entities")
    async def entities(self, raw_element: dict) -> list[Element]:
        return await self.extract_entities(raw_element["text"], raw_element["entities"])

    @m.entity(TelegramCapability.deserialize_element, raw_element="caption")
    async def caption(self, raw_element: dict) -> list[Element]:
        result: list[Element] = []
        caption: str = raw_element.popitem()[-1]
        result.extend(await TelegramCapability(self.staff).deserialize_element(raw_element))
        result.append(Text(caption))
        return result

    @m.entity(TelegramCapability.deserialize_element, raw_element="caption_entities")
    async def caption_entities(self, raw_element: dict) -> list[Element]:
        result: list[Element] = []
        entities: list[dict] = raw_element.popitem()[-1]
        caption: str = raw_element.popitem()[-1]
        result.extend(await TelegramCapability(self.staff).deserialize_element(raw_element))
        result.extend(await self.extract_entities(caption, entities))
        return result

    @m.entity(TelegramCapability.deserialize_element, raw_element="photo")
    async def photo(self, raw_element: dict) -> list[Element]:
        photo: dict = raw_element["photo"][-1]
        file_id: str = photo["file_id"]
        file_unique_id: str = photo["file_unique_id"]

        assert self.context
        selector = Selector().land(self.context.land).file_id(file_id).file_unique_id(file_unique_id)

        return [
            Picture(
                TelegramPhotoResource(
                    selector=selector,
                    file_id=file_id,
                    file_unique_id=file_unique_id,
                    width=photo["width"],
                    height=photo["height"],
                    file_size=photo.get("file_size"),
                ),
                has_spoiler=photo.get("has_media_spoiler", False),
            )
        ]

    def _thumb_resource(self, thumbnail: dict | None) -> TelegramPhotoResource | None:
        if not thumbnail:
            return None
        file_id: str = thumbnail["file_id"]
        file_unique_id: str = thumbnail["file_unique_id"]

        assert self.context
        selector = Selector().land(self.context.land).file_id(file_id).file_unique_id(file_unique_id)

        return TelegramPhotoResource(
            selector=selector,
            file_id=file_id,
            file_unique_id=file_unique_id,
            width=thumbnail["width"],
            height=thumbnail["height"],
            file_size=thumbnail.get("file_size"),
        )

    @m.entity(TelegramCapability.deserialize_element, raw_element="animation")
    async def animation(self, raw_element: dict) -> list[Element]:
        animation: dict = raw_element["animation"]
        file_id: str = animation["file_id"]
        file_unique_id: str = animation["file_unique_id"]

        assert self.context
        selector = Selector().land(self.context.land).file_id(file_id).file_unique_id(file_unique_id)
        thumbnail = self._thumb_resource(animation.get("thumb"))

        return [
            Animation(
                TelegramAnimationResource(
                    selector=selector,
                    file_id=file_id,
                    file_unique_id=file_unique_id,
                    width=animation["width"],
                    height=animation["height"],
                    duration=animation["duration"],
                    thumbnail=thumbnail,
                    file_name=animation.get("file_name"),
                    mime_type=animation.get("mime_type"),
                    file_size=animation.get("file_size"),
                )
            )
        ]

    @m.entity(TelegramCapability.deserialize_element, raw_element="audio")
    async def audio(self, raw_element: dict) -> list[Element]:
        audio: dict = raw_element["audio"]
        file_id: str = audio["file_id"]
        file_unique_id: str = audio["file_unique_id"]

        assert self.context
        selector = Selector().land(self.context.land).file_id(file_id).file_unique_id(file_unique_id)
        thumbnail = self._thumb_resource(audio.get("thumb"))

        return [
            File(
                TelegramAudioResource(
                    selector=selector,
                    file_id=file_id,
                    file_unique_id=file_unique_id,
                    duration=audio["duration"],
                    performer=audio.get("performer"),
                    title=audio.get("title"),
                    file_name=audio.get("file_name"),
                    mime_type=audio.get("mime_type"),
                    file_size=audio.get("file_size"),
                    thumbnail=thumbnail,
                ),
            )
        ]

    @m.entity(TelegramCapability.deserialize_element, raw_element="doucument")
    async def document(self, raw_element: dict) -> list[Element]:
        document: dict = raw_element["document"]
        file_id: str = document["file_id"]
        file_unique_id: str = document["file_unique_id"]

        assert self.context
        selector = Selector().land(self.context.land).file_id(file_id).file_unique_id(file_unique_id)
        thumbnail = self._thumb_resource(document.get("thumb"))

        return [
            File(
                TelegramDocumentResource(
                    selector=selector,
                    file_id=file_id,
                    file_unique_id=file_unique_id,
                    file_name=document["file_name"],
                    mime_type=document["mime_type"],
                    file_size=document.get("file_size"),
                    thumbnail=thumbnail,
                )
            )
        ]

    @m.entity(TelegramCapability.deserialize_element, raw_element="video")
    async def video(self, raw_element: dict) -> list[Element]:
        video: dict = raw_element["video"]
        file_id: str = video["file_id"]
        file_unique_id: str = video["file_unique_id"]

        assert self.context
        selector = Selector().land(self.context.land).file_id(file_id).file_unique_id(file_unique_id)
        thumbnail = self._thumb_resource(video.get("thumb"))

        return [
            Video(
                TelegramVideoResource(
                    selector=selector,
                    file_id=file_id,
                    file_unique_id=file_unique_id,
                    width=video["width"],
                    height=video["height"],
                    duration=video["duration"],
                    thumbnail=thumbnail,
                    file_name=video.get("file_name"),
                    mime_type=video.get("mime_type"),
                    file_size=video.get("file_size"),
                ),
                has_spoiler=video.get("has_media_spoiler", False),
            )
        ]

    @m.entity(TelegramCapability.deserialize_element, raw_element="video_note")
    async def video_note(self, raw_element: dict) -> list[Element]:
        video_note: dict = raw_element["video_note"]
        file_id: str = video_note["file_id"]
        file_unique_id: str = video_note["file_unique_id"]

        assert self.context
        selector = Selector().land(self.context.land).file_id(file_id).file_unique_id(file_unique_id)
        thumbnail = self._thumb_resource(video_note.get("thumb"))

        return [
            VideoNote(
                TelegramVideoNoteResource(
                    selector=selector,
                    file_id=file_id,
                    file_unique_id=file_unique_id,
                    length=video_note["length"],
                    duration=video_note["duration"],
                    thumbnail=thumbnail,
                    file_size=video_note.get("file_size"),
                ),
            )
        ]

    @m.entity(TelegramCapability.deserialize_element, raw_element="voice")
    async def voice(self, raw_element: dict) -> list[Element]:
        voice: dict = raw_element["voice"]
        file_id: str = voice["file_id"]
        file_unique_id: str = voice["file_unique_id"]

        assert self.context
        selector = Selector().land(self.context.land).file_id(file_id).file_unique_id(file_unique_id)

        return [
            Audio(
                TelegramVoiceResource(
                    selector=selector,
                    file_id=file_id,
                    file_unique_id=file_unique_id,
                    duration=voice["duration"],
                    mime_type=voice.get("mime_type"),
                    file_size=voice.get("file_size"),
                ),
                duration=voice["duration"],
            )
        ]

    @m.entity(TelegramCapability.deserialize_element, raw_element="sticker")
    async def sticker(self, raw_element: dict) -> list[Element]:
        sticker: dict = raw_element["sticker"]
        file_id: str = sticker["file_id"]
        file_unique_id: str = sticker["file_unique_id"]

        assert self.context
        selector = Selector().land(self.context.land).file_id(file_id).file_unique_id(file_unique_id)
        thumbnail = self._thumb_resource(sticker.get("thumb"))

        if premium_animation := sticker.get("premium_animation"):
            premium_animation_file_id: str = premium_animation["file_id"]
            premium_animation_file_unique_id: str = premium_animation["file_unique_id"]
            premium_animation_selector = (
                Selector()
                .land(self.context.land)
                .file_id(premium_animation_file_id)
                .file_unique_id(premium_animation_file_unique_id)
            )
            premium_animation_resource = TelegramFileResource(
                selector=premium_animation_selector,
                file_id=premium_animation_file_id,
                file_unique_id=premium_animation_file_unique_id,
                file_size=premium_animation.get("file_size"),
                file_path=premium_animation.get("file_path"),
            )
        else:
            premium_animation_resource = None

        return [
            Sticker(
                TelegramStickerResource(
                    selector=selector,
                    file_id=file_id,
                    file_unique_id=file_unique_id,
                    type=sticker["type"],
                    width=sticker["width"],
                    height=sticker["height"],
                    is_animated=sticker["is_animated"],
                    is_video=sticker["is_video"],
                    thumb=thumbnail,
                    emoji=sticker.get("emoji"),
                    set_name=sticker.get("set_name"),
                    premium_animation=premium_animation_resource,
                    mask_position=sticker.get("mask_position"),
                    custom_emoji_id=sticker.get("custom_emoji_id"),
                    need_repainting=sticker.get("need_repainting"),
                    file_size=sticker.get("file_size"),
                ),
            )
        ]
