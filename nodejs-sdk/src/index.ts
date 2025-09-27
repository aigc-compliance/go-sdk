/**
 * AIGC Compliance Node.js SDK
 * 
 * Official Node.js SDK for AIGC Compliance API
 * AI content detection and watermarking with EU GDPR and China Cybersecurity Law compliance
 * 
 * @example
 * ```typescript
 * import { ComplianceClient } from '@aigc-compliance/sdk';
 * 
 * const client = new ComplianceClient({ apiKey: 'your_api_key' });
 * 
 * // Process image for compliance
 * const result = await client.comply(imageBuffer, { region: 'eu' });
 * console.log(`AI Generated: ${result.is_ai_generated}`);
 * ```
 */

export { ComplianceClient } from './client';
export * from './types';

// Re-export for default import compatibility
import { ComplianceClient } from './client';
export default ComplianceClient;