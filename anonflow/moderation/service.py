from typing import Optional

from anonflow.interfaces import PostResponsesPort
from anonflow.services.transport.types import RequestContext

from .events import ModerationDecisionEvent, ModerationStartedEvent
from .executor import ModerationExecutor


class ModerationService:
    def __init__(
        self,
        responses_port: PostResponsesPort,
        moderation_executor: ModerationExecutor
    ):
        self._responses_port = responses_port
        self._moderation_executor = moderation_executor

    async def process(self, context: RequestContext, text: Optional[str] = None, image: Optional[str] = None):
        is_approved = False
        async for event in self._moderation_executor.process(text, image):
            if isinstance(event, ModerationDecisionEvent):
                is_approved = event.is_approved
                await self._responses_port.post_moderation_decision(context, event.is_approved, event.reason)
            elif isinstance(event, ModerationStartedEvent):
                await self._responses_port.post_moderation_started(context)

        return is_approved
