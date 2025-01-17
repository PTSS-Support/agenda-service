from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from src.auth.jwt_validator import TokenUserExtractor
from src.auth.context import set_user_context, clear_user_context
from src.exceptions.api_exception import APIException
from src.exceptions.error_codes import ErrorCode
from src.settings import settings


class AuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.token_extractor = TokenUserExtractor(
            keycloak_public_key=settings.KEYCLOAK_PUBLIC_KEY,
            jwt_validation_enabled=settings.JWT_VALIDATION_ENABLED
        )

    async def dispatch(self, request: Request, call_next):
        try:
            token = request.cookies.get(settings.ACCESS_TOKEN_COOKIE_NAME)
            if token:
                try:
                    user_context = self.token_extractor.extract_user_context(token)
                    set_user_context(user_context)
                except Exception as e:
                    raise APIException(
                        message="Invalid or expired authentication token",
                        error_code=ErrorCode.INVALID_TOKEN
                    ) from e

            response = await call_next(request)
            return response
        finally:
            clear_user_context()