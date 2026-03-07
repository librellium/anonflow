from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    pass


@dataclass(frozen=True)
class ModerationDecisionEvent(Event):
    is_approved: bool
    reason: str


@dataclass(frozen=True)
class ModerationStartedEvent(Event):
    pass
