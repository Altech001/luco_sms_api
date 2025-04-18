import hashlib
import re
import base64
from passlib.context import CryptContext  # type: ignore


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)
def generate_salt(length: int = 16) -> str:
    """
    Generate a random salt of the specified length.
    """
    return base64.b64encode(hashlib.sha256(str(length).encode()).digest()).decode()[:length]
def generate_hash(data: str) -> str:
    """
    Generate a SHA-256 hash of the input data.
    """
    return hashlib.sha256(data.encode()).hexdigest()
def validate_password(password: str) -> bool:
    """
    Validate the password against the specified criteria.
    """
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True
def validate_username(username: str) -> bool:
    """
    Validate the username against the specified criteria.
    """
    if len(username) < 3:
        return False
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False
    return True
def validate_email(email: str) -> bool:
    """
    Validate the email address against the specified criteria.
    """
    if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
        return False
    return True
