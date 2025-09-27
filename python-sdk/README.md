# AIGC Compliance Python SDK

[![PyPI version](https://badge.fury.io/py/aigc-compliance.svg)](https://badge.fury.io/py/aigc-compliance)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Official Python SDK for AIGC Compliance API - AI content detection and watermarking with EU GDPR and China Cybersecurity Law compliance.

## 🚀 Quick Start

### Installation

```bash
pip install aigc-compliance
```

### Basic Usage

```python
from aigc_compliance import ComplianceClient

# Initialize client
client = ComplianceClient(api_key="your_api_key_here")

# Process image for AI detection and compliance
result = client.comply(
    file_path="image.jpg", 
    region="EU",
    watermark_position="bottom-right",
    include_base64=True
)

print(f"Compliant: {result['compliant']}")
print(f"AI Probability: {result['ai_probability']}")
print(f"Processing Time: {result['processing_time']}ms")
```

## 🌍 Compliance Regions

### EU GDPR Compliance
```python
result = client.comply(
    file_path="image.jpg",
    region="EU",
    watermark_position="bottom-right"
)
# Returns compliance result with EU GDPR metadata
```

### China Cybersecurity Law Compliance
```python
result = client.comply(
    file_path="image.jpg", 
    region="CN",
    watermark_position="top-left",
    logo_file="custom_logo.png",
    save_to_disk=True
)
# Returns compliance result with China Cybersecurity Law compliance
```

## 📖 Features

### ✅ Core Features (All Plans)
- **AI Content Detection**: Advanced ML models for AI-generated content identification
- **Watermarking**: Automatic watermark application with custom text and logos
- **Multi-Region Compliance**: EU GDPR and China Cybersecurity Law support
- **Rate Limiting**: Built-in rate limit handling with exponential backoff
- **Error Handling**: Comprehensive error types with detailed messages

### 🚀 Pro Features
- **Custom Watermarks**: Personalized watermark text and positioning
- **Metadata Levels**: Basic and detailed compliance metadata
- **Legacy Support**: `/v1/tag` endpoint for URL-based processing

### 🏢 Enterprise Features
- **Batch Processing**: Process up to 100 images in a single request
- **Webhooks**: Real-time notifications for completed processing
- **Advanced Analytics**: Detailed usage statistics and insights
- **Custom Metadata**: Attach additional metadata to processing requests

## 📚 API Reference

### ComplianceClient

#### Constructor
```python
ComplianceClient(
    api_key: str,
    base_url: Optional[str] = None,
    timeout: float = 30,
    max_retries: int = 3,
    user_agent: Optional[str] = None
)
```

#### Core Methods

##### comply()
Process image for AI detection and compliance watermarking.

```python
def comply(
    file_path: str,
    region: str = "EU",
    watermark_position: str = "bottom-right",
    logo_file: Optional[str] = None,
    include_base64: bool = True,
    save_to_disk: bool = False,
    output_path: Optional[str] = None
) -> ComplianceResponse
```

**Parameters:**
- `image`: Image file (file object, bytes, or file path)
- `region`: Compliance region ("eu" for GDPR, "cn" for China)
- `watermark_text`: Custom watermark text
- `watermark_logo`: Whether to apply logo watermark
- `metadata_level`: Level of compliance metadata
- `custom_metadata`: Additional metadata (Enterprise only)

**Returns:**
```python
{
    "is_ai_generated": bool,
    "confidence": float,
    "watermark_applied": bool,
    "processing_time_ms": int,
    "quota_remaining": int,
    "compliance_metadata": {
        "ai_generated_probability": float,
        "content_type": str,
        "processing_timestamp": str,
        "gdpr_compliant": bool,  # EU region
        # For China region (detailed):
        "cybersecurity_law_compliance": bool,
        "watermark_info": {...},
        "content_labeling": {...}
    }
}
```

##### tag() (Legacy)
Process image from URL (Pro/Enterprise only).

```python
def tag(
    image_url: str,
    region: Literal["eu", "cn"] = "eu",
    watermark_text: Optional[str] = None,
    watermark_logo: bool = True,
    metadata_level: Literal["basic", "detailed"] = "basic",
) -> ComplianceResponse
```

##### batch_process() (Enterprise)
Process multiple images in batch.

```python
def batch_process(
    items: List[BatchItem],
    region: Literal["eu", "cn"] = "eu",
    watermark_logo: bool = True,
    metadata_level: Literal["basic", "detailed"] = "basic",
) -> BatchResponse
```

**Example:**
```python
items = [
    {"id": "img1", "image": image1_bytes, "custom_metadata": {"source": "upload"}},
    {"id": "img2", "image": image2_bytes, "custom_metadata": {"source": "api"}},
]
result = client.batch_process(items, region="eu")
```

##### get_analytics() (Enterprise)
Get usage analytics and insights.

```python
def get_analytics(
    period: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> AnalyticsResponse
```

##### Webhook Management (Enterprise)
```python
# Register webhook
webhook = client.register_webhook(
    url="https://your-app.com/webhooks/compliance",
    events=["compliance.completed", "batch.finished"],
    secret="your_webhook_secret"
)

# List webhooks
webhooks = client.list_webhooks()

# Delete webhook
client.delete_webhook(webhook_id="webhook_123")
```

## 🔧 Advanced Usage

### Context Manager
```python
with ComplianceClient(api_key="your_key") as client:
    result = client.comply(image, region="eu")
    # Client automatically closed
```

### Error Handling
```python
from aigc_compliance import (
    ComplianceClient,
    ComplianceAuthenticationError,
    ComplianceQuotaExceededError,
    ComplianceRateLimitError,
)

try:
    result = client.comply(image)
except ComplianceAuthenticationError:
    print("Invalid API key")
except ComplianceQuotaExceededError as e:
    print(f"Quota exceeded: {e.quota_used}/{e.quota_limit}")
except ComplianceRateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
```

### Custom Configuration
```python
client = ComplianceClient(
    api_key="your_key",
    base_url="https://custom-api.example.com",
    timeout=60,
    max_retries=5,
    user_agent="MyApp/1.0"
)
```

## 📊 Response Examples

### Basic EU Response
```json
{
  "is_ai_generated": true,
  "confidence": 0.95,
  "watermark_applied": true,
  "processing_time_ms": 1250,
  "quota_remaining": 245,
  "compliance_metadata": {
    "ai_generated_probability": 0.95,
    "content_type": "image/jpeg",
    "processing_timestamp": "2024-01-15T10:30:45Z",
    "gdpr_compliant": true
  }
}
```

### Detailed China Response
```json
{
  "is_ai_generated": true,
  "confidence": 0.97,
  "watermark_applied": true,
  "processing_time_ms": 1450,
  "quota_remaining": 244,
  "compliance_metadata": {
    "ai_generated_probability": 0.97,
    "content_type": "image/jpeg",
    "processing_timestamp": "2024-01-15T10:30:45Z",
    "cybersecurity_law_compliance": true,
    "watermark_info": {
      "text": "AI生成内容",
      "logo_applied": true,
      "position": "bottom-right",
      "transparency": 0.7
    },
    "content_labeling": {
      "category": "ai_generated",
      "compliance_level": "full",
      "regulatory_notes": "符合网络安全法要求"
    }
  }
}
```

## 🔐 Authentication

1. **Get API Key**: Sign up at [AIGC Compliance Dashboard](https://www.aigc-compliance.com/dashboard)
2. **Set API Key**: 
   ```python
   # Method 1: Direct initialization
   client = ComplianceClient(api_key="sk_live_...")
   
   # Method 2: Environment variable
   import os
   client = ComplianceClient(api_key=os.getenv("AIGC_API_KEY"))
   ```

## 📈 Plans & Quotas

| Plan | Monthly Quota | Features |
|------|---------------|----------|
| **Free** | 10 requests | Basic detection, EU watermarks |
| **Starter** | 100 requests | Custom watermarks, both regions |
| **Pro** | 1,000 requests | Legacy endpoints, detailed metadata |
| **Enterprise** | 10,000+ requests | Batch processing, webhooks, analytics |

## 🛠️ Development

### Requirements
- Python 3.7+
- `requests >= 2.25.0`

### Optional Dependencies
```bash
# Development tools
pip install aigc-compliance[dev]
```

### Testing
```python
import pytest
from aigc_compliance import ComplianceClient

def test_compliance_detection():
    client = ComplianceClient(api_key="test_key")
    # Add your test image
    with open("test_image.jpg", "rb") as f:
        result = client.comply(f)
    assert "is_ai_generated" in result
```

## 🔗 Links

- **Dashboard**: https://www.aigc-compliance.com/dashboard
- **Documentation**: https://www.aigc-compliance.com/docs
- **API Status**: https://status.aigc-compliance.com
- **Support**: support@aigc-compliance.com

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Need help?** Check our [comprehensive documentation](https://www.aigc-compliance.com/docs) or contact [support@aigc-compliance.com](mailto:support@aigc-compliance.com).