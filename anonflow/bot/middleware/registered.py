from aiogram import BaseMiddleware
from aiogram.enums import ChatType
from aiogram.types import Message

from anonflow.services import UserService
from anonflow.translator import Translator


class RegisteredMiddleware(BaseMiddleware):
    def __init__(self, user_service: UserService, translator: Translator):
        super().__init__()

        self.user_service = user_service
        self.translator = translator

    async def __call__(self, handler, event, data):
        _ = self.translator.get()

        message = getattr(event, "message", None)
        if isinstance(message, Message) and message.chat.type == ChatType.PRIVATE:
            text = message.text or message.caption or ""

            is_user_exists = await self.user_service.has(message.chat.id)
            if not is_user_exists and not text.startswith("/start"):
                await message.answer(_("messages.user.start_required", message))
                return

        return await handler(event, data)
