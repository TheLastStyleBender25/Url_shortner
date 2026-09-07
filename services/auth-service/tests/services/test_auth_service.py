from datetime import datetime, timezone
from uuid import uuid4
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.services.auth_service import AuthService
from app.schemas.user import LoginRequest, CreateUser, NewTokenRequest, ForgetPasswordRequest, VerifyOTP
from app.exceptions.auth_exceptions import UserNotFoundException, InvalidCredentialsException, \
    EmailAlreadyExistsException, InvalidRefreshTokenException, InvalidTokenException


@pytest.fixture
def auth_service():
    return AuthService()

@pytest.fixture
def db():
    db = MagicMock()
    db.execute = AsyncMock()
    return db


@pytest.mark.asyncio
async def test_login_user_not_found(auth_service, db):
    data = LoginRequest(email='test@example.com', password='password123')
    auth_service.user_repo.get_by_email = AsyncMock(return_value=False)
    with pytest.raises(UserNotFoundException):
        await auth_service.login(data, db)
    auth_service.user_repo.get_by_email.assert_awaited_once_with(data.email, db)

@pytest.mark.asyncio
async def test_login_invalid_password(auth_service, db):
    data = LoginRequest(email='test@example.com', password='wrongpassword')
    user = MagicMock()
    user.email = data.email
    user.password = 'hashedpassword'
    user.is_verified = True
    auth_service.user_repo.get_by_email = AsyncMock(return_value=user)
    with patch('app.services.auth_service.verify_password', return_value=False):
        with pytest.raises(InvalidCredentialsException):
            await auth_service.login(data, db)

@pytest.mark.asyncio
async def test_login_valid_password(auth_service, db):
    data = LoginRequest(email='test@example.com', password='correctpassword')
    user_id = uuid4()
    user = MagicMock()

    user.email = data.email
    user.password_hash = 'hashed_password'
    user.is_verified = True
    user.id = user_id

    auth_service.user_repo.get_by_email = AsyncMock(return_value=user)
    auth_service.rt_repo.delet_by_id = AsyncMock()
    auth_service.rt_repo.create = AsyncMock()

    with patch('app.services.auth_service.verify_password', return_value=True), patch("app.services.auth_service.create_access_token", return_value="access-token"),patch("app.services.auth_service.create_refresh_token",return_value="refresh-token"),patch("app.services.auth_service.hash_refresh_token", return_value="hashed-refresh-token"):
        result = await auth_service.login(data, db)

    assert result.access_token == "access-token"
    assert result.refresh_token == "refresh-token"

    auth_service.user_repo.get_by_email.assert_awaited_once_with(data.email,db,)

    auth_service.rt_repo.delet_by_id.assert_awaited_once_with(db,user.id)

    auth_service.rt_repo.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_login_unverified_user(auth_service, db):
    data = LoginRequest(email='test@example.com', password='correctpassword')
    user_id = uuid4()
    user = MagicMock()

    user.email = data.email
    user.password_hash = 'hashed_password'
    user.is_verified = False
    user.id = user_id

    auth_service.user_repo.get_by_email = AsyncMock(return_value=user)

    with patch('app.services.auth_service.verify_password', return_value=True):
        with pytest.raises(UserNotFoundException):
            await auth_service.login(data, db)

    auth_service.user_repo.get_by_email.assert_awaited_once_with(data.email, db)


@pytest.mark.asyncio
async def test_register_user_email_exists(auth_service, db):
    data = CreateUser(name='test', email='test@gmail.com', password='testpassword')

    auth_service.user_repo.get_by_email = AsyncMock(return_value=MagicMock())

    with pytest.raises(EmailAlreadyExistsException):
        await auth_service.register_user(data, db)

    auth_service.user_repo.get_by_email.assert_awaited_once_with(data.email, db)


@pytest.mark.asyncio
async def test_register_user_success(auth_service, db):
    data = CreateUser(name='test', email='test@gmail.com', password='testpassword')

    created_user = MagicMock()

    created_user.id = uuid4()
    created_user.name = data.name
    created_user.email = data.email
    created_user.password_hash = "hashed_password"
    created_user.is_verified = False
    created_user.created_at = datetime.now(timezone.utc)
    created_user.updated_at = datetime.now(timezone.utc)

    auth_service.user_repo.get_by_email = AsyncMock(return_value=None)
    auth_service.user_repo.create = AsyncMock(return_value=created_user)

    with patch('app.services.auth_service.hash_password', return_value="hashed_password"), patch("app.services.auth_service.send_verification_email_task") as email_task, patch(
            "app.services.auth_service.cleanup_task") as cleanup_task:
        auth_service.verification_service.create_token = AsyncMock(return_value="verification-token")
        auth_service.verification_service.token_expiry_seconds = 300
        result = await auth_service.register_user(data, db)

    assert result == created_user

    auth_service.user_repo.get_by_email.assert_awaited_once_with(data.email,db)

    auth_service.user_repo.create.assert_awaited_once()

    auth_service.verification_service.create_token.assert_awaited_once_with(data.email)

    email_task.delay.assert_called_once_with(data.email,"verification-token")

    cleanup_task.apply_async.assert_called_once_with(args=[data.email],countdown=360)


@pytest.mark.asyncio
async def test_get_new_token_invalid_refresh_token(auth_service, db):
    token = NewTokenRequest(token='invalid-refresh-token')
    auth_service.rt_repo.get_by_token_hash = AsyncMock(return_value=None)

    with patch("app.services.auth_service.hash_refresh_token",return_value="hashed-token"):
        with pytest.raises(InvalidRefreshTokenException):
            await auth_service.get_new_token(db, token)

    auth_service.rt_repo.get_by_token_hash.assert_awaited_once_with(db,"hashed-token")


@pytest.mark.asyncio
async def test_get_new_token_decode_failure(auth_service, db):
    token = NewTokenRequest(token='invalid-refresh-token')
    auth_service.rt_repo.get_by_token_hash = AsyncMock(return_value=MagicMock())

    with patch("app.services.auth_service.hash_refresh_token",return_value="hashed-token"), patch("app.services.auth_service.decode_token",side_effect=InvalidRefreshTokenException()):
        with pytest.raises(InvalidRefreshTokenException):
            await auth_service.get_new_token(db, token)

    auth_service.rt_repo.get_by_token_hash.assert_awaited_once_with(db,"hashed-token")


@pytest.mark.asyncio
async def test_verify_email_invalid_token(auth_service, db):
    token = 'invalid-token'

    auth_service.verification_service.verify_token = AsyncMock(return_value=None)

    with pytest.raises(InvalidTokenException):
        await auth_service.verify_email(token, db)

    auth_service.verification_service.verify_token.assert_awaited_once_with(token)


@pytest.mark.asyncio
async def test_verify_email_success(auth_service, db):
    token = 'valid-token'

    user = MagicMock()

    user.email = "test@example.com"
    user.is_verified = False

    auth_service.verification_service.verify_token = AsyncMock(return_value=user.email)
    auth_service.user_repo.get_by_email = AsyncMock(return_value=user)

    db.commit = AsyncMock()
    await auth_service.verify_email(token, db)
    assert user.is_verified is True

    auth_service.verification_service.verify_token.assert_awaited_once_with(token)
    auth_service.user_repo.get_by_email.assert_awaited_once_with(user.email,db)

    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_forgot_password_user_not_found(auth_service, db):
    data = ForgetPasswordRequest(email="test@example.com")

    auth_service.user_repo.get_by_email = AsyncMock(return_value=None)

    with pytest.raises(UserNotFoundException):
        await auth_service.forgot_password(data, db)

    auth_service.user_repo.get_by_email.assert_awaited_once_with(data.email,db)


@pytest.mark.asyncio
async def test_forgot_password_success(auth_service, db):
    data = ForgetPasswordRequest(email="test@example.com")

    user = MagicMock()
    user.email = data.email
    user.is_verified = True

    auth_service.user_repo.get_by_email = AsyncMock(return_value=user)
    auth_service.otp_service.create_otp = AsyncMock(return_value='123456')

    with patch("app.services.auth_service.send_password_reset_otp") as otp_task:
        await auth_service.forgot_password(data, db)

    auth_service.user_repo.get_by_email.assert_awaited_once_with(data.email,db)

    auth_service.otp_service.create_otp.assert_awaited_once_with(data.email)

    otp_task.assert_called_once_with(data.email,"123456")


@pytest.mark.asyncio
async def test_verify_otp_invalid_otp(auth_service, db):
    data = VerifyOTP(email="test@example.com",otp="123456",new_password="newpassword123")

    auth_service.otp_service.verify_otp = AsyncMock(return_value=False)

    with pytest.raises(InvalidTokenException):
        await auth_service.verify_otp(data, db)

    auth_service.otp_service.verify_otp.assert_awaited_once_with(data.email,data.otp)


@pytest.mark.asyncio
async def test_verify_otp_success(auth_service, db):
    data = VerifyOTP(email="test@example.com",otp="123456", new_password="newpassword123")

    user = MagicMock()
    user.email = data.email
    user.password_hash = "old-hashed-password"

    auth_service.otp_service.verify_otp = AsyncMock(return_value=True)

    auth_service.user_repo.get_by_email = AsyncMock(return_value=user)

    db.commit = AsyncMock()

    with patch("app.services.auth_service.hash_password",return_value="new-hashed-password"):

        await auth_service.verify_otp(data, db)

    assert user.password_hash == "new-hashed-password"

    auth_service.otp_service.verify_otp.assert_awaited_once_with(data.email,data.otp)

    auth_service.user_repo.get_by_email.assert_awaited_once_with(data.email,db)

    db.commit.assert_awaited_once()




