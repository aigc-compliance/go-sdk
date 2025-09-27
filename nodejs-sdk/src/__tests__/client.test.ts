import { ComplianceClient } from '../client';
import { ComplianceAuthenticationError } from '../types';

describe('ComplianceClient', () => {
  let client: ComplianceClient;

  beforeEach(() => {
    client = new ComplianceClient({ apiKey: 'test-api-key', baseURL: 'https://api.test.com' });
  });

  describe('Constructor', () => {
    it('should create client with API key', () => {
      expect(client).toBeDefined();
    });

    it('should throw error for empty API key', () => {
      expect(() => new ComplianceClient({ apiKey: '' })).toThrow(ComplianceAuthenticationError);
    });

    it('should accept custom options', () => {
      const customClient = new ComplianceClient({
        apiKey: 'test-key',
        baseURL: 'https://custom.api.com',
        timeout: 60000,
        maxRetries: 5
      });

      expect(customClient).toBeDefined();
    });
  });

  describe('API Methods', () => {
    it('should have all required methods per documentation', () => {
      expect(typeof client.comply).toBe('function');
      expect(typeof client.tag).toBe('function');
      expect(typeof client.batchProcess).toBe('function');
      expect(typeof client.getAnalytics).toBe('function');
      expect(typeof client.registerWebhook).toBe('function');
      expect(typeof client.listWebhooks).toBe('function');
      expect(typeof client.deleteWebhook).toBe('function');
      expect(typeof client.getQuotaInfo).toBe('function');
      expect(typeof client.getHealth).toBe('function');
      expect(typeof client.downloadFile).toBe('function');
    });
  });
});