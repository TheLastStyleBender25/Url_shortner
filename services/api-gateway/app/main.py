from fastapi import FastAPI
from app.api.proxy import router as proxy_router

app = FastAPI(title="API Gateway",version="1.0.0")

app.include_router(proxy_router)


@app.get("/health")
async def health():
    return {"status": "ok"}