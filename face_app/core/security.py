from datetime import datetime, timedelta, timezone
from typing import Optional

from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from bson import ObjectId

from face_app.core.config import settings
from face_app.core.database import get_db


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token"
)
def create_access_token(
    payload: dict,
    expires: timedelta
) -> str:
    data = payload.copy()
    data.update({
        "exp": datetime.now(timezone.utc) + expires,
        "iat": datetime.now(timezone.utc),
        "sub": "access"
    })

    return jwt.encode(
        data,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

def create_refresh_token(payload: dict) -> str:
    data = payload.copy()
    data.update({
        "sub": "refresh",
        "iat": datetime.now(timezone.utc)
    })

    return jwt.encode(
        data,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
def decode_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db = Depends(get_db)
) -> dict:
    payload = decode_token(token)

    if payload.get("sub") != "access":
        raise HTTPException(
            status_code=401,
            detail="Invalid access token"
        )

    user_id = payload.get("id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload"
        )

    try:
        oid = ObjectId(user_id)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid user id"
        )

    user = await db.users.find_one({"_id": oid})
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user
def require_active_user(user: dict = Depends(get_current_user)):
    if not user.get("is_active", True):
        raise HTTPException(403, "User is inactive")
    return user
