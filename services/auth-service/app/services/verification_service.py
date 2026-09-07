import secrets
from app.core.redis_component import redis_client

class VerificationService:

    token_expiry_seconds = 60*15

    async def create_token(self, email:str)-> str:
        token = secrets.token_urlsafe(32)
        key = f"email_verification:{token}"
        await redis_client.setex(key, self.token_expiry_seconds, email)
        return token

    async def verify_token(self, token:str)-> str|None:
        key = f"email_verification:{token}"
        email = await redis_client.get(key)
        if email is None:
            return None
        await redis_client.delete(key)
        return email


