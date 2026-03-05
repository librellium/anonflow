from aiogram import BaseMiddleware
from aiogram.types import Message

from anonflow.interfaces import UserResponsesPort
from anonflow.services import ModeratorService
from anonflow.services.transport.types import RequestContext


class BannedMiddleware(BaseMiddleware):
    def __init__(self, responses_port: UserResponsesPort, moderator_service: ModeratorService):
        super().__init__()

        self._responses_port = responses_port
        self._moderator_service = moderator_service

    async def __call__(self, handler, event, data):
        message = getattr(event, "message", None)
        if isinstance(message, Message):
            if await self._moderator_service.is_banned(message.chat.id):
                await self._responses_port.user_banned(RequestContext(message.chat.id, data["user_language"]))
                return

        return await handler(event, data)
