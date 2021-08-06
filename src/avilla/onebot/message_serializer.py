import base64

from avilla.builtins.elements import (Image, Notice, NoticeAll, PlainText,
                                      Video, Voice)
from avilla.onebot.elements import (Anonymous, CustomMusicShare, Dice, Face,
                                    FlashImage, FriendRecommend,
                                    GroupRecommend, JsonMessage, Location,
                                    MusicShare, Poke, Rps, Shake, Share,
                                    XmlMessage)
from avilla.utilles.message import MessageSerializeBus

onebot_msg_serializer = MessageSerializeBus()


@onebot_msg_serializer.register(PlainText)
async def _plaintext_serializer(element: PlainText):
    return {"type": "text", "data": {"text": element.text}}


@onebot_msg_serializer.register(Image)
async def _image_serializer(element: Image):
    return {
        "type": "image",
        "data": {"file": f"base64://{base64.b64encode(await element.provider()).decode('utf-8')}"},
    }


@onebot_msg_serializer.register(Voice)
async def _voice_serializer(element: Voice):
    return {
        "type": "record",
        "data": {"file": f"base64://{base64.b64encode(await element.provider()).decode('utf-8')}"},
    }


@onebot_msg_serializer.register(Notice)
async def _notice_serializer(element: Notice):
    return {"type": "at", "data": {"qq": int(element.target)}}


@onebot_msg_serializer.register(NoticeAll)
async def _noticeall_serializer(_: NoticeAll):
    return {"type": "at", "data": {"qq": "all"}}


@onebot_msg_serializer.register(Video)
async def _video_serializer(element: Video):
    return {
        "type": "video",
        "data": {"file": f"base64://{base64.b64encode(await element.provider()).decode('utf-8')}"},
    }


@onebot_msg_serializer.register(FlashImage)
async def _flashimage_serializer(element: FlashImage):
    return {
        "type": "image",
        "data": {
            "type": "flash",
            "file": f"base64://{base64.b64encode(await element.provider()).decode('utf-8')}",
        },
    }


@onebot_msg_serializer.register(Face)
async def _face_serializer(element: Face):
    return {"type": "face", "data": {"id": element.id}}


@onebot_msg_serializer.register(Rps)
async def _rps_serializer(_: Rps):
    return {"type": "rps", "data": {}}


@onebot_msg_serializer.register(Dice)
async def _dice_serializer(_: Dice):
    return {"type": "dice", "data": {}}


@onebot_msg_serializer.register(Shake)
async def _shake_serializer(_: Shake):
    return {"type": "shake", "data": {}}


@onebot_msg_serializer.register(Poke)
async def _poke_serializer(element: Poke):
    return {
        "type": "poke",
        "data": {
            "type": element.type,
            "id": element.id,
        },
    }


@onebot_msg_serializer.register(Anonymous)
async def _anonymous_serializer(_: Anonymous):
    return {"type": "anonymous", "data": {}}


@onebot_msg_serializer.register(Share)
async def _share_serializer(element: Share):
    return {
        "type": "share",
        "data": {
            "url": element.url,
            "title": element.title,
            "content": element.content,
            "image": element.image,
        },
    }


@onebot_msg_serializer.register(FriendRecommend)
async def _friendrecommend_serializer(element: FriendRecommend):
    return {"type": "contact", "data": {"type": "qq", "id": element.id}}


@onebot_msg_serializer.register(GroupRecommend)
async def _grouprecommend_serializer(element: GroupRecommend):
    return {"type": "contact", "data": {"type": "group", "id": element.id}}


@onebot_msg_serializer.register(Location)
async def _location_serializer(element: Location):
    return {
        "type": "location",
        "data": {
            "lat": element.lat,
            "lon": element.lon,
            "title": element.title,
            "content": element.content,
        },
    }


@onebot_msg_serializer.register(MusicShare)
async def _musicshare_serializer(element: MusicShare):
    return {"type": "music", "data": {"type": element.type, "id": element.id}}


@onebot_msg_serializer.register(CustomMusicShare)
async def _custommusicshare_serializer(element: CustomMusicShare):
    return {
        "type": "music",
        "data": {
            "type": "custom",
            "url": element.url,
            "audio": element.audio,
            "title": element.title,
            "content": element.content,
            "image": element.image,
        },
    }


@onebot_msg_serializer.register(XmlMessage)
async def _xmlmessage_serializer(element: XmlMessage):
    return {"type": "xml", "data": {"xml": element.xml}}


@onebot_msg_serializer.register(JsonMessage)
async def _jsonmessage_serializer(element: JsonMessage):
    return {"type": "json", "data": {"json": element.json}}
