
from pathlib import Path
import qrcode


def generate_qr(text: str, output: Path, box_size: int = 6, border: int = 4) -> Path:
    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=box_size, border=border)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    output.parent.mkdir(parents=True, exist_ok=True)
    img.save(output)
    return output


def ascii_qr(text: str) -> str:
    qr = qrcode.QRCode(border=1)
    qr.add_data(text)
    qr.make(fit=True)
    m = qr.get_matrix()
    lines = []
    for row in m:
        line = ''.join('  ' if not cell else '██' for cell in row)
        lines.append(line)
    return "\n".join(lines)
