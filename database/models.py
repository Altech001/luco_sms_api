from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    wallet_balance: float
    created_at: datetime

class TopupRequest(BaseModel):
    amount: float

class SMSRequest(BaseModel):
    recipient: str
    message: str

class SMSResponse(BaseModel):
    id: int
    recipient: str
    message: str
    status: str
    cost: float
    created_at: datetime


class APIKeyResponse(BaseModel):
    id: int
    key: str
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True