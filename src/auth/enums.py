from enum import Enum


class Role(Enum):
    ADMIN = "ADMIN"
    HCP = "HCP"
    CORE_USER = "CORE_USER"
    FAMILY_MEMBER = "FAMILY_MEMBER"

    @staticmethod
    def from_string(role_str: str) -> "Role":
        try:
            return Role[role_str.upper()]
        except KeyError:
            raise ValueError(f"Invalid role: {role_str}")
