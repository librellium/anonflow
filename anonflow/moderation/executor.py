import asyncio
import logging
import textwrap
from typing import AsyncGenerator, Optional, Literal

from .events import Event, ModerationDecisionEvent, ModerationStartedEvent
from .planner import ModerationPlanner


class ModerationExecutor:
    def __init__(self, moderation_planner: ModerationPlanner):
        self._logger = logging.getLogger(__name__)

        self._moderation_planner = moderation_planner
        self._moderation_planner.set_functions(self.moderation_decision)

    def moderation_decision(self, status: Literal["approve", "reject"], reason: str):
        moderation_map = {"approve": True, "reject": False}
        return ModerationDecisionEvent(is_approved=moderation_map.get(status.lower(), False), reason=reason)
    moderation_decision.description = textwrap.dedent( # type: ignore
        """
        Processes a message with a moderation decision by status and reason.
        This function must be called whenever there is no exact user request or no other available function
        matching the user's intent. Status must be either "approve if the message is allowed, or "reject" if it should be blocked.
        """
    ).strip()

    async def process(self, text: Optional[str] = None, image: Optional[str] = None) -> AsyncGenerator[Event, None]:
        yield ModerationStartedEvent()

        functions = await self._moderation_planner.plan(text, image)
        function_names = self._moderation_planner.get_function_names()

        for function in functions:
            func_name = function.get("name", "")
            func_args = function.get("args", {})

            method = getattr(self, func_name, None)

            if method is None or func_name not in function_names:
                self._logger.warning("Function %s not found, skipping.", func_name)
                continue

            self._logger.info("Executing %s.", func_name)
            try:
                if asyncio.iscoroutinefunction(method):
                    yield await method(**func_args)
                else:
                    yield await asyncio.to_thread(method, **func_args)
            except Exception:
                self._logger.exception("Failed to execute %s.", func_name)
