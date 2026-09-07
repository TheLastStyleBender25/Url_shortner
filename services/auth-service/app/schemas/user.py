from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class CreateUser(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64)

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    name: str

    model_config = {"from_attributes": True}

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64)

class NewTokenRequest(BaseModel):
    token:str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'

class ForgetPasswordRequest(BaseModel):
    email: EmailStr

class VerifyOTP(BaseModel):
    email: EmailStr
    otp:str=Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")
    new_password: str = Field(..., min_length=8, max_length=64)