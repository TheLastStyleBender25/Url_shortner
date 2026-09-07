import pytest

from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.services.url_service import UrlService
from app.schemas.url import CreateUrlRequest
from app.exceptions.exceptions import (
    UrlNotFoundException,
    UrlExpiredException,
    UnauthorizedException,
)




def test_generate_short_code():
    service = UrlService()

    result = service.generate_short_code()

    assert len(result) == 6
    assert result.isalnum()




@pytest.mark.asyncio
async def test_create_url_success():
    service = UrlService()

    db = MagicMock()
    user_id = uuid4()

    data = CreateUrlRequest(
        url="https://example.com"
    )

    # No collision
    service.url_repo.get_by_short_code = AsyncMock(
        return_value=None
    )

    # Simulate SQLAlchemy generating the UUID
    async def fake_create(url, db):
        url.id = uuid4()
        return url

    service.url_repo.create = AsyncMock(
        side_effect=fake_create
    )

    with patch(
        "app.services.url_service.cleanup_task"
    ) as cleanup_task:

        result = await service.create_url(
            user_id=user_id,
            url=data,
            db=db
        )

    assert result.id is not None
    assert str(result.url) == "https://example.com/"
    assert len(result.short) == 6
    assert result.is_active is True

    service.url_repo.get_by_short_code.assert_awaited_once()
    service.url_repo.create.assert_awaited_once()

    cleanup_task.apply_async.assert_called_once()


@pytest.mark.asyncio
async def test_create_url_short_code_collision():
    service = UrlService()

    db = MagicMock()
    user_id = uuid4()

    data = CreateUrlRequest(
        url="https://example.com"
    )

    existing_url = MagicMock()

    # First code already exists.
    # Second code is available.
    service.url_repo.get_by_short_code = AsyncMock(
        side_effect=[
            existing_url,
            None
        ]
    )

    # Simulate SQLAlchemy generating UUID
    async def fake_create(url, db):
        url.id = uuid4()
        return url

    service.url_repo.create = AsyncMock(
        side_effect=fake_create
    )

    with patch(
        "app.services.url_service.cleanup_task"
    ) as cleanup_task:

        result = await service.create_url(
            user_id=user_id,
            url=data,
            db=db
        )

    assert result.id is not None
    assert str(result.url) == "https://example.com/"
    assert len(result.short) == 6

    assert service.url_repo.get_by_short_code.await_count == 2

    service.url_repo.create.assert_awaited_once()

    cleanup_task.apply_async.assert_called_once()




@pytest.mark.asyncio
async def test_get_url_by_short_code_not_found():
    service = UrlService()

    db = MagicMock()

    service.url_repo.get_by_short_code = AsyncMock(
        return_value=None
    )

    with pytest.raises(UrlNotFoundException):
        await service.get_url_by_short_code(
            short_code="ABC123",
            db=db
        )

    service.url_repo.get_by_short_code.assert_awaited_once_with(
        "ABC123",
        db
    )


@pytest.mark.asyncio
async def test_get_url_by_short_code_inactive():
    service = UrlService()

    db = MagicMock()

    url = MagicMock()
    url.is_active = False

    service.url_repo.get_by_short_code = AsyncMock(
        return_value=url
    )

    with pytest.raises(UrlNotFoundException):
        await service.get_url_by_short_code(
            short_code="ABC123",
            db=db
        )

    service.url_repo.get_by_short_code.assert_awaited_once_with(
        "ABC123",
        db
    )


@pytest.mark.asyncio
async def test_get_url_by_short_code_expired():
    service = UrlService()

    db = MagicMock()

    url = MagicMock()

    url.is_active = True

    url.expires_at = (
        datetime.now(timezone.utc)
        - timedelta(minutes=1)
    )

    service.url_repo.get_by_short_code = AsyncMock(
        return_value=url
    )

    with pytest.raises(UrlExpiredException):
        await service.get_url_by_short_code(
            short_code="ABC123",
            db=db
        )

    service.url_repo.get_by_short_code.assert_awaited_once_with(
        "ABC123",
        db
    )


@pytest.mark.asyncio
async def test_get_url_by_short_code_success():
    service = UrlService()

    db = MagicMock()

    url = MagicMock()

    url.is_active = True

    url.expires_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=5)
    )

    url.original_url = "https://example.com"

    service.url_repo.get_by_short_code = AsyncMock(
        return_value=url
    )

    result = await service.get_url_by_short_code(
        short_code="ABC123",
        db=db
    )

    assert str(result.or_url) == "https://example.com/"

    service.url_repo.get_by_short_code.assert_awaited_once_with(
        "ABC123",
        db
    )



@pytest.mark.asyncio
async def test_get_url_by_id_not_found():
    service = UrlService()

    db = MagicMock()

    url_id = uuid4()
    user_id = uuid4()

    service.url_repo.get_by_id = AsyncMock(
        return_value=None
    )

    with pytest.raises(UrlNotFoundException):
        await service.get_url_by_id(
            url_id=url_id,
            user_id=user_id,
            db=db
        )

    service.url_repo.get_by_id.assert_awaited_once_with(
        db,
        url_id
    )


@pytest.mark.asyncio
async def test_get_url_by_id_unauthorized():
    service = UrlService()

    db = MagicMock()

    url_id = uuid4()

    requested_user_id = uuid4()
    actual_user_id = uuid4()

    url = MagicMock()

    url.id = url_id
    url.user_id = actual_user_id

    service.url_repo.get_by_id = AsyncMock(
        return_value=url
    )

    with pytest.raises(UnauthorizedException):
        await service.get_url_by_id(
            url_id=url_id,
            user_id=requested_user_id,
            db=db
        )

    service.url_repo.get_by_id.assert_awaited_once_with(
        db,
        url_id
    )


@pytest.mark.asyncio
async def test_get_url_by_id_success():
    service = UrlService()

    db = MagicMock()

    user_id = uuid4()
    url_id = uuid4()

    url = MagicMock()

    url.id = url_id
    url.user_id = user_id
    url.original_url = "https://example.com"
    url.short_code = "ABC123"
    url.expires_at = None
    url.is_active = True
    url.created_at = datetime.now(timezone.utc)

    service.url_repo.get_by_id = AsyncMock(
        return_value=url
    )

    result = await service.get_url_by_id(
        url_id=url_id,
        user_id=user_id,
        db=db
    )

    assert result.id == url_id
    assert str(result.url) == "https://example.com/"
    assert result.short == "ABC123"
    assert result.expires_at is None
    assert result.is_active is True
    assert result.created_at == url.created_at

    service.url_repo.get_by_id.assert_awaited_once_with(
        db,
        url_id
    )



@pytest.mark.asyncio
async def test_delete_url_not_found():
    service = UrlService()

    db = MagicMock()

    url_id = uuid4()
    user_id = uuid4()

    service.url_repo.get_by_id = AsyncMock(
        return_value=None
    )

    with pytest.raises(UrlNotFoundException):
        await service.delete_url(
            url_id=url_id,
            user_id=user_id,
            db=db
        )

    service.url_repo.get_by_id.assert_awaited_once_with(
        db,
        url_id
    )


@pytest.mark.asyncio
async def test_delete_url_unauthorized():
    service = UrlService()

    db = MagicMock()

    url_id = uuid4()

    requested_user_id = uuid4()
    actual_user_id = uuid4()

    url = MagicMock()

    url.id = url_id
    url.user_id = actual_user_id
    url.is_active = True

    service.url_repo.get_by_id = AsyncMock(
        return_value=url
    )

    with pytest.raises(UnauthorizedException):
        await service.delete_url(
            url_id=url_id,
            user_id=requested_user_id,
            db=db
        )

    service.url_repo.get_by_id.assert_awaited_once_with(
        db,
        url_id
    )


@pytest.mark.asyncio
async def test_delete_url_success():
    service = UrlService()

    db = MagicMock()
    db.commit = AsyncMock()

    url_id = uuid4()
    user_id = uuid4()

    url = MagicMock()

    url.id = url_id
    url.user_id = user_id
    url.is_active = True

    service.url_repo.get_by_id = AsyncMock(
        return_value=url
    )

    await service.delete_url(
        url_id=url_id,
        user_id=user_id,
        db=db
    )

    assert url.is_active is False

    db.commit.assert_awaited_once()

    service.url_repo.get_by_id.assert_awaited_once_with(
        db,
        url_id
    )
