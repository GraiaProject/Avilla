from __future__ import annotations

import asyncio
from contextlib import suppress
from typing import TYPE_CHECKING, cast
import binascii

import aiohttp
from aiohttp import web
from launart import Service
from launart.manager import Launart
from launart.utilles import any_completed
from loguru import logger
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from avilla.core.account import AccountInfo
from avilla.core.selector import Selector
from avilla.qqapi.account import QQAPIAccount
from avilla.qqapi.const import PLATFORM
from avilla.standard.core.account import (
    AccountAvailable,
    AccountRegistered,
    AccountUnavailable,
    AccountUnregistered,
)

from .base import QQAPINetworking
from .util import Opcode, Payload
from ..audit import MessageAudited, audit_result
from ..capability import QQAPICapability

if TYPE_CHECKING:
    from avilla.qqapi.protocol import QQAPIWebhookConfig, QQAPIProtocol


class QQAPIWebhookConnection(QQAPINetworking):
    def __init__(
        self,
        protocol: QQAPIProtocol,
        config: QQAPIWebhookConfig,
        app_id: str,
        secret: str,
        network: QQAPIWebhookNetworking,
    ) -> None:
        super().__init__(protocol, config, app_id, secret)
        self.session = network.session
        self.close_signal = network.close_signal

    @property
    def alive(self) -> bool:
        return not self.close_signal.is_set()


class QQAPIWebhookNetworking(Service):
    required: set[str] = set()
    stages: set[str] = {"preparing", "blocking", "cleanup"}
    session: aiohttp.ClientSession

    config: QQAPIWebhookConfig
    wsgi: web.Application | None = None

    @property
    def id(self):
        return f"qqapi/connection/server#{self.config.host}:{self.config.port}"

    def __init__(self, protocol: QQAPIProtocol, config: QQAPIWebhookConfig) -> None:
        super().__init__()
        self.protocol = protocol
        self.close_signal: asyncio.Event = asyncio.Event()
        self.config = config
        self.connection: dict[str, QQAPIWebhookConnection] = {}

    @property
    def alive(self):
        return self.wsgi is not None

    async def wait_for_available(self):
        await self.status.wait_for_available()

    async def handle_request(self, req: web.Request):
        header = req.headers
        data = await req.json()
        payload = Payload(**data)
        bot_id = header["X-Bot-Appid"]
        secret = self.config.secrets[bot_id]
        if payload.opcode == Opcode.SERVER_VERIFY:
            logger.info(f"QQAPI Verifying current server...")
            plain_token = payload.data["plain_token"]
            event_ts = payload.data["event_ts"]
            seed = secret.encode()
            while len(seed) < 32:
                seed += secret.encode()
            seed = seed[:32]
            try:
                private_key = Ed25519PrivateKey.from_private_bytes(seed)
            except Exception as e:
                logger.exception(f"Failed to generate ed25519 private key: {e}")
                return web.Response(status=500)
            msg = f"{event_ts}{plain_token}".encode()
            try:
                signature = private_key.sign(msg)
                signature_hex = binascii.hexlify(signature).decode()
            except Exception as e:
                logger.exception(f"Failed to sign message: {e}")
                return web.Response(status=500)
            return web.json_response({"plain_token": plain_token, "signature": signature_hex})

        if self.config.verify_payload:
            ed25519 = header["X-Signature-Ed25519"]
            timestamp = header["X-Signature-Timestamp"]

            seed = secret.encode()
            while len(seed) < 32:
                seed *= 2
            seed = seed[:32]
            try:
                private_key = Ed25519PrivateKey.from_private_bytes(seed)
                public_key = private_key.public_key()
            except Exception as e:
                logger.exception(f"Failed to generate ed25519 public key: {e}")
                return web.Response(status=500)
            if not ed25519:
                logger.warning(f"Missing ed25519 signature")
                return web.Response(status=401)
            sig = binascii.unhexlify(ed25519)
            if len(sig) != 64 or sig[63] & 224 != 0:
                logger.warning(f"Invalid ed25519 signature")
                return web.Response(status=401)
            if not timestamp:
                logger.warning(f"Missing timestamp")
                return web.Response(status=401)
            msg = timestamp.encode() + await req.read()
            try:
                public_key.verify(sig, msg)
            except InvalidSignature:
                logger.warning(f"Invalid payload: {payload}")
                return web.Response(status=401)
            except Exception as e:
                logger.exception(f"Failed to verify ed25519 signature: {e}")
                return web.Response(status=401)

        account_route = Selector().land("qqapi").account(bot_id)
        if account_route in self.protocol.avilla.accounts:
            account = cast(QQAPIAccount, self.protocol.avilla.accounts[account_route].account)
        else:
            account = QQAPIAccount(account_route, self.protocol)
            self.protocol.avilla.accounts[account_route] = AccountInfo(
                account_route,
                account,
                self.protocol,
                PLATFORM,
            )
            connection = QQAPIWebhookConnection(self.protocol, self.config, bot_id, secret, self)
            self.protocol.service.accounts[bot_id] = account
            account.connection = connection
            self.connection[bot_id] = connection
            self.protocol.avilla.broadcast.postEvent(AccountRegistered(self.protocol.avilla, account))
            self.protocol.avilla.broadcast.postEvent(AccountAvailable(self.protocol.avilla, account))

        async def event_parse_task(_data: Payload):
            event_type = _data.type
            if not event_type:
                raise ValueError("event type is None")
            with suppress(NotImplementedError):
                event = await QQAPICapability(account.connection.staff).event_callback(event_type.lower(), _data.data)
                if event is not None:
                    if isinstance(event, MessageAudited):
                        audit_result.add_result(event)
                    await self.protocol.post_event(event)  # type: ignore
                return
            logger.warning(f"received unsupported event {event_type.lower()}: {_data.data}")
            return

        asyncio.create_task(event_parse_task(payload))
        return web.Response()

    async def daemon(self, manager: Launart, site: web.TCPSite):
        while not manager.status.exiting:
            await site.start()
            self.close_signal.clear()
            close_task = asyncio.create_task(self.close_signal.wait())
            sigexit_task = asyncio.create_task(manager.status.wait_for_sigexit())
            done, pending = await any_completed(
                sigexit_task,
                close_task,
            )
            if sigexit_task in done:
                logger.info(f"{self.id} Webhook server exiting...")
                self.close_signal.set()
                for bot_id in self.connection.keys():
                    with suppress(KeyError):
                        account_route = Selector().land("qqapi").account(bot_id)
                        account = self.protocol.avilla.accounts[account_route].account
                        await self.protocol.avilla.broadcast.postEvent(AccountUnregistered(self.protocol.avilla, account))
                        del self.protocol.service.accounts[bot_id]
                        del self.protocol.avilla.accounts[account_route]
                self.connection.clear()
                return

            if close_task in done:
                await site.stop()
                logger.warning(f"{self.id} Connection closed by server, will reconnect in 5 seconds...")
                for bot_id in self.connection.keys():
                    account = self.protocol.service.accounts[bot_id]
                    await self.protocol.avilla.broadcast.postEvent(AccountUnavailable(self.protocol.avilla, account))
                    with suppress(KeyError):
                        del self.protocol.service.accounts[bot_id]
                await asyncio.sleep(5)
                logger.info(f"{self} Reconnecting...")
                continue

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            self.session = aiohttp.ClientSession()
            logger.info(f"starting server on {self.config.host}:{self.config.port}")
            self.wsgi = web.Application(logger=logger)  # type: ignore
            self.wsgi.router.freeze = lambda: None  # monkey patch
            self.wsgi.router.add_post(self.config.path, self.handle_request)
            runner = web.AppRunner(self.wsgi)
            await runner.setup()
            site = web.TCPSite(runner, self.config.host, self.config.port, ssl_context=self.config.ssl_context)

        async with self.stage("blocking"):
            await self.daemon(manager, site)

        async with self.stage("cleanup"):
            await site.stop()
            await self.wsgi.shutdown()
            await self.wsgi.cleanup()
            await self.session.close()
