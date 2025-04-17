import africastalking
from dotenv import load_dotenv
import os

load_dotenv()

class LucoSMS:
    def __init__(self, api_key=SANDBOX_API_KEY, username='sandbox', sender_id="ddddd"):
        africastalking.initialize(username=username, api_key=api_key)
        self.sender_id = sender_id
        self.sms = africastalking.SMS

    def send_message(self, message, recipients):

        try:
            response = self.sms.send(message, recipients)
            return response
        except Exception as e:
            raise Exception(f"Failed to send SMS: {str(e)}")

