from typing import Optional

from aiogram import Router

from anonflow.config import Config
from anonflow.moderation import ModerationExecutor

from .routers import MediaRouter, StartRouter, TextRouter
from .utils import MessageManager, TemplateRenderer


def build(config: Config,
          message_manager: MessageManager,
          template_renderer: TemplateRenderer,
          executor: Optional[ModerationExecutor] = None):
    main_router = Router()

    main_router.include_routers(
        StartRouter(
            template_renderer=template_renderer
        ),
        TextRouter(
            config=config,
            message_manager=message_manager,
            template_renderer=template_renderer,
            moderation_executor=executor
        ),
        MediaRouter(
            config=config,
            message_manager=message_manager,
            template_renderer=template_renderer,
            moderation_executor=executor
        )
    )

    return main_router