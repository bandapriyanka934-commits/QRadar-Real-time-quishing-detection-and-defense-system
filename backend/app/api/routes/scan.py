"""
Scan API Endpoints.
Provides URL scanning, Image QR scanning (with multi-QR support), and QR decoding.
"""

import os
from typing import List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.scan import URLScanRequest, SecurityResult, MultiQRDecodeResponse, QRItem
from app.services.scan_service import scan_service
from app.services.qr_decoder import qr_decoder_service
from app.services.url_analyzer import url_analyzer_service
from app.core.config import settings
from app.core.rate_limiter import rate_limit_dependency

router = APIRouter(
    prefix="/scan",
    tags=["Scanning & Security Evaluation"],
    dependencies=[Depends(rate_limit_dependency)]
)


@router.post(
    "/url",
    response_model=SecurityResult,
    summary="Analyze URL or QR Text Payload",
    description="Performs complete security analysis (Heuristics, ML, Threat Intelligence, Risk Scoring) on a URL string."
)
async def scan_url(
    payload: URLScanRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Analyzes a URL or text string and returns authoritative risk verdict,
    risk score (0-100), recommended action (ALLOW/WARN/BLOCK), and explainable reasons.
    """
    if not payload.url or not payload.url.strip():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="URL payload cannot be empty.")
    
    result = await scan_service.analyze_and_persist(
        raw_content=payload.url.strip(),
        db=db,
        source=payload.source or "manual"
    )
    return result


@router.post(
    "/image",
    response_model=Union[SecurityResult, MultiQRDecodeResponse],
    summary="Scan QR Code from Uploaded Image",
    description="Uploads an image file, extracts and decodes QR codes. If 1 QR code is found, analyzes it immediately. If multiple are found, returns list for user selection."
)
async def scan_image(
    file: UploadFile = File(..., description="Image file containing QR code(s)"),
    selected_index: Optional[int] = Form(None, description="Index of QR code to analyze if image contains multiple"),
    db: AsyncSession = Depends(get_db)
):
    # Validate file format via extension or MIME type
    ext = os.path.splitext(file.filename or "")[1].lower()
    content_type = (file.content_type or "").lower()
    is_valid_ext = ext in settings.ALLOWED_IMAGE_EXTENSIONS
    is_valid_mime = content_type.startswith("image/") or content_type == "application/octet-stream"

    if not is_valid_ext and not is_valid_mime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext or content_type}'. Allowed formats: {', '.join(settings.ALLOWED_IMAGE_EXTENSIONS)}"
        )

    # Read bytes with size limit check
    image_bytes = await file.read()
    max_bytes = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
    if len(image_bytes) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image file exceeds maximum allowable size of {settings.MAX_IMAGE_SIZE_MB}MB."
        )

    # Decode QR codes from image bytes
    try:
        decoded_items = qr_decoder_service.decode_image_bytes(image_bytes)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not decoded_items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No readable QR code was detected in the uploaded image. Please ensure good lighting and resolution."
        )

    # If selected_index was passed (user picked from multiple QRs)
    if selected_index is not None:
        if 0 <= selected_index < len(decoded_items):
            chosen_content = decoded_items[selected_index]["content"]
            return await scan_service.analyze_and_persist(
                raw_content=chosen_content,
                db=db,
                source="gallery"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid selected_index {selected_index}. Image contains {len(decoded_items)} QR code(s)."
            )

    # If exactly 1 QR code found, analyze directly
    if len(decoded_items) == 1:
        return await scan_service.analyze_and_persist(
            raw_content=decoded_items[0]["content"],
            db=db,
            source="gallery"
        )

    # Multiple QR codes found: return list for user selection
    qr_list = []
    for item in decoded_items:
        parsed = url_analyzer_service.parse_and_normalize(item["content"])
        qr_list.append(QRItem(
            content=item["content"],
            qr_type=parsed.content_type,
            polygon=item.get("polygon")
        ))

    return MultiQRDecodeResponse(
        total_found=len(qr_list),
        qr_codes=qr_list
    )


@router.post(
    "/decode-only",
    response_model=MultiQRDecodeResponse,
    summary="Decode QR codes without executing security evaluation",
    description="Fast decoder endpoint for image inspection and preview."
)
async def decode_only(
    file: UploadFile = File(...)
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    content_type = (file.content_type or "").lower()
    is_valid_ext = ext in settings.ALLOWED_IMAGE_EXTENSIONS
    is_valid_mime = content_type.startswith("image/") or content_type == "application/octet-stream"

    if not is_valid_ext and not is_valid_mime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext or content_type}'. Allowed formats: {', '.join(settings.ALLOWED_IMAGE_EXTENSIONS)}"
        )

    image_bytes = await file.read()
    max_bytes = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
    if len(image_bytes) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image file exceeds maximum allowable size of {settings.MAX_IMAGE_SIZE_MB}MB."
        )

    try:
        decoded_items = qr_decoder_service.decode_image_bytes(image_bytes)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    qr_list = []
    for item in decoded_items:
        parsed = url_analyzer_service.parse_and_normalize(item["content"])
        qr_list.append(QRItem(
            content=item["content"],
            qr_type=parsed.content_type,
            polygon=item.get("polygon")
        ))

    return MultiQRDecodeResponse(
        total_found=len(qr_list),
        qr_codes=qr_list
    )
