from aiogram import BaseMiddleware
from aiogram.enums import ChatType
from aiogram.types import Message

from anonflow.interfaces import UserResponsesPort
from anonflow.services import UserService
from anonflow.services.transport.types import RequestContext


class NotRegisteredMiddleware(BaseMiddleware):
    def __init__(self, responses_port: UserResponsesPort, user_service: UserService):
        super().__init__()

        self._responses_port = responses_port
        self._user_service = user_service

    async def __call__(self, handler, event, data):
        message = getattr(event, "message", None)
        if isinstance(message, Message) and message.chat.type == ChatType.PRIVATE:
            text = message.text or message.caption or ""

            is_user_exists = await self._user_service.has(message.chat.id)
            if not is_user_exists and not text.startswith("/start"):
                await self._responses_port.user_not_registered(RequestContext(message.chat.id, data["user_language"]))
                return

        return await handler(event, data)
