from dataclasses import dataclass
from typing import List, Optional, Union

from aiogram.types import ChatIdUnion, MediaUnion


@dataclass
class BotMessagePreparedEvent:
    content: Union[str, List[MediaUnion]]
    is_post: bool
    moderation_approved: bool

@dataclass
class ExecutorDeletionEvent:
    success: bool
    message_id: Optional[ChatIdUnion] = None


@dataclass
class ModerationDecisionEvent:
    approved: bool
    explanation: str


@dataclass
class ModerationStartedEvent:
    pass


Events = Union[BotMessagePreparedEvent, ExecutorDeletionEvent, ModerationDecisionEvent, ModerationStartedEvent]
