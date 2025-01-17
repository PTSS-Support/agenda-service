import json
import logging
import traceback
from typing import Dict, Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from src.exceptions.api_exception import APIException
from src.exceptions.error_codes import ErrorCode

logger = logging.getLogger(__name__)

def _log_request_details(request: Request) -> Dict[str, Any]:
    """Helper function to collect common request details for logging"""
    return {
        "method": request.method,
        "url": str(request.url),
        "client_host": request.client.host if request.client else "unknown",
        "headers": dict(request.headers),
    }


def configure_exception_handlers(app: FastAPI):
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Handles FastAPI's RequestValidationError and formats it according to our API standard
        """
        request_details = _log_request_details(request)

        # For query parameters, body, etc.
        model = None
        for error in exc.errors():
            # Try to get the Pydantic model that was used for validation
            if hasattr(error, 'ctx') and hasattr(error['ctx'], 'model'):
                model = error['ctx'].model
                break

        errors = []
        for error in exc.errors():
            field_name = error["loc"][-1]

            # If we have a model and it has field info, use that for the message
            if model and hasattr(model, 'model_fields') and field_name in model.model_fields:
                field_info = model.model_fields[field_name]
                if field_info.description:
                    errors.append(f"Invalid {field_name}: {field_info.description}.")
                    continue

            # Fallback to a generic message
            errors.append(f"Invalid value provided for {field_name}.")

        return JSONResponse(
            status_code=ErrorCode.VALIDATION_ERROR.status,
            content={
                "code": ErrorCode.VALIDATION_ERROR.code,
                "message": " ".join(errors)
            }
        )

    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        request_details = _log_request_details(request)

        # Log based on the severity of the error
        if exc.status_code >= 500:
            logger.error(
                "API error occurred",
                extra={
                    "request": request_details,
                    "error_code": exc.detail.get("code"),
                    "error_message": exc.detail.get("message"),
                    "status_code": exc.status_code,
                    "traceback": traceback.format_exc()
                }
            )
        else:
            logger.warning(
                "API error occurred",
                extra={
                    "request": request_details,
                    "error_code": exc.detail.get("code"),
                    "error_message": exc.detail.get("message"),
                    "status_code": exc.status_code
                }
            )
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """
        Handles any unhandled exceptions to prevent exposing internal errors
        """
        request_details = _log_request_details(request)
        error_details = {
            "request": request_details,
            "error_type": exc.__class__.__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc()
        }

        # Just add a distinctive marker to make it clear our handler caught it
        logger.error(
            "=== Exception Handler Caught: {} ===".format(exc.__class__.__name__),
            extra=error_details
        )

        logger.error(f"Error message: {str(exc)}")
        logger.debug(f"Full traceback:\n{traceback.format_exc()}")

        return JSONResponse(
            status_code=500,
            content={
                "code": ErrorCode.INTERNAL_SERVER_ERROR.code,
                "message": "An unexpected error occurred"
            }
        )