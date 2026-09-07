from app.core.celery import celery_app
from app.services.email_service import EmailService


@celery_app.task(name="auth_email_task")
def send_verification_email_task(email:str, token: str) -> None:
    email_service = EmailService()
    verification_link = (f"http://localhost:8000/auth/verify-email?token={token}")
    email_service.send_verification_email(email, verification_link)

@celery_app.task(name="auth_otp_task")
def send_password_reset_otp(email:str, otp:str) -> None:
    email_service = EmailService()
    email_service.send_password_reset_otp(email, otp)