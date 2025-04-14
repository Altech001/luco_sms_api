from fastapi import HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from database.db_connection import get_db
from database.schema import APIKeys, Users

api_key_header = APIKeyHeader(name="X-API-Key")

async def get_api_user(
    api_key: str = Security(api_key_header),
    db: Session = Depends(get_db)
) -> Users:
    api_key_db = db.query(APIKeys).filter(
        APIKeys.key == api_key,
        APIKeys.is_active == True
    ).first()
    
    if not api_key_db:
        raise HTTPException(
            status_code=401,
            detail="Invalid or inactive API key"
        )
    
    user = db.query(Users).filter(Users.id == api_key_db.user_id).first()
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )
    
    return user
