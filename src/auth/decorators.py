from functools import wraps
from typing import List
from fastapi import HTTPException, Request

from src.auth.context import get_user_context
from src.auth.enums import Role
from src.exceptions.api_exception import APIException
from src.exceptions.error_codes import ErrorCode


def authentication(roles: List[Role], message: str = "Unauthorized access"):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, request: Request, **kwargs):
            user_context = get_user_context()

            if not user_context:
                raise APIException("Invalid or missing authentication token", ErrorCode.INVALID_TOKEN)

            if not any(role in user_context.roles for role in roles):
                raise APIException("Unauthorised access", ErrorCode.INSUFFICIENT_PERMISSIONS)

            return await func(*args, request=request, **kwargs)

        return wrapper

    return decorator