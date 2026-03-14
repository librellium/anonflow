from aiogram import BaseMiddleware
from aiogram.types import Message

from anonflow.bot.transport.types import RequestContext
from anonflow.interfaces import UserResponsesPort
from anonflow.services import ModeratorService

from .utils import extract_message, extract_user


class UserBannedMiddleware(BaseMiddleware):
    def __init__(
        self, responses_port: UserResponsesPort, moderator_service: ModeratorService
    ):
        super().__init__()

        self._responses_port = responses_port
        self._moderator_service = moderator_service

    async def __call__(self, handler, event, data):
        message = extract_message(event)
        from_user = extract_user(event)
        if isinstance(message, Message) and from_user:
            if await self._moderator_service.is_banned(from_user.id):
                await self._responses_port.user_banned(
                    RequestContext(message.chat.id, data["user_language"])
                )
                return

        return await handler(event, data)
