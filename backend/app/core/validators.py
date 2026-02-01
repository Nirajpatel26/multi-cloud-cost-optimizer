# Validation utilities for API inputs
from datetime import datetime
from typing import Optional
from app.core.exceptions import InvalidDateFormatError, InvalidParameterError


def validate_date_format(date_string: str, field_name: str) -> datetime:
    """
    Validate and parse date string in YYYY-MM-DD format
    
    Args:
        date_string: Date string to validate
        field_name: Name of the field (for error messages)
    
    Returns:
        datetime object if valid
    
    Raises:
        InvalidDateFormatError: If date format is invalid
    """
    if not date_string:
        return None
    
    try:
        # Try to parse the date
        parsed_date = datetime.strptime(date_string, "%Y-%m-%d")
        return parsed_date
    except ValueError:
        raise InvalidDateFormatError(field_name, date_string)


def validate_date_range(start_date: Optional[str], end_date: Optional[str]) -> tuple:
    """
    Validate start and end date range
    
    Args:
        start_date: Start date string
        end_date: End date string
    
    Returns:
        Tuple of (start_datetime, end_datetime)
    
    Raises:
        InvalidParameterError: If end_date is before start_date
    """
    start_dt = validate_date_format(start_date, "start_date") if start_date else None
    end_dt = validate_date_format(end_date, "end_date") if end_date else None
    
    # Check if end_date is before start_date
    if start_dt and end_dt and end_dt < start_dt:
        raise InvalidParameterError(
            "date_range",
            "end_date must be after start_date"
        )
    
    return start_dt, end_dt


def validate_cpu_threshold(threshold: float) -> float:
    """
    Validate CPU threshold percentage
    
    Args:
        threshold: CPU threshold value
    
    Returns:
        Validated threshold
    
    Raises:
        InvalidParameterError: If threshold is not between 0 and 100
    """
    if threshold < 0 or threshold > 100:
        raise InvalidParameterError(
            "cpu_threshold",
            "CPU threshold must be between 0 and 100"
        )
    
    return threshold


def validate_region(region: str) -> str:
    """
    Validate AWS region format
    
    Args:
        region: AWS region string
    
    Returns:
        Validated region
    
    Raises:
        InvalidParameterError: If region format is invalid
    """
    # Basic validation - regions should follow pattern like us-east-1
    valid_patterns = ["us-", "eu-", "ap-", "sa-", "ca-", "me-", "af-"]
    
    if not any(region.startswith(pattern) for pattern in valid_patterns):
        raise InvalidParameterError(
            "region",
            f"Invalid AWS region format: {region}"
        )
    
    return region
