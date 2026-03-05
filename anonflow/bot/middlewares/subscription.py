from typing import Tuple

from aiogram import BaseMiddleware
from aiogram.enums import ChatMemberStatus, ChatType
from aiogram.types import ChatIdUnion, Message

from anonflow.interfaces import UserResponsesPort
from anonflow.services.transport.types import RequestContext


class SubscriptionMiddleware(BaseMiddleware):
    def __init__(self, responses_port: UserResponsesPort, channel_ids: Tuple[ChatIdUnion]):
        super().__init__()

        self._responses_port = responses_port
        self._channel_ids = channel_ids

    async def __call__(self, handler, event, data):
        message = getattr(event, "message", None)
        if isinstance(message, Message) and message.chat.type == ChatType.PRIVATE:
            user_id = message.from_user.id # type: ignore
            for channel_id in self._channel_ids:
                member = await message.bot.get_chat_member(channel_id, user_id) # type: ignore
                if member.status in (ChatMemberStatus.KICKED, ChatMemberStatus.LEFT):
                    await self._responses_port.user_subscription_required(RequestContext(message.chat.id, data["user_language"]))
                    return

        return await handler(event, data)
