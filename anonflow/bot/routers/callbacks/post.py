from aiogram import Router
from aiogram.types import CallbackQuery

from anonflow.bot.keyboards.callbacks import PostCallbackData
from anonflow.bot.transport.types import RequestContext
from anonflow.interfaces import PostResponsesPort, ModeratorResponsesPort
from anonflow.services import ModeratorService
from anonflow.services.moderator.permissions import ModeratorPermission


class PostRouter(Router):
    def __init__(
        self,
        post_responses_port: PostResponsesPort,
        moderator_responses_port: ModeratorResponsesPort,
        moderator_service: ModeratorService
    ):
        super().__init__()

        self._post_responses_port = post_responses_port
        self._moderator_responses_port = moderator_responses_port
        self._moderator_service = moderator_service

    async def _on_post_callback_query(self, query: CallbackQuery, callback_data: PostCallbackData, user_language: str):
        message = query.message

        if message:
            if await self._moderator_service.can(query.from_user.id, ModeratorPermission.MANAGE_POSTS):
                await self._post_responses_port.post_moderators_decision(
                    RequestContext(message.chat.id, user_language),
                    True if callback_data.action == "approve" else False,
                    message.message_id
                )
            else:
                await self._moderator_responses_port.moderator_permission_error(
                    RequestContext(message.chat.id, user_language), query.id
                )

    def setup(self):
        self.callback_query.register(self._on_post_callback_query, PostCallbackData.filter())
