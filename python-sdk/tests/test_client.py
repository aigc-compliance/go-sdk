"""
Test suite for AIGC Compliance Python SDK
"""
import pytest
import json
from unittest.mock import Mock, patch, mock_open
from requests import Response
from aigc_compliance import (
    ComplianceClient,
    ComplianceAuthenticationError,
    ComplianceRateLimitError,
    ComplianceQuotaExceededError,
    ComplianceValidationError,
)


class TestComplianceClient:
    """Test ComplianceClient functionality"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return ComplianceClient(api_key="test_key")
    
    @pytest.fixture
    def mock_response(self):
        """Mock successful response"""
        response = Mock(spec=Response)
        response.status_code = 200
        response.json.return_value = {
            "is_ai_generated": True,
            "confidence": 0.95,
            "watermark_applied": True,
            "processing_time_ms": 1250,
            "quota_remaining": 245,
            "compliance_metadata": {
                "ai_generated_probability": 0.95,
                "content_type": "image/jpeg",
                "processing_timestamp": "2024-01-15T10:30:45Z",
                "gdpr_compliant": True,
            }
        }
        response.headers = {
            "X-RateLimit-Limit": "1000",
            "X-RateLimit-Remaining": "999",
            "X-RateLimit-Reset": "1642248645",
        }
        return response
    
    def test_client_initialization(self):
        """Test client initialization"""
        client = ComplianceClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.base_url == ComplianceClient.DEFAULT_BASE_URL
        assert "Bearer test_key" in client.session.headers["Authorization"]
    
    def test_client_initialization_no_api_key(self):
        """Test client initialization without API key"""
        with pytest.raises(ComplianceAuthenticationError):
            ComplianceClient(api_key="")
    
    @patch('requests.Session.request')
    def test_comply_with_file_path(self, mock_request, client, mock_response):
        """Test comply with file path"""
        mock_request.return_value = mock_response
        
        with patch("builtins.open", mock_open(read_data=b"fake_image_data")):
            result = client.comply("test_image.jpg", region="eu")
        
        assert result["is_ai_generated"] is True
        assert result["confidence"] == 0.95
        assert "_rate_limit" in result
        mock_request.assert_called_once()
    
    @patch('requests.Session.request')
    def test_comply_with_bytes(self, mock_request, client, mock_response):
        """Test comply with bytes data"""
        mock_request.return_value = mock_response
        image_data = b"fake_image_data"
        
        result = client.comply(image_data, region="cn", watermark_text="AI生成")
        
        assert result["is_ai_generated"] is True
        mock_request.assert_called_once()
        
        # Check that watermark_text was included in request
        call_args = mock_request.call_args
        assert "data" in call_args.kwargs
    
    @patch('requests.Session.request')
    def test_tag_endpoint(self, mock_request, client, mock_response):
        """Test legacy tag endpoint"""
        mock_request.return_value = mock_response
        
        result = client.tag("https://example.com/image.jpg", region="eu")
        
        assert result["is_ai_generated"] is True
        mock_request.assert_called_once()
        
        # Verify endpoint
        call_args = mock_request.call_args
        assert "/v1/tag" in str(call_args)
    
    @patch('requests.Session.request')
    def test_batch_process(self, mock_request, client):
        """Test batch processing"""
        batch_response = Mock(spec=Response)
        batch_response.status_code = 200
        batch_response.json.return_value = {
            "batch_id": "batch_123",
            "total_processed": 2,
            "successful": 2,
            "failed": 0,
            "processing_time_ms": 2500,
            "results": [
                {
                    "id": "img1",
                    "is_ai_generated": True,
                    "confidence": 0.95,
                    "watermark_applied": True,
                    "processing_time_ms": 1200,
                    "compliance_metadata": {},
                    "error": None,
                },
                {
                    "id": "img2",
                    "is_ai_generated": False,
                    "confidence": 0.25,
                    "watermark_applied": False,
                    "processing_time_ms": 1300,
                    "compliance_metadata": {},
                    "error": None,
                }
            ]
        }
        batch_response.headers = {"X-RateLimit-Limit": "100", "X-RateLimit-Remaining": "98", "X-RateLimit-Reset": "1642248645"}
        mock_request.return_value = batch_response
        
        items = [
            {"id": "img1", "image": b"image1_data"},
            {"id": "img2", "image": b"image2_data", "custom_metadata": {"source": "upload"}},
        ]
        
        result = client.batch_process(items, region="eu")
        
        assert result["batch_id"] == "batch_123"
        assert result["successful"] == 2
        mock_request.assert_called_once()
    
    def test_batch_process_too_many_items(self, client):
        """Test batch processing with too many items"""
        items = [{"id": f"img{i}", "image": b"data"} for i in range(101)]
        
        with pytest.raises(ComplianceValidationError) as exc_info:
            client.batch_process(items)
        
        assert "Maximum 100 items" in str(exc_info.value)
    
    @patch('requests.Session.request')
    def test_get_analytics(self, mock_request, client):
        """Test analytics endpoint"""
        analytics_response = Mock(spec=Response)
        analytics_response.status_code = 200
        analytics_response.json.return_value = {
            "current_period": {
                "total_requests": 150,
                "ai_generated_detected": 75,
                "watermarks_applied": 140,
                "quota_used": 150,
                "quota_limit": 1000,
                "period_start": "2024-01-01T00:00:00Z",
                "period_end": "2024-01-31T23:59:59Z",
            },
            "previous_period": {
                "total_requests": 120,
                "ai_generated_detected": 60,
                "watermarks_applied": 115,
                "quota_used": 120,
                "quota_limit": 1000,
                "period_start": "2023-12-01T00:00:00Z",
                "period_end": "2023-12-31T23:59:59Z",
            },
            "growth_rate": 0.25
        }
        mock_request.return_value = analytics_response
        
        result = client.get_analytics(period="month")
        
        assert result["growth_rate"] == 0.25
        assert result["current_period"]["total_requests"] == 150
        mock_request.assert_called_once()
    
    @patch('requests.Session.request')
    def test_webhook_operations(self, mock_request, client):
        """Test webhook CRUD operations"""
        # Test register webhook
        webhook_response = Mock(spec=Response)
        webhook_response.status_code = 200
        webhook_response.json.return_value = {
            "webhook_id": "wh_123",
            "url": "https://example.com/webhook",
            "events": ["compliance.completed"],
            "secret": "wh_secret_123",
            "created_at": "2024-01-15T10:30:45Z",
        }
        mock_request.return_value = webhook_response
        
        result = client.register_webhook(
            url="https://example.com/webhook",
            events=["compliance.completed"],
            secret="my_secret"
        )
        
        assert result["webhook_id"] == "wh_123"
        mock_request.assert_called_once()
        
        # Test list webhooks
        list_response = Mock(spec=Response)
        list_response.status_code = 200
        list_response.json.return_value = {
            "webhooks": [
                {"webhook_id": "wh_123", "url": "https://example.com/webhook"}
            ]
        }
        mock_request.return_value = list_response
        
        webhooks = client.list_webhooks()
        assert len(webhooks) == 1
        
        # Test delete webhook
        delete_response = Mock(spec=Response)
        delete_response.status_code = 204
        mock_request.return_value = delete_response
        
        result = client.delete_webhook("wh_123")
        assert result is True
    
    @patch('requests.Session.request')
    def test_error_handling_401(self, mock_request, client):
        """Test authentication error handling"""
        error_response = Mock(spec=Response)
        error_response.status_code = 401
        error_response.json.return_value = {"message": "Invalid API key"}
        mock_request.return_value = error_response
        
        with pytest.raises(ComplianceAuthenticationError) as exc_info:
            client.comply(b"fake_data")
        
        assert "Invalid API key" in str(exc_info.value)
    
    @patch('requests.Session.request')
    def test_error_handling_429(self, mock_request, client):
        """Test rate limit error handling"""
        error_response = Mock(spec=Response)
        error_response.status_code = 429
        error_response.headers = {"Retry-After": "60"}
        error_response.json.return_value = {"message": "Rate limit exceeded"}
        mock_request.return_value = error_response
        
        with pytest.raises(ComplianceRateLimitError) as exc_info:
            client.comply(b"fake_data")
        
        assert exc_info.value.retry_after == 60
    
    @patch('requests.Session.request')
    def test_error_handling_402(self, mock_request, client):
        """Test quota exceeded error handling"""
        error_response = Mock(spec=Response)
        error_response.status_code = 402
        error_response.json.return_value = {
            "message": "Quota exceeded",
            "quota_limit": 1000,
            "quota_used": 1000,
        }
        mock_request.return_value = error_response
        
        with pytest.raises(ComplianceQuotaExceededError) as exc_info:
            client.comply(b"fake_data")
        
        assert exc_info.value.quota_limit == 1000
        assert exc_info.value.quota_used == 1000
    
    @patch('requests.Session.request')
    def test_retry_logic(self, mock_request, client):
        """Test retry logic for transient failures"""
        # First call fails with 429, second succeeds
        error_response = Mock(spec=Response)
        error_response.status_code = 429
        error_response.headers = {"Retry-After": "1"}
        error_response.json.return_value = {"message": "Rate limit exceeded"}
        
        success_response = Mock(spec=Response)
        success_response.status_code = 200
        success_response.json.return_value = {"is_ai_generated": True, "confidence": 0.95}
        success_response.headers = {"X-RateLimit-Limit": "1000", "X-RateLimit-Remaining": "999", "X-RateLimit-Reset": "1642248645"}
        
        mock_request.side_effect = [error_response, success_response]
        
        # This should succeed after retry
        with patch('time.sleep'):  # Mock sleep to speed up test
            result = client.comply(b"fake_data")
        
        assert result["is_ai_generated"] is True
        assert mock_request.call_count == 2
    
    def test_context_manager(self):
        """Test context manager functionality"""
        with ComplianceClient(api_key="test_key") as client:
            assert client.api_key == "test_key"
        # Session should be closed after context exit
    
    @patch('requests.Session.request')
    def test_quota_info(self, mock_request, client):
        """Test quota information endpoint"""
        quota_response = Mock(spec=Response)
        quota_response.status_code = 200
        quota_response.json.return_value = {
            "quota_limit": 1000,
            "quota_used": 150,
            "quota_remaining": 850,
            "plan": "pro",
            "billing_period_start": "2024-01-01T00:00:00Z",
            "billing_period_end": "2024-01-31T23:59:59Z",
        }
        mock_request.return_value = quota_response
        
        result = client.get_quota_info()
        
        assert result["quota_remaining"] == 850
        assert result["plan"] == "pro"
        mock_request.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])