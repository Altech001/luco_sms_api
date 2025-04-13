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
