import logging
import jwt
from uuid import UUID

from src.auth.context import UserContext
from src.auth.decorators import Role
import json
import base64

from src.exceptions.api_exception import APIException
from src.exceptions.error_codes import ErrorCode


class TokenUserExtractor:
    def __init__(self, keycloak_public_key: str, jwt_validation_enabled: bool = True):
        self.keycloak_public_key = keycloak_public_key
        self.jwt_validation_enabled = jwt_validation_enabled
        self.logger = logging.getLogger(__name__)

        if keycloak_public_key:
            try:
                # Format the key in PEM format
                formatted_key = (
                    "-----BEGIN PUBLIC KEY-----\n"
                    f"{keycloak_public_key}\n"
                    "-----END PUBLIC KEY-----"
                )
                self.keycloak_public_key = formatted_key
            except Exception as e:
                self.logger.error(f"Failed to format public key: {str(e)}")
                self.keycloak_public_key = None

    def extract_user_context(self, token: str) -> UserContext:
        try:
            if self.jwt_validation_enabled:
                self._validate_configuration()

            jwt_payload = self._parse_jwt(token)
            return self._create_user_context(jwt_payload)
        except APIException:
            raise
        except Exception as e:
            self.logger.error(f"Failed to verify token: {str(e)}")
            raise APIException(
                message="Authentication failed",
                error_code=ErrorCode.INVALID_TOKEN
            )

    def _validate_configuration(self):
        if self.jwt_validation_enabled and not self.keycloak_public_key:
            raise APIException(
                message="Keycloak public key is required for JWT validation",
                error_code=ErrorCode.INTERNAL_SERVER_ERROR
            )

    def _parse_jwt(self, token: str) -> dict:
        if not token:
            raise APIException(
                message="Authentication failed",
                error_code=ErrorCode.INVALID_TOKEN
            )

        if self.jwt_validation_enabled:
            try:
                return jwt.decode(
                    token,
                    self.keycloak_public_key,
                    algorithms=["RS256"],
                    options={"verify_aud": False}
                )
            except jwt.InvalidTokenError as e:
                self.logger.error(f"Failed to decode JWT: {str(e)}")
                raise APIException(
                    message="Authentication failed",
                    error_code=ErrorCode.INVALID_TOKEN
                )

        self.logger.info("JWT validation is disabled")
        return self._parse_unvalidated_jwt(token)

    def _parse_unvalidated_jwt(self, token: str) -> dict:
        try:
            parts = token.split(".")
            if len(parts) != 3:
                raise APIException(
                    message="Invalid JWT format",
                    error_code=ErrorCode.INVALID_TOKEN
                )

            payload = base64.urlsafe_b64decode(parts[1] + "=" * (-len(parts[1]) % 4))
            return json.loads(payload)
        except Exception as e:
            self.logger.error(f"Failed to parse unvalidated JWT: {str(e)}")
            raise APIException(
                message="Invalid token format",
                error_code=ErrorCode.INVALID_TOKEN
            )

    def _create_user_context(self, payload: dict) -> UserContext:
        try:
            user_id = UUID(payload.get("user_id", ""))
            group_id = UUID(payload.get("group_id")) if payload.get("group_id") else None
            roles = self._extract_role(payload)

            return UserContext(
                user_id=user_id,
                group_id=group_id,
                roles=roles,
            )

        except APIException:
            raise
        except Exception as e:
            self.logger.error(f"Failed to create user context: {str(e)}")
            raise APIException(
                message="Invalid token payload",
                error_code=ErrorCode.INVALID_TOKEN
            )

    def _extract_role(self, payload: dict) -> set[Role]:
        try:
            role_str = payload.get("role")
            if not role_str:
                self.logger.error("No role found in payload")
                raise APIException(
                    message="No valid role found",
                    error_code=ErrorCode.INSUFFICIENT_PERMISSIONS
                )

            role = Role.from_string(role_str.strip())
            return {role}

        except ValueError as e:
            self.logger.error(f"Invalid role value: {role_str}, error: {str(e)}")
            raise APIException(
                message="Invalid role",
                error_code=ErrorCode.INSUFFICIENT_PERMISSIONS
            )

    def _extract_has_pin(self, payload: dict) -> bool:
        has_pin = payload.get("has_pin", False)
        return bool(has_pin)