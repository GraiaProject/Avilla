from datetime import datetime
from typing import TYPE_CHECKING, Optional

from avilla.core.operator import OperatorCache
from avilla.core.selectors import mainline as mainline_selector
from avilla.core.utilles import Registrar
from avilla.core.utilles.operator import OperatorImplementDispatch
from avilla.onebot.interface import OnebotInterface
from avilla.onebot.utilles import raise_for_obresp

if TYPE_CHECKING:
    from avilla.onebot.operator import OnebotOperator

registrar = Registrar()


@registrar.decorate("patterns")
class OnebotOperatorDispatch(OperatorImplementDispatch):
    @staticmethod
    @registrar.register(("mainline.name", "get"))
    async def get_mainline_name(operator: "OnebotOperator", _, cache: OperatorCache = None):
        if cache:
            cached_value = await cache.get("mainline.name", None)
            print(f"cached_value: {cached_value}")
            if cached_value is not None:
                return cached_value
        if not operator.mainline:
            raise ValueError("context error: mainline missing")

        ob = operator.protocol.avilla.get_interface(OnebotInterface)
        resp = await ob.action(
            operator.account, "get_group_info", {"group_id": int(operator.mainline.path["group"])}
        )
        raise_for_obresp(resp)
        data = resp["data"]
        if cache:
            await cache.set("mainline.name", data["group_name"])
            if "member_count" in data:
                await cache.set("mainline.current_count", data["member_count"])
            if "max_member_count" in data:
                await cache.set("mainline.max_count", data["max_member_count"])
            if "group_memo" in data:
                await cache.set("mainline.description", data["group_memo"])
            if "group_create_time" in data:
                await cache.set("mainline.create_time", datetime.fromtimestamp(data["group_create_time"]))
        return data["group_name"]

    @staticmethod
    @registrar.register(("mainline.name", "set"))
    async def set_mainline_name(operator: "OnebotOperator", _, name: str, cache: OperatorCache = None):
        if cache:
            await cache.set("mainline.name", name)
        if not operator.mainline:
            raise ValueError("context error: mainline missing")
        ob = operator.protocol.avilla.get_interface(OnebotInterface)
        resp = await ob.action(
            operator.account,
            "set_group_name",
            {"group_id": int(operator.mainline.path["group"]), "group_name": name},
        )
        raise_for_obresp(resp)

    @staticmethod
    @registrar.register(("mainline.description", "get"))
    async def get_mainline_description(operator: "OnebotOperator", _, cache: OperatorCache = None):
        # Onebot 规范不支持 get_group_info 获取群组描述, 但 gocq 提供了 group_memo 字段。
        raise NotImplementedError

    @staticmethod
    @registrar.register(("mainline.description", "set"))
    async def set_mainline_description(
        operator: "OnebotOperator", _, description: str, cache: OperatorCache = None
    ):
        # Onebot 同样不支持设置群组描述， gocq 看起来也一样
        raise NotImplementedError

    @staticmethod
    @registrar.register(("mainline.current_count", "get"))
    async def get_mainline_current_count(operator: "OnebotOperator", _, cache: OperatorCache = None):
        if cache:
            cached_value = await cache.get("mainline.current_count", None)
            if cached_value is not None:
                return cached_value
        if not operator.mainline:
            raise ValueError("context error: mainline missing")

        ob = operator.protocol.avilla.get_interface(OnebotInterface)
        resp = await ob.action(
            operator.account, "get_group_info", {"group_id": int(operator.mainline.path["group"])}
        )
        raise_for_obresp(resp)
        data = resp["data"]
        if cache:
            await cache.set("mainline.current_count", data["member_count"])
            if "group_name" in data:
                await cache.set("mainline.name", data["group_name"])
            if "max_member_count" in data:
                await cache.set("mainline.max_count", data["max_member_count"])
            if "group_memo" in data:
                await cache.set("mainline.description", data["group_memo"])
            if "group_create_time" in data:
                await cache.set("mainline.create_time", datetime.fromtimestamp(data["group_create_time"]))
        return data["member_count"]

    @staticmethod
    @registrar.register(("mainline.max_count", "get"))
    async def get_mainline_max_count(operator: "OnebotOperator", _, cache: OperatorCache = None):
        if cache:
            cached_value = await cache.get("mainline.max_count", None)
            if cached_value is not None:
                return cached_value
        if not operator.mainline:
            raise ValueError("context error: mainline missing")

        ob = operator.protocol.avilla.get_interface(OnebotInterface)
        resp = await ob.action(
            operator.account, "get_group_info", {"group_id": int(operator.mainline.path["group"])}
        )
        raise_for_obresp(resp)
        data = resp["data"]
        if cache:
            await cache.set("mainline.max_count", data["max_member_count"])
            if "member_count" in data:
                await cache.set("mainline.current_count", data["member_count"])
            if "group_name" in data:
                await cache.set("mainline.name", data["group_name"])
            if "group_memo" in data:
                await cache.set("mainline.description", data["group_memo"])
            if "group_create_time" in data:
                await cache.set("mainline.create_time", datetime.fromtimestamp(data["group_create_time"]))
        return data["max_member_count"]

    @staticmethod
    @registrar.register(("member.name", "get"))
    async def get_member_name(operator: "OnebotOperator", _, cache: OperatorCache = None):
        if cache:
            cached_value = await cache.get("member.name", None)
            if cached_value is not None:
                return cached_value
        if not operator.ctx or "member" not in operator.ctx.path:
            raise ValueError("context error: member missing")
        if (
            "mainline" not in operator.ctx.path
            or not operator.mainline
            or "group" not in operator.mainline.path
        ):
            # 需要注意的是，后期可能有 channel for ob 支持，
            # 那时候就要通过判断 keypath 来知道用哪个接口了。
            # 因为 member 同样适用于 channel(channel.guild 也一样。)
            raise ValueError("context error: mainline missing")
        if "mainline" in operator.ctx.path:
            mainline: mainline_selector = operator.ctx.path["mainline"]
        elif operator.mainline:
            mainline = operator.mainline
        else:
            raise ValueError("context error: invalid mainline setting")
        ob = operator.protocol.avilla.get_interface(OnebotInterface)
        resp = await ob.action(
            operator.account,
            "get_group_member_info",
            {"group_id": int(mainline.path["group"]), "member_id": int(operator.ctx.path["member"])},
        )
        raise_for_obresp(resp)
        data = resp["data"]
        if cache:
            await cache.set("member.name", data["nickname"])
            await cache.set("member.nickname", data["card"])
            await cache.set("member.budget", data["title"])
            await cache.set("member.level", data["level"])
            await cache.set("member.joined_at", datetime.fromtimestamp(data["join_time"]))
            await cache.set("member.last_active_at", datetime.fromtimestamp(data["last_sent_time"]))
        return data["nickname"]

    @staticmethod
    @registrar.register(("member.nickname", "get"))
    async def get_member_nickname(operator: "OnebotOperator", _, cache: OperatorCache = None):
        if cache:
            cached_value = await cache.get("member.nickname", None)
            if cached_value is not None:
                return cached_value
        if not operator.ctx or "member" not in operator.ctx.path:
            raise ValueError("context error: member missing")
        if (
            "mainline" not in operator.ctx.path
            or not operator.mainline
            or "group" not in operator.mainline.path
        ):
            # 需要注意的是，后期可能有 channel for ob 支持，
            # 那时候就要通过判断 keypath 来知道用哪个接口了。
            # 因为 member 同样适用于 channel(channel.guild 也一样。)
            raise ValueError("context error: mainline missing")
        if "mainline" in operator.ctx.path:
            mainline: mainline_selector = operator.ctx.path["mainline"]
        elif operator.mainline:
            mainline = operator.mainline
        else:
            raise ValueError("context error: invalid mainline setting")
        ob = operator.protocol.avilla.get_interface(OnebotInterface)
        resp = await ob.action(
            operator.account,
            "get_group_member_info",
            {"group_id": int(mainline.path["group"]), "member_id": int(operator.ctx.path["member"])},
        )
        raise_for_obresp(resp)
        data = resp["data"]
        if cache:
            await cache.set("member.nickname", data["card"])
            await cache.set("member.name", data["nickname"])
            await cache.set("member.budget", data["title"])
            await cache.set("member.level", data["level"])
            await cache.set("member.joined_at", datetime.fromtimestamp(data["join_time"]))
            await cache.set("member.last_active_at", datetime.fromtimestamp(data["last_sent_time"]))
        return data["card"]

    @staticmethod
    @registrar.register(("member.nickname", "set"))
    async def set_member_nickname(operator: "OnebotOperator", value: str, cache: OperatorCache = None):
        if not operator.ctx or "member" not in operator.ctx.path:
            raise ValueError("context error: member missing")
        if (
            "mainline" not in operator.ctx.path
            or not operator.mainline
            or "group" not in operator.mainline.path
        ):
            # 需要注意的是，后期可能有 channel for ob 支持，
            # 那时候就要通过判断 keypath 来知道用哪个接口了。
            # 因为 member 同样适用于 channel(channel.guild 也一样。)
            raise ValueError("context error: mainline missing")
        if "mainline" in operator.ctx.path:
            mainline: mainline_selector = operator.ctx.path["mainline"]
        elif operator.mainline:
            mainline = operator.mainline
        else:
            raise ValueError("context error: invalid mainline setting")
        ob = operator.protocol.avilla.get_interface(OnebotInterface)
        resp = await ob.action(
            operator.account,
            "set_group_card",
            {
                "group_id": int(mainline.path["group"]),
                "member_id": int(operator.ctx.path["member"]),
                "card": value,
            },
        )
        raise_for_obresp(resp)
        return

    @staticmethod
    @registrar.register(("member.nickname", "reset"))
    async def reset_member_nickname(operator: "OnebotOperator", _, cache: OperatorCache = None):
        if not operator.ctx or "member" not in operator.ctx.path:
            raise ValueError("context error: member missing")
        if (
            "mainline" not in operator.ctx.path
            or not operator.mainline
            or "group" not in operator.mainline.path
        ):
            # 需要注意的是，后期可能有 channel for ob 支持，
            # 那时候就要通过判断 keypath 来知道用哪个接口了。
            # 因为 member 同样适用于 channel(channel.guild 也一样。)
            raise ValueError("context error: mainline missing")
        if "mainline" in operator.ctx.path:
            mainline: mainline_selector = operator.ctx.path["mainline"]
        elif operator.mainline:
            mainline = operator.mainline
        else:
            raise ValueError("context error: invalid mainline setting")
        ob = operator.protocol.avilla.get_interface(OnebotInterface)
        resp = await ob.action(
            operator.account,
            "set_group_card",
            {
                "group_id": int(mainline.path["group"]),
                "member_id": int(operator.ctx.path["member"]),
                "card": "",
            },
        )
        raise_for_obresp(resp)
        return

    @staticmethod
    @registrar.register(("member.budget", "get"))
    async def get_member_budget(operator: "OnebotOperator", _, cache: OperatorCache = None):
        if cache:
            cached_value = await cache.get("member.budget", None)
            if cached_value is not None:
                return cached_value
        if not operator.ctx or "member" not in operator.ctx.path:
            raise ValueError("context error: member missing")
        if (
            "mainline" not in operator.ctx.path
            or not operator.mainline
            or "group" not in operator.mainline.path
        ):
            # 需要注意的是，后期可能有 channel for ob 支持，
            # 那时候就要通过判断 keypath 来知道用哪个接口了。
            # 因为 member 同样适用于 channel(channel.guild 也一样。)
            raise ValueError("context error: mainline missing")
        if "mainline" in operator.ctx.path:
            mainline: mainline_selector = operator.ctx.path["mainline"]
        elif operator.mainline:
            mainline = operator.mainline
        else:
            raise ValueError("context error: invalid mainline setting")
        ob = operator.protocol.avilla.get_interface(OnebotInterface)
        resp = await ob.action(
            operator.account,
            "get_group_member_info",
            {"group_id": int(mainline.path["group"]), "member_id": int(operator.ctx.path["member"])},
        )
        raise_for_obresp(resp)
        data = resp["data"]
        if cache:
            await cache.set("member.budget", data["title"])
            await cache.set("member.name", data["nickname"])
            await cache.set("member.nickname", data["card"])
            await cache.set("member.level", data["level"])
            await cache.set("member.joined_at", datetime.fromtimestamp(data["join_time"]))
            await cache.set("member.last_active_at", datetime.fromtimestamp(data["last_sent_time"]))
        return data["title"]

    @staticmethod
    @registrar.register(("member.budget", "set"))
    async def set_member_budget(operator: "OnebotOperator", value: str, cache: OperatorCache = None):
        if cache:
            cached_value = await cache.get("member.budget", None)
            if cached_value is not None and cached_value == value:
                return
        if not operator.ctx or "member" not in operator.ctx.path:
            raise ValueError("context error: member missing")
        if (
            "mainline" not in operator.ctx.path
            or not operator.mainline
            or "group" not in operator.mainline.path
        ):
            # 需要注意的是，后期可能有 channel for ob 支持，
            # 那时候就要通过判断 keypath 来知道用哪个接口了。
            # 因为 member 同样适用于 channel(channel.guild 也一样。)
            raise ValueError("context error: mainline missing")
        if "mainline" in operator.ctx.path:
            mainline: mainline_selector = operator.ctx.path["mainline"]
        elif operator.mainline:
            mainline = operator.mainline
        else:
            raise ValueError("context error: invalid mainline setting")

        ob = operator.protocol.avilla.get_interface(OnebotInterface)
        resp = await ob.action(
            operator.account,
            "set_group_special_title",
            {
                "group_id": int(mainline.path["group"]),
                "user_id": int(operator.ctx.path["member"]),
                "title": value,
            },
        )
        raise_for_obresp(resp)

    @staticmethod
    @registrar.register(("member.budget", "reset"))
    async def reset_member_budget(operator: "OnebotOperator", _, cache: OperatorCache = None):
        if not operator.ctx or "member" not in operator.ctx.path:
            raise ValueError("context error: member missing")
        if (
            "mainline" not in operator.ctx.path
            or not operator.mainline
            or "group" not in operator.mainline.path
        ):
            # 需要注意的是，后期可能有 channel for ob 支持，
            # 那时候就要通过判断 keypath 来知道用哪个接口了。
            # 因为 member 同样适用于 channel(channel.guild 也一样。)
            raise ValueError("context error: mainline missing")
        if "mainline" in operator.ctx.path:
            mainline: mainline_selector = operator.ctx.path["mainline"]
        elif operator.mainline:
            mainline = operator.mainline
        else:
            raise ValueError("context error: invalid mainline setting")
        ob = operator.protocol.avilla.get_interface(OnebotInterface)
        resp = await ob.action(
            operator.account,
            "set_group_special_title",
            {
                "group_id": int(mainline.path["group"]),
                "user_id": int(operator.ctx.path["member"]),
                "title": "",
            },
        )
        raise_for_obresp(resp)
        return

    @staticmethod
    @registrar.register(("member.muted", "get"))
    async def get_member_muted(operator: "OnebotOperator", _, cache: OperatorCache = None):
        # Onebot 没有获取禁言状态的接口。
        raise NotImplementedError

    @staticmethod
    @registrar.register(("member.muted", "set"))
    async def set_member_muted(operator: "OnebotOperator", value: bool, cache: OperatorCache = None):
        # Onebot 没有禁言状态的接口。
        raise NotImplementedError

    @staticmethod
    @registrar.register(("member.mute_period", "get"))
    async def get_member_mute_period(operator: "OnebotOperator", _, cache: OperatorCache = None):
        # Onebot 没有获取禁言时间的接口。
        raise NotImplementedError

    @staticmethod
    @registrar.register(("member.joined_at", "get"))
    async def get_member_joined_at(operator: "OnebotOperator", _, cache: OperatorCache = None):
        if cache:
            cached_value = await cache.get("member.name", None)
            if cached_value is not None:
                return cached_value
        if not operator.ctx or "member" not in operator.ctx.path:
            raise ValueError("context error: member missing")
        if (
            "mainline" not in operator.ctx.path
            or not operator.mainline
            or "group" not in operator.mainline.path
        ):
            # 需要注意的是，后期可能有 channel for ob 支持，
            # 那时候就要通过判断 keypath 来知道用哪个接口了。
            # 因为 member 同样适用于 channel(channel.guild 也一样。)
            raise ValueError("context error: mainline missing")
        if "mainline" in operator.ctx.path:
            mainline: mainline_selector = operator.ctx.path["mainline"]
        elif operator.mainline:
            mainline = operator.mainline
        else:
            raise ValueError("context error: invalid mainline setting")
        ob = operator.protocol.avilla.get_interface(OnebotInterface)
        resp = await ob.action(
            operator.account,
            "get_group_member_info",
            {"group_id": int(mainline.path["group"]), "member_id": int(operator.ctx.path["member"])},
        )
        raise_for_obresp(resp)
        data = resp["data"]
        if cache:
            await cache.set("member.name", data["nickname"])
            await cache.set("member.nickname", data["card"])
            await cache.set("member.budget", data["title"])
            await cache.set("member.level", data["level"])
            await cache.set("member.joined_at", datetime.fromtimestamp(data["join_time"]))
            await cache.set("member.last_active_at", datetime.fromtimestamp(data["last_sent_time"]))
        return datetime.fromtimestamp(data["last_sent_time"])

    @staticmethod
    @registrar.register(("member.last_active_at", "get"))
    async def get_member_last_active_at(operator: "OnebotOperator", _, cache: OperatorCache = None):
        if cache:
            cached_value = await cache.get("member.name", None)
            if cached_value is not None:
                return cached_value
        if not operator.ctx or "member" not in operator.ctx.path:
            raise ValueError("context error: member missing")
        if (
            "mainline" not in operator.ctx.path
            or not operator.mainline
            or "group" not in operator.mainline.path
        ):
            # 需要注意的是，后期可能有 channel for ob 支持，
            # 那时候就要通过判断 keypath 来知道用哪个接口了。
            # 因为 member 同样适用于 channel(channel.guild 也一样。)
            raise ValueError("context error: mainline missing")
        if "mainline" in operator.ctx.path:
            mainline: mainline_selector = operator.ctx.path["mainline"]
        elif operator.mainline:
            mainline = operator.mainline
        else:
            raise ValueError("context error: invalid mainline setting")
        ob = operator.protocol.avilla.get_interface(OnebotInterface)
        resp = await ob.action(
            operator.account,
            "get_group_member_info",
            {"group_id": int(mainline.path["group"]), "member_id": int(operator.ctx.path["member"])},
        )
        raise_for_obresp(resp)
        data = resp["data"]
        if cache:
            await cache.set("member.name", data["nickname"])
            await cache.set("member.nickname", data["card"])
            await cache.set("member.budget", data["title"])
            await cache.set("member.level", data["level"])
            await cache.set("member.joined_at", datetime.fromtimestamp(data["join_time"]))
            await cache.set("member.last_active_at", datetime.fromtimestamp(data["last_sent_time"]))
        return datetime.fromtimestamp(data["last_sent_time"])

    @staticmethod
    @registrar.register(("contact.name", "get"))
    async def get_contact_name(operator: "OnebotOperator", _, cache: OperatorCache = None):
        if cache:
            cached_value = await cache.get("contact.name", None)
            if cached_value is not None:
                return cached_value
        if not operator.ctx:
            raise ValueError("context error: ctx missing")
        ctxtype, ctxid = operator.ctx.last()
        ob = operator.protocol.avilla.get_interface(OnebotInterface)
        if ctxtype == "friend":
            resp = await ob.action(operator.account, "get_friend_list", {})
            raise_for_obresp(resp)
            data = resp["data"]
            for f in data:
                if f["user_id"] == ctxid:
                    if cache:
                        await cache.set("contact.name", f["nickname"])
                        await cache.set("contact.nickname", f["remark"])
                    return f["nickname"]
            else:
                raise ValueError("context error: contact not found")
        elif ctxtype == "stranger":
            resp = await ob.action(operator.account, "get_stranger_info", {"user_id": int(ctxid)})
            raise_for_obresp(resp)
            data = resp["data"]
            if cache:
                await cache.set("contact.name", data["nickname"])
                await cache.set("contact.nickname", data["nickname"])
            return data["nickname"]

    @staticmethod
    @registrar.register(("contact.nickname", "get"))
    async def get_contact_nickname(operator: "OnebotOperator", _, cache: OperatorCache = None):
        if cache:
            cached_value = await cache.get("contact.nickname", None)
            if cached_value is not None:
                return cached_value
        if not operator.ctx:
            raise ValueError("context error: ctx missing")
        ctxtype, ctxid = operator.ctx.last()
        ob = operator.protocol.avilla.get_interface(OnebotInterface)
        if ctxtype == "friend":
            resp = await ob.action(operator.account, "get_friend_list", {})
            raise_for_obresp(resp)
            data = resp["data"]
            for f in data:
                if f["user_id"] == ctxid:
                    if cache:
                        await cache.set("contact.name", f["nickname"])
                        await cache.set("contact.nickname", f["remark"])
                    return f["remark"]
            else:
                raise ValueError("context error: contact not found")
        elif ctxtype == "stranger":
            resp = await ob.action(operator.account, "get_stranger_info", {"user_id": int(ctxid)})
            raise_for_obresp(resp)
            data = resp["data"]
            if cache:
                await cache.set("contact.name", data["nickname"])
                await cache.set("contact.nickname", data["nickname"])
            return data["nickname"]

    # TODO: request

    @staticmethod
    @registrar.register(("contact.avatar", "get"))
    async def get_contact_avatar(operator: "OnebotOperator", _, cache: OperatorCache = None):
        # TODO: contact avatar get
        raise NotImplementedError

    @staticmethod
    @registrar.register(("mainline.avatar", "get"))
    async def get_mainline_avatar(operator: "OnebotOperator", _, cache: OperatorCache = None):
        # TODO: mainline avatar get
        raise NotImplementedError

    @staticmethod
    @registrar.register(("member.avatar", "get"))
    async def get_member_avatar(operator: "OnebotOperator", _, cache: OperatorCache = None):
        # TODO: member avatar get
        raise NotImplementedError

    @staticmethod
    @registrar.register(("self.name", "get"))
    async def get_self_name(operator: "OnebotOperator", _, cache: OperatorCache = None):
        if cache:
            cached_value = await cache.get("self.name", None)
            if cached_value is not None:
                return cached_value
        if not operator.ctx:
            raise ValueError("context error: ctx missing")
        ob = operator.protocol.avilla.get_interface(OnebotInterface)
        resp = await ob.action(operator.account, "get_login_info", {})
        raise_for_obresp(resp)
        data = resp["data"]
        if cache:
            await cache.set("self.name", data["nickname"])
            # await cache.set("self.nickname", data['nickname'])
            # 这个有上下文（based on mainline)
        return data["nickname"]

    @staticmethod
    @registrar.register(("self.nickname", "get"))
    async def get_self_nickname(operator: "OnebotOperator", _, cache: OperatorCache = None):
        if cache:
            cached_value = await cache.get("self.nickname", None)
            if cached_value is not None:
                return cached_value
        if not operator.ctx:
            raise ValueError("context error: ctx missing")
        ob = operator.protocol.avilla.get_interface(OnebotInterface)
        # 我想想。。。如果是群这种有 card，就返回 card, 否则 fallback 到 get_login_info nickname
        mainline: Optional[mainline_selector] = None
        if "mainline" in operator.ctx.path:
            mainline = operator.ctx.path["mainline"]
        elif operator.mainline:
            mainline = operator.mainline
        if mainline:
            # 以后还得写 channel..
            # bryan & elaina: mdzz...
            resp = await ob.action(
                operator.account,
                "get_group_member_info",
                {"group_id": int(mainline.path["group"]), "user_id": int(operator.account.path["account"])},
            )
            raise_for_obresp(resp)
            data = resp["data"]
            if cache:
                await cache.set("self.name", data["nickname"])
                await cache.set("self.nickname", data["remark"])
            return data["remark"]
        else:
            resp = await ob.action(operator.account, "get_login_info", {})
            raise_for_obresp(resp)
            data = resp["data"]
            if cache:
                await cache.set("self.name", data["nickname"])
                await cache.set("self.nickname", data["nickname"])
            return data["nickname"]

    # TODO： 不搞了，太多了，以后再说吧。
    #     ： 唔。。。self，request，channel, etc, 我反正麻了。。。
