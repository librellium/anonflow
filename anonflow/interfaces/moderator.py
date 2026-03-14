from typing import Optional, Protocol

from anonflow.bot.transport.types import RequestContext


class ModeratorResponsesPort(Protocol):
    async def moderator_permission_error(self, context: RequestContext, callback_query_id: Optional[str] = None): ...
