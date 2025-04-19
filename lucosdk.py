import requests
from typing import Dict, List, Optional, Union

class LucoSMSClient:
    def __init__(self, api_key: str, base_url: str = "https://luco-sms-api.onrender.com"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }

    def send_sms(self, recipient: str, message: str) -> Dict:
        """Send SMS to a single recipient"""
        endpoint = f"{self.base_url}/api/v1/client/send-sms"
        payload = {
            "recipient": recipient,
            "message": message
        }
        response = requests.post(endpoint, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def get_balance(self) -> Dict:
        """Get current wallet balance"""
        endpoint = f"{self.base_url}/api/v1/wallet-balance"
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_delivery_report(self, sms_id: int) -> Dict:
        """Get delivery report for a specific SMS"""
        endpoint = f"{self.base_url}/api/v1/delivery_report"
        params = {"sms_id": sms_id}
        response = requests.get(endpoint, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_sms_history(self) -> List[Dict]:
        """Get SMS sending history"""
        endpoint = f"{self.base_url}/api/v1/sms_history"
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        return response.json()


