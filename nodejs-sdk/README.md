# AIGC Compliance Node.js SDK

[![npm version](https://badge.fury.io/js/%40aigc-compliance%2Fsdk.svg)](https://badge.fury.io/js/%40aigc-compliance%2Fsdk)
[![Node.js 14+](https://img.shields.io/badge/node-14+-green.svg)](https://nodejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-4.5+-blue.svg)](https://www.typescriptlang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Official Node.js SDK for AIGC Compliance API - AI content detection and watermarking with EU GDPR and China Cybersecurity Law compliance.

## 🚀 Quick Start

### Installation

```bash
npm install @aigc-compliance/sdk
```

### Basic Usage

```typescript
import { ComplianceClient } from '@aigc-compliance/sdk';
import fs from 'fs';

// Initialize client
const client = new ComplianceClient({
  apiKey: 'your_api_key_here'
});

// Process image for AI detection and compliance
// Basic compliance request (EXACT match with documentation)
const image = fs.readFileSync('ai-generated-image.jpg');
const result = await client.comply(image, { region: 'EU' });

console.log(`Status: ${result.status}`);
console.log(`Region Applied: ${result.region_applied}`);
console.log(`File Hash: ${result.file_hash}`);
console.log(`Download URL: ${result.download_url}`);
console.log(`Processing Time: ${result.processing_time_ms}ms`);
```

### JavaScript (CommonJS)

```javascript
const { ComplianceClient } = require('@aigc-compliance/sdk');
const fs = require('fs');

const client = new ComplianceClient({
  apiKey: 'your_api_key_here'
});

// Advanced request with all options (Professional plan example)
const logoFile = fs.readFileSync('logo.png');
const result = await client.comply(fs.readFileSync('image.jpg'), {
  region: 'CN',
  watermark_text: 'Company Name',
  watermark_position: 'bottom-left',
  logo_file: logoFile,
  include_base64: true,
  save_to_disk: true
});

console.log('Processing completed:', result.status);
    console.log(`AI Generated: ${result.is_ai_generated}`);
  })
  .catch(console.error);
```

## 🌍 Compliance Regions

### EU GDPR Compliance
```typescript
const result = await client.comply(image, { region: 'eu' });
// Returns basic compliance metadata
```

### China Cybersecurity Law Compliance
```typescript
const result = await client.comply(image, { 
  region: 'cn',
  watermarkText: 'AI生成内容',
  metadataLevel: 'detailed'
});
// Returns enhanced metadata with Chinese regulatory compliance
```

## 📖 Features

### ✅ Core Features (All Plans)
- **AI Content Detection**: Advanced ML models for AI-generated content identification
- **Watermarking**: Automatic watermark application with custom text and logos
- **Multi-Region Compliance**: EU GDPR and China Cybersecurity Law support
- **Rate Limiting**: Built-in rate limit handling with exponential backoff
- **Error Handling**: Comprehensive error types with detailed messages
- **TypeScript Support**: Full type definitions included

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

### ComplianceClient Constructor

```typescript
new ComplianceClient({
  apiKey: string;
  baseURL?: string;           // Custom API base URL
  timeout?: number;           // Request timeout (default: 30000ms)
  maxRetries?: number;        // Max retry attempts (default: 3)
  userAgent?: string;         // Custom user agent
})
```

### Core Methods

#### comply()
Process image for AI detection and compliance watermarking.

```typescript
async comply(
  image: Buffer | string,               // Image buffer or file path
  options?: {
    region?: 'eu' | 'cn';              // Compliance region
    watermarkText?: string;             // Custom watermark text
    watermarkLogo?: boolean;            // Apply logo watermark (default: true)
    metadataLevel?: 'basic' | 'detailed'; // Metadata detail level
    customMetadata?: Record<string, any>; // Additional metadata (Enterprise)
  }
): Promise<ComplianceResponse>
```

**Example:**
```typescript
// From file path
const result1 = await client.comply('path/to/image.jpg', {
  region: 'eu',
  watermarkText: 'AI Generated Content'
});

// From buffer
const imageBuffer = fs.readFileSync('image.jpg');
const result2 = await client.comply(imageBuffer, {
  region: 'cn',
  metadataLevel: 'detailed'
});
```

**Response:**
```typescript
interface ComplianceResponse {
  is_ai_generated: boolean;
  confidence: number;
  watermark_applied: boolean;
  processing_time_ms: number;
  quota_remaining: number;
  compliance_metadata: {
    ai_generated_probability: number;
    content_type: string;
    processing_timestamp: string;
    gdpr_compliant: boolean;  // EU region
    // For China region (detailed):
    cybersecurity_law_compliance?: boolean;
    watermark_info?: WatermarkInfo;
    content_labeling?: ContentLabeling;
  };
  _rateLimitInfo?: RateLimitInfo;
}
```

#### tag() (Legacy - Pro/Enterprise)
Process image from URL.

```typescript
async tag(
  imageUrl: string,
  options?: {
    region?: 'eu' | 'cn';
    watermarkText?: string;
    watermarkLogo?: boolean;
    metadataLevel?: 'basic' | 'detailed';
  }
): Promise<ComplianceResponse>
```

**Example:**
```typescript
const result = await client.tag('https://example.com/image.jpg', {
  region: 'cn',
  watermarkText: 'AI生成内容'
});
```

#### batchProcess() (Enterprise)
Process multiple images in batch.

```typescript
async batchProcess(
  items: BatchItem[],           // Max 100 items
  options?: {
    region?: 'eu' | 'cn';
    watermarkLogo?: boolean;
    metadataLevel?: 'basic' | 'detailed';
  }
): Promise<BatchResponse>
```

**Example:**
```typescript
const items = [
  { 
    id: 'img1', 
    image: fs.readFileSync('image1.jpg'),
    custom_metadata: { source: 'upload' }
  },
  { 
    id: 'img2', 
    image: fs.readFileSync('image2.jpg'),
    custom_metadata: { source: 'api' }
  }
];

const result = await client.batchProcess(items, { region: 'eu' });
console.log(`Processed: ${result.successful}/${result.total_processed}`);
```

#### getAnalytics() (Enterprise)
Get usage analytics and insights.

```typescript
async getAnalytics(options?: {
  period?: 'day' | 'week' | 'month';
  startDate?: string;          // YYYY-MM-DD
  endDate?: string;            // YYYY-MM-DD
}): Promise<AnalyticsResponse>
```

**Example:**
```typescript
// Monthly analytics
const monthly = await client.getAnalytics({ period: 'month' });

// Custom period
const custom = await client.getAnalytics({
  startDate: '2024-01-01',
  endDate: '2024-01-31'
});
```

#### Webhook Management (Enterprise)

```typescript
// Register webhook
const webhook = await client.registerWebhook({
  url: 'https://your-app.com/webhooks/compliance',
  events: ['compliance.completed', 'batch.finished'],
  secret: 'your_webhook_secret'
});

// List webhooks
const webhooks = await client.listWebhooks();

// Delete webhook
await client.deleteWebhook(webhook.webhook_id);
```

## 🔧 Advanced Usage

### Error Handling

```typescript
import {
  ComplianceClient,
  ComplianceAuthenticationError,
  ComplianceQuotaExceededError,
  ComplianceRateLimitError,
  ComplianceValidationError
} from '@aigc-compliance/sdk';

try {
  const result = await client.comply(image);
} catch (error) {
  if (error instanceof ComplianceAuthenticationError) {
    console.error('Invalid API key');
  } else if (error instanceof ComplianceQuotaExceededError) {
    console.error(`Quota exceeded: ${error.quotaUsed}/${error.quotaLimit}`);
  } else if (error instanceof ComplianceRateLimitError) {
    console.error(`Rate limited. Retry after ${error.retryAfter}s`);
  } else if (error instanceof ComplianceValidationError) {
    console.error('Validation error:', error.fieldErrors);
  }
}
```

### Custom Configuration

```typescript
const client = new ComplianceClient({
  apiKey: 'your_key',
  baseURL: 'https://custom-api.example.com',
  timeout: 60000,      // 60 seconds
  maxRetries: 5,
  userAgent: 'MyApp/1.0'
});
```

### Rate Limit Information

```typescript
const result = await client.comply(image);
if (result._rateLimitInfo) {
  console.log(`Rate limit: ${result._rateLimitInfo.remaining}/${result._rateLimitInfo.limit}`);
  console.log(`Resets at: ${result._rateLimitInfo.reset}`);
}
```

### Environment Variables

```typescript
// Set API key via environment
const client = new ComplianceClient({
  apiKey: process.env.AIGC_API_KEY!
});
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
   ```typescript
   // Method 1: Direct initialization
   const client = new ComplianceClient({ apiKey: 'sk_live_...' });
   
   // Method 2: Environment variable
   const client = new ComplianceClient({ apiKey: process.env.AIGC_API_KEY });
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
- Node.js 14+
- TypeScript 4.5+ (for TypeScript usage)

### Building from Source

```bash
# Clone repository
git clone https://github.com/aigc-compliance/nodejs-sdk.git
cd nodejs-sdk

# Install dependencies
npm install

# Build TypeScript
npm run build

# Run tests
npm test

# Run tests with coverage
npm run test:coverage
```

### Testing

```typescript
import { ComplianceClient } from '@aigc-compliance/sdk';

describe('AIGC Compliance SDK', () => {
  const client = new ComplianceClient({ apiKey: 'test_key' });
  
  it('should detect AI generated content', async () => {
    const result = await client.comply(testImageBuffer);
    expect(typeof result.is_ai_generated).toBe('boolean');
  });
});
```

## 🔗 Links

- **npm Package**: https://www.npmjs.com/package/@aigc-compliance/sdk
- **Dashboard**: https://www.aigc-compliance.com/dashboard
- **Documentation**: https://www.aigc-compliance.com/docs
- **API Status**: https://status.aigc-compliance.com
- **Support**: support@aigc-compliance.com

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Need help?** Check our [comprehensive documentation](https://www.aigc-compliance.com/docs) or contact [support@aigc-compliance.com](mailto:support@aigc-compliance.com).