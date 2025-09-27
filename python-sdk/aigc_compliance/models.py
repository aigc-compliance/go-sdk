"""
Type definitions for AIGC Compliance SDK
"""
from typing import Dict, Any, Optional, List, Union, Literal
from datetime import datetime

try:
    from typing_extensions import TypedDict
except ImportError:
    from typing import TypedDict

# Enums for better type safety
Plan = Literal["free", "starter", "pro", "enterprise"]
Region = Literal["eu", "cn"]
MetadataLevel = Literal["basic", "detailed"]

class ComplianceMetadata(TypedDict, total=False):
    """Metadata for EU GDPR compliance"""
    ai_generated_probability: float
    content_type: str
    processing_timestamp: str
    gdpr_compliant: bool

class ChinaComplianceMetadata(TypedDict, total=False):
    """Enhanced metadata for China Cybersecurity Law compliance"""
    ai_generated_probability: float
    content_type: str
    processing_timestamp: str
    cybersecurity_law_compliance: bool
    watermark_info: Dict[str, Any]
    content_labeling: Dict[str, str]

class WatermarkInfo(TypedDict, total=False):
    """Watermark information"""
    text: Optional[str]
    logo_applied: bool
    position: str
    transparency: float

class ComplianceResponse(TypedDict):
    """Response from /comply endpoint"""
    is_ai_generated: bool
    confidence: float
    watermark_applied: bool
    processing_time_ms: int
    quota_remaining: int
    compliance_metadata: Union[ComplianceMetadata, ChinaComplianceMetadata]

class BatchItem(TypedDict):
    """Single item in batch processing"""
    id: str
    image: bytes
    custom_metadata: Optional[Dict[str, Any]]

class BatchResult(TypedDict):
    """Result for single batch item"""
    id: str
    is_ai_generated: bool
    confidence: float
    watermark_applied: bool
    processing_time_ms: int
    compliance_metadata: Union[ComplianceMetadata, ChinaComplianceMetadata]
    error: Optional[str]

class BatchResponse(TypedDict):
    """Response from /batch endpoint"""
    batch_id: str
    total_processed: int
    successful: int
    failed: int
    processing_time_ms: int
    results: List[BatchResult]

class AnalyticsData(TypedDict):
    """Analytics data structure"""
    total_requests: int
    ai_generated_detected: int
    watermarks_applied: int
    quota_used: int
    quota_limit: int
    period_start: str
    period_end: str

class AnalyticsResponse(TypedDict):
    """Response from /analytics endpoint"""
    current_period: AnalyticsData
    previous_period: AnalyticsData
    growth_rate: float

class WebhookEventData(TypedDict):
    """Webhook event data"""
    event_id: str
    timestamp: str
    data: Dict[str, Any]

class WebhookEvent(TypedDict):
    """Webhook event structure"""
    event: Literal["compliance.completed", "batch.finished", "quota.exceeded"]
    data: WebhookEventData

class RateLimitInfo(TypedDict):
    """Rate limit information"""
    limit: int
    remaining: int
    reset: datetime