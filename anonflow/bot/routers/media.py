import asyncio
import base64
from asyncio import CancelledError
from contextlib import suppress
from io import BytesIO
from typing import Dict, FrozenSet, List

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.types import Message

from anonflow.config.models import ForwardingType
from anonflow.interfaces import PostResponsesPort
from anonflow.moderation import ModerationService
from anonflow.bot.transport.content import (
    ContentGroup,
    ContentMediaItem,
    MediaType
)
from anonflow.bot.transport.types import RequestContext


class MediaRouter(Router):
    def __init__(
        self,
        responses_port: PostResponsesPort,
        moderation_service: ModerationService,
        forwarding_types: FrozenSet[ForwardingType]
    ):
        super().__init__()

        self._responses_port = responses_port
        self._moderation_service = moderation_service
        self._forwarding_types = forwarding_types

        self._media_groups: Dict[str, List[Message]] = {}
        self._media_groups_tasks: Dict[str, asyncio.Task] = {}
        self._media_groups_lock = asyncio.Lock()

    @staticmethod
    async def get_b64image(message: Message):
        if message.photo and message.bot:
            photo = message.photo[-1]
            file = await message.bot.get_file(photo.file_id)
            if file:
                buffer = BytesIO()
                await message.bot.download(file, buffer)
                buffer.seek(0)
                return (base64.b64encode(buffer.read())).decode()

    def _can_send_media(self, msgs: List[Message]):
        return any(
            (msg.photo and "photo" in self._forwarding_types) or
            (msg.video and "video" in self._forwarding_types)
            for msg in msgs
        )

    def _get_media(self, message: Message):
        if message.photo and "photo" in self._forwarding_types:
            return {"type": MediaType.PHOTO, "file_id": message.photo[-1].file_id}
        elif message.video and "video" in self._forwarding_types:
            return {"type": MediaType.VIDEO, "file_id": message.video.file_id}

    async def _process_messages(self, messages: List[Message], user_language: str):
        if not messages:
            return

        if not self._can_send_media(messages):
            return

        context = RequestContext(messages[0].chat.id, user_language)
        is_approved = False

        content_group = ContentGroup()
        caption = next((msg.caption for msg in messages if msg.caption), "")

        for message in messages:
            is_approved = await self._moderation_service.process(
                context,
                message.caption,
                await self.get_b64image(message)
            )

            media = self._get_media(message)
            if media:
                content_group.append(ContentMediaItem(**media, caption=caption))

        await self._responses_port.post_prepared(
            context, content_group, is_approved
        )

    async def _on_media(self, message: Message, user_language: str):
        if message.chat.type != ChatType.PRIVATE:
            return

        media_group_id = message.media_group_id

        async def await_media_group():
            with suppress(CancelledError):
                await asyncio.sleep(2)
                async with self._media_groups_lock:
                    messages = self.media_groups.pop(media_group_id, []) # type: ignore
                    self.media_groups_tasks.pop(media_group_id, None) # type: ignore

                await self._process_messages(messages, user_language)

        if media_group_id:
            async with self._media_groups_lock:
                self._media_groups.setdefault(media_group_id, []).append(message)

                task = self._media_groups_tasks.get(media_group_id)
                if task:
                    task.cancel()

                self._media_groups_tasks[media_group_id] = asyncio.create_task(
                    await_media_group()
                )
            return

        await self._process_messages([message], user_language)

    def setup(self):
        self.message.register(self._on_media, F.photo | F.video)
