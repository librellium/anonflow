import asyncio
import logging

from aiogram import Bot, Dispatcher

from podslv21_bot import __version_str__
from podslv21_bot.bot import (GlobalSlowmodeMiddleware,
                              MessageManager,
                              TemplateRenderer,
                              build)
from podslv21_bot.config import Config
from podslv21_bot.moderation import (ModerationExecutor,
                                     ModerationPlanner,
                                     RuleManager)

from . import paths


async def main():
    with open(".env", "w") as env_file:
        env_file.write(f"APP_VERSION={__version_str__}\n")

    if not paths.CONFIG_FILE.exists():
        Config().save(paths.CONFIG_FILE)

    config = Config.load(paths.CONFIG_FILE)

    logging.basicConfig(format=config.logging.fmt,
                        datefmt=config.logging.date_fmt,
                        level=config.logging.level)

    bot = Bot(token=config.bot.token.get_secret_value())
    dispatcher = Dispatcher()

    message_manager = MessageManager()
    renderer = TemplateRenderer(paths.TEMPLATES_DIR)

    executor = None
    if config.moderation.enabled:
        rule_manager = RuleManager(paths.RULES_DIR)
        rule_manager.reload()

        planner = ModerationPlanner(config, rule_manager)
        executor = ModerationExecutor(config, bot, planner)

    dispatcher.update.middleware(
        GlobalSlowmodeMiddleware(delay=5, template_renderer=renderer)
    )
    
    dispatcher.include_router(
        build(
            config=config,
            message_manager=message_manager,
            template_renderer=renderer,
            executor=executor
        )
    )

    await dispatcher.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())