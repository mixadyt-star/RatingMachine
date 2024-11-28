from typing import NoReturn
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL
import hashlib
import json
import ssl

import config

#TODO: clear when expires
def store_code(email: str, code: str) -> NoReturn:
    with open("data/email_codes.json", 'r') as f:
        codes = json.loads(f.read())

    codes[email] = code

    with open("data/email_codes.json", 'w') as f:
        f.write(json.dumps(codes))

def get_code(email: str) -> str:
    with open("data/email_codes.json", 'r') as f:
        codes = json.loads(f.read())

    return codes.get(email)

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

def send_verification(receiver: str, code: str) -> NoReturn:
    verification_message = """
    Чтобы закончить регистрацию, подтвердите свою почту. Для этого введите код в поле на странице:
    <h1 style = "margin-top: 50px;text-align: center">{}</h1>
    """

    send_email(receiver, "Подтверждение почты", verification_message.format(code))