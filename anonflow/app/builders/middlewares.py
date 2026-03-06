from anonflow.bot.middlewares.user import (
    UserBannedMiddleware,
    UserContextMiddleware,
    UserLanguageMiddleware,
    UserNotRegisteredMiddleware,
    UserSubscriptionMiddleware,
    UserThrottlingMiddleware
)
from anonflow.bot.transport import ResponsesRouter
from anonflow.config import Config
from anonflow.services import ModeratorService, UserService


def build_middlewares(
    config: Config,
    responses_router: ResponsesRouter,
    user_service: UserService,
    moderator_service: ModeratorService,
):
    middlewares = []

    middlewares.append(
        UserContextMiddleware(
            user_service=user_service
        )
    )

    middlewares.append(
        UserLanguageMiddleware()
    )

    middlewares.append(
        UserBannedMiddleware(
            responses_port=responses_router,
            moderator_service=moderator_service
        )
    )

    if config.behavior.subscription_requirement.enabled:
        middlewares.append(
            UserSubscriptionMiddleware(
                responses_port=responses_router,
                channel_ids=config.behavior.subscription_requirement.channel_ids
            )
        )

    middlewares.append(
        UserNotRegisteredMiddleware(
            responses_port=responses_router
        )
    )

    if config.behavior.throttling.enabled:
        middlewares.append(
            UserThrottlingMiddleware(
                responses_port=responses_router,
                delay=config.behavior.throttling.delay,
                allowed_chat_ids=config.forwarding.moderation_chat_ids
            )
        )

    return middlewares
