"""
Generates safe, high-quality demonstration QR code images for QRadar testing.
"""

import os
import qrcode
from PIL import Image, ImageDraw, ImageFont

DEMO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "demo_assets"))
os.makedirs(DEMO_DIR, exist_ok=True)

DEMO_SAMPLES = [
    {
        "filename": "1_safe_google_qr.png",
        "content": "https://www.google.com/search?q=cybersecurity+research",
        "title": "Safe Global Domain"
    },
    {
        "filename": "2_typosquatting_paypal_qr.png",
        "content": "http://paypa1-account-verification.xyz/login.php",
        "title": "Brand Look-alike / Typosquatting (paypa1)"
    },
    {
        "filename": "3_ip_address_host_qr.png",
        "content": "http://192.168.1.105:8080/secure/paypal_login.htm",
        "title": "Rogue Direct IP Host (:8080)"
    },
    {
        "filename": "4_userinfo_at_trick_qr.png",
        "content": "https://paypal.com@evil-phishing-gate.ru/login",
        "title": "Deceptive Userinfo '@' Trick"
    },
    {
        "filename": "5_dangerous_scheme_qr.png",
        "content": "javascript:alert('Quishing Attack Blocked by QRadar')",
        "title": "Dangerous Scheme (javascript:)"
    },
    {
        "filename": "6_url_shortener_qr.png",
        "content": "http://bit.ly/3xSampleShortener",
        "title": "Cloaked URL Shortener (bit.ly)"
    }
]


def generate_qr_images():
    print(f"Generating {len(DEMO_SAMPLES)} demonstration QR images in {DEMO_DIR}...")
    for sample in DEMO_SAMPLES:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(sample["content"])
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        target_path = os.path.join(DEMO_DIR, sample["filename"])
        img.save(target_path)
        print(f"  [+] Created {sample['filename']} ({sample['title']}) -> {target_path}")

    # Generate multi-QR image (2 QR codes placed side-by-side in one image)
    multi_qr_path = os.path.join(DEMO_DIR, "7_multi_qr_sample.png")
    qr1 = qrcode.make("https://www.google.com").convert("RGB")
    qr2 = qrcode.make("http://paypa1-security.xyz/login").convert("RGB")

    combined = Image.new("RGB", (qr1.width + qr2.width + 40, max(qr1.height, qr2.height) + 40), color="white")
    combined.paste(qr1, (20, 20))
    combined.paste(qr2, (qr1.width + 20, 20))
    combined.save(multi_qr_path)
    print(f"  [+] Created multi-QR sample -> {multi_qr_path}")
    print("All demo QR codes generated successfully!")


if __name__ == "__main__":
    generate_qr_images()
