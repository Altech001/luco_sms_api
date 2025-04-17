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


# @luco_router.post("/send-sms")
# async def client_send_sms(
#     sms: SMSRequest,
#     current_user: Users = Depends(get_api_user),
#     db: Session = Depends(get_db)
# ):
#     # Convert single recipient to list if necessary
#     recipients = sms.recipient if isinstance(sms.recipient, list) else [sms.recipient]
    
#     # Calculate total cost for all messages
#     total_cost = SMS_COST * len(recipients)
    
#     if current_user.wallet_balance < total_cost:
#         raise HTTPException(
#             status_code=400,
#             detail="Insufficient balance in wallet"
#         )
    
#     try:
#         sms_client = LucoSMS()
#         response = sms_client.send_message(sms.message, recipients)
        
#         if not response or 'SMSMessageData' not in response:
#             raise HTTPException(
#                 status_code=500,
#                 detail="SMS sending failed - No response data"
#             )
        
#         recipients_data = response.get('SMSMessageData', {}).get('Recipients', [])
#         successful_recipients = []
        
#         # Process each recipient's response
#         for recipient_data in recipients_data:
#             if recipient_data.get('status') == 'Success':
#                 successful_recipients.append(recipient_data.get('number'))
        
#         if not successful_recipients:
#             raise HTTPException(
#                 status_code=500,
#                 detail="SMS sending failed - No successful deliveries"
#             )

#         # Update wallet balance based on successful messages
#         successful_cost = SMS_COST * len(successful_recipients)
#         current_user.wallet_balance -= successful_cost
        
#         # Record SMS messages and transactions for successful deliveries
#         for recipient in successful_recipients:
#             sms_message = schema.SmsMessages(
#                 user_id=current_user.id,
#                 recipient=recipient,
#                 message=sms.message,
#                 status="sent",
#                 cost=SMS_COST
#             )
            
#             transaction = schema.Transactions(
#                 user_id=current_user.id,
#                 amount=-SMS_COST,
#                 transaction_type="sms_deduction"
#             )
            
#             db.add(sms_message)
#             db.add(transaction)
            
#             db.flush()  # Get the ID before commit
            
#             sms_delivery_report = schema.SmsDeliveryReports(
#                 sms_id=sms_message.id,
#                 status="delivered"
#             )
            
#             db.add(sms_delivery_report)
        
#         db.commit()
        
#         return {
#             "status": "success",
#             "message": f"SMS sent successfully to {len(successful_recipients)} recipients",
#             "successful_recipients": successful_recipients,
#             "remaining_balance": current_user.wallet_balance
#         }
        
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"SMS sending failed: {str(e)}"
#         )
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
        response = sms_client.send_message(sms.message, [sms.recipient])
        
        if not response or 'SMSMessageData' not in response:
            raise HTTPException(
                status_code=500,
                detail="SMS sending failed - No response data"
            )
        
        recipients = response.get('SMSMessageData', {}).get('Recipients', [])
        if not recipients or recipients[0].get('status') != 'Success':
            raise HTTPException(
                status_code=500,
                detail="SMS sending failed - Delivery error"
            )

        # Update wallet balance
        current_user.wallet_balance -= SMS_COST
        
        # Record SMS message
        sms_message = schema.SmsMessages(
            user_id=current_user.id,
            recipient=sms.recipient,
            message=sms.message,
            status="sent",
            cost=SMS_COST
        )
        
        # Record transaction
        transaction = schema.Transactions(
            user_id=current_user.id,
            amount=-SMS_COST,
            transaction_type="sms_deduction"
        )
        
        db.add(sms_message)
        db.add(transaction)
        db.commit()
        
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

