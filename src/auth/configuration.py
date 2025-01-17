from fastapi import FastAPI, Security
from fastapi.openapi.models import SecurityScheme, SecuritySchemeType, APIKeyIn
from typing import Dict, Any


def configure_security_scheme(app: FastAPI, cookie_name: str = "access_token") -> None:
    security_scheme: Dict[str, Any] = {
        "type": "apiKey",
        "in": "cookie",
        "name": cookie_name,
        "description": "JWT token in cookie for authentication"
    }

    # Add security scheme to the OpenAPI specification
    app.openapi_schema = None  # Clear existing schema

    # Update all routes to use this security scheme
    if app.openapi() is not None:
        if "components" not in app.openapi():
            app.openapi()["components"] = {}
        if "securitySchemes" not in app.openapi()["components"]:
            app.openapi()["components"]["securitySchemes"] = {}

        app.openapi()["components"]["securitySchemes"]["CookieAuth"] = security_scheme
        app.openapi()["security"] = [{"CookieAuth": []}]