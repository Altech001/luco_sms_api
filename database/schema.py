from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database.db_connection import Base

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    wallet_balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())
    promo_code_usages = relationship("PromoCodeUsage", back_populates="user")

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
    
#=============== Promo Codes ===============

class PromoCode(Base):
    __tablename__ = "promo_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    discount_type = Column(String)  # 'percentage' or 'fixed' or 'referral'
    discount_value = Column(Float)  # reward amount for new customer
    referrer_reward = Column(Float, nullable=True)  # reward amount for referrer
    valid_from = Column(DateTime)
    valid_until = Column(DateTime)
    max_uses = Column(Integer, nullable=True)
    current_uses = Column(Integer, default=0)
    min_purchase_amount = Column(Float, default=0)
    is_active = Column(Boolean, default=True)
    is_referral = Column(Boolean, default=False)
    referrer_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # user who created the referral code
    
    usages = relationship("PromoCodeUsage", back_populates="promo_code")
    referrer = relationship("Users", foreign_keys=[referrer_id])

class PromoCodeUsage(Base):
    __tablename__ = "promo_code_usages"
    
    id = Column(Integer, primary_key=True, index=True)
    promo_code_id = Column(Integer, ForeignKey("promo_codes.id"))
    user_id = Column(Integer, ForeignKey("users.id"))  # referred user
    referrer_reward_paid = Column(Boolean, default=False)
    referred_reward_paid = Column(Boolean, default=False)
    used_at = Column(DateTime, default=func.now())
    
    promo_code = relationship("PromoCode", back_populates="usages")
    user = relationship("Users", back_populates="promo_code_usages")