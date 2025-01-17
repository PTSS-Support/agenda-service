from enum import Enum


class Role(Enum):
    ADMIN = "ADMIN"
    HCP = "HCP"
    PRIMARY_CAREGIVER = "PRIMARY_CAREGIVER"
    FAMILY_MEMBER = "FAMILY_MEMBER"
    PATIENT = "PATIENT"

    @staticmethod
    def from_string(role_str: str) -> "Role":
        try:
            return Role[role_str.upper()]
        except KeyError:
            raise ValueError(f"Invalid role: {role_str}")
