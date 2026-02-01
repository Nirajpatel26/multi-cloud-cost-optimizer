# Custom exceptions for the API
from fastapi import HTTPException, status


class DatabaseConnectionError(HTTPException):
    """Raised when database connection fails"""
    def __init__(self, detail: str = "Failed to connect to database"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail
        )


class InvalidDateFormatError(HTTPException):
    """Raised when date format is invalid"""
    def __init__(self, field_name: str, provided_value: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "INVALID_DATE_FORMAT",
                    "message": f"Invalid date format for {field_name}. Expected YYYY-MM-DD",
                    "details": {
                        "parameter": field_name,
                        "provided_value": provided_value
                    }
                }
            }
        )


class ResourceNotFoundError(HTTPException):
    """Raised when requested resource is not found"""
    def __init__(self, resource_type: str, resource_id: str = None):
        detail = f"{resource_type} not found"
        if resource_id:
            detail += f" with id: {resource_id}"
        
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "RESOURCE_NOT_FOUND",
                    "message": detail
                }
            }
        )


class InvalidParameterError(HTTPException):
    """Raised when request parameter is invalid"""
    def __init__(self, parameter: str, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "INVALID_PARAMETER",
                    "message": message,
                    "details": {
                        "parameter": parameter
                    }
                }
            }
        )
