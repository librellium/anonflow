from pathlib import Path
from typing import List, Literal, Optional, Set, TypeAlias, Union

from pydantic import BaseModel, Field, HttpUrl, SecretStr

ForwardingType: TypeAlias = Literal["text", "photo", "video"]
ModerationBackend: TypeAlias = Literal["omni", "gpt"]
LoggingLevel: TypeAlias = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class App(BaseModel):
    language: str = "ru"
    fallback_language: str = "ru"


class BotBehaviorThrottling(BaseModel):
    enabled: bool = True
    delay: float = 120


class BotBehaviorSubscriptionRequirement(BaseModel):
    enabled: bool = True
    channel_ids: List[int] = Field(default_factory=list)


class BotBehavior(BaseModel):
    throttling: BotBehaviorThrottling = Field(default_factory=BotBehaviorThrottling)
    subscription_requirement: BotBehaviorSubscriptionRequirement = Field(default_factory=BotBehaviorSubscriptionRequirement)  # fmt: skip


class BotForwarding(BaseModel):
    moderation_chat_id: Optional[int] = None
    publication_channel_ids: List[int] = Field(default_factory=list)
    types: Set[ForwardingType] = Field(default_factory=lambda: {"text", "photo", "video"})


class Bot(BaseModel):
    token: Optional[SecretStr] = None
    timeout: int = 10
    behavior: BotBehavior = Field(default_factory=BotBehavior)
    forwarding: BotForwarding = Field(default_factory=BotForwarding)


class DatabaseMigrations(BaseModel):
    backend: str = "sqlite"


class Database(BaseModel):
    backend: str = "sqlite+aiosqlite"
    name_or_path: Optional[Union[str, Path]] = "anonflow.db"
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[SecretStr] = None
    migrations: DatabaseMigrations = Field(default_factory=DatabaseMigrations)


class OpenAI(BaseModel):
    api_key: Optional[SecretStr] = None
    base_url: Optional[HttpUrl] = None
    proxy: Optional[HttpUrl] = None
    timeout: int = 10
    max_retries: int = 0


class Moderation(BaseModel):
    enabled: bool = True
    model: str = "gpt-5-mini"
    backends: Set[ModerationBackend] = Field(default_factory=lambda: {"omni", "gpt"})


class Logging(BaseModel):
    level: LoggingLevel = "INFO"
    fmt: Optional[str] = "%(asctime)s.%(msecs)03d %(levelname)s [%(name)s] %(message)s"
    date_fmt: Optional[str] = "%Y-%m-%d %H:%M:%S"
