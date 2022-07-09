from __future__ import annotations

from typing import TYPE_CHECKING

from graia.amnesia.message.element import Text

from avilla.core.elements import Audio, Image, Notice, NoticeAll
from avilla.core.utilles.message_deserializer import MessageDeserializer, deserializer
from avilla.core.utilles.selector import Selector
from avilla.elizabeth.element import FlashImage
from avilla.elizabeth.resource import ElizabethAudioResource, ElizabethImageResource

if TYPE_CHECKING:
    from .protocol import ElizabethProtocol

class ElizabethMessageDeserializer(MessageDeserializer["ElizabethProtocol"]):
    def get_element_type(self, raw: dict) -> str:
        return raw['type']
    
    @deserializer("Plain")
    def plain(self, protocol: "ElizabethProtocol", raw: dict):
        return Text(raw['text'])
    
    @deserializer("At")
    def at(self, protocol: "ElizabethProtocol", raw: dict):
        return Notice(Selector().contact(raw['target']))  # 请使用 rs.complete.
    
    @deserializer("AtAll")
    def at_all(self, protocol: "ElizabethProtocol", raw: dict):
        return NoticeAll()
    
    @deserializer("Image")
    def image(self, protocol: "ElizabethProtocol", raw: dict):
        # mainline 后续修饰
        return Image(ElizabethImageResource(
            raw['imageId'], raw['url'], raw['path'], raw['base64']
        ))
    
    @deserializer("FlashImage")
    def flash_image(self, protocol: "ElizabethProtocol", raw: dict):
        return FlashImage(ElizabethImageResource(
            raw['imageId'], raw['url'], raw['path'], raw['base64']
        ))
    
    @deserializer("Voice")
    def voice(self, protocol: "ElizabethProtocol", raw: dict):
        return Audio(ElizabethAudioResource(
            raw['voiceId'], raw['url'], raw['path'], raw['base64'], raw['length']
        ))

    # TODO: 更多的消息元素支持