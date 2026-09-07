from uuid import UUID
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.engine import result
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.database import get_db
from app.schemas.user import UserResponse, CreateUser, TokenResponse, NewTokenRequest, LoginRequest, ForgetPasswordRequest, VerifyOTP
from app.services.auth_service import AuthService
from app.core.rate_limiter import rate_limit

router = APIRouter(tags=['auth'], prefix="/auth")

auth = AuthService()

@router.post("/register", response_model=UserResponse)
async def register(user: CreateUser, db:AsyncSession = Depends(get_db), checker:None = Depends(rate_limit(5, 60))):
    result = await auth.register_user(user, db)
    return result

@router.post("/login", response_model=TokenResponse)
async def login(data:LoginRequest, db:AsyncSession = Depends(get_db), checker:None = Depends(rate_limit(5, 60))):
    result = await auth.login(data, db)
    return result

@router.post("/token", response_model=TokenResponse)
async def new_tokens(data:NewTokenRequest, db:AsyncSession = Depends(get_db), checker:None = Depends(rate_limit(5, 60))):
    result = await auth.get_new_token(db, data)
    return result

@router.get("/verify-email")
async def verify_email(token:str, db:AsyncSession = Depends(get_db)):
    await auth.verify_email(token, db)
    return {"message": "Email verified successfully"}

@router.post("/forgot-password")
async def forgot_password(email:ForgetPasswordRequest, db:AsyncSession = Depends(get_db), checker:None = Depends(rate_limit(5, 60))):
    await auth.forgot_password(email, db)
    return {"message": "Password reset email sent"}

@router.post('/verify-otp')
async def verify_otp(data:VerifyOTP, db:AsyncSession = Depends(get_db), checker:None = Depends(rate_limit(5, 60))):
    await auth.verify_otp(data, db)
    return {"message": "Password reset successfully"}

@router.get("/health")
async def health():
    return {"status": "ok"}



