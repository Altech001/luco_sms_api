from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.db_connection import get_db
import database.schema
from database.models import UserCreate, UserResponse, TopupRequest, SMSRequest, SMSResponse
from typing import List
import hashlib
from africastalking import SMS  # Assuming this is the Africa's Talking SMS integration

app = FastAPI()
SMS_COST = 32.0  # 32 UGX per SMS
# at_sms = SMS(username="your_username", api_key="your_api_key")  # Africa's Talking SMS

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(Users).filter(Users.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = Users(
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/topup")
def topup_wallet(topup: TopupRequest, user_id: int, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.wallet_balance += topup.amount
    transaction = Transactions(
        user_id=user_id,
        amount=topup.amount,
        transaction_type="topup"
    )
    db.add(transaction)
    db.commit()
    return {"message": "Wallet topped up successfully", "new_balance": user.wallet_balance}

@app.post("/send-sms", response_model=SMSResponse)
def send_sms(sms: SMSRequest, user_id: int, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.wallet_balance < SMS_COST:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Send SMS via Africa's Talking
    try:
        response = at_sms.send(sms.message, [sms.recipient])
        
        # Deduct cost and record message
        user.wallet_balance -= SMS_COST
        sms_message = SmsMessages(
            user_id=user_id,
            recipient=sms.recipient,
            message=sms.message,
            cost=SMS_COST
        )
        
        transaction = Transactions(
            user_id=user_id,
            amount=-SMS_COST,
            transaction_type="sms_deduction"
        )
        
        db.add(sms_message)
        db.add(transaction)
        db.commit()
        db.refresh(sms_message)
        return sms_message
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SMS sending failed: {str(e)}")

@app.get("/wallet-balance")
def get_wallet_balance(user_id: int, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"balance": user.wallet_balance}

@app.get("/sms-history", response_model=List[SMSResponse])
def get_sms_history(user_id: int, db: Session = Depends(get_db)):
    messages = db.query(SmsMessages).filter(SmsMessages.user_id == user_id).all()
    return messages

# Demo endpoint
@app.post("/demo/send-sms")
def demo_send_sms(sms: SMSRequest):
    try:
        response = at_sms.send(sms.message, [sms.recipient])
        return {"message": "Demo SMS sent successfully", "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo SMS failed: {str(e)}")