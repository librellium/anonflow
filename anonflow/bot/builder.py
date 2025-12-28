from typing import Optional

from aiogram import Router

from anonflow.config import Config
from anonflow.moderation import ModerationExecutor
from anonflow.translator import Translator

from .events import EventHandler
from .routers import InfoRouter, MediaRouter, StartRouter, TextRouter


def build(
    config: Config,
    translator: Translator,
    event_handler: EventHandler,
    executor: Optional[ModerationExecutor] = None,
) -> Router:
    main_router = Router()

    routers = [
        StartRouter(translator=translator),
        InfoRouter(translator=translator),
        TextRouter(config=config, translator=translator, event_handler=event_handler, moderation_executor=executor),
        MediaRouter(config=config, translator=translator, event_handler=event_handler, moderation_executor=executor),
    ]

    for router in routers:
        router.setup()

    main_router.include_routers(*routers)
    return main_router
