from enum import Enum
import starlette.status as http_status


class ErrorCode(Enum):
    INVALID_TOKEN = ("AUTH0001", http_status.HTTP_401_UNAUTHORIZED)
    INSUFFICIENT_PERMISSIONS = ("AUTH0002", http_status.HTTP_403_FORBIDDEN)
    INVALID_GROUP_ID = ("AUTH0003", http_status.HTTP_400_BAD_REQUEST)

    VALIDATION_ERROR = ("SYS0001", http_status.HTTP_400_BAD_REQUEST)
    INTERNAL_SERVER_ERROR = ("SYS0002", http_status.HTTP_500_INTERNAL_SERVER_ERROR)

    BAD_REQUEST = ("AGENDA0001", http_status.HTTP_400_BAD_REQUEST)

    def __init__(self, code, status=http_status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.code = code
        self.status = status
