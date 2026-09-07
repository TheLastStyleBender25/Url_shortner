from fastapi import FastAPI
from app.api.v1.url import router as url_router
from app.exceptions.exceptions import UnauthorizedException, UrlExpiredException, UrlNotFoundException
from app.exceptions.handlers import unauthorized_handler, url_expired_handler, url_not_found_handler


app = FastAPI(title="url")

app.add_exception_handler(UnauthorizedException,unauthorized_handler)
app.add_exception_handler(UrlExpiredException,url_expired_handler)
app.add_exception_handler(UrlNotFoundException,url_not_found_handler)

app.include_router(url_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}