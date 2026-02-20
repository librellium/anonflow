import asyncio
import logging
import textwrap
from typing import AsyncGenerator, Literal, Optional

from anonflow.services.transport.results import (
    Results,
    ModerationDecisionResult,
    ModerationStartedResult
)

from .planner import ModerationPlanner


class ModerationExecutor:
    def __init__(self, planner: ModerationPlanner):
        self._logger = logging.getLogger(__name__)

        self.planner = planner
        self.planner.set_functions(self.moderation_decision)

    def moderation_decision(self, status: Literal["approve", "reject"], reason: str):
        moderation_map = {"approve": True, "reject": False}
        return ModerationDecisionResult(is_approved=moderation_map.get(status.lower(), False), reason=reason)
    moderation_decision.description = textwrap.dedent( # type: ignore
        """
        Processes a message with a moderation decision by status and reason.
        This function must be called whenever there is no exact user request or no other available function
        matching the user's intent. Status must be either "approve if the message is allowed, or "reject" if it should be blocked.
        """
    ).strip()

    async def process(self, text: Optional[str] = None, image: Optional[str] = None) -> AsyncGenerator[Results, None]:
        yield ModerationStartedResult()

        functions = await self.planner.plan(text, image)
        function_names = self.planner.get_function_names()

        for func in functions:
            func_name = func.get("name", "")
            func_args = func.get("args", {})

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
