from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from app.core.config import settings
import hashlib
import os
import base64

# -----------------------------
# Şifreleme / Hash Fonksiyonları
# -----------------------------

def hash_password(password: str) -> str:
    """
    Şifreyi hashler (scrypt ile) ve base64 encode eder.
    """
    salt = os.urandom(16)  # rastgele salt
    hashed = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return base64.b64encode(salt + hashed).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Kullanıcının girdiği şifreyi, saklanan hash ile karşılaştırır.
    """
    decoded = base64.b64decode(hashed_password.encode())
    salt = decoded[:16]
    stored_hash = decoded[16:]
    new_hash = hashlib.scrypt(plain_password.encode(), salt=salt, n=2**14, r=8, p=1)
    return new_hash == stored_hash

# -----------------------------
# JWT Token Fonksiyonları
# -----------------------------

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
