from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from anonflow.services import UserService
from anonflow.interfaces import UserResponsesPort
from anonflow.services.transport.types import RequestContext


class StartRouter(Router):
    def __init__(self, responses_port: UserResponsesPort, user_service: UserService):
        super().__init__()

        self._responses_port = responses_port
        self._user_service = user_service

    async def _on_start(self, message: Message, user_language: str):
        if message.from_user:
            await self._user_service.add(message.from_user.id)
        await self._responses_port.user_start(RequestContext(message.chat.id, user_language))

    def setup(self):
        self.message.register(self._on_start, CommandStart())
