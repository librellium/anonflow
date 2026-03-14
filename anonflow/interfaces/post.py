from typing import Protocol, Union

from anonflow.bot.transport.content import ContentGroup, ContentItem
from anonflow.bot.transport.types import RequestContext


class PostResponsesPort(Protocol):
    async def post_prepared(self, context: RequestContext, content: Union[ContentItem, ContentGroup], is_approved: bool): ...  # fmt: skip
    async def post_moderators_decision(self, context: RequestContext, is_approved: bool, message_id: int): ... # fmt: skip
    async def post_moderation_decision(self, context: RequestContext, is_approved: bool, reason: str): ...  # fmt: skip
    async def post_moderation_started(self, context: RequestContext): ...  # fmt: skip
