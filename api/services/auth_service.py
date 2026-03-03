"""
Authentication Service – JWT-based admin auth.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from ..config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_prefix}/auth/login")

ALGORITHM = "HS256"


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_admin(username: str, password: str) -> bool:
    """Check credentials against the configured admin account."""
    if username != settings.admin_username:
        return False
    # Support both plain-text (dev) and bcrypt-hashed passwords in config
    stored = settings.admin_password
    try:
        return verify_password(password, stored)
    except Exception:
        # Fallback: plain comparison (for dev setups where password isn't hashed)
        return password == stored


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.jwt_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_admin(token: str = Depends(oauth2_scheme)) -> dict:
    """FastAPI dependency – validates JWT and returns payload."""
    payload = decode_token(token)
    username: Optional[str] = payload.get("sub")
    if not username or username != settings.admin_username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorised",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"username": username, "role": payload.get("role", "admin")}


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """FastAPI dependency – validates any JWT (admin or regular user)."""
    payload = decode_token(token)
    username: Optional[str] = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"username": username, "role": payload.get("role", "user")}
