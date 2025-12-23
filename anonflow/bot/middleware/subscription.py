from typing import List

from aiogram import BaseMiddleware
from aiogram.enums import ChatMemberStatus
from aiogram.types import ChatIdUnion, Message

from anonflow.translator import Translator

from .utils import extract_message


class SubscriptionMiddleware(BaseMiddleware):
    def __init__(self, channel_ids: List[ChatIdUnion], translator: Translator):
        super().__init__()

        self.channel_ids = channel_ids
        self.translator = translator

    async def __call__(self, handler, event, data):
        _ = self.translator.get()

        message = extract_message(event)

        if isinstance(message, Message):
            user_id = message.from_user.id
            for channel_id in self.channel_ids:
                member = await message.bot.get_chat_member(channel_id, user_id)
                if member.status in (ChatMemberStatus.KICKED, ChatMemberStatus.LEFT):
                    await message.answer(_("messages.user.subscription_required", message=message))
                    return

        return await handler(event, data)
