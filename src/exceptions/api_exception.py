from fastapi import HTTPException
from src.exceptions.error_codes import ErrorCode


class APIException(HTTPException):
    def __init__(self, message: str, error_code: ErrorCode):
        super().__init__(status_code=error_code.status, detail={
            "message": message,
            "code": error_code.code
        })
