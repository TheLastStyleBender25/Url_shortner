import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import Request
from fastapi.testclient import TestClient
from app.main import app
from app.api.proxy import (
    auth_proxy,
    url_proxy,
    forward_request,
)


client = TestClient(app)



def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}



@pytest.mark.asyncio
async def test_auth_proxy():
    request = MagicMock(spec=Request)

    with patch(
        "app.api.proxy.forward_request",
        new_callable=AsyncMock
    ) as mock_forward:

        mock_forward.return_value = MagicMock()

        await auth_proxy(
            path="login",
            request=request
        )

        mock_forward.assert_awaited_once_with(
            request=request,
            target_url=(
                "http://auth-service-URL:8000/auth/login"
            )
        )




@pytest.mark.asyncio
async def test_url_proxy():
    request = MagicMock(spec=Request)

    with patch(
        "app.api.proxy.forward_request",
        new_callable=AsyncMock
    ) as mock_forward:

        mock_forward.return_value = MagicMock()

        await url_proxy(
            path="getshort/ABC123",
            request=request
        )

        mock_forward.assert_awaited_once_with(
            request=request,
            target_url=(
                "http://url-service-URL:8000/url/getshort/ABC123"
            )
        )



@pytest.mark.asyncio
async def test_forward_request():
    request = MagicMock(spec=Request)

    request.body = AsyncMock(
        return_value=b'{"email":"test@example.com"}'
    )

    request.method = "POST"
    request.headers = {
        "content-type": "application/json"
    }
    request.query_params = {
        "page": "1"
    }

    mock_response = MagicMock()

    mock_response.content = b'{"status":"success"}'
    mock_response.status_code = 200
    mock_response.headers = {
        "content-type": "application/json"
    }

    with patch(
        "app.api.proxy.httpx.AsyncClient"
    ) as mock_client:

        mock_client_instance = MagicMock()

        mock_client.return_value.__aenter__ = AsyncMock(
            return_value=mock_client_instance
        )

        mock_client.return_value.__aexit__ = AsyncMock(
            return_value=None
        )

        mock_client_instance.request = AsyncMock(
            return_value=mock_response
        )

        result = await forward_request(
            request=request,
            target_url="http://test-service/test"
        )

    mock_client_instance.request.assert_awaited_once_with(
        method="POST",
        url="http://test-service/test",
        headers={
            "content-type": "application/json"
        },
        content=b'{"email":"test@example.com"}',
        params={
            "page": "1"
        }
    )

    assert result.status_code == 200
    assert result.body == b'{"status":"success"}'



@pytest.mark.asyncio
async def test_auth_proxy_nested_path():
    request = MagicMock(spec=Request)

    with patch(
        "app.api.proxy.forward_request",
        new_callable=AsyncMock
    ) as mock_forward:

        mock_forward.return_value = MagicMock()

        await auth_proxy(
            path="verify-email/token123",
            request=request
        )

        mock_forward.assert_awaited_once_with(
            request=request,
            target_url=(
                "http://auth-service-URL:8000/"
                "auth/verify-email/token123"
            )
        )



@pytest.mark.asyncio
async def test_url_proxy_nested_path():
    request = MagicMock(spec=Request)

    with patch(
        "app.api.proxy.forward_request",
        new_callable=AsyncMock
    ) as mock_forward:

        mock_forward.return_value = MagicMock()

        await url_proxy(
            path="get/12345678-1234-1234-1234-123456789abc",
            request=request
        )

        mock_forward.assert_awaited_once_with(
            request=request,
            target_url=(
                "http://url-service-URL:8000/"
                "url/get/12345678-1234-1234-1234-123456789abc"
            )
        )