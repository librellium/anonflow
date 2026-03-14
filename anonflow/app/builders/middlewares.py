from itertools import chain

from aiogram import Dispatcher

from anonflow.bot.middlewares import (
    UserBannedMiddleware,
    UserContextMiddleware,
    UserLanguageMiddleware,
    UserNotRegisteredMiddleware,
    UserSubscriptionMiddleware,
    UserThrottlingMiddleware,
)
from anonflow.bot.transport import ResponsesRouter
from anonflow.config import Config
from anonflow.services import ModeratorService, UserService


def build_middlewares(
    config: Config,
    dispatcher: Dispatcher,
    responses_router: ResponsesRouter,
    user_service: UserService,
    moderator_service: ModeratorService,
):
    middlewares = []

    middlewares.append(UserContextMiddleware(user_service=user_service))

    middlewares.append(
        UserLanguageMiddleware(fallback_language=config.app.fallback_language)
    )

    middlewares.append(
        UserBannedMiddleware(
            responses_port=responses_router, moderator_service=moderator_service
        )
    )

    if config.bot.behavior.subscription_requirement.enabled:
        middlewares.append(
            UserSubscriptionMiddleware(
                responses_port=responses_router,
                channel_ids=config.bot.behavior.subscription_requirement.channel_ids,
            )
        )

    middlewares.append(UserNotRegisteredMiddleware(responses_port=responses_router))

    if config.bot.behavior.throttling.enabled:
        ignored_commands = ("/" + c for c in chain.from_iterable(
            getattr(command, "commands", [])
            for dp_router in dispatcher.sub_routers
            for router in dp_router.sub_routers
            for handler in router.message.handlers
            for command in handler.flags.get("commands", [])
        ))

        middlewares.append(
            UserThrottlingMiddleware(
                responses_port=responses_router,
                delay=config.bot.behavior.throttling.delay,
                ignored_chat_ids=[config.bot.forwarding.moderation_chat_id],
                ignored_commands=ignored_commands
            )
        )

    return middlewares
