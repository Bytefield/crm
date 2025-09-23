"""
Security utilities for input validation, output sanitization, and protection.
"""
import re
from typing import Any, Dict, List, Optional, Union
from fastapi import HTTPException, status
from pydantic import BaseModel, validator
import html
from datetime import datetime

class SanitizedStr(str):
    """String class that automatically escapes HTML/JS content."""
    def __new__(cls, value: Any):
        if value is None:
            return None
        # Convert to string and escape HTML
        escaped = html.escape(str(value))
        # Remove any remaining HTML tags
        clean = re.sub(r'<[^>]*>', '', escaped)
        return super().__new__(cls, clean)

def sanitize_input(data: Any) -> Any:
    """Recursively sanitize input data."""
    if isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    elif isinstance(data, str):
        return SanitizedStr(data)
    return data

def validate_email(email: str) -> str:
    """Validate and sanitize email address."""
    if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    return email.lower().strip()

def validate_password(password: str) -> str:
    """Validate password strength."""
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    if not re.search(r'[A-Z]', password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one uppercase letter"
        )
    if not re.search(r'[a-z]', password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one lowercase letter"
        )
    if not re.search(r'\d', password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one number"
        )
    return password

class SQLInjectionProtection(BaseModel):
    """Base model with SQL injection protection."""
    class Config:
        extra = 'forbid'  # Prevent extra fields
        anystr_strip_whitespace = True  # Strip whitespace from strings

    @validator('*', pre=True)
    def check_sql_injection(cls, v):
        if isinstance(v, str):
            # Check for common SQL injection patterns
            sql_injection_patterns = [
                r'(?i)(\b(?:union|select|insert|delete|update|drop|alter|create|truncate|exec|xp_|--|;|/\*|\*/)\b)',
                r'(\b(?:or\s+\d+=\d+\s*--|\s*;\s*--|/\*.*\*/|\b(?:true|false|null)\b|\b(?:and|or)\s+[\w\d]+\s*[=<>!]+\s*[\w\d]+\s*--))',
                r'(\b(?:select\s+\*\s+from|insert\s+into|delete\s+from|update\s+\w+\s+set|drop\s+table|create\s+table|truncate\s+table)\b)'
            ]
            
            for pattern in sql_injection_patterns:
                if re.search(pattern, v, re.IGNORECASE):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid input detected"
                    )
        return v

def sanitize_output(data: Any) -> Any:
    """Sanitize output data to prevent XSS and injection attacks."""
    if isinstance(data, dict):
        return {k: sanitize_output(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_output(item) for item in data]
    elif isinstance(data, str):
        # Escape HTML and JavaScript
        return html.escape(data)
    return data

def validate_date_format(date_str: str) -> str:
    """Validate date format (YYYY-MM-DD)."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return date_str
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )

def validate_integer(value: Any) -> int:
    """Validate and convert to integer."""
    try:
        return int(value)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid integer value"
        )
