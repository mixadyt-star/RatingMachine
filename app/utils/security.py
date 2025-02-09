from pyzbar.pyzbar import decode
from cv2.typing import MatLike
from typing import NoReturn
from hashlib import sha256
from io import BytesIO
from PIL import Image
import secrets
import qrcode
import cv2

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

    hashed_code = hash(secret_code)

    image_data = BytesIO()
    image = qrcode.make(hashed_code)
    image.save(image_data, fromat = "png")

    image_data.seek(0)
    return image_data

def read_qrcode(img: MatLike) -> str:
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    decocdeQR = decode(Image.fromarray(img))
    return decocdeQR[0].data.decode('ascii')

def store_secret_code(secret_code: str | int) -> NoReturn:
    storing.store("data/secret_code.json", "secret_code", str(secret_code))

def get_secret_code() -> str | None:
    return storing.get_data("data/secret_code.json")["secret_code"]

def create_secret_code(length: int = 20) -> str:
    """
    Creates randomized secret code
    """

    return secrets.token_urlsafe(length)[0:length]