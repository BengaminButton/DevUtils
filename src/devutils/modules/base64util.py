
import base64


def b64_encode(data: bytes) -> bytes:
    return base64.b64encode(data)


def b64_decode(data: bytes) -> bytes:
    return base64.b64decode(data)
