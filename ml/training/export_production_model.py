"""
Export All Production Model Artifacts for CardioPulse.

Trains all four baseline classifiers defined in disease_prediction.py:
  1. Logistic Regression
  2. Support Vector Machine
  3. Random Forest
  4. XGBoost

Serializes for each:
  - Complete fitted sklearn Pipeline (ColumnTransformer preprocessor + Classifier)
  - Preprocessor strictly fitted on training split only
  - Evaluated on test split
  - Stored in ml/artifacts/ as:
      - logistic_regression.joblib
      - svm.joblib
      - random_forest.joblib
      - xgboost.joblib
      - model.joblib (backwards-compatible copy of default)
      - model_registry.json
      - model_metadata.json
"""

import json
from pathlib import Path
import warnings

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC
from xgboost import XGBClassifier

from ml.config import (
    ARTIFACT_DIR,
    CANONICAL_FEATURES,
    CATEGORICAL_FEATURES,
    DATASET_PATH,
    EDUCATIONAL_DISCLAIMER,
    EXCLUDED_FEATURES,
    NUMERICAL_FEATURES,
    RANDOM_STATE,
    TEST_SIZE,
)

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

MODEL_CONFIGS = {
    "logistic_regression": {
        "display_name": "Logistic Regression",
        "artifact_name": "logistic_regression.joblib",
        "version": "v1",
        "description": "Regularized linear classification model with standard scaling and calibrated probability estimation.",
        "estimator": lambda: LogisticRegression(max_iter=2000, random_state=RANDOM_STATE),
    },
    "svm": {
        "display_name": "Support Vector Machine",
        "artifact_name": "svm.joblib",
        "version": "v1",
        "description": "Margin-based classifier with radial basis function kernel and calibrated probability estimation.",
        "estimator": lambda: SVC(probability=True, random_state=RANDOM_STATE),
    },
    "random_forest": {
        "display_name": "Random Forest",
        "artifact_name": "random_forest.joblib",
        "version": "v1",
        "description": "Ensemble of 300 decision trees trained with bootstrap aggregating.",
        "estimator": lambda: RandomForestClassifier(n_estimators=300, random_state=RANDOM_STATE),
    },
    "xgboost": {
        "display_name": "XGBoost",
        "artifact_name": "xgboost.joblib",
        "version": "v1",
        "description": "Gradient-boosted decision trees with regularized objective optimization.",
        "estimator": lambda: XGBClassifier(
            n_estimators=300,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric="logloss",
            random_state=RANDOM_STATE,
        ),
    },
}


def load_dataset(dataset_path: Path) -> pd.DataFrame:
    """Load and format the UCI Cleveland dataset identically to disease_prediction.py."""
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found at {dataset_path}")

    standard_cols = [
        "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
        "thalach", "exang", "oldpeak", "slope", "ca", "thal", "num"
    ]

    df_raw = pd.read_csv(dataset_path, header=None, na_values=["?", "NA", "null", "none", ""])
    first_row_strings = sum(
        isinstance(val, str) and not val.replace('.', '', 1).isdigit() for val in df_raw.iloc[0]
    )

    if first_row_strings > 3:
        df = pd.read_csv(dataset_path, na_values=["?", "NA", "null", "none", ""])
        df.columns = [str(col).strip().lower() for col in df.columns]
    else:
        df = df_raw
        if df.shape[1] == len(standard_cols):
            df.columns = standard_cols
        else:
            df.columns = [f"col_{i}" for i in range(df.shape[1])]

    if "target" in df.columns:
        df["target"] = pd.to_numeric(df["target"], errors="coerce")
        df["target"] = (df["target"] > 0).astype(int)
    elif "num" in df.columns:
        df["num"] = pd.to_numeric(df["num"], errors="coerce")
        df["target"] = (df["num"] > 0).astype(int)
    else:
        last_col = df.columns[-1]
        df[last_col] = pd.to_numeric(df[last_col], errors="coerce")
        df["target"] = (df[last_col] > 0).astype(int)

    return df


def build_preprocessor() -> ColumnTransformer:
    num_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    cat_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    return ColumnTransformer(
        transformers=[
            ("num", num_transformer, NUMERICAL_FEATURES),
            ("cat", cat_transformer, CATEGORICAL_FEATURES)
        ],
        remainder="drop"
    )


def export_all():
    print("=" * 60)
    print("SERIALIZING ALL FOUR PRODUCTION ML MODELS")
    print("=" * 60)

    df = load_dataset(DATASET_PATH)
    X = df.drop(columns=[col for col in EXCLUDED_FEATURES if col in df.columns], errors="ignore").copy()
    y = df["target"].copy()

    for col in CANONICAL_FEATURES:
        X[col] = pd.to_numeric(X[col], errors="coerce")
    X = X[CANONICAL_FEATURES]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    registry_data = {
        "models": {},
        "default_model_id": "logistic_regression"
    }

    for model_id, cfg in MODEL_CONFIGS.items():
        print(f"Training pipeline for: {cfg['display_name']} ({model_id})...")
        preprocessor = build_preprocessor()
        pipeline = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("model", cfg["estimator"]())
        ])

        pipeline.fit(X_train, y_train)

        y_pred = pipeline.predict(X_test)
        y_prob = pipeline.predict_proba(X_test)[:, 1]

        acc = round(float(accuracy_score(y_test, y_pred)), 4)
        prec = round(float(precision_score(y_test, y_pred, zero_division=0)), 4)
        rec = round(float(recall_score(y_test, y_pred, zero_division=0)), 4)
        f1 = round(float(f1_score(y_test, y_pred, zero_division=0)), 4)
        roc_auc = round(float(roc_auc_score(y_test, y_prob)), 4)
        cm = confusion_matrix(y_test, y_pred)
        tn, fp, fn, tp = [int(v) for v in cm.ravel()]

        print(f"  [{cfg['display_name']}] Acc: {acc:.4f} | Prec: {prec:.4f} | Rec: {rec:.4f} | F1: {f1:.4f} | AUC: {roc_auc:.4f}")

        artifact_path = ARTIFACT_DIR / cfg["artifact_name"]
        joblib.dump(pipeline, artifact_path, compress=3)
        print(f"  Saved artifact: {artifact_path}")

        # Also write legacy model.joblib for default
        if model_id == "logistic_regression":
            legacy_path = ARTIFACT_DIR / "model.joblib"
            joblib.dump(pipeline, legacy_path, compress=3)

        registry_data["models"][model_id] = {
            "id": model_id,
            "display_name": cfg["display_name"],
            "artifact": cfg["artifact_name"],
            "version": cfg["version"],
            "description": cfg["description"],
            "metrics": {
                "accuracy": acc,
                "precision": prec,
                "recall": rec,
                "f1_score": f1,
                "roc_auc": roc_auc,
            },
            "confusion_matrix": {
                "TN": tn,
                "FP": fp,
                "FN": fn,
                "TP": tp,
            }
        }

    registry_path = ARTIFACT_DIR / "model_registry.json"
    with open(registry_path, "w", encoding="utf-8") as f:
        json.dump(registry_data, f, indent=2)
    print(f"\nModel registry written to: {registry_path}")

    # Maintain legacy model_metadata.json pointing to default with multi-model section
    metadata_path = ARTIFACT_DIR / "model_metadata.json"
    default_cfg = registry_data["models"]["logistic_regression"]
    metadata_data = {
        "model_name": default_cfg["display_name"],
        "model_version": f"heart-disease-logistic-regression-{default_cfg['version']}",
        "task": "binary classification",
        "dataset": "UCI Cleveland Heart Disease Dataset",
        "selection_criterion": "ROC-AUC",
        "random_state": RANDOM_STATE,
        "test_size": TEST_SIZE,
        "features": CANONICAL_FEATURES,
        "numerical_features": NUMERICAL_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "metrics": default_cfg["metrics"],
        "confusion_matrix": default_cfg["confusion_matrix"],
        "disclaimer": EDUCATIONAL_DISCLAIMER,
        "models": registry_data["models"],
    }
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata_data, f, indent=2)
    print(f"Model metadata written to: {metadata_path}")
    print("\nAll four models successfully exported!")


if __name__ == "__main__":
    export_all()
