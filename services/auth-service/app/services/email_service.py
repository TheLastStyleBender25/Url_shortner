import resend
from app.core.config import settings

class EmailService:
    def __init__(self):
        resend.api_key = settings.RESEND_API_KEY

    def send_verification_email(self, email:str, link:str):
        params = {
            "from": settings.EMAIL_FROM,
            "to": [email],
            "subject": "Verify your Frostbite account",
            "html": f"""
                <h2>Welcome to Frostbite!</h2>

                <p>
                    Please verify your email address by clicking
                    the link below:
                </p>

                <p>
                    <a href="{link}">
                        Verify Email
                    </a>
                </p>

                <p>
                    This verification link will expire in 15 minutes.
                </p>
            """,
        }
        return resend.Emails.send(params)

    def send_password_reset_otp(self, email:str, otp:str):
        params = {
            "from": settings.EMAIL_FROM,
            "to": [email],
            "subject": "Your Frostbite password reset OTP",
            "html": f"""
                    <h2>Password Reset</h2>

                    <p>
                        Use the following OTP to reset your Frostbite password:
                    </p>

                    <h1>{otp}</h1>

                    <p>
                        This OTP will expire in 5 minutes.
                    </p>

                    <p>
                        If you did not request a password reset,
                        you can safely ignore this email.
                    </p>
                """,
        }

        return resend.Emails.send(params)
