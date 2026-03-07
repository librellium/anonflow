from aiogram import Router

from anonflow.bot.routers import MediaRouter, StartRouter, TextRouter
from anonflow.bot.transport import ResponsesRouter
from anonflow.config import Config
from anonflow.moderation import ModerationService
from anonflow.services import ModeratorService, UserService


def build_routers(
    config: Config,
    responses_router: ResponsesRouter,
    user_service: UserService,
    moderator_service: ModeratorService,
    moderation_service: ModerationService,
) -> Router:
    main_router = Router()

    routers = [
        StartRouter(responses_port=responses_router, user_service=user_service),
        TextRouter(
            responses_port=responses_router,
            moderation_service=moderation_service,
            forwarding_types=config.forwarding.types,
        ),
        MediaRouter(
            responses_port=responses_router,
            moderation_service=moderation_service,
            forwarding_types=config.forwarding.types,
        ),
    ]

    for router in routers:
        router.setup()

    main_router.include_routers(*routers)
    return main_router
