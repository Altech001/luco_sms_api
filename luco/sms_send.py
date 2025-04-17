import africastalking
from dotenv import load_dotenv
import os

load_dotenv()

class LucoSMS:

    def __init__(self, api_key=None, username='altech'):
        self.api_key = api_key or os.getenv("LIVE_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided either in constructor or as environment variable")
        
        africastalking.initialize(username=username, api_key=self.api_key)
        self.sms = africastalking.SMS

    def send_message(self, message, recipients):

        try:
            response = self.sms.send(message, recipients)
            return response
        except Exception as e:
            raise Exception(f"Failed to send SMS: {str(e)}")

