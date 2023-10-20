from dataclasses import dataclass
from enum import IntEnum
from typing import Literal, TypedDict


class MsgType(IntEnum):
    normal = 2
    may_file = 3
    system = 5
    voice = 6
    video = 7
    value8 = 8
    reply = 9
    wallet = 10
    ark = 11
    may_market = 17


class SubMsgTypes(TypedDict):
    text: bool
    image: bool
    face: bool
    link: bool
    forward: bool
    reply: bool
    market_face: bool
    file: bool


@dataclass
class MsgTypes:
    chat: Literal["friend", "group"]
    msg: MsgType
    sub: SubMsgTypes
    send: Literal["system", "normal"]

    @property
    def group(self):
        return self.chat == "group"


def pre_deserialize(elements: list[dict]):
    res = []
    for elem in elements:
        slot = {}
        data = {k: v for k, v in elem.items() if v is not None}
        for k, v in data.items():
            if k.endswith("Element"):
                slot["type"] = k[:-7]
                slot.update(v)
            elif k != "elementType":
                slot[k] = v
        res.append(slot)
    return res


def get_msg_types(raw_event: dict) -> MsgTypes:
    return MsgTypes(
        **{
            "chat": "friend" if raw_event["chatType"] == 1 else "group",
            "msg": MsgType(raw_event["msgType"]),
            "sub": {
                "text": bool(raw_event["subMsgType"] & (1 << 0)),
                "image": bool(raw_event["subMsgType"] & (1 << 1)),
                "face": bool(raw_event["subMsgType"] & (1 << 4)),
                "link": bool(raw_event["subMsgType"] & (1 << 7)),
                "forward": bool(raw_event["subMsgType"] & (1 << 3)),
                "reply": (raw_event["msgType"] == 9 and bool(raw_event["subMsgType"] & (1 << 5))),
                "market_face": (raw_event["msgType"] == 17 and bool(raw_event["subMsgType"] & (1 << 3))),
                "file": (raw_event["msgType"] == 3 and bool(raw_event["subMsgType"] & (1 << 9))),
            },
            "send": "system" if raw_event["sendType"] == 3 else "normal",
        }
    )


"""\
1 ===> text, at, ...
    content
    atType {0: not At, 1: everyone, 2: someone (atNtUid, atNtUin)}
2 ===> image(pic)
    fileName
    md5HexStr
    sourcePath
    fileUuid
    fileSubId
    picSubType {0: normal image (summary = ''), 1: emoji (summary = '[动画表情]')}
3 ===> file
    fileMd5
    fileName
    fileSize
    fileUuid
4 ===> voice(ptt)
    fileName
    filePath
    md5HexStr
    voiceChangeType {0: normal, 1: magic}
    canConvert2Text
        text
    waveAmplitudes
    fileUuid
5 ===> video
    filePath
    fileName
    videoMd5
    thumbMd5
    fileTime
    thumbSize
    fileFormat
    fileSize
    thumbWidth
    thumbHeight
    busiType
    subBusiType
    thumbPath
    transferStatus
    progress
    invalidState
    fileUuid
    fileSubId
    fileBizId
6 ===> face, poke
    faceIndex
    faceText {None: normal, '/xxx': sticker, '': poke}
    faceType {1: normal, 2: normal-extended, 3: sticker, 5: poke}
    packId {None: other, '1': sticker}
    stickerId {None: other, 'xxx': sticker}
    sourceType {None: other, 1: sticker}
    stickerType {None: other, 1: sticker}
    randomType {None: other, 1: sticker}
    pokeType {None: other, xxx: poke}
    spokeSummary {None: other, '': poke}
    doubleHit {None: other, xxx: poke}
    vaspokeId {None: other, xxx: poke}
    vaspokeName {None: other, 'xxx': poke}
7 ===> reply
    replayMsgId
    replayMsgSeq
    replyMsgTime
    sourceMsgIdInRecords
    sourceMsgTextElems
    senderUid
    senderUidStr
    senderUin
8 ==> grayTip
10 ===> app(ark) # 小程序，公告什么的
    bytesData (application/json)
11 ===> marketFace
    itemType
    faceInfo
    emojiPackageId
    subType
    faceName
    emojiId
    key
    staticFacePath
    dynamicFacePath
16 ===> multiForwardMsg
    xmlContent
    resId
    fileName
"""
