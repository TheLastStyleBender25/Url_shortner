from uuid import UUID
from starlette import status
from app.services.url_service import UrlService
from app.schemas.url import UrlResponse, UrlListResponse, CreateUrlRequest, TokenPayload, ShortToUrlResponse
from fastapi import Depends
from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.rate_limiter import rate_limit
from fastapi.responses import RedirectResponse


router = APIRouter(tags=["URL Service"], prefix="/url")

url_service = UrlService()

@router.post('/create', response_model=UrlResponse)
async def create_url(url: CreateUrlRequest, db: AsyncSession = Depends(get_db), current_user: TokenPayload = Depends(get_current_user), checker:None = Depends(rate_limit(5, 60))):
    result = await url_service.create_url(current_user.id,url=url,db=db)
    return result

@router.get("/allurls",response_model=UrlListResponse)
async def get_my_urls(db: AsyncSession = Depends(get_db), current_user: TokenPayload = Depends(get_current_user), checker:None = Depends(rate_limit(5, 60))):
    result = await url_service.get_user_urls(user_id=current_user.id,db=db)
    return result

@router.get("/get/{url_id}",response_model=UrlResponse)
async def get_url(url_id: UUID,db: AsyncSession = Depends(get_db), current_user: TokenPayload = Depends(get_current_user), checker:None = Depends(rate_limit(5, 60))):
    result = await url_service.get_url_by_id(url_id=url_id,user_id=current_user.id,db=db)
    return result

@router.get("/getshort/{code}")
async def redirect_url(code:str, db:AsyncSession=Depends(get_db)):
    url = await url_service.get_url_by_short_code(code, db)
    return RedirectResponse(url=url.or_url,status_code=307)

@router.delete("/delete/{url_id}")
async def delete_url(url_id: UUID, db: AsyncSession = Depends(get_db), current_user: TokenPayload = Depends(get_current_user), checker:None = Depends(rate_limit(5, 60))):
    await url_service.delete_url(url_id=url_id,user_id=current_user.id,db=db)
    return {'message':'success'}

@router.get("/health")
async def health():
    return {"status": "ok"}
