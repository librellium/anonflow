from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from anonflow.services import UserService
from anonflow.translator import Translator


class StartRouter(Router):
    def __init__(self, translator: Translator, user_service: UserService):
        super().__init__()

        self.translator = translator
        self.user_service = user_service

    def setup(self):
        @self.message(CommandStart())
        async def on_start(message: Message):
            await self.user_service.add(message.chat.id)
            _ = self.translator.get()
            await message.answer(_("messages.command.start", message=message))
