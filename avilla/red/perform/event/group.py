from __future__ import annotations

from loguru import logger

from avilla.core.context import Context
from avilla.core.event import MetadataModified, ModifyDetail
from avilla.core.selector import Selector
from avilla.red.capability import RedCapability
from avilla.red.collector.connection import ConnectionCollector
from avilla.standard.core.profile import Summary


class RedEventGroupPerform((m := ConnectionCollector())._):
    m.namespace = "avilla.protocol/red::event"
    m.identify = "group"


    @m.entity(RedCapability.event_callback, event_type="group::name_update")
    async def group_name_change(self, event_type: ..., raw_event: dict):
        account = self.connection.account
        if account is None:
            logger.warning(f"Unknown account received message {raw_event}")
            return
        group = Selector().land(account.route["land"]).group(str(raw_event.get("peerUin", raw_event.get("peerUid"))))
        group_data = raw_event["elements"][0]["grayTipElement"]["groupElement"]
        operator = group.member(str(group_data["memberUin"]))
        context = Context(
            account,
            operator,
            group,
            group,
            group.member(account.route["account"]),
        )
        return MetadataModified(
            context,
            group,
            Summary,
            {Summary.inh(lambda x: x.name): ModifyDetail("update", group_data["groupName"], "")},
            operator=operator,
            scene=group,
        )


_ = {
    "msgId": "7273401197226772043",
    "msgRandom": "7198583817760031691",
    "msgSeq": "6288",
    "cntSeq": "0",
    "chatType": 2,
    "msgType": 5,
    "subMsgType": 8,
    "sendType": 3,
    "senderUid": "",
    "peerUid": "592387986",
    "channelId": "",
    "guildId": "",
    "guildCode": "0",
    "fromUid": "0",
    "fromAppid": "0",
    "msgTime": "1693470682",
    "msgMeta": "0x",
    "sendStatus": 2,
    "sendMemberName": "",
    "sendNickName": "",
    "guildName": "",
    "channelName": "",
    "elements": [
        {
            "elementType": 8,
            "elementId": "7273401197226772044",
            "extBufForUI": "0x",
            "textElement": None,
            "faceElement": None,
            "marketFaceElement": None,
            "replyElement": None,
            "picElement": None,
            "pttElement": None,
            "videoElement": None,
            "grayTipElement": {
                "subElementType": 4,
                "revokeElement": None,
                "proclamationElement": None,
                "emojiReplyElement": None,
                "groupElement": {
                    "type": 5,
                    "role": 2,
                    "groupName": "虚无遗境",
                    "memberUid": "u_ZLOOr1URIwoiy98-sw6eew",
                    "memberNick": "不知道问RF",
                    "memberRemark": "",
                    "adminUid": "",
                    "adminNick": "",
                    "adminRemark": "",
                    "createGroup": None,
                    "memberAdd": None,
                    "shutUp": None,
                    "memberUin": "3165388245",
                    "adminUin": "516689493",
                },
                "buddyElement": None,
                "feedMsgElement": None,
                "essenceElement": None,
                "groupNotifyElement": None,
                "buddyNotifyElement": None,
                "xmlElement": None,
                "fileReceiptElement": None,
                "localGrayTipElement": None,
                "blockGrayTipElement": None,
                "aioOpGrayTipElement": None,
                "jsonGrayTipElement": None,
            },
            "arkElement": None,
            "fileElement": None,
            "liveGiftElement": None,
            "markdownElement": None,
            "structLongMsgElement": None,
            "multiForwardMsgElement": None,
            "giphyElement": None,
            "walletElement": None,
            "inlineKeyboardElement": None,
            "textGiftElement": None,
            "calendarElement": None,
            "yoloGameResultElement": None,
            "avRecordElement": None,
        }
    ],
    "records": [],
    "emojiLikesList": [],
    "commentCnt": "0",
    "directMsgFlag": 0,
    "directMsgMembers": [],
    "peerName": "",
    "freqLimitInfo": None,
    "editable": False,
    "avatarMeta": "",
    "avatarPendant": "",
    "feedId": "",
    "roleId": "0",
    "timeStamp": "0",
    "clientIdentityInfo": None,
    "isImportMsg": False,
    "atType": 0,
    "fromChannelRoleInfo": {"roleId": "0", "name": "", "color": 0},
    "fromGuildRoleInfo": {"roleId": "0", "name": "", "color": 0},
    "levelRoleInfo": {"roleId": "0", "name": "", "color": 0},
    "recallTime": "0",
    "isOnlineMsg": False,
    "generalFlags": "0x",
    "clientSeq": "0",
    "fileGroupSize": None,
    "foldingInfo": None,
    "nameType": 0,
    "avatarFlag": 0,
    "anonymousExtInfo": None,
    "personalMedal": None,
    "roleManagementTag": None,
    "senderUin": "516689493",
    "peerUin": "592387986",
}
