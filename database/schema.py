from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from database.db_connection import Base

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    wallet_balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())

class Transactions(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(20), nullable=False)  # "topup" or "sms_deduction"
    created_at = Column(DateTime, default=func.now())

class Contacts(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=False)

class SmsMessages(Base):
    __tablename__ = "sms_messages"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipient = Column(String(20), nullable=False)
    message = Column(String(160), nullable=False)
    status = Column(String(20), default="pending")
    cost = Column(Float, default=32.0)  # 32 UGX per SMS
    created_at = Column(DateTime, default=func.now())

class SmsDeliveryReports(Base):
    __tablename__ = "sms_delivery_reports"
    id = Column(Integer, primary_key=True)
    sms_id = Column(Integer, ForeignKey("sms_messages.id"), nullable=False)
    status = Column(String(20), nullable=False)
    updated_at = Column(DateTime, default=func.now())

class SmsTemplates(Base):
    __tablename__ = "sms_templates"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(50), nullable=False)
    content = Column(String(160), nullable=False)

class ContactGroups(Base):
    __tablename__ = "contact_groups"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(50), nullable=False)

class APIKeys(Base):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key = Column(String(100), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)