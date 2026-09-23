"""
Standalone Evaluation and Inference Module for Phishing Detection Model.
Computes class probability, confidence score, uncertainty score, and decision margin.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

import sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from feature_extraction import extract_features_vector, FEATURE_NAMES


class ModelEvaluator:
    def __init__(self, model_path: str = "ml/models/phishing_rf_model.joblib"):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Trained model not found at {model_path}. Run train.py first.")
        self.model = joblib.load(model_path)
        self.model_path = model_path

    def predict_url(self, url: str) -> Dict[str, Any]:
        """Runs inference on a single URL string with confidence and uncertainty scores."""
        feat_vector = np.array([extract_features_vector(url)], dtype=np.float32)
        probabilities = self.model.predict_proba(feat_vector)[0]
        phishing_prob = float(probabilities[1])
        benign_prob = float(probabilities[0])
        is_phishing = bool(phishing_prob >= 0.5)

        # Calculate confidence (distance from decision boundary 0.5 scaled to 0-1)
        confidence = round(abs(phishing_prob - 0.5) * 2.0, 4)
        uncertainty = round(1.0 - confidence, 4)
        margin = round(phishing_prob - 0.5, 4)

        return {
            "url": url,
            "is_phishing": is_phishing,
            "phishing_probability": round(phishing_prob, 4),
            "benign_probability": round(benign_prob, 4),
            "confidence_score": confidence,
            "uncertainty_score": uncertainty,
            "decision_margin": margin,
        }

    def evaluate_dataset(self, csv_path: str) -> Dict[str, Any]:
        """Evaluates model against a labeled CSV with 'url' and 'label' columns."""
        df = pd.read_csv(csv_path)
        X = np.array([extract_features_vector(str(u)) for u in df["url"]], dtype=np.float32)
        y_true = np.array(df["label"], dtype=np.int32)
        
        y_pred = self.model.predict(X)
        y_prob = self.model.predict_proba(X)[:, 1]
        
        acc = float(accuracy_score(y_true, y_pred))
        prec = float(precision_score(y_true, y_pred, zero_division=0))
        rec = float(recall_score(y_true, y_pred, zero_division=0))
        f1 = float(f1_score(y_true, y_pred, zero_division=0))
        roc_auc = float(roc_auc_score(y_true, y_prob))
        cm = confusion_matrix(y_true, y_pred).tolist()
        report = classification_report(y_true, y_pred, output_dict=True)
        
        return {
            "total_samples": len(df),
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1_score": f1,
            "roc_auc": roc_auc,
            "confusion_matrix": cm,
            "report": report
        }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate QRadar Random Forest Phishing Classifier")
    parser.add_argument("--dataset", type=str, default="ml/data/phishing_dataset.csv", help="Path to labeled CSV dataset")
    args = parser.parse_args()

    evaluator = ModelEvaluator()
    print("=" * 60)
    print("QRADAR — MODEL EVALUATION & INFERENCE BENCHMARK")
    print("=" * 60)

    if os.path.exists(args.dataset):
        print(f"\n[1] Evaluating dataset: {args.dataset}...")
        metrics = evaluator.evaluate_dataset(args.dataset)
        print("-" * 40)
        print(f"  Total Samples : {metrics['total_samples']}")
        print(f"  Accuracy      : {metrics['accuracy'] * 100:.2f}%")
        print(f"  Precision     : {metrics['precision'] * 100:.2f}%")
        print(f"  Recall        : {metrics['recall'] * 100:.2f}%")
        print(f"  F1-Score      : {metrics['f1_score'] * 100:.2f}%")
        print(f"  ROC-AUC       : {metrics['roc_auc']:.4f}")
        print("-" * 40)
        print(f"  Confusion Matrix (TN, FP / FN, TP):")
        print(f"    {metrics['confusion_matrix'][0]}")
        print(f"    {metrics['confusion_matrix'][1]}")

    sample_tests = [
        "https://www.google.com/search?q=cybersecurity",
        "https://github.com/torvalds/linux",
        "http://paypa1-account-verification.xyz/login.php",
        "http://192.168.1.50:8080/bank/login.htm",
        "https://chase.com@secure-credential-harvest-gate.ru/signon",
    ]
    print("\n[2] Evaluating sample demonstration URLs:")
    for u in sample_tests:
        res = evaluator.predict_url(u)
        print(f"  [{'PHISHING' if res['is_phishing'] else 'BENIGN':8s}] (prob={res['phishing_probability']:.2f}, conf={res['confidence_score']:.2f}, uncert={res['uncertainty_score']:.2f}) -> {u}")

