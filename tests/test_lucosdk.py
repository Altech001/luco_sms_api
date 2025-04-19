import pytest
import requests_mock
from lucosdk import LucoSMSClient
import requests

@pytest.fixture
def client():
    return LucoSMSClient(api_key="test_api_key", base_url="https://luco-sms-api.onrender.com")

base_url = "https://luco-sms-api.onrender.com"

@pytest.fixture
def mock_api():
    with requests_mock.Mocker() as m:
        yield m

def test_send_sms(client, mock_api):
    mock_response = {
        "status": "success",
        "message": "SMS sent successfully",
        "remaining_balance": 1000.0
    }
    mock_api.post(f"{base_url}/api/v1/client/send-sms", json=mock_response)
    
    response = client.send_sms(recipient="+256700000000", message="Test message")
    assert response["status"] == "success"
    assert "remaining_balance" in response

def test_get_balance(client, mock_api):
    mock_response = {"balance": 1000.0}
    mock_api.get(f"{base_url}/api/v1/wallet-balance", json=mock_response)
    
    response = client.get_balance()
    assert "balance" in response
    assert isinstance(response["balance"], float)

def test_get_delivery_report(client, mock_api):
    mock_response = {
        "delivery_reports": [
            {"status": "delivered", "timestamp": "2024-01-01T12:00:00Z"}
        ]
    }
    mock_api.get(f"{base_url}/api/v1/delivery_report", json=mock_response)
    
    response = client.get_delivery_report(sms_id=123)
    assert "delivery_reports" in response

def test_get_sms_history(client, mock_api):
    mock_response = [
        {
            "id": 1,
            "recipient": "+256708215305",
            "message": "Test message",
            "status": "delivered"
        }
    ]
    mock_api.get(f"{base_url}/api/v1/sms_history", json=mock_response)
    
    response = client.get_sms_history()
    assert isinstance(response, list)
    assert len(response) > 0
    assert "recipient" in response[0]

def test_invalid_api_key(mock_api):
    client = LucoSMSClient(api_key="invalid_key")
    mock_api.post(
        f"{base_url}/api/v1/client/send-sms",
        status_code=401,
        json={"detail": "Invalid API key"}
    )
    
    with pytest.raises(requests.exceptions.HTTPError):
        client.send_sms(recipient="+256708215305", message="Test message")

def test_server_error(client, mock_api):
    mock_api.post(
        f"{base_url}/api/v1/client/send-sms",
        status_code=500,
        json={"detail": "Internal server error"}
    )
    
    with pytest.raises(requests.exceptions.HTTPError):
        client.send_sms(recipient="+256708215305", message="Test message")
