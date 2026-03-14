from typing import Iterable

from aiogram import BaseMiddleware
from aiogram.enums import ChatMemberStatus, ChatType
from aiogram.types import ChatIdUnion, Message

from anonflow.bot.transport.types import RequestContext
from anonflow.interfaces import UserResponsesPort

from .utils import extract_message, extract_user


class UserSubscriptionMiddleware(BaseMiddleware):
    def __init__(
        self, responses_port: UserResponsesPort, channel_ids: Iterable[ChatIdUnion]
    ):
        super().__init__()

        self._responses_port = responses_port
        self._channel_ids = channel_ids

    async def __call__(self, handler, event, data):
        message = extract_message(event)
        from_user = extract_user(event)
        if (
            isinstance(message, Message)
            and from_user is not None
            and message.bot is not None
            and message.chat.type == ChatType.PRIVATE
        ):
            for channel_id in self._channel_ids:
                member = await message.bot.get_chat_member(channel_id, from_user.id)
                if member.status in (ChatMemberStatus.KICKED, ChatMemberStatus.LEFT):
                    await self._responses_port.user_subscription_required(
                        RequestContext(message.chat.id, data["user_language"])
                    )
                    return

        return await handler(event, data)
