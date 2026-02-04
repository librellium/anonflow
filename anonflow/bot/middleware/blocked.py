from aiogram import BaseMiddleware
from aiogram.types import Message

from anonflow.services import ModeratorService
from anonflow.translator import Translator


class BlockedMiddleware(BaseMiddleware):
    def __init__(self, moderator_service: ModeratorService, translator: Translator):
        super().__init__()

        self.moderator_service = moderator_service
        self.translator = translator

    async def __call__(self, handler, event, data):
        _ = self.translator.get()

        message = getattr(event, "message", None)
        if isinstance(message, Message):
            if await self.moderator_service.is_banned(message.chat.id):
                await message.answer(_("messages.user.blocked", message))
                return

        return await handler(event, data)
