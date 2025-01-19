# src/utils/validation_utils.py
from fastapi import HTTPException
from src.exceptions.error_codes import ErrorCode

def validate_group_id(user_context):
    if not user_context or not user_context.group_id:
        raise HTTPException(
            status_code=ErrorCode.INVALID_GROUP_ID.status,
            detail={
                "code": ErrorCode.INVALID_GROUP_ID.code,
                "message": "Group ID is required"
            }
        )
