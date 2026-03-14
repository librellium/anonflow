from dataclasses import dataclass, asdict
from enum import Enum


@dataclass
class ModeratorPermissions:
    can_manage_posts: bool = False
    can_manage_bans: bool = False
    can_manage_moderators: bool = False

    def to_dict(self):
        return asdict(self)


class ModeratorPermission(str, Enum):
    MANAGE_POSTS = "can_manage_posts"
    MANAGE_BANS = "can_manage_bans"
    MANAGE_MODERATORS = "can_manage_moderators"
