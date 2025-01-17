from functools import wraps
from typing import List
from fastapi import HTTPException, Request

from src.auth.context import get_user_context
from src.auth.enums import Role


def authentication(roles: List[Role], message: str = "Unauthorized access"):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, request: Request, **kwargs):
            user_context = get_user_context()

            if not user_context:
                raise HTTPException(status_code=401, detail="No authenticated user context found")

            if not any(role in user_context.roles for role in roles):
                raise HTTPException(status_code=403, detail=message)

            return await func(*args, request=request, **kwargs)

        return wrapper

    return decorator