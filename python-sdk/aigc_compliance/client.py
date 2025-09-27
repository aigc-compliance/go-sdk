"""
AIGC Compliance API Client

Official Python client for AIGC Compliance API.
Provides comprehensive AI content detection and watermarking capabilities.
"""
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Union, BinaryIO
from urllib.parse import urljoin
import requests

from .exceptions import (
    ComplianceAPIError,
    ComplianceAuthenticationError,
    ComplianceRateLimitError,
    ComplianceQuotaExceededError,
    ComplianceValidationError,
    ComplianceServerError,
    ComplianceNetworkError,
)
# Note: Using basic types instead of custom types for simplicity


class ComplianceClient:
    """
    Official AIGC Compliance API Client
    
    Provides access to AI content detection, watermarking, and compliance features.
    Supports both EU GDPR and China Cybersecurity Law requirements.
    
    Example:
        >>> from aigc_compliance import ComplianceClient
        >>> client = ComplianceClient(api_key="your_api_key")
        >>> 
        >>> # Detect and watermark AI content
        >>> with open("image.jpg", "rb") as f:
        ...     result = client.comply(f, region="eu")
        >>> print(f"AI Generated: {result['is_ai_generated']}")
    """
    
    DEFAULT_BASE_URL = "https://api.aigc-compliance.com"
    DEFAULT_TIMEOUT = 30
    DEFAULT_MAX_RETRIES = 3
    
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        user_agent: Optional[str] = None,
    ) -> None:
        """
        Initialize AIGC Compliance client
        
        Args:
            api_key: Your AIGC Compliance API key
            base_url: Custom API base URL (defaults to production)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            user_agent: Custom user agent string
        """
        if not api_key:
            raise ComplianceAuthenticationError("API key is required")
        
        self.api_key = api_key
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "User-Agent": user_agent or f"aigc-compliance-python/1.0.0",
            "Content-Type": "application/json",
        })
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> requests.Response:
        """Make HTTP request with error handling and retries"""
        url = urljoin(self.base_url, endpoint)
        
        # Remove Content-Type header for multipart requests
        headers = dict(self.session.headers)
        if files:
            headers.pop("Content-Type", None)
        
        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    files=files,
                    params=params,
                    headers=headers,
                    timeout=self.timeout,
                    **kwargs,
                )
                
                # Handle rate limiting with exponential backoff
                if response.status_code == 429:
                    if attempt < self.max_retries:
                        retry_after = int(response.headers.get("Retry-After", 2 ** attempt))
                        time.sleep(retry_after)
                        continue
                    
                    raise ComplianceRateLimitError(
                        retry_after=int(response.headers.get("Retry-After", 0)),
                        response_data=self._parse_response(response),
                    )
                
                # Handle other HTTP errors
                self._handle_http_error(response)
                return response
                
            except requests.RequestException as e:
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise ComplianceNetworkError(
                    f"Network request failed: {str(e)}", original_error=e
                )
        
        raise ComplianceNetworkError("Maximum retries exceeded")
    
    def _handle_http_error(self, response: requests.Response) -> None:
        """Handle HTTP error responses"""
        if response.status_code < 400:
            return
        
        error_data = self._parse_response(response)
        message = error_data.get("message", f"HTTP {response.status_code}")
        
        if response.status_code == 401:
            raise ComplianceAuthenticationError(message, error_data)
        elif response.status_code == 402:
            raise ComplianceQuotaExceededError(
                message,
                quota_limit=error_data.get("quota_limit"),
                quota_used=error_data.get("quota_used"),
                response_data=error_data,
            )
        elif response.status_code == 422:
            raise ComplianceValidationError(
                message,
                field_errors=error_data.get("field_errors", {}),
                response_data=error_data,
            )
        elif response.status_code >= 500:
            raise ComplianceServerError(message, error_data)
        else:
            raise ComplianceAPIError(message, response.status_code, error_data)
    
    def _parse_response(self, response: requests.Response) -> Dict[str, Any]:
        """Parse JSON response with error handling"""
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"message": response.text or "Unknown error"}
    
    def _get_rate_limit_info(self, response: requests.Response) -> Dict[str, Any]:
        """Extract rate limit information from response headers"""
        return {
            "limit": int(response.headers.get("X-RateLimit-Limit", 0)),
            "remaining": int(response.headers.get("X-RateLimit-Remaining", 0)),
            "reset": datetime.fromtimestamp(
                int(response.headers.get("X-RateLimit-Reset", 0))
            ),
        }
    
    def comply(
        self,
        file_path: str,
        region: str = "EU",
        watermark_position: str = "bottom-right",
        logo_file: Optional[str] = None,
        include_base64: bool = True,
        save_to_disk: bool = False,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Make an image compliant with AIGC regulations.
        
        Args:
            file_path: Path to the image file to process
            region: Region for processing ("EU" or "CN")
            watermark_position: Position for watermark ("top-left", "top-right", "bottom-left", "bottom-right")
            logo_file: Optional path to logo file to include
            include_base64: Whether to include base64 encoded image in response
            save_to_disk: Whether to save the processed image to disk
            output_path: Optional path to save the processed image
            
        Returns:
            Dict containing the compliance response
        """
        if region not in ["EU", "CN"]:
            raise ValueError("Region must be either 'EU' or 'CN'")
        
        try:
            with open(file_path, 'rb') as image_file:
                files = {'file': ('image.jpg', image_file, 'image/jpeg')}
                
                # Add logo file if provided
                if logo_file:
                    with open(logo_file, 'rb') as logo:
                        files['logo_file'] = ('logo.png', logo, 'image/png')
                
                data = {
                    'region': region,
                    'watermark_position': watermark_position,
                    'include_base64': str(include_base64).lower(),
                    'save_to_disk': str(save_to_disk).lower()
                }
                
                response = self.session.post(
                    f"{self.base_url}/comply",
                    files=files,
                    data=data,
                    timeout=30
                )
                response.raise_for_status()
                
                result = response.json()
                
                if output_path and 'processedImage' in result:
                    # Save the processed image
                    if result['processedImage'].startswith('data:'):
                        # Handle base64 encoded image
                        import base64
                        image_data = result['processedImage'].split(',')[1]
                        with open(output_path, 'wb') as f:
                            f.write(base64.b64decode(image_data))
                
                return result
        except FileNotFoundError:
            raise ValueError(f"Image file not found: {file_path}")
        except requests.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Compliance check failed: {str(e)}")
    
    def tag(
        self,
        image_url: str,
        region: str = "EU",
        watermark_text: Optional[str] = None,
        watermark_logo: bool = True,
        metadata_level: str = "basic",
    ) -> Dict[str, Any]:
        """
        Legacy endpoint: Process image from URL for AI detection
        
        Args:
            image_url: URL of the image to process
            region: Compliance region ("EU" or "CN")
            watermark_text: Custom watermark text
            watermark_logo: Whether to apply logo watermark
            metadata_level: Level of compliance metadata
        
        Returns:
            Dict containing the detection results
        """
        if region not in ["EU", "CN"]:
            raise ValueError("Region must be either 'EU' or 'CN'")
            
        data = {
            "image_url": image_url,
            "region": region,
            "watermark_logo": watermark_logo,
            "metadata_level": metadata_level,
        }
        
        if watermark_text:
            data["watermark_text"] = watermark_text
        
        try:
            response = self.session.post(
                f"{self.base_url}/v1/tag",
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Tag operation failed: {str(e)}")

    def health(self) -> Dict[str, Any]:
        """
        Check API health status
        
        Returns:
            Dict containing health status information
        """
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Health check failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Health check failed: {str(e)}")

    def download_file(self, filename: str) -> bytes:
        """
        Download a processed file
        
        Args:
            filename: Name of the file to download
            
        Returns:
            File content as bytes
        """
        try:
            response = self.session.get(
                f"{self.base_url}/download/{filename}",
                timeout=60
            )
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            raise Exception(f"File download failed: {str(e)}")
        except Exception as e:
            raise Exception(f"File download failed: {str(e)}")
    
    def batch_process(
        self,
        items: List[Dict[str, Any]],
        region: str = "EU",
        watermark_logo: bool = True,
        metadata_level: str = "basic",
    ) -> Dict[str, Any]:
        """
        Process multiple images in batch (Enterprise feature)
        
        Args:
            items: List of batch items to process (max 100)
            region: Compliance region ("EU" or "CN")
            watermark_logo: Apply logo watermark to all images
            metadata_level: Level of compliance metadata
        
        Returns:
            Dict with results for all processed items
        
        Raises:
            ValueError: If more than 100 items provided or invalid region
        """
        if len(items) > 100:
            raise ValueError("Maximum 100 items per batch")
            
        if region not in ["EU", "CN"]:
            raise ValueError("Region must be either 'EU' or 'CN'")
        
        # Prepare multipart data
        files = {}
        data = {
            "region": region,
            "watermark_logo": str(watermark_logo).lower(),
            "metadata_level": metadata_level,
        }
        
        for i, item in enumerate(items):
            files[f"images_{i}"] = (f"image_{i}.jpg", item["image"], "image/jpeg")
            if item.get("custom_metadata"):
                data[f"custom_metadata_{i}"] = json.dumps(item["custom_metadata"])
        
        response = self._make_request("POST", "/v1/batch", files=files, data=data)
        result = self._parse_response(response)
        result["_rate_limit"] = self._get_rate_limit_info(response)
        
        return result  # type: ignore
    
    def get_analytics(
        self,
        period: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get usage analytics (Enterprise feature)
        
        Args:
            period: Predefined period ("day", "week", "month")
            start_date: Custom start date (YYYY-MM-DD)
            end_date: Custom end date (YYYY-MM-DD)
        
        Returns:
            AnalyticsResponse with usage statistics
        """
        params = {}
        if period:
            params["period"] = period
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        response = self._make_request("GET", "/v1/analytics", params=params)
        return self._parse_response(response)  # type: ignore
    
    def register_webhook(
        self,
        url: str,
        events: List[str],
        secret: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Register webhook endpoint (Enterprise feature)
        
        Args:
            url: Webhook endpoint URL
            events: List of events to subscribe to
            secret: Optional webhook secret for validation
        
        Returns:
            Webhook registration details
        """
        data = {
            "url": url,
            "events": events,
        }
        if secret:
            data["secret"] = secret
        
        response = self._make_request("POST", "/v1/webhooks", data=data)
        return self._parse_response(response)
    
    def list_webhooks(self) -> List[Dict[str, Any]]:
        """List registered webhooks (Enterprise feature)"""
        response = self._make_request("GET", "/v1/webhooks")
        return self._parse_response(response)["webhooks"]
    
    def delete_webhook(self, webhook_id: str) -> bool:
        """Delete webhook (Enterprise feature)"""
        response = self._make_request("DELETE", f"/v1/webhooks/{webhook_id}")
        return response.status_code == 204
    
    def get_quota_info(self) -> Dict[str, Any]:
        """Get current quota information"""
        response = self._make_request("GET", "/quota")
        return self._parse_response(response)
    
    def close(self) -> None:
        """Close the HTTP session"""
        self.session.close()
    
    def __enter__(self) -> "ComplianceClient":
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit"""
        self.close()