from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


from database.db_connection import get_db
from database import schema


promo_router = APIRouter(
    prefix="/api/v1/promo",
    tags=["Promo Codes"]
)

class PromoCodeBase(BaseModel):
    code: str
    discount_type: str  # 'percentage', 'fixed', or 'referral'
    discount_value: float
    referrer_reward: Optional[float] = None
    valid_from: datetime
    valid_until: datetime
    max_uses: Optional[int] = None
    min_purchase_amount: float = 0
    is_active: bool = True
    is_referral: bool = False
    referrer_id: Optional[int] = None

class PromoCodeCreate(PromoCodeBase):
    pass

class PromoCode(PromoCodeBase):
    id: int
    current_uses: int = 0
    
    class Config:
        orm_mode = True

class ValidatePromoRequest(BaseModel):
    code: str
    user_id: int
    cart_total: float

class PromoCodeResponse(BaseModel):
    valid: bool
    discount_amount: Optional[float] = None
    referrer_reward: Optional[float] = None
    is_referral: bool = False
    message: str

# Create a new promo code
@promo_router.post("/promo-codes/", response_model=PromoCode, status_code=status.HTTP_201_CREATED)
def create_promo_code(promo_code: PromoCodeCreate, db: Session = Depends(get_db)):
    existing_code = db.query(schema.PromoCode).filter(schema.PromoCode.code == promo_code.code).first()
    if existing_code:
        raise HTTPException(status_code=400, detail="Promo code already exists")
    
    db_promo_code = schema.PromoCode(**promo_code.model_dump(), current_uses=0)
    db.add(db_promo_code)
    db.commit()
    db.refresh(db_promo_code)
    return db_promo_code

# Validate promo code
@promo_router.post("/promo-codes/validate/", response_model=PromoCodeResponse)
def validate_promo_code(request: ValidatePromoRequest, db: Session = Depends(get_db)):
    # Find the promo code
    promo_code = db.query(schema.PromoCode).filter(
        schema.PromoCode.code == request.code,
        schema.PromoCode.is_active == True
    ).first()
    
    if not promo_code:
        return PromoCodeResponse(valid=False, message="Invalid promo code")
    
    # Check if promo code is expired
    now = datetime.now()
    if now < promo_code.valid_from or now > promo_code.valid_until:
        return PromoCodeResponse(valid=False, message="Promo code has expired")
    
    # Check usage limit
    if promo_code.max_uses and promo_code.current_uses >= promo_code.max_uses:
        return PromoCodeResponse(valid=False, message="Promo code usage limit reached")
    
    # Check if user has already used this code
    user_usage = db.query(schema.PromoCodeUsage).filter(
        schema.PromoCodeUsage.promo_code_id == promo_code.id,
        schema.PromoCodeUsage.user_id == request.user_id
    ).first()
    
    if user_usage:
        return PromoCodeResponse(valid=False, message="You have already used this promo code")
    
    # Check minimum purchase amount
    if request.cart_total < promo_code.min_purchase_amount:
        min_amount = promo_code.min_purchase_amount
        return PromoCodeResponse(
            valid=False, 
            message=f"Minimum purchase of ${min_amount:.2f} required to use this code"
        )
    
    # Calculate discount
    discount_amount = 0
    if promo_code.discount_type == "percentage":
        discount_amount = request.cart_total * (promo_code.discount_value / 100)
    else:  # fixed amount or referral
        discount_amount = min(promo_code.discount_value, request.cart_total)
    
    return PromoCodeResponse(
        valid=True,
        discount_amount=discount_amount,
        referrer_reward=promo_code.referrer_reward if promo_code.is_referral else None,
        is_referral=promo_code.is_referral,
        message="Promo code applied successfully"
    )

# Apply promo code to an order
@promo_router.post("/promo-codes/apply/")
def apply_promo_code(
    code: str, 
    user_id: int, 
    db: Session = Depends(get_db)
):
    promo_code = db.query(schema.PromoCode).filter(
        schema.PromoCode.code == code,
        schema.PromoCode.is_active == True
    ).first()
    
    if not promo_code:
        raise HTTPException(status_code=400, detail="Invalid promo code")
    
    # Create usage record with referral tracking
    usage = schema.PromoCodeUsage(
        promo_code_id=promo_code.id,
        user_id=user_id,
        referrer_reward_paid=False,
        referred_reward_paid=False
    )
    db.add(usage)
    
    # Update promo code usage count
    promo_code.current_uses += 1
    
    db.commit()
    
    return {"message": "Promo code applied successfully"}

# New endpoint to create referral code
@promo_router.post("/referral-codes/", response_model=PromoCode)
def create_referral_code(
    user_id: int,
    discount_value: float,
    referrer_reward: float,
    db: Session = Depends(get_db)
):
    # Generate unique referral code (you might want to implement a better generation method)
    code = f"REF{user_id}{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    promo_code = schema.PromoCode(
        code=code,
        discount_type="referral",
        discount_value=discount_value,
        referrer_reward=referrer_reward,
        valid_from=datetime.now(),
        valid_until=datetime.now().replace(year=datetime.now().year + 1),  # Valid for 1 year
        is_active=True,
        is_referral=True,
        referrer_id=user_id
    )
    
    db.add(promo_code)
    db.commit()
    db.refresh(promo_code)
    
    return promo_code

# List all promo codes (admin endpoint)
@promo_router.get("/promo-codes/", response_model=list[PromoCode])
def list_promo_codes(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    promo_codes = db.query(schema.PromoCode).offset(skip).limit(limit).all()
    return promo_codes

# Get a specific promo code
@promo_router.get("/promo-codes/{code}", response_model=PromoCode)
def get_promo_code(code: str, db: Session = Depends(get_db)):
    promo_code = db.query(schema.PromoCode).filter(schema.PromoCode.code == code).first()
    if promo_code is None:
        raise HTTPException(status_code=404, detail="Promo code not found")
    return promo_code

# Update a promo code
@promo_router.put("/promo-codes/{code}", response_model=PromoCode)
def update_promo_code(code: str, promo_update: PromoCodeBase, db: Session = Depends(get_db)):
    promo_code = db.query(schema.PromoCode).filter(schema.PromoCode.code == code).first()
    if promo_code is None:
        raise HTTPException(status_code=404, detail="Promo code not found")
    
    for key, value in promo_update.dict().items():
        setattr(promo_code, key, value)
    
    db.commit()
    db.refresh(promo_code)
    return promo_code

# Deactivate a promo code
@promo_router.delete("/promo-codes/{code}")
def deactivate_promo_code(code: str, db: Session = Depends(get_db)):
    promo_code = db.query(schema.PromoCode).filter(schema.PromoCode.code == code).first()
    if promo_code is None:
        raise HTTPException(status_code=404, detail="Promo code not found")
    
    promo_code.is_active = False
    db.commit()
    
    return {"message": "Promo code deactivated successfully"}

