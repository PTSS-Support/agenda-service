import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

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
        self.logger = logging.getLogger(__name__)

    async def dispatch(self, request: Request, call_next):
        try:
            token = request.cookies.get(settings.ACCESS_TOKEN_COOKIE_NAME)
            if token:
                try:
                    user_context = self.token_extractor.extract_user_context(token)
                    self.logger.info(f"Authenticated user {user_context.user_id} with roles: {user_context.roles}")
                    if user_context.group_id:
                        self.logger.info(f"User belongs to group: {user_context.group_id}")
                    set_user_context(user_context)
                except APIException as e:
                    self.logger.error(f"Authentication error: {str(e)}")
                    return JSONResponse(
                        status_code=e.status_code,
                        content=e.detail
                    )
                except Exception as e:
                    self.logger.error(f"Unexpected authentication error: {str(e)}")
                    raise APIException(
                        message="Authentication failed",
                        error_code=ErrorCode.INTERNAL_SERVER_ERROR
                    )

            response = await call_next(request)
            return response
        finally:
            clear_user_context()
