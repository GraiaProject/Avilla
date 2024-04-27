from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from graia.amnesia.builtins.memcache import Memcache, MemcacheService

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.profile import Avatar, Nick, Summary
from avilla.standard.core.relation.capability import RelationshipTerminate
from avilla.telegram.perform.resource_fetch import TelegramResourceFetchPerform

if TYPE_CHECKING:
    from avilla.telegram.account import TelegramAccount  # noqa
    from avilla.telegram.protocol import TelegramProtocol  # noqa


class TelegramChatActionPerform((m := AccountCollector["TelegramProtocol", "TelegramAccount"]())._):
    m.namespace = "avilla.protocol/telegram::action"
    m.identify = "chat"

    @staticmethod
    def extract_username(chat: dict[str, str]) -> str:
        if "username" in chat:
            return chat["username"]
        return f'{chat.get("first_name", "")} {chat.get("last_name", "")}'.strip()

    @m.pull("land.chat", Nick)
    @m.pull("land.chat.member", Nick)
    @m.pull("land.chat.thread.member", Nick)
    async def get_chat_nick(self, target: Selector, route: ...) -> Nick:
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        if raw := await cache.get(f"telegram/chat({target.last_value})"):
            return Nick(username := self.extract_username(raw), username, raw.get("title"))
        result = (await self.account.connection.call("getChat", chat_id=target.last_value))["result"]
        await cache.set(f"telegram/chat({target.last_value})", result, expire=timedelta(minutes=5))
        return Nick(username := self.extract_username(result), username, result.get("title"))

    @m.pull("land.chat", Summary)
    @m.pull("land.chat.member", Summary)
    @m.pull("land.chat.thread.member", Summary)
    async def get_chat_summary(self, target: Selector, route: ...) -> Summary:
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        if raw := await cache.get(f"telegram/chat({target.last_value})"):
            return Summary(self.extract_username(raw), raw.get("bio") or raw.get("description"))
        result = (await self.account.connection.call("getChat", chat_id=target.last_value))["result"]
        await cache.set(f"telegram/chat({target.last_value})", result, expire=timedelta(minutes=5))
        return Summary(self.extract_username(result), result.get("bio") or result.get("description"))

    @RelationshipTerminate.terminate.collect(m, target="land.chat")
    @RelationshipTerminate.terminate.collect(m, target="land.chat.thread")
    async def leave_chat(self, target: Selector):
        await self.account.connection.call("leaveChat", chat_id=target.into("::chat").last_value)

    @m.pull("land.chat", Avatar)
    @m.pull("land.chat.thread", Avatar)
    async def get_chat_profile_photo(self, target: Selector, route: ...) -> Avatar:
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        connection = self.account.connection
        if raw := await cache.get(f"telegram/chat({target.last_value})"):
            if raw["type"] == "private":
                return await self.get_user_profile_photo(target, route)
            file_id = raw.get("photo", {}).get("big_file_id")
        else:
            result = (await connection.call("getChat", chat_id=target.last_value))["result"]
            await cache.set(f"telegram/chat({target.last_value})", result, expire=timedelta(minutes=5))
            if result["type"] == "private":
                return await self.get_user_profile_photo(target, route)
            file_id = result.get("photo", {}).get("big_file_id")
        file_resource = await TelegramResourceFetchPerform(self.staff).get_file_resource(file_id)
        url = connection.config.file_base_url / f"bot{connection.config.token}" / str(file_resource.file_path)
        return Avatar(str(url))

    @m.pull("land.chat.member", Avatar)
    @m.pull("land.chat.thread.member", Avatar)
    async def get_user_profile_photo(self, target: Selector, route: ...) -> Avatar:
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        connection = self.account.connection
        if raw := await cache.get(f"telegram/user({target.last_value})::profile_photos"):
            file_id = raw["photos"][0][-1]["file_id"]
        else:
            result = (await connection.call("getUserProfilePhotos", user_id=target.last_value))["result"]
            await cache.set(f"telegram/user({target.last_value})::profile_photos", result, expire=timedelta(minutes=5))
            file_id = result["photos"][0][-1]["file_id"]
        file_resource = await TelegramResourceFetchPerform(self.staff).get_file_resource(file_id)
        url = connection.config.file_base_url / f"bot{connection.config.token}" / str(file_resource.file_path)
        return Avatar(str(url))
