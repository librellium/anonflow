from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Iterable, Optional


class MediaType(str, Enum):
    PHOTO = "photo"
    VIDEO = "video"


@dataclass
class ContentItem(ABC):
    @abstractmethod
    def translate(self, translator: Callable): ...


@dataclass
class ContentTextItem(ContentItem):
    text: str

    def translate(self, translator: Callable):
        self.text = translator(self.text)


@dataclass
class ContentMediaItem(ContentItem):
    type: MediaType
    file_id: str
    caption: Optional[str] = None

    def translate(self, translator: Callable):
        self.caption = translator(self.caption)


class ContentGroup(list):
    def __init__(self, items: Optional[Iterable[ContentItem]] = None):
        return super().__init__(items or [])

    def translate(self, translator: Callable):
        for item in self:
            item.translate(translator)
