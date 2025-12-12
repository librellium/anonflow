from aiogram import Bot
from aiogram.types import ChatIdUnion, Message
from aiogram.exceptions import TelegramBadRequest
from contextlib import suppress
from typing import Dict

from anonflow.config import Config
from anonflow.moderation.models import (
    Events,
    ExecutorDeletionEvent,
    ModerationDecisionEvent,
    ModerationStartedEvent,
)

from .template_renderer import TemplateRenderer


class EventHandler:
    def __init__(self, bot: Bot, config: Config, template_renderer: TemplateRenderer):
        self.bot = bot
        self.config = config
        self.renderer = template_renderer

        self._messages: Dict[ChatIdUnion, Message] = {}

    async def handle(self, event: Events, message: Message):
        moderation_chat_ids = self.config.forwarding.moderation_chat_ids

        if isinstance(event, ModerationStartedEvent):
            self._messages[message.chat.id] = await message.answer(
                await self.renderer.render(
                    "messages/users/moderation/pending.j2",
                    message=message
                )
            )
        elif isinstance(event, ModerationDecisionEvent):
            with suppress(TelegramBadRequest):
                if message.chat.id in self._messages:
                    await self._messages.get(message.chat.id).delete()
            if event.approved:
                await message.answer(
                    await self.renderer.render(
                        "messages/users/send/success.j2",
                        message=message,
                    )
                )
            else:
                await message.answer(
                    await self.renderer.render(
                        "messages/users/moderation/rejected.j2",
                        message=message,
                    )
                )
        elif isinstance(event, ExecutorDeletionEvent) and moderation_chat_ids:
            for chat_id in moderation_chat_ids:
                if event.success:
                    await message.bot.send_message(
                        chat_id,
                        await self.renderer.render(
                            "messages/staff/deletion/success.j2",
                            message=message,
                            message_id=event.message_id,
                        )
                    )
                else:
                    await message.bot.send_message(
                        chat_id,
                        await self.renderer.render(
                            "messages/staff/deletion/failure.j2",
                            message=message,
                            message_id=event.message_id,
                        )
                    )
