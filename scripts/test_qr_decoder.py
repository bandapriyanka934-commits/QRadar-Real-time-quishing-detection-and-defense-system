"""
Test script to verify QR decoder on generated sample QR assets.
"""

import os
import sys

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in [BACKEND_DIR, ROOT_DIR, os.path.join(ROOT_DIR, "ml", "src")]:
    if p not in sys.path:
        sys.path.insert(0, p)

from app.services.qr_decoder import qr_decoder_service

DEMO_DIR = os.path.join(ROOT_DIR, "demo_assets")

def test_decoder_on_samples():
    print("Testing QR Decoder on generated demo assets...")
    for filename in sorted(os.listdir(DEMO_DIR)):
        if not filename.endswith(".png"):
            continue
        filepath = os.path.join(DEMO_DIR, filename)
        with open(filepath, "rb") as f:
            bytes_data = f.read()
        
        decoded = qr_decoder_service.decode_image_bytes(bytes_data)
        print(f"\n[File: {filename}] -> Found {len(decoded)} QR code(s):")
        for idx, item in enumerate(decoded):
            print(f"   [{idx + 1}] {item['content']}")

if __name__ == "__main__":
    test_decoder_on_samples()
