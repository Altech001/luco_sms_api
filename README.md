# Luco SMS SDK

Official Python SDK for the Luco SMS API system.

## Installation

```bash
pip install lucosms
```

## Usage

```python
from lucosdk import LucoSMSClient

# Initialize the client
client = LucoSMSClient(api_key="your_api_key")

# Send an SMS
response = client.send_sms(
    recipient="+256700000000",
    message="Hello from Luco SMS!"
)

# Check wallet balance
balance = client.get_balance()

# Get delivery report
report = client.get_delivery_report(sms_id=123)

# Get SMS history
history = client.get_sms_history()
```

## Documentation

For detailed API documentation, visit our [official documentation](https://docs.lucosms.com).

## License

This project is licensed under the MIT License - see the LICENSE file for details.


##
I've enhanced the rate limiting functionality and integrated it across the application. Here's what's been done:

Enhanced the rate limiter module with:

Configurable rate limits
Different rate limit types (standard, strict, and API-based)
Custom key functions for more granular control
Easy-to-use decorators
Set up the rate limiter in the main FastAPI application

Applied rate limits to SMS endpoints:

API endpoints (/api/v1/client/send-sms) use api_rate_limit (100 requests/minute)
Standard endpoints (/api/v1/send_sms) use standard_rate_limit (60 requests/minute)
Now you can easily add rate limiting to other endpoints using any of these decorators:

@standard_rate_limit() - 60 requests per minute
@strict_rate_limit() - 30 requests per minute
@api_rate_limit() - 100 requests per minute with API key consideration
Or create custom rate limits using:
@rate_limit("20/minute", error_message="Custom error message")

The rate limits are now enforced per IP address for standard routes and per IP+API key combination for API routes, providing better control over API usage.