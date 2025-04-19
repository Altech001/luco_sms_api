from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Annotated
from typing import List
import hashlib
from database import schema
from sqlalchemy.orm import Session
from database.models import ContactRequest, SMSRequest, SMSResponse, SMSTemplate, TopupRequest, UserCreate, UserResponse
from database.db_connection import get_db
import time
from fastapi.concurrency import run_in_threadpool
from dotenv import load_dotenv
import os


load_dotenv()

SANDBOX_API_KEY = os.getenv("API_KEY")


from luco.sms_send import LucoSMS

user_router = APIRouter(
    prefix="/api/v1",
    tags=["Luco SMS"]
)


SMS_COST = 32.0

#Injection Dependency =================================================
# dep_db: Annotated[Session, Depends(get_db)] = Depends(get_db)
dep_db  = Annotated[Session, Depends(get_db)]

#========================= User Endpoints ================================

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@user_router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(schema.Users).filter(schema.Users.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = schema.Users(
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

#==============ACCOUNT ENDPOINTS START =======================================================
@user_router.post("/topup")
def topup_wallet(topup: TopupRequest, user_id: int, db: Session = Depends(get_db)):
    user = db.query(schema.Users).filter(schema.Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not Found")
    
    user.wallet_balance += topup.amount
    transaction = schema.Transactions(
        user_id=user_id,
        amount=topup.amount,
        transaction_type="topup"
    )
    db.add(transaction)
    db.commit()
    return {"message": "Wallet topped up successfully", "new_balance": user.wallet_balance}


@user_router.get("/wallet-balance")
def get_wallet_balance(user_id: int, db: Session = Depends(get_db)):
    user = db.query(schema.Users).filter(schema.Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"balance": user.wallet_balance}


@user_router.get("/transaction_history")
def transaction_history(user_id: int, db: dep_db, skip : int,limit: int = 10):
    user = db.query(schema.Users).filter(schema.Users.id == user_id).first()
    if not user:
        raise HTTPException(detail="User not Found", status_code=404)
    
    transactions = db.query(schema.Transactions).filter(schema.Transactions.user_id == user_id).all()
    transactions = transactions[skip:skip+limit]
    if not transactions:
        raise HTTPException(detail="No transactions found", status_code=404)
    
    return transactions


@user_router.delete("/transcation_delete")
def delete_transaction(transaction_id: int, user_id: int, db: dep_db):
    user = db.query(schema.Users).filter(schema.Users.id == user_id).first()
    if not user:
        raise HTTPException(detail="User not Found", status_code=404)
    
    transaction = db.query(schema.Transactions).filter(schema.Transactions.id == transaction_id).first()
    if not transaction:
        raise HTTPException(detail="No transaction found", status_code=404)
    db.delete(transaction)
    db.commit()
    return {
        "message": "Transaction deleted successfully"
    }
    
@user_router.delete("/all_transaction")
def delete_all_transactions(user_id: int, db: dep_db):
    user = db.query(schema.Users).filter(schema.Users.id == user_id).first()
    if not user:
        raise HTTPException(detail="User not Found", status_code=404)
    
    transactions = db.query(schema.Transactions).filter(schema.Transactions.user_id == user_id).all()
    if not transactions:
        raise HTTPException(detail="No transactions found", status_code=404)
    for transaction in transactions:
        db.delete(transaction)
    db.commit()
    return {
        "message": "All transactions deleted successfully"
    }
    
    
    


#============== ACCOUNT ENDPOINTS END   =======================================================


#============= SMS TEMPLATE ENDPOINTS START ===================================================

@user_router.post("/smstemplate")
def sms_template(template: SMSTemplate, user_id: int, db: dep_db):
    user = db.query(schema.Users).filter(schema.Users.id == user_id).first()
    if not user:
        raise HTTPException(detail="User not Found", status_code=404)
    
    sms_template = schema.SmsTemplates(
        user_id=user.id,
        name= user.username,
        content=template.content
    )
    # sms_template = SMSTemplate
    db.add(sms_template)
    db.commit()
    db.refresh(sms_template)
    
    return sms_template

@user_router.get("/smstemplate", response_model=List[SMSTemplate])
def fetch_sms_templates(user_id: int, db: dep_db):
    user = db.query(schema.Users).filter(schema.Users.id == user_id).first()
    if not user:
        raise HTTPException(detail="User not Found", status_code=404)
    
    templates = db.query(schema.SmsTemplates).filter(schema.SmsTemplates.user_id == user_id).all()
    
    return templates

@user_router.put("/sms_temp_update")
def sms_template_update(user_id: int, new_content: str, db: dep_db):
    user = db.query(schema.Users).filter(schema.Users.id == user_id).first()
    if not user:
        raise HTTPException(detail="User not Found", status_code=404)
    
    template = db.query(schema.SmsTemplates).filter(schema.SmsTemplates.user_id == user_id).first()
    if not template:
        raise HTTPException(detail="No template found", status_code=404)
    
    current_content = template.content
    
    template.content = new_content
    db.commit()
    db.refresh(template)
    
    return {
        "message": "Template updated successfully",
        "old_content": current_content,
        "new_content": template.content
    }
    

@user_router.delete("/sms_template")
def delete_sms_template(template_id: int, user_id: int, db: dep_db):
    user = db.query(schema.Users).filter(schema.Users.id == user_id).first()
    if not user:
        raise HTTPException(detail="User not Found", status_code=404)
    
    sms_template = db.query(schema.SmsTemplates).filter(schema.SmsTemplates.id == template_id).first()
    if not sms_template:
        raise HTTPException(detail="No template found", status_code=404)
    
    db.delete(sms_template)
    db.commit()
    
    return {
        "message": "SMS template deleted successfully"
    }


#============= SMS TEMPLATE ENDPOINTS START ===================================================
@user_router.get("/delivery_report")
def delivery_report(user_id: int, sms_id : int, db: dep_db):
    user = db.query(schema.Users).filter(schema.Users.id == user_id).first()
    if not user:
        raise HTTPException(detail="User not Found", status_code=404)
    
    delivery_reports = db.query(schema.SmsDeliveryReports).filter(schema.SmsDeliveryReports.sms_id == sms_id).all()
    if not delivery_reports:
        raise HTTPException(detail="No delivery report found", status_code=404)
    
    return {
        "delivery_reports": delivery_reports
    }



@user_router.get("/sms_history", response_model=List[SMSResponse])
def sms_history(user_id: int, db: dep_db):
    user = db.query(schema.Users).filter(schema.Users.id == user_id).first()
    if not user:
        raise HTTPException(detail="User not Found", status_code=404)
    message = db.query(schema.SmsMessages).filter(schema.SmsMessages.user_id == user_id).all()
    if not message:
        raise HTTPException(detail="No message found", status_code=404)
    
    return message


@user_router.delete("/delivery_report")
def delete_delivery_report(report_id: int, user_id: int, db: dep_db):
    user = db.query(schema.Users).filter(schema.Users.id == user_id).first()
    if not user:
        raise HTTPException(detail="User not Found", status_code=404)
    
    delivery_report = db.query(schema.SmsDeliveryReports).filter(schema.SmsDeliveryReports.id == report_id).first()
    if not delivery_report:
        raise HTTPException(detail="No delivery report found", status_code=404)
    
    db.delete(delivery_report)
    db.commit()
    
    return {
        "message": "Delivery report deleted successfully"
    }
    
@user_router.delete("/sms_history")
def delete_sms_history(message_id: int, user_id: int, db: dep_db):
    user = db.query(schema.Users).filter(schema.Users.id == user_id).first()
    if not user:
        raise HTTPException(detail="User not Found", status_code=404)
    
    sms_message = db.query(schema.SmsMessages).filter(schema.SmsMessages.id == message_id).first()
    if not sms_message:
        raise HTTPException(detail="No message found", status_code=404)
    
    db.delete(sms_message)
    db.commit()
    
    return {
        "message": "SMS history deleted successfully"
    }
    
@user_router.delete("/user_account")
async def delete_user_account(user_id: int, db: dep_db):
    user = db.query(schema.Users).filter(schema.Users.id == user_id).first()
    if not user:
        raise HTTPException(detail="User not Found", status_code=404)
    
    # Simulate a delay of 2 minutes
    await run_in_threadpool(time.sleep, 120)
    
    db.delete(user)
    db.commit()
    
    return {
        "message": "User account deleted successfully"
    }
    
#========================= Contact Endpoints ============================
@user_router.post("/contact")
def add_contact(contact: ContactRequest, user_id: int, db: dep_db):
    user = db.query(schema.Users).filter(schema.Users.id == user_id).first()
    if not user:
        raise HTTPException(detail="User not Found", status_code=404)
    
    contact = schema.Contacts(
        user_id=user.id,
        name=contact.name,
        phone_number=contact.phone_number
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    
    return contact

@user_router.get("/contact", response_model=List[ContactRequest])
def fetch_contacts(user_id: int, db: dep_db, skip: int, limit: int = 10):
    user = db.query(schema.Users).filter(schema.Users.id == user_id).first()
    if not user:
        raise HTTPException(detail="User not Found", status_code=404)
    
    contacts = db.query(schema.Contacts).filter(schema.Contacts.user_id == user_id).all()
    contacts = contacts[skip:skip+limit]
    if not contacts:
        raise HTTPException(detail="No contacts found", status_code=404)
    
    return contacts

@user_router.patch("/contact")
def update_contact(contact_id: int, contact_request: ContactRequest, user_id: int, db: dep_db):
    user = db.query(schema.Users).filter(schema.Users.id == user_id).first()
    if not user:
        raise HTTPException(detail="User not Found", status_code=404)
    
    contact = db.query(schema.Contacts).filter(schema.Contacts.id == contact_id).first()
    if not contact:
        raise HTTPException(detail="No contact found", status_code=404)
    
    # Update the contact fields with the new data
    contact.name = contact_request.name
    contact.phone_number = contact_request.phone_number
    db.commit()
    db.refresh(contact)
    
    return contact


@user_router.delete("/contact")
def delete_contact(contact_id: int, user_id: int, db: dep_db):
    user = db.query(schema.Users).filter(schema.Users.id == user_id).first()
    if not user:
        raise HTTPException(detail="User not Found", status_code=404)
    
    contact = db.query(schema.Contacts).filter(schema.Contacts.id == contact_id).first()
    if not contact:
        raise HTTPException(detail="No contact found", status_code=404)
    
    db.delete(contact)
    db.commit()
    
    return {
        "message": "Contact deleted successfully"
    }

#***********Function to delete all the contacts of a user***********

def delete_all_contacts(user_id: int, db: dep_db):
    try:
        user = db.query(schema.Users).filter(schema.Users.id == user_id).first()
        if not user:
            raise HTTPException(detail="User not Found", status_code=404)
        
        contacts = db.query(schema.Contacts).filter(schema.Contacts.user_id == user_id).all()
        if not contacts:
            raise HTTPException(detail="No contacts found", status_code=404)
        
        for contact in contacts:
            db.delete(contact)
            
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error during auto-deletion: {str(e)}"
        )    
    
#***********Function to delete all the contacts of a user***********
    
@user_router.delete("/all_contacts")
def delete_contact(backgroundtask: BackgroundTasks, user_id: int, db: dep_db):
    user = db.query(schema.Users).filter(schema.Users.id == user_id).first()
    if not user:
        raise HTTPException(detail="User not Found", status_code=404)
    
    contacts = db.query(schema.Contacts).filter(schema.Contacts.user_id == user_id).all()
    if not contacts:
        raise HTTPException(detail="No contacts found", status_code=404)
    
    backgroundtask.add_task(delete_all_contacts, user_id, db)
        
    db.commit()
    
    return {
        "message": "All Contacts deleted successfully"
    }
#=========================End of User Endpoints =========================

