from typing import Optional, Tuple, Union

from aiogram.types import ChatIdUnion

from anonflow.bot.keyboards import Keyboards
from anonflow.interfaces import (
    ModeratorResponsesPort,
    PostResponsesPort,
    UserResponsesPort,
)
from anonflow.translator import Translator

from .content import ContentGroup, ContentItem
from .delivery import DeliveryService
from .types import RequestContext


class ResponsesRouter(ModeratorResponsesPort, PostResponsesPort, UserResponsesPort):
    def __init__(
        self,
        moderation_chat_id: ChatIdUnion,
        publication_channel_ids: Tuple[ChatIdUnion],
        delivery_service: DeliveryService,
        translator: Translator,
    ):
        self._moderation_chat_id = moderation_chat_id
        self._publication_channel_ids = publication_channel_ids
        self._delivery_service = delivery_service
        self._translator = translator

    async def _get_translators(self, user_language: str, keyboards_from_user: bool = False):
        return (
            await self._translator.get(),
            await self._translator.get(
                user_language
            ),
            await self._translator.get(
                user_language if keyboards_from_user else None, domain="keyboards"
            )
        )

    async def moderator_permission_error(self, context: RequestContext, callback_query_id: Optional[str] = None):
        t_app, t_user, t_kb = await self._get_translators(context.user_language)
        if callback_query_id:
            await self._delivery_service.answer_callback_query(
                callback_query_id, t_user("moderator.permission_error")
            )
        else:
            await self._delivery_service.send_text(
                context.chat_id, t_user("moderator.permission_error")
            )

    async def post_moderators_decision(
        self, context: RequestContext, is_approved: bool, message_id: int
    ):
        await self._delivery_service.remove_reply_markup(context.chat_id, message_id)
        if is_approved:
            for chat_id in self._publication_channel_ids:
                await self._delivery_service.copy(chat_id, context.chat_id, message_id)

    async def post_moderation_decision(
        self, context: RequestContext, is_approved: bool, reason: str
    ):
        t_app, t_user, t_kb = await self._get_translators(context.user_language)
        if is_approved:
            await self._delivery_service.send_text(
                self._moderation_chat_id,
                t_app(
                    "moderator.moderation_approved",
                    reason=reason,
                ),
            )
        else:
            await self._delivery_service.send_text(
                self._moderation_chat_id,
                t_app(
                    "moderator.moderation_rejected",
                    reason=reason,
                ),
            )

        if is_approved:
            await self._delivery_service.send_text(
                context.chat_id, t_user("user.moderation_approved")
            )
        else:
            await self._delivery_service.send_text(
                context.chat_id, t_user("user.moderation_rejected")
            )

    async def post_moderation_started(self, context: RequestContext):
        t_app, t_user, t_kb = await self._get_translators(context.user_language)
        await self._delivery_service.send_with_delete(
            5, self._delivery_service.send_text, context.chat_id, t_user("user.moderation_started")
        )

    async def post_prepared(
        self,
        context: RequestContext,
        content: Union[ContentItem, ContentGroup],
        is_approved: bool,
    ):
        t_app, t_user, t_kb = await self._get_translators(context.user_language)

        content.translate(lambda t: t_app("channel.post", text=t))

        await self._delivery_service.send_content(
            self._moderation_chat_id,
            content,
            reply_markup=(
                Keyboards.get_post_markup(t_kb) if not is_approved else None
            ),
        )

        if is_approved:
            for chat_id in self._publication_channel_ids:
                await self._delivery_service.send_content(chat_id, content)

    async def user_banned(self, context: RequestContext):
        t_app, t_user, t_kb = await self._get_translators(context.user_language)
        await self._delivery_service.send_text(context.chat_id, t_user("user.banned"))

    async def user_not_registered(self, context: RequestContext):
        t_app, t_user, t_kb = await self._get_translators(context.user_language)
        await self._delivery_service.send_text(
            context.chat_id, t_user("user.not_registered")
        )

    async def user_start(self, context: RequestContext):
        t_app, t_user, t_kb = await self._get_translators(context.user_language)
        await self._delivery_service.send_text(context.chat_id, t_user("user.command_start"))

    async def user_subscription_required(self, context: RequestContext):
        t_app, t_user, t_kb = await self._get_translators(context.user_language)
        await self._delivery_service.send_text(
            context.chat_id, t_user("user.subscription_required")
        )

    async def user_throttled(self, context: RequestContext, remaining_time: int):
        t_app, t_user, t_kb = await self._get_translators(context.user_language)
        await self._delivery_service.send_text(
            context.chat_id,
            t_user(
                "user.throttled",
                n=remaining_time,
                remaining_time=remaining_time,
            ),
        )
