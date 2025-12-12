from dataclasses import dataclass
from typing import Union

from aiogram.types import ChatIdUnion


@dataclass
class ExecutorDeletionEvent:
    success: bool
    message_id: ChatIdUnion


@dataclass
class ModerationDecisionEvent:
    approved: bool
    explanation: str


@dataclass
class ModerationStartedEvent:
    pass


Events = Union[ExecutorDeletionEvent, ModerationDecisionEvent, ModerationStartedEvent]
