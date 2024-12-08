from typing import NoReturn
from hashlib import sha256
from io import BytesIO
import secrets
import qrcode

from data import storing

def hash(string: str | int) -> str:
    """
    Returns hash
    """

    return sha256(str(string).encode("utf-8")).hexdigest()

def create_qrcode(secret_code: int | str) -> BytesIO:
    """
    Returns byte stream qr code
    """

    hash = hash(secret_code)

    image_data = BytesIO()
    image = qrcode.make(hash)
    image.save(image_data, fromat = "png")

    image_data.seek(0)
    return image_data

def store_secret_code(secret_code: str | int) -> NoReturn:
    storing.store("data/secret_code.json", "secret_code", str(secret_code))

def get_secret_code() -> str | None:
    return storing.get_data("data/secret_code.json")["secret_code"]

def create_secret_code(length: int = 20) -> str:
    """
    Creates randomized secret code
    """

    return secrets.token_urlsafe(length)[0:length]