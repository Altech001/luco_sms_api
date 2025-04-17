from fastapi import APIRouter, HTTPException, Depends
from database import schema
from sqlalchemy.orm import Session
from database.db_connection import get_db
from database.models import SMSRequest
from auth.api_auth import get_api_user
from luco.sms_send import LucoSMS
from database.schema import Users

luco_router = APIRouter(
    prefix="/api/v1/client",
    tags=["Client SMS API"]
)

SMS_COST = 32.0

@luco_router.post("/send-sms")
async def client_send_sms(
    sms: SMSRequest,
    current_user: Users = Depends(get_api_user),
    db: Session = Depends(get_db)
):
    if current_user.wallet_balance < SMS_COST:
        raise HTTPException(
            status_code=400,
            detail="Insufficient balance in wallet"
        )
    
    try:
        sms_client = LucoSMS()
        response = sms_client.send_message(sms.message, sms.recipient)
        
        if not response or 'SMSMessageData' not in response:
            raise HTTPException(
                status_code=500,
                detail="SMS sending failed - No response data"
            )
        
        recipients = response.get('SMSMessageData', {}).get('Recipients', [])
        if not recipients or not any(recipient.get('status') == 'Success' for recipient in recipients):
            raise HTTPException(
                status_code=500,
                detail="SMS sending failed - Delivery error"
            )

        # Update wallet balance
        current_user.wallet_balance -= SMS_COST
        
        # Record SMS message for each recipient
        sms_messages = []
        for recipient in sms.recipient:
            sms_message = schema.SmsMessages(
                user_id=current_user.id,
                recipient=recipient,
                message=sms.message,
                status="sent",
                cost=SMS_COST
            )
            sms_messages.append(sms_message)
            db.add(sms_message)

        # Record transaction
        transaction = schema.Transactions(
            user_id=current_user.id,
            amount=-SMS_COST * len(sms.recipient),
            transaction_type="sms_deduction"
        )
        
        db.add(transaction)
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
            "remaining_balance": current_user.wallet_balance
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"SMS sending failed: {str(e)}"
        )

