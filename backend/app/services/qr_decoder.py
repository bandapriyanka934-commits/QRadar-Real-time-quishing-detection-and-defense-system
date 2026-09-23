"""
QR Code Image Decoding Service.
Supports single and multiple QR code detection and extraction from image buffers using OpenCV.
"""

import io
import cv2
import numpy as np
from PIL import Image
from typing import List, Dict, Any, Tuple


class QRDecoderService:
    def __init__(self):
        self.detector = cv2.QRCodeDetector()

    def decode_image_bytes(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """
        Decodes all QR codes found in raw image bytes.
        Returns a list of dicts with 'content' and optional 'polygon' coordinates.
        """
        if not image_bytes:
            return []

        # Convert bytes to numpy array for OpenCV
        try:
            pil_image = Image.open(io.BytesIO(image_bytes))
            # Convert to RGB then OpenCV BGR
            pil_image = pil_image.convert("RGB")
            cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        except Exception as e:
            raise ValueError(f"Invalid or corrupted image format: {str(e)}")

        results: List[Dict[str, Any]] = []

        # 1. Try OpenCV multi-detection first
        try:
            retval, decoded_info, points, _ = self.detector.detectAndDecodeMulti(cv_image)
            if retval and decoded_info:
                for idx, text in enumerate(decoded_info):
                    if text and text.strip():
                        poly = points[idx].tolist() if points is not None and len(points) > idx else None
                        results.append({
                            "content": text.strip(),
                            "polygon": poly
                        })
        except Exception:
            pass

        # 2. Fallback to single detection if multi didn't return any
        if not results:
            try:
                text, points, _ = self.detector.detectAndDecode(cv_image)
                if text and text.strip():
                    poly = points.tolist() if points is not None else None
                    results.append({
                        "content": text.strip(),
                        "polygon": poly
                    })
            except Exception:
                pass

        # 3. Fallback to grayscale + thresholding if still empty
        if not results:
            try:
                gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
                # Otsu thresholding
                _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                text, points, _ = self.detector.detectAndDecode(thresh)
                if text and text.strip():
                    poly = points.tolist() if points is not None else None
                    results.append({
                        "content": text.strip(),
                        "polygon": poly
                    })
            except Exception:
                pass

        # 4. Fallback to pyzbar if available and still nothing found
        if not results:
            try:
                from pyzbar.pyzbar import decode as pyzbar_decode
                pyz_results = pyzbar_decode(cv_image)
                for item in pyz_results:
                    data = item.data.decode("utf-8", errors="ignore").strip()
                    if data:
                        results.append({
                            "content": data,
                            "polygon": [[p.x, p.y] for p in item.polygon] if item.polygon else None
                        })
            except Exception:
                pass

        # Deduplicate while preserving order
        unique_results: List[Dict[str, Any]] = []
        seen = set()
        for r in results:
            content = r["content"]
            if content not in seen:
                seen.add(content)
                unique_results.append(r)

        return unique_results


qr_decoder_service = QRDecoderService()
