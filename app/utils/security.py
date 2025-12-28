from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from cryptography.fernet import Fernet
from app.config import settings
import base64
import hashlib


# Password hashing with Argon2
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# JWT Bearer scheme
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash password using Argon2"""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate JWT token"""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Dependency to get current authenticated user"""
    payload = decode_token(credentials.credentials)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    return username


# Email encryption (server-side AES)
def _get_fernet() -> Fernet:
    """Get Fernet instance for email encryption"""
    key = hashlib.sha256(settings.EMAIL_ENCRYPTION_KEY.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key))


def encrypt_email(email: str) -> str:
    """Encrypt email for server storage"""
    return _get_fernet().encrypt(email.encode()).decode()


def decrypt_email(encrypted: str) -> str:
    """Decrypt email (rarely needed)"""
    return _get_fernet().decrypt(encrypted.encode()).decode()
