import logging
from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from anonflow import __version_str__, paths
from anonflow.bot.transport import DeliveryService, ResponsesRouter
from anonflow.config import Config
from anonflow.database import (
    BanRepository,
    Database,
    ModeratorRepository,
    UserRepository,
)
from anonflow.moderation import (
    ModerationExecutor,
    ModerationPlanner,
    ModerationService,
    RuleManager,
)
from anonflow.services import ModeratorService, UserService
from anonflow.translator import Translator

from .builders import build_middlewares, build_routers
from .helpers import require


class Application:
    def __init__(self):
        self._logger = logging.getLogger(__name__)

        self._bot: Optional[Bot] = None
        self._dispatcher: Optional[Dispatcher] = None
        self._config: Optional[Config] = None
        self._database: Optional[Database] = None
        self._moderator_service: Optional[ModeratorService] = None
        self._user_service: Optional[UserService] = None
        self._translator: Optional[Translator] = None
        self._rule_manager: Optional[RuleManager] = None
        self._moderation_planner: Optional[ModerationPlanner] = None
        self._moderation_executor: Optional[ModerationExecutor] = None
        self._moderation_service: Optional[ModerationService] = None
        self._responses_router: Optional[ResponsesRouter] = None

    def _init_config(self):
        config_filepath = paths.CONFIG_FILEPATH

        if not config_filepath.exists():
            Config().save(config_filepath)
            raise RuntimeError(
                "Config file was just created. Please fill it out and restart the application."
            )

        self._config = Config.load(config_filepath)

    def _init_logging(self):
        with require(self, "_config") as config:
            logging.basicConfig(
                format=config.logging.fmt,
                datefmt=config.logging.date_fmt,
                level=config.logging.level,
            )

    async def _init_database(self):
        with require(self, "_config") as config:
            self._database = Database(config.get_database_url())
            await self._database.init()

            self._moderator_service = ModeratorService(
                self._database, BanRepository(), ModeratorRepository()
            )
            await self._moderator_service.init()
            self._user_service = UserService(self._database, UserRepository())

    def _init_bot(self):
        with require(self, "_config") as config:
            bot_token = config.bot.token
            if not bot_token:
                raise ValueError("bot.token is required and cannot be empty")

            self._bot = Bot(
                token=bot_token.get_secret_value(),
                default=DefaultBotProperties(parse_mode="HTML"),
            )
            self._dispatcher = Dispatcher(storage=MemoryStorage())

    def _init_translator(self):
        with require(self, "_config") as config:
            self._translator = Translator(
                translations_dir=paths.TRANSLATIONS_DIR,
                default_language=config.app.language
            )

    def _init_transport(self):
        with require(self, "_bot", "_config", "_translator") as (
            bot,
            config,
            translator,
        ):
            self._responses_router = ResponsesRouter(
                moderation_chat_id=config.bot.forwarding.moderation_chat_id,
                publication_channel_ids=config.bot.forwarding.publication_channel_ids,
                delivery_service=DeliveryService(bot),
                translator=translator,
            )

    def _init_moderation(self):
        with require(self, "_config", "_responses_router") as (
            config,
            responses_router,
        ):
            self._rule_manager = RuleManager(rules_dir=paths.RULES_DIR)
            self._rule_manager.reload()

            api_key = config.openai.api_key
            if not api_key and config.moderation.enabled:
                raise ValueError("openai.api_key is required and cannot be empty")

            base_url = config.openai.base_url
            proxy = config.openai.proxy

            self._moderation_planner = ModerationPlanner(
                api_key=api_key.get_secret_value() if api_key else None,
                gpt_model=config.moderation.model,
                backends=config.moderation.backends,
                rule_manager=self._rule_manager,
                base_url=str(base_url) if base_url else None,
                proxy=str(proxy) if proxy else None,
                timeout=config.openai.timeout,
                max_retries=config.openai.max_retries,
            )
            self._moderation_planner.set_enabled(config.moderation.enabled)
            self._moderation_executor = ModerationExecutor(self._moderation_planner)

            self._moderation_service = ModerationService(
                responses_router, self._moderation_executor
            )

    def _init_routers(self):
        with require(
            self,
            "_dispatcher",
            "_config",
            "_responses_router",
            "_user_service",
            "_moderator_service",
            "_moderation_service",
        ) as (
            dispatcher,
            config,
            responses_router,
            user_service,
            moderator_service,
            moderation_service,
        ):
            dispatcher.include_router(
                build_routers(
                    config=config,
                    responses_router=responses_router,
                    user_service=user_service,
                    moderator_service=moderator_service,
                    moderation_service=moderation_service,
                )
            )

    def _init_middleware(self):
        with require(
            self,
            "_dispatcher",
            "_config",
            "_responses_router",
            "_user_service",
            "_moderator_service",
        ) as (
            dispatcher,
            config,
            responses_router,
            user_service,
            moderator_service
        ):
            middlewares = build_middlewares(
                config=config,
                dispatcher=dispatcher,
                responses_router=responses_router,
                user_service=user_service,
                moderator_service=moderator_service,
            )

            for middleware in middlewares:
                dispatcher.update.middleware(middleware)

    async def init(self):
        self._init_config()
        self._init_logging()
        await self._init_database()
        self._init_bot()
        self._init_translator()
        self._init_transport()
        self._init_moderation()
        self._init_routers()
        self._init_middleware()

    async def run(self):
        try:
            await self.init()
        except:
            if self._bot:
                await self._bot.session.close()
            if self._database:
                await self._database.close()
            if self._moderation_planner:
                await self._moderation_planner.close()
            raise

        self._logger.info(
            f"Anonflow v{__version_str__} has been successfully initialized."
        )

        with require(
            self, "_bot", "_dispatcher", "_database", "_moderation_planner"
        ) as (bot, dispatcher, database, moderation_planner):
            try:
                await dispatcher.start_polling(bot)
            finally:
                self._logger.info("Shutting down Anonflow...")
                await bot.session.close()
                await database.close()
                await moderation_planner.close()
