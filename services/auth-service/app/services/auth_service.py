from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, RefreshToken
from app.schemas.user import CreateUser, UserResponse, LoginRequest, TokenResponse, NewTokenRequest, ForgetPasswordRequest, VerifyOTP
from app.repositories.UserRepository import UserRepository
from app.repositories.RefreshTokenRepository import RefreshTokenRepository
from app.core.jwt import create_access_token, create_refresh_token, decode_token
from app.core.security import hash_password, verify_password, hash_refresh_token
from app.services.verification_service import VerificationService
from app.tasks.email_tasks import send_verification_email_task, send_password_reset_otp
from app.tasks.cleanup_tasks import cleanup_task
from app.services.otp_service import OTPService
from app.exceptions.auth_exceptions import EmailAlreadyExistsException, InvalidCredentialsException, InvalidRefreshTokenException, CeleryTaskException, UserNotFoundException, UserNotVerifiedException, IncorrectOTPException, InvalidTokenException

class AuthService:

    def __init__(self):
        self.user_repo = UserRepository()
        self.rt_repo = RefreshTokenRepository()
        self.verification_service = VerificationService()
        self.otp_service = OTPService()


    async def register_user(self, user: CreateUser, db : AsyncSession) -> UserResponse:
        exist = await self.user_repo.get_by_email(user.email, db)
        if exist:
            raise EmailAlreadyExistsException()
        new_user = User(email=user.email, name=user.name, password_hash=hash_password(user.password))
        created_user = await self.user_repo.create(db, new_user)
        token_verify = await self.verification_service.create_token(created_user.email)
        send_verification_email_task.delay(created_user.email, token_verify)
        cleanup_task.apply_async(args=[created_user.email], countdown=self.verification_service.token_expiry_seconds+60)
        return created_user

    async def login(self, data: LoginRequest, db: AsyncSession) -> TokenResponse:
        user = await self.user_repo.get_by_email(data.email, db)
        if not user:
            raise UserNotFoundException()
        if not verify_password(data.password, user.password_hash):
            raise InvalidCredentialsException()
        if not user.is_verified:
            raise UserNotFoundException()
        await self.rt_repo.delet_by_id(db, user.id)

        access_token = create_access_token(user.email, user.id)
        refresh_token = create_refresh_token(user.email)

        rft = RefreshToken(user_id=user.id, token_hash=hash_refresh_token(refresh_token))
        await self.rt_repo.create(db, rft)

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)


    async def get_new_token(self, db: AsyncSession, data:NewTokenRequest) -> TokenResponse:
        hash = hash_refresh_token(data.token)
        found = await self.rt_repo.get_by_token_hash(db, hash)
        if not found:
            raise InvalidRefreshTokenException()
        try:
            decode = decode_token(data.token)
        except Exception:
            raise InvalidRefreshTokenException()
        user_email = decode.get('sub')
        user = await self.user_repo.get_by_email(user_email, db)
        if not user:
            raise UserNotFoundException()

        await self.rt_repo.delet_by_id(db, user.id)

        access_token = create_access_token(user.email, user.id)
        refresh_token = create_refresh_token(user.email)

        rft = RefreshToken(user_id=user.id, token_hash=hash_refresh_token(refresh_token))
        await self.rt_repo.create(db, rft)

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)


    async def verify_email(self, token: str, db: AsyncSession) -> None:
        email = await self.verification_service.verify_token(token)
        if email is None:
            raise InvalidTokenException()
        user = await self.user_repo.get_by_email(email, db)
        if not user:
            raise UserNotFoundException()
        if user.is_verified:
            return
        user.is_verified = True
        await db.commit()

    async def forgot_password(self, data: ForgetPasswordRequest, db: AsyncSession) -> None:
        user = await self.user_repo.get_by_email(data.email, db)
        if not user:
            raise UserNotFoundException()
        if not user.is_verified:
            raise UserNotFoundException()
        otp = await self.otp_service.create_otp(data.email)
        send_password_reset_otp(data.email, otp)

    async def verify_otp(self, data: VerifyOTP, db:AsyncSession) -> None:
        valid = await self.otp_service.verify_otp(data.email, data.otp)
        if not valid:
            raise InvalidTokenException()
        user = await self.user_repo.get_by_email(data.email, db)
        if not user:
            raise UserNotFoundException()
        user.password_hash = hash_password(data.new_password)
        await db.commit()



















