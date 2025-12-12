from typing import List

from aiogram import BaseMiddleware
from aiogram.enums import ChatMemberStatus
from aiogram.types import ChatIdUnion, Message

from anonflow.bot.utils.template_renderer import TemplateRenderer

from .utils import extract_message


class SubscriptionMiddleware(BaseMiddleware):
    def __init__(self, channel_ids: List[ChatIdUnion], template_renderer: TemplateRenderer):
        super().__init__()

        self.channel_ids = channel_ids
        self.renderer = template_renderer

    async def __call__(self, handler, event, data):
        message = extract_message(event)

        if isinstance(message, Message):
            user_id = message.from_user.id
            for channel_id in self.channel_ids:
                member = await message.bot.get_chat_member(channel_id, user_id)
                if member.status in (ChatMemberStatus.KICKED, ChatMemberStatus.LEFT):
                    await message.answer(
                        await self.renderer.render(
                            "messages/users/send/subscription_required.j2", message=message
                        )
                    )
                    return

        return await handler(event, data)
