from pydantic import BaseModel, EmailStr
from typing import Optional, List, Union
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    wallet_balance: float
    created_at: datetime

class TopupRequest(BaseModel):
    amount: float

    
class SMSRequest(BaseModel):
    recipient: List[str] # Can be either a single string or list of strings
    message: str

# class SMSRequest(BaseModel):
#     recipient: List[str]
#     message: str

class SMSTemplate(BaseModel):
    id:int
    name: Optional[str] = None
    content: str

class SMSResponse(BaseModel):
    id: int
    recipient: str
    message: str
    status: str
    cost: float
    created_at: datetime


class ContactRequest(BaseModel):
    id: int
    name: Optional[str]
    phone_number: str

class APIKeyResponse(BaseModel):
    id: int
    key: str
    is_active: bool

    class Config:
        orm_mode = True