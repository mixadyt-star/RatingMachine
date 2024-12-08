from typing import NoReturn
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL
import hashlib
import ssl

from data import storing
import config

def store_code(email: str, code: str | int) -> NoReturn:
    storing.store("data/email_codes.json", email, str(code))

def get_code(email: str) -> str | None:
    storing.get_data("data/email_codes.json")[email]

def send_email(receiver: str, subject: str, body: str) -> NoReturn:
    context = ssl.create_default_context()

    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = config.SENDER_ALIAS + f" <{config.SENDER_EMAIL}>"
    message['To'] = receiver
    message.attach(MIMEText(body, "html"))

    with SMTP_SSL(config.SMTP_SERVER, config.SMTP_PORT, context = context) as server:
        server.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)
        server.sendmail(config.SENDER_EMAIL, receiver, message.as_string())
        server.quit()

def send_verification(receiver: str, code: str | int) -> NoReturn:
    verification_message = """
    Чтобы закончить регистрацию, подтвердите свою почту. Для этого введите код в поле на странице:
    <h1 style = "margin-top: 50px;text-align: center">{}</h1>
    """

    send_email(receiver, "Подтверждение почты", verification_message.format(str(code)))