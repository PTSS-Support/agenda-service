from typing import Optional
import jwt
from uuid import UUID
from fastapi import HTTPException
from src.auth.context import UserContext
from src.auth.decorators import Role
import json
import base64


class TokenUserExtractor:
    def __init__(self, keycloak_public_key: str, jwt_validation_enabled: bool = True):
        self.keycloak_public_key = keycloak_public_key
        self.jwt_validation_enabled = jwt_validation_enabled

    def extract_user_context(self, token: str) -> UserContext:
        try:
            if self.jwt_validation_enabled:
                payload = jwt.decode(
                    token,
                    self.keycloak_public_key,
                    algorithms=["RS256"],
                    options={"verify_aud": False}
                )
            else:
                # For development/testing, parse without verification
                parts = token.split(".")
                if len(parts) != 3:
                    raise HTTPException(status_code=401, detail="Invalid token format")
                payload = json.loads(base64.b64decode(parts[1] + "==").decode("utf-8"))

            return self._create_user_context(payload)
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))

    def _create_user_context(self, payload: dict) -> UserContext:
        try:
            user_id = UUID(payload.get("user_id"))
            group_id = UUID(payload.get("group_id")) if payload.get("group_id") else None

            # Extract roles
            roles = set()
            if specific_role := payload.get("role"):
                try:
                    roles.add(Role.from_string(specific_role))
                except ValueError:
                    pass

            if system_roles := payload.get("roles", []):
                for role in system_roles:
                    try:
                        roles.add(Role.from_string(role))
                    except ValueError:
                        continue

            has_pin = bool(payload.get("has_pin", False))

            return UserContext(
                user_id=user_id,
                group_id=group_id,
                roles=roles,
                has_pin=has_pin
            )
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Invalid token payload: {str(e)}")
