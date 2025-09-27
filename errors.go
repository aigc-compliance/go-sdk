package aigcompliance

import "fmt"

// APIError represents a general API error
type APIError struct {
	Message      string                 `json:"message"`
	StatusCode   int                    `json:"status_code"`
	ResponseData map[string]interface{} `json:"response_data"`
}

func (e *APIError) Error() string {
	if e.StatusCode > 0 {
		return fmt.Sprintf("[%d] %s", e.StatusCode, e.Message)
	}
	return e.Message
}

// AuthenticationError represents an authentication error (401)
type AuthenticationError struct {
	Message      string                 `json:"message"`
	ResponseData map[string]interface{} `json:"response_data"`
}

func (e *AuthenticationError) Error() string {
	return fmt.Sprintf("Authentication Error: %s", e.Message)
}

// RateLimitError represents a rate limit error (429)
type RateLimitError struct {
	Message      string                 `json:"message"`
	RetryAfter   int                    `json:"retry_after"`
	ResponseData map[string]interface{} `json:"response_data"`
}

func (e *RateLimitError) Error() string {
	if e.RetryAfter > 0 {
		return fmt.Sprintf("Rate Limit Error: %s (retry after %ds)", e.Message, e.RetryAfter)
	}
	return fmt.Sprintf("Rate Limit Error: %s", e.Message)
}

// QuotaExceededError represents a quota exceeded error (402)
type QuotaExceededError struct {
	Message      string                 `json:"message"`
	QuotaLimit   int                    `json:"quota_limit"`
	QuotaUsed    int                    `json:"quota_used"`
	ResponseData map[string]interface{} `json:"response_data"`
}

func (e *QuotaExceededError) Error() string {
	if e.QuotaLimit > 0 && e.QuotaUsed > 0 {
		return fmt.Sprintf("Quota Exceeded: %s (%d/%d)", e.Message, e.QuotaUsed, e.QuotaLimit)
	}
	return fmt.Sprintf("Quota Exceeded: %s", e.Message)
}

// ValidationError represents a validation error (422)
type ValidationError struct {
	Message      string                 `json:"message"`
	FieldErrors  map[string]string      `json:"field_errors"`
	ResponseData map[string]interface{} `json:"response_data"`
}

func (e *ValidationError) Error() string {
	return fmt.Sprintf("Validation Error: %s", e.Message)
}

// ServerError represents a server error (5xx)
type ServerError struct {
	Message      string                 `json:"message"`
	ResponseData map[string]interface{} `json:"response_data"`
}

func (e *ServerError) Error() string {
	return fmt.Sprintf("Server Error: %s", e.Message)
}

// NetworkError represents a network error
type NetworkError struct {
	Message string `json:"message"`
	Err     error  `json:"-"`
}

func (e *NetworkError) Error() string {
	if e.Err != nil {
		return fmt.Sprintf("Network Error: %s (%v)", e.Message, e.Err)
	}
	return fmt.Sprintf("Network Error: %s", e.Message)
}

func (e *NetworkError) Unwrap() error {
	return e.Err
}