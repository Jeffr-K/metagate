from datetime import datetime
from typing import Any, TypeVar, Generic

from pydantic import BaseModel, Field

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    success: bool = Field(default=True, description="Response success status")
    status_code: int = Field(description="HTTP status code")
    message: str = Field(description="Response message")
    data: T = Field(default=None, description="Response data")
    timestamp: str = Field(description="Response timestamp")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "status_code": 200,
                "message": "Request processed successfully",
                "data": {"user_id": 1, "name": "John Doe"},
                "timestamp": "2024-06-24T10:30:00.123456"
            }
        }
    }


class ErrorResponse(BaseModel):
    success: bool = Field(default=False, description="Response success status")
    status_code: int = Field(description="HTTP status code")
    message: str = Field(description="Error message")
    error: Any = Field(default=None, description="Error details")
    timestamp: str = Field(description="Response timestamp")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": False,
                "status_code": 400,
                "message": "Bad request",
                "error": {"field": "email", "reason": "Invalid email format"},
                "timestamp": "2024-06-24T10:30:00.123456"
            }
        }
    }


class BusinessResponse(Generic[T]):

    @classmethod
    def success(
        cls,
        status_code: int = 200,
        data: T = None,
        message: str = "Success",
    ) -> SuccessResponse[T]:
        return SuccessResponse[T](
            status_code=status_code,
            message=message,
            data=data,
            timestamp=datetime.now().isoformat()
        )

    @classmethod
    def failure(
        cls,
        status_code: int = 400,
        error: Any = None,
        message: str = "An error occurred",
    ) -> ErrorResponse:
        return ErrorResponse(
            status_code=status_code,
            message=message,
            error=error,
            timestamp=datetime.now().isoformat()
        )