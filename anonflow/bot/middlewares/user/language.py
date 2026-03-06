from aiogram import BaseMiddleware
from aiogram.types import Message


class UserLanguageMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(self, handler, event, data):
        data["user_language"] = None

        message = getattr(event, "message", None)
        if isinstance(message, Message) and message.from_user:
            user = data.get("user")
            data["user_language"] = (
                user.language
                if user else message.from_user.language_code
            )

        return await handler(event, data)
