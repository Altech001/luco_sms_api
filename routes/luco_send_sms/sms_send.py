from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Annotated, Optional
from rate_limiter.rate_limiter import standard_rate_limit

from database.db_connection import get_db
from database import schema
from database.models import SMSRequest
from luco.sms_send import LucoSMS
import os

sms_router = APIRouter(
    prefix="/api/v1",
    tags=["Send SMS"]
)

load_dotenv()

SANDBOX_API_KEY = os.getenv("SANDBOX_API_KEY")

user_router = APIRouter(
    prefix="/api/v1",
    tags=["Luco SMS"]
)

SMS_COST = 32.0

dep_db = Annotated[Session, Depends(get_db)]

@sms_router.post("/send_sms")
@standard_rate_limit()  # Apply standard rate limiting (60/minute)
def send_sms(request: Request, sms: SMSRequest, user_id: int, db: dep_db):
    user = db.query(schema.Users).filter(schema.Users.id == user_id).first()
    if not user:
        raise HTTPException(detail="User not Found", status_code=404)
    
    # Calculate total cost based on number of recipients
    total_cost = SMS_COST * len(sms.recipient)
    
    if user.wallet_balance < total_cost:
        raise HTTPException(detail="Insufficient balance", status_code=400)
    
    try:        
        sms_client = LucoSMS()
        # Pass the full list of recipients
        response = sms_client.send_message(sms.message, sms.recipient)
        
        if not response or 'SMSMessageData' not in response:
            raise HTTPException(detail="SMS sending failed - No response data", status_code=500)
        
        recipients = response.get('SMSMessageData', {}).get('Recipients', [])
        if not recipients or recipients[0].get('status') != 'Success':
            raise HTTPException(detail="SMS sending failed - Delivery error", status_code=500)

        user.wallet_balance -= total_cost
        
        # Create an SMS message record for each recipient
        sms_messages = []
        for recipient in sms.recipient:
            sms_message = schema.SmsMessages(
                user_id=user.id,
                recipient=recipient,
                message=sms.message,
                status="sent",
                cost=SMS_COST
            )
            sms_messages.append(sms_message)
            
            transaction = schema.Transactions(
                user_id=user.id,
                amount=-SMS_COST,
                transaction_type="sms_deduction"
            )
            db.add(transaction)
        
        # Add all SMS messages
        db.add_all(sms_messages)
        db.commit()
        
        # Create delivery reports
        for sms_message in sms_messages:
            sms_delivery_report = schema.SmsDeliveryReports(
                sms_id=sms_message.id,
                status="delivered"
            )
            db.add(sms_delivery_report)
        
        db.commit()
        
        return {
            "status": "success",
            "message": "SMS sent successfully",
            "recipients_count": len(sms.recipient),
            "total_cost": total_cost,
            "delivery_status": "delivered"
        }
        
    except Exception as e:
        raise HTTPException(detail=f"SMS sending failed: {str(e)}", status_code=500)

