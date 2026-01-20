from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# -------- USER REGISTER --------
class CreateUserRequest(BaseModel):
    user_name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

class CreateUserResponse(BaseModel):
    user_id: int
    user_name: str
    email: EmailStr
    message: str = "User created successfully"


# -------- AUTH --------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# -------- FACE VERIFY --------
class FaceVerifyResponse(BaseModel):
    verified: bool
    similarity: float
    message: str


# -------- USER INFO --------
class UserResponse(BaseModel):
    id: int
    user_name: str
    email: EmailStr
    is_active: bool
    is_verified: bool

    class Config:
        from_attributes = True
