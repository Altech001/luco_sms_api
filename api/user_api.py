from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db_connection import get_db
from models import Users, APIKeys
from schemas import UserResponse  # Assuming this exists in schemas.py
import secrets
import string

router = APIRouter(
    prefix="/api-keys",
    tags=["API Keys"]
)

def generate_api_key(length: int = 32) -> str:
    """Generate a secure random API key"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

@router.post("/generate", response_model=dict)
def generate_user_api_key(user_id: int, db: Session = Depends(get_db)):
    """
    Generate a new API key for a user
    """
    # Verify user exists
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate new API key
    api_key = generate_api_key()
    
    # Check if key already exists (unlikely due to randomness, but good practice)
    existing_key = db.query(APIKeys).filter(APIKeys.key == api_key).first()
    if existing_key:
        raise HTTPException(status_code=400, detail="API key generation collision occurred")

    # Create new API key entry
    new_api_key = APIKeys(
        user_id=user_id,
        key=api_key,
        is_active=True
    )
    
    db.add(new_api_key)
    db.commit()
    db.refresh(new_api_key)
    
    return {
        "api_key": new_api_key.key,
        "message": "API key generated successfully",
        "created_at": new_api_key.created_at
    }

@router.get("/list", response_model=list[dict])
def list_api_keys(user_id: int, db: Session = Depends(get_db)):
    """
    List all API keys for a user
    """
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    api_keys = db.query(APIKeys).filter(APIKeys.user_id == user_id).all()
    
    return [{
        "id": key.id,
        "key": key.key[-8:],  # Show only last 8 characters for security
        "is_active": key.is_active,
        "created_at": key.created_at
    } for key in api_keys]

@router.put("/deactivate/{key_id}", response_model=dict)
def deactivate_api_key(key_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Deactivate an existing API key
    """
    api_key = db.query(APIKeys).filter(
        APIKeys.id == key_id,
        APIKeys.user_id == user_id
    ).first()
    
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found or not owned by user")
    
    if not api_key.is_active:
        raise HTTPException(status_code=400, detail="API key already deactivated")
    
    api_key.is_active = False
    db.commit()
    
    return {"message": "API key deactivated successfully"}

@router.delete("/delete/{key_id}", response_model=dict)
def delete_api_key(key_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Delete an existing API key
    """
    api_key = db.query(APIKeys).filter(
        APIKeys.id == key_id,
        APIKeys.user_id == user_id
    ).first()
    
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found or not owned by user")
    
    db.delete(api_key)
    db.commit()
    
    return {"message": "API key deleted successfully"}