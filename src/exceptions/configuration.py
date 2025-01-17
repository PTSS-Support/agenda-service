from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from src.exceptions.api_exception import APIException
from src.exceptions.error_codes import ErrorCode


def configure_exception_handlers(app: FastAPI):
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Handles FastAPI's RequestValidationError and formats it according to our API standard
        """
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
        """
        Handles our custom APIException
        """
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """
        Handles any unhandled exceptions to prevent exposing internal errors, if you get this, it might be a different status code
        """
        return JSONResponse(
            status_code=500,
            content={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        )