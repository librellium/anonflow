from typing import Optional

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.types import Message

from anonflow.bot.events.models import BotMessagePreparedEvent
from anonflow.bot.events.event_handler import EventHandler, ModerationDecisionEvent
from anonflow.config import Config
from anonflow.moderation import ModerationExecutor
from anonflow.translator import Translator


class TextRouter(Router):
    def __init__(
        self,
        config: Config,
        translator: Translator,
        event_handler: EventHandler,
        moderation_executor: Optional[ModerationExecutor] = None,
    ):
        super().__init__()

        self.config = config
        self.translator = translator
        self.event_handler = event_handler
        self.executor = moderation_executor

    def setup(self):
        @self.message(F.text)
        async def on_text(message: Message):

            _ = self.translator.get()

            moderation = self.config.moderation.enabled
            moderation_passed = not moderation

            if (
                message.chat.type == ChatType.PRIVATE
                and "text" in self.config.forwarding.types
            ):
                if moderation:
                    async for event in self.executor.process_message(message): # type: ignore
                        if isinstance(event, ModerationDecisionEvent):
                            moderation_passed = event.approved
                        await self.event_handler.handle(event, message)

                if moderation_passed:
                    await self.event_handler.handle(BotMessagePreparedEvent(_("messages.channel.text", message=message)), message)
