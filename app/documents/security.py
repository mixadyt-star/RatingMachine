import secrets
import qrcode
from hashlib import sha256
from io import BytesIO

def create_qrcode(secret_code: int | str) -> BytesIO:
    """
    Returns byte stream qr code
    """

    hash = sha256(str(secret_code).encode("utf-8")).hexdigest()

    image_data = BytesIO()
    image = qrcode.make(hash)
    image.save(image_data, fromat = "png")

    image_data.seek(0)
    return image_data

def create_secret_code(length: int = 20) -> str:
    """
    Creates randomized secret code
    """

    return secrets.token_urlsafe(length)

if __name__ == "__main__":
    print(create_qrcode(create_secret_code(100)))