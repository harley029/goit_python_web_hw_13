from fastapi_mail import FastMail, MessageSchema, MessageType
from fastapi_mail.errors import ConnectionErrors

from pydantic import EmailStr

from src.services.auth import auth_serviсe

from src.conf.config import conf


async def send_email(email: EmailStr, username: str, host: str):
    try:
        token_verification = auth_serviсe.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )
        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_verification.html")
    except ConnectionErrors as err:
        print(err)


async def send_password_reset_email(email: EmailStr, username: str, host: str):
    try:
        token_verification = auth_serviсe.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Password reset ",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )
        fm = FastMail(conf)
        await fm.send_message(message, template_name="password_reset_mail.html")
    except ConnectionErrors as err:
        print(err)