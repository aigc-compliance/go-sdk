"""
AIGC Compliance Python SDK

Official Python SDK for AIGC Compliance API - AI content detection and watermarking.
Supports EU GDPR and China Cybersecurity Law compliance.
"""

from .client import ComplianceClient
from .exceptions import (
    ComplianceAPIError,
    ComplianceAuthenticationError,
    ComplianceRateLimitError,
    ComplianceQuotaExceededError,
    ComplianceValidationError,
)
from .models import (
    ComplianceResponse,
    BatchResponse,
    AnalyticsResponse,
    WebhookEvent,
    Plan,
    Region,
    MetadataLevel,
)

__version__ = "1.0.0"
__author__ = "AIGC Compliance Team"
__email__ = "support@aigc-compliance.com"

__all__ = [
    "ComplianceClient",
    "ComplianceAPIError",
    "ComplianceAuthenticationError", 
    "ComplianceRateLimitError",
    "ComplianceQuotaExceededError",
    "ComplianceValidationError",
    "ComplianceResponse",
    "BatchResponse",
    "AnalyticsResponse",
    "WebhookEvent",
    "Plan",
    "Region",
    "MetadataLevel",
]