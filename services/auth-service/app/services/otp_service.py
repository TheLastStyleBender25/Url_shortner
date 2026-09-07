import secrets
from app.core.redis_component import redis_client

class OTPService:
    otp_expiry_seconds = 60*5

    async def create_otp(self, email:str)->str:
        otp = f"{secrets.randbelow(1_000_000):06d}"
        key = f"password_reset_otp:{email}"
        await  redis_client.setex(key, self.otp_expiry_seconds, otp)
        return otp

    async def verify_otp(self, email:str, otp:str)->bool:
        key = f"password_reset_otp:{email}"
        stored_otp = await redis_client.get(key)
        if stored_otp is None:
            return False
        if stored_otp != otp:
            return False
        await redis_client.delete(key)
        return True


