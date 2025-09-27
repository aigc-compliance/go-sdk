"""
Exceptions for AIGC Compliance SDK
"""
from typing import Optional, Dict, Any


class ComplianceAPIError(Exception):
    """Base exception for all AIGC Compliance API errors"""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class ComplianceAuthenticationError(ComplianceAPIError):
    """Raised when API key is invalid or missing"""
    
    def __init__(
        self,
        message: str = "Invalid or missing API key",
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, 401, response_data)


class ComplianceRateLimitError(ComplianceAPIError):
    """Raised when rate limit is exceeded"""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, 429, response_data)
        self.retry_after = retry_after

    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.retry_after:
            return f"{base_msg} (retry after {self.retry_after}s)"
        return base_msg


class ComplianceQuotaExceededError(ComplianceAPIError):
    """Raised when API quota is exceeded"""
    
    def __init__(
        self,
        message: str = "API quota exceeded",
        quota_limit: Optional[int] = None,
        quota_used: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, 402, response_data)
        self.quota_limit = quota_limit
        self.quota_used = quota_used

    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.quota_limit and self.quota_used:
            return f"{base_msg} ({self.quota_used}/{self.quota_limit})"
        return base_msg


class ComplianceValidationError(ComplianceAPIError):
    """Raised when request validation fails"""
    
    def __init__(
        self,
        message: str = "Request validation failed",
        field_errors: Optional[Dict[str, str]] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, 422, response_data)
        self.field_errors = field_errors or {}


class ComplianceServerError(ComplianceAPIError):
    """Raised when server encounters an internal error"""
    
    def __init__(
        self,
        message: str = "Internal server error",
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, 500, response_data)


class ComplianceNetworkError(ComplianceAPIError):
    """Raised when network request fails"""
    
    def __init__(
        self,
        message: str = "Network request failed",
        original_error: Optional[Exception] = None,
    ) -> None:
        super().__init__(message, None)
        self.original_error = original_error