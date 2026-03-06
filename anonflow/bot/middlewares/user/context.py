from aiogram import BaseMiddleware
from aiogram.types import Message

from anonflow.services import UserService


class UserContextMiddleware(BaseMiddleware):
    def __init__(self, user_service: UserService):
        super().__init__()

        self._user_service = user_service

    async def __call__(self, handler, event, data):
        data["user"] = None

        message = getattr(event, "message", None)
        if isinstance(message, Message) and message.from_user:
            data["user"] = await self._user_service.get(message.from_user.id)

        return await handler(event, data)
