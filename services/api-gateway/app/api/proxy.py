from fastapi import APIRouter, Request
from fastapi.responses import Response
import httpx
from app.core.config import settings
from app.core.logger import logger

router = APIRouter()


@router.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def auth_proxy(path:str, request: Request):
    logger.info(f"Request path: {path}")
    return await forward_request(request=request, target_url=f"{settings.AUTH_SERVICE_URL}/auth/{path}")


@router.api_route("/url/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def url_proxy(path:str, request: Request):
    logger.info(f"Request path: {path}")
    return await forward_request(request=request, target_url=f"{settings.URL_SERVICE_URL}/url/{path}")



async def forward_request(request: Request, target_url:str):
    body = await request.body()
    async with httpx.AsyncClient() as client:
        response = await client.request(method=request.method,
                                        url=target_url,
                                        headers=dict(request.headers),
                                        content=body,
                                        params=request.query_params)

    return Response(content=response.content,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.headers.get("content-type"))
