"""
Machine Learning Inference Service for Phishing URL Detection.
Loads the serialized Random Forest model singleton at startup and computes phishing probabilities.
Truthfully validates model metadata and feature extractor consistency.
"""

import os
import json
import logging
import joblib
import numpy as np
from typing import Dict, Any, Optional

import sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", ".."))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))

for p in [ROOT_DIR, BACKEND_DIR, os.path.join(ROOT_DIR, "ml", "src")]:
    if p not in sys.path:
        sys.path.insert(0, p)

from feature_extraction import extract_features_vector, FEATURE_NAMES
from app.core.config import settings

logger = logging.getLogger("qradar.ml_engine")


class MLEngineService:
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = self._resolve_path(model_path or settings.ML_MODEL_PATH)
        self.metadata_path = self._resolve_path(settings.ML_METADATA_PATH)
        self.model = None
        self.metadata = {}
        self.is_available = False
        self.load_error: Optional[str] = None
        self._load_model()

    def _resolve_path(self, relative_or_abs_path: str) -> str:
        """Resolves file path against multiple possible base directories."""
        if not relative_or_abs_path:
            return ""
        if os.path.isabs(relative_or_abs_path) and os.path.exists(relative_or_abs_path):
            return relative_or_abs_path

        candidates = [
            relative_or_abs_path,
            os.path.join(ROOT_DIR, relative_or_abs_path),
            os.path.join(BACKEND_DIR, relative_or_abs_path),
            os.path.join(ROOT_DIR, "ml", "models", os.path.basename(relative_or_abs_path)),
            os.path.join(BACKEND_DIR, "..", "ml", "models", os.path.basename(relative_or_abs_path)),
        ]
        for c in candidates:
            if os.path.exists(c):
                return os.path.abspath(c)
        return os.path.abspath(os.path.join(ROOT_DIR, relative_or_abs_path))

    def _load_model(self):
        """Attempts to load the trained Random Forest model and validates metadata consistency."""
        logger.info(f"[ML] Loading Random Forest model from {self.model_path}...")
        
        if not os.path.exists(self.model_path):
            err_msg = f"ML Model file not found at {self.model_path}"
            logger.error(f"[ML ERROR] {err_msg}")
            self.load_error = err_msg
            self.is_available = False
            return

        try:
            self.model = joblib.load(self.model_path)
            
            # Load and validate metadata consistency
            if os.path.exists(self.metadata_path):
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)

            # Feature consistency check
            meta_features = self.metadata.get("feature_names") or self.metadata.get("features")
            if meta_features and meta_features != FEATURE_NAMES:
                err_msg = f"ML feature extractor mismatch! Model metadata has {len(meta_features)} features, extractor has {len(FEATURE_NAMES)}"
                logger.error(f"[ML ERROR] {err_msg}")
                self.load_error = err_msg
                self.is_available = False
                return

            self.is_available = True
            self.load_error = None
            version = self.metadata.get("version", "1.0.0")
            n_features = len(FEATURE_NAMES)
            logger.info(f"[ML] Random Forest model loaded successfully (features: {n_features}, version: {version})")
        except Exception as e:
            self.load_error = str(e)
            logger.error(f"[ML ERROR] Failed to load Random Forest model from {self.model_path}: {e}", exc_info=True)
            self.model = None
            self.is_available = False

    def predict(self, url: str) -> Dict[str, Any]:
        """
        Runs feature extraction and model inference for a single URL.
        Computes phishing probability, confidence score (|p - 0.5| * 2), and uncertainty (1 - confidence).
        """
        if not self.is_available or self.model is None:
            reason = self.load_error or "ML model artifact unavailable"
            logger.warning(f"[ML ERROR] Cannot predict for '{url}': {reason}")
            return {
                "available": False,
                "status": "UNAVAILABLE",
                "model_name": "Random Forest",
                "prediction": None,
                "confidence": None,
                "uncertainty": None,
                "phishing_probability": None,
                "model_version": None,
                "reason": reason,
            }

        try:
            # 1. Extract feature vector matching training schema (exactly 18 features)
            feat_vec = extract_features_vector(url)
            X = np.array([feat_vec], dtype=np.float32)

            # 2. Predict probability and binary class
            pred_proba = self.model.predict_proba(X)[0]
            phishing_prob = float(pred_proba[1])
            is_phishing = bool(phishing_prob >= 0.5)
            prediction = "Phishing" if is_phishing else "Legitimate"

            # 3. Compute Confidence and Uncertainty
            confidence = round(abs(phishing_prob - 0.5) * 2.0, 4)
            uncertainty = round(1.0 - confidence, 4)

            logger.info(
                f"[ML] Prediction completed for '{url}': {prediction} "
                f"({int(round(confidence * 100))}% confidence, probability: {round(phishing_prob, 4)}, uncertainty: {uncertainty})"
            )

            return {
                "available": True,
                "status": "ANALYZED",
                "model_name": "Random Forest",
                "prediction": prediction,
                "confidence": confidence,
                "uncertainty": uncertainty,
                "phishing_probability": round(phishing_prob, 4),
                "model_version": self.metadata.get("version", "1.0.0"),
                "reason": None,
            }
        except Exception as e:
            logger.error(f"[ML ERROR] Error during ML inference for URL '{url}': {e}", exc_info=True)
            return {
                "available": False,
                "status": "UNAVAILABLE",
                "model_name": "Random Forest",
                "prediction": None,
                "confidence": None,
                "uncertainty": None,
                "phishing_probability": None,
                "model_version": self.metadata.get("version", "1.0.0"),
                "reason": f"Inference error: {str(e)}",
            }

    def not_applicable(self, reason: str = "Non-web QR payload") -> Dict[str, Any]:
        """Returns standard response representation when ML does not apply."""
        return {
            "available": False,
            "status": "NOT_APPLICABLE",
            "model_name": "Random Forest",
            "prediction": None,
            "confidence": None,
            "uncertainty": None,
            "phishing_probability": None,
            "model_version": self.metadata.get("version", "1.0.0"),
            "reason": reason,
        }


ml_engine_service = MLEngineService()
