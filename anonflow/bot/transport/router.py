from itertools import chain
from typing import Tuple, Union

from aiogram.types import ChatIdUnion

from anonflow.interfaces import PostResponsesPort, UserResponsesPort
from anonflow.translator import Translator

from .content import ContentGroup, ContentItem
from .delivery import DeliveryService
from .types import RequestContext


class ResponsesRouter(PostResponsesPort, UserResponsesPort):
    def __init__(
        self,
        moderation_chat_ids: Tuple[ChatIdUnion],
        publication_channel_ids: Tuple[ChatIdUnion],
        delivery_service: DeliveryService,
        translator: Translator
    ):
        self._moderation_chat_ids = moderation_chat_ids
        self._publication_channel_ids = publication_channel_ids
        self._delivery_service = delivery_service
        self._translator = translator

    async def post_moderation_decision(
        self,
        context: RequestContext,
        is_approved: bool,
        reason: str
    ):
        _ = await self._translator.get(context.user_language)
        for chat_id in self._moderation_chat_ids:
            if is_approved:
                await self._delivery_service.send_text(
                    chat_id,
                    _(
                        "messages.staff.moderation_approved",
                        reason=reason,
                    )
                )
            else:
                await self._delivery_service.send_text(
                    chat_id,
                    _(
                        "messages.staff.moderation_rejected",
                        reason=reason,
                    )
                )

        if not is_approved:
            await self._delivery_service.send_text(
                context.chat_id,
                _("messages.user.moderation_rejected")
            )

    async def post_moderation_started(self, context: RequestContext):
        _ = await self._translator.get(context.user_language)
        await self._delivery_service.send_text(
            context.chat_id,
            _("messages.user.moderation_started")
        )

    async def post_prepared(
        self,
        context: RequestContext,
        content: Union[ContentItem, ContentGroup],
        is_approved: bool
    ):
        _ = await self._translator.get(context.user_language)

        chat_ids = (
            chain(self._moderation_chat_ids, self._publication_channel_ids)
            if is_approved else iter(self._moderation_chat_ids)
        )

        translator = lambda t: _(
            "messages.channel.post",
            text=t
        )
        content.translate(translator)

        for chat_id in chat_ids:
            await self._delivery_service.send_content(
                chat_id, content
            )

        if is_approved:
            await self._delivery_service.send_text(
                context.chat_id,
                _("messages.user.moderation_approved")
            )

    async def user_banned(self, context: RequestContext):
        _ = await self._translator.get(context.user_language)
        await self._delivery_service.send_text(
            context.chat_id,
            _("messages.user.banned")
        )

    async def user_not_registered(self, context: RequestContext):
        _ = await self._translator.get(context.user_language)
        await self._delivery_service.send_text(
            context.chat_id,
            _("messages.user.not_registered")
        )

    async def user_start(self, context: RequestContext):
        _ = await self._translator.get(context.user_language)
        await self._delivery_service.send_text(
            context.chat_id,
            _("messages.user.command_start")
        )

    async def user_subscription_required(self, context: RequestContext):
        _ = await self._translator.get(context.user_language)
        await self._delivery_service.send_text(
            context.chat_id,
            _("messages.user.subscription_required")
        )

    async def user_throttled(self, context: RequestContext, remaining_time: int):
        _ = await self._translator.get(context.user_language)
        await self._delivery_service.send_text(
            context.chat_id,
            _(
                "messages.user.throttled",
                n=remaining_time,
                remaining_time=remaining_time
            )
        )
