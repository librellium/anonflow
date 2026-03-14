import asyncio
from typing import Set

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.types import Message

from anonflow.bot.transport.content import ContentTextItem
from anonflow.bot.transport.types import RequestContext
from anonflow.config.models import ForwardingType
from anonflow.interfaces import PostResponsesPort
from anonflow.moderation import ModerationService


class TextRouter(Router):
    def __init__(
        self,
        responses_port: PostResponsesPort,
        moderation_service: ModerationService,
        forwarding_types: Set[ForwardingType],
    ):
        super().__init__()

        self._responses_port = responses_port
        self._moderation_service = moderation_service
        self._forwarding_types = forwarding_types

    async def _process(self, message: Message, user_language: str):
        context = RequestContext(message.chat.id, user_language)

        is_approved = await self._moderation_service.process(context, message.text)

        await self._responses_port.post_prepared(
            context, ContentTextItem(message.text or ""), is_approved
        )

    async def _on_text(self, message: Message, user_language: str):
        if message.chat.type == ChatType.PRIVATE and "text" in self._forwarding_types:
            asyncio.create_task(self._process(message, user_language))

    def setup(self):
        self.message.register(self._on_text, F.text)
