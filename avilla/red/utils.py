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
    itemType == 6
    faceInfo == 1
    emojiPackageId
    subType == 3
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
