from typing import Tuple

from aiogram.types import ChatIdUnion

from anonflow.services import (
    ModeratorService,
    ResponsesRouter,
    UserService
)

from anonflow.bot.middlewares import (
    BannedMiddleware,
    LanguageMiddleware,
    NotRegisteredMiddleware,
    SubscriptionMiddleware,
    ThrottlingMiddleware
)

def build(
    responses_router: ResponsesRouter,
    user_service: UserService,
    moderator_service: ModeratorService,

    subscription_requirement: bool,
    subscription_channel_ids: Tuple[ChatIdUnion],

    throttling: bool,
    throttling_delay: float,
    throttling_allowed_chat_ids: Tuple[ChatIdUnion]
):
    middlewares = []

    middlewares.append(
        LanguageMiddleware(
            user_service=user_service
        )
    )

    middlewares.append(
        BannedMiddleware(
            responses_port=responses_router,
            moderator_service=moderator_service
        )
    )

    if subscription_requirement:
        middlewares.append(
            SubscriptionMiddleware(
                responses_port=responses_router,
                channel_ids=subscription_channel_ids
            )
        )

    middlewares.append(
        NotRegisteredMiddleware(
            responses_port=responses_router,
            user_service=user_service
        )
    )

    if throttling:
        middlewares.append(
            ThrottlingMiddleware(
                responses_port=responses_router,
                delay=throttling_delay,
                allowed_chat_ids=throttling_allowed_chat_ids
            )
        )

    return middlewares
