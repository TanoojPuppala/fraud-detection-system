"""
Security Utilities: Password Hashing & JWT Authentication.
"""

import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import jwt

from backend.app.core.config import settings

# Salt for password hashing
SALT = b"fraud_guard_ai_system_salt_2026"


def get_password_hash(password: str) -> str:
    """
    Computes secure SHA256 HMAC digest of password.
    """
    return hmac.new(SALT, password.encode("utf-8"), hashlib.sha256).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies plain text password against stored HMAC hash.
    """
    computed = get_password_hash(plain_password)
    return hmac.compare_digest(computed, hashed_password)


def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
