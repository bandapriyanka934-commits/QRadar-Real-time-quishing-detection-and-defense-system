"""
Model Training and Evaluation Pipeline for Phishing URL Detection.
Trains a Scikit-Learn Random Forest Classifier and saves serialized artifacts
along with comprehensive evaluation metrics (Precision, Recall, F1, Accuracy, ROC-AUC)
and provenance documentation.
"""

import os
import json
import hashlib
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from datetime import datetime, timezone
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)

import sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from feature_extraction import FEATURE_NAMES, extract_features_vector
from dataset import prepare_and_save_dataset, DATASET_PROVENANCE


def train_phishing_model(
    data_path: str = "ml/data/phishing_dataset.csv",
    model_output_path: str = "ml/models/phishing_rf_model.joblib",
    metadata_output_path: str = "ml/models/model_metadata.json",
    reports_dir: str = "ml/reports"
):
    print("=" * 60)
    print("QRADAR — MACHINE LEARNING PHISHING CLASSIFICATION TRAINING")
    print("=" * 60)

    # 1. Ensure dataset exists
    if not os.path.exists(data_path):
        print(f"[1/6] Dataset not found at {data_path}. Generating balanced dataset...")
        df = prepare_and_save_dataset(data_path)
    else:
        print(f"[1/6] Loading existing dataset from {data_path}...")
        df = pd.read_csv(data_path)

    print(f"      Total records: {len(df)}")
    print(f"      Class distribution: {df['label'].value_counts().to_dict()}")

    # Calculate dataset SHA-256
    with open(data_path, "rb") as f:
        dataset_hash = hashlib.sha256(f.read()).hexdigest()

    # 2. Extract feature matrix X and label vector y
    print("[2/6] Extracting numerical feature vectors for all URLs...")
    X_list = []
    y_list = []

    for idx, row in df.iterrows():
        url = str(row["url"])
        label = int(row["label"])
        feats = extract_features_vector(url)
        X_list.append(feats)
        y_list.append(label)

    X = np.array(X_list, dtype=np.float32)
    y = np.array(y_list, dtype=np.int32)
    print(f"      Feature matrix shape: {X.shape}, Features count: {len(FEATURE_NAMES)}")

    # 3. Domain / Group-Aware Train/Test Split
    print("[3/6] Splitting dataset into 80% train and 20% test sets (domain/group-aware to prevent domain leakage)...")
    from sklearn.model_selection import GroupShuffleSplit
    
    groups = df["domain_group"].values if "domain_group" in df.columns else np.array([u.split("/")[2] if "://" in u else u for u in df["url"]])
    gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
    train_idx, test_idx = next(gss.split(X, y, groups=groups))
    
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    
    train_groups = set(groups[train_idx])
    test_groups = set(groups[test_idx])
    overlap = train_groups.intersection(test_groups)
    print(f"      Train samples: {len(X_train)} (unique domain groups: {len(train_groups)})")
    print(f"      Test samples:  {len(X_test)} (unique domain groups: {len(test_groups)})")
    print(f"      Domain leakage check: {len(overlap)} overlapping domains between train & test.")

    # 4. Train Random Forest Classifier
    print("[4/6] Training Random Forest Classifier...")
    hyperparameters = {
        "n_estimators": 100,
        "max_depth": 22,
        "min_samples_split": 4,
        "min_samples_leaf": 2,
        "class_weight": "balanced",
        "random_state": 42
    }
    rf_model = RandomForestClassifier(
        n_estimators=hyperparameters["n_estimators"],
        max_depth=hyperparameters["max_depth"],
        min_samples_split=hyperparameters["min_samples_split"],
        min_samples_leaf=hyperparameters["min_samples_leaf"],
        class_weight=hyperparameters["class_weight"],
        n_jobs=-1,
        random_state=hyperparameters["random_state"]
    )
    rf_model.fit(X_train, y_train)

    # 5. Evaluate Model
    print("[5/6] Evaluating model on unseen holdout test set...")
    y_pred = rf_model.predict(X_test)
    y_pred_proba = rf_model.predict_proba(X_test)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    roc_auc = float(roc_auc_score(y_test, y_pred_proba))
    cm = confusion_matrix(y_test, y_pred).tolist()

    print("\n" + "-" * 40)
    print(f"  ACCURACY : {acc * 100:.2f}%")
    print(f"  PRECISION: {prec * 100:.2f}%")
    print(f"  RECALL   : {rec * 100:.2f}%")
    print(f"  F1-SCORE : {f1 * 100:.2f}%")
    print(f"  ROC-AUC  : {roc_auc:.4f}")
    print("-" * 40)

    # 6. Save Artifacts & Reports
    print("[6/6] Exporting artifacts, model weights, and reports...")
    os.makedirs(os.path.dirname(model_output_path), exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)

    joblib.dump(rf_model, model_output_path)
    print(f"      Model saved -> {model_output_path}")

    # Export metrics JSON
    metrics = {
        "model_type": "RandomForestClassifier",
        "evaluation_dataset": "Holdout 20% Test Split",
        "test_samples": len(X_test),
        "train_samples": len(X_train),
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(roc_auc, 4),
        "confusion_matrix": {
            "true_negative": cm[0][0],
            "false_positive": cm[0][1],
            "false_negative": cm[1][0],
            "true_positive": cm[1][1]
        },
        "classification_report": classification_report(y_test, y_pred, output_dict=True),
        "evaluated_at": datetime.now(timezone.utc).isoformat()
    }

    metrics_path = os.path.join(reports_dir, "metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"      Metrics saved -> {metrics_path}")

    # Plot and save confusion matrix figure
    fig, ax = plt.subplots(figsize=(5, 4))
    im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    ax.set_title("Confusion Matrix (Holdout Test Set)")
    fig.colorbar(im)
    tick_marks = np.arange(2)
    ax.set_xticks(tick_marks)
    ax.set_xticklabels(["Benign", "Phishing"])
    ax.set_yticks(tick_marks)
    ax.set_yticklabels(["Benign", "Phishing"])

    # Annotate numbers
    thresh = np.array(cm).max() / 2.
    for i in range(2):
        for j in range(2):
            ax.text(j, i, format(cm[i][j], 'd'),
                    ha="center", va="center",
                    color="white" if cm[i][j] > thresh else "black")

    ax.set_ylabel("True Label")
    ax.set_xlabel("Predicted Label")
    plt.tight_layout()
    cm_plot_path = os.path.join(reports_dir, "confusion_matrix.png")
    plt.savefig(cm_plot_path, dpi=150)
    plt.close()
    print(f"      Confusion matrix plot saved -> {cm_plot_path}")

    # Export rich model metadata
    importances_dict = {
        FEATURE_NAMES[i]: round(float(rf_model.feature_importances_[i]), 4)
        for i in np.argsort(rf_model.feature_importances_)[::-1]
    }

    metadata = {
        "model_name": "QRadar Random Forest Phishing Classifier",
        "model_type": "RandomForestClassifier",
        "version": "1.2.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "training_timestamp": datetime.now(timezone.utc).isoformat(),
        "framework": "Scikit-Learn",
        "feature_names": FEATURE_NAMES,
        "features": FEATURE_NAMES,
        "feature_order": FEATURE_NAMES,
        "feature_count": len(FEATURE_NAMES),
        "feature_importances": importances_dict,
        "hyperparameters": hyperparameters,
        "dataset_provenance": DATASET_PROVENANCE,
        "dataset_hash_sha256": dataset_hash,
        "total_dataset_samples": len(df),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "preprocessing_info": {
            "normalization": "lowercase scheme/host, stripped trailing whitespace",
            "deduplication": "exact URL deduplication",
            "train_test_split": "Domain/Group-aware split (GroupShuffleSplit 80/20) with 0 domain leakage"
        },
        "metrics_summary": {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc_auc, 4)
        }
    }

    with open(metadata_output_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"      Metadata saved -> {metadata_output_path}")

    print("\nTraining and Evaluation successfully completed.")
    return rf_model, metrics


if __name__ == "__main__":
    train_phishing_model()
