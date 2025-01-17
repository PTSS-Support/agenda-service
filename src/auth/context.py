from dataclasses import dataclass
from typing import Optional, Set
from uuid import UUID
import contextvars

from src.auth.enums import Role

user_context_var = contextvars.ContextVar("user_context", default=None)

@dataclass
class UserContext:
    user_id: UUID
    group_id: Optional[UUID]
    roles: Set[Role]
    has_pin: bool

def get_user_context() -> Optional[UserContext]:
    return user_context_var.get()

def set_user_context(context: UserContext):
    user_context_var.set(context)

def clear_user_context():
    user_context_var.set(None)