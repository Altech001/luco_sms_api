import base64
import secrets
import string
import hashlib


def generate_api_key(length: int = 32) -> str:
    """Generate a secure random API key"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# print(generate_api_key(length=20))

def unquie_api_key(length: int = 32):
    api_key = hashlib.sha256("altech".encode()).hexdigest()[:length]
    return api_key

# print(unquie_api_key(length=20))