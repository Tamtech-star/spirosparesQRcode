import qrcode
from PIL import Image

def generate_secure_qr(url_to_encode, size=(250, 250), border_size=4):
    """Generates a QR code for the specified secure HTTPS URL."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10, 
        border=border_size,
    )
    qr.add_data(url_to_encode)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    if size:
        qr_img = qr_img.resize(size, Image.Resampling.NEAREST)
        
    return qr_img