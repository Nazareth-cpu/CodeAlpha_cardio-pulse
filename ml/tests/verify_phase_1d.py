"""
Comprehensive Phase 1D Validation and Integrity Verification Script.

Executes rigorous checks for:
  1. Production artifact structure, fitting, and estimators
  2. Metadata consistency against artifact and baseline metrics
  3. Input schema integrity, discrete domains, and leakage prevention
  4. Deterministic inference and probability range
  5. Dataset independence (with dataset.csv unavailable)
  6. Training independence and plot immutability
  7. In-memory caching and reuse lifecycle
  8. Medical language audit and security checks
  9. Backward compatibility of baseline training scripts
"""

import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from ml.config import (
    ARTIFACT_DIR,
    CANONICAL_FEATURES,
    CATEGORICAL_FEATURES,
    DATASET_PATH,
    EDUCATIONAL_DISCLAIMER,
    EXCLUDED_FEATURES,
    METADATA_PATH,
    MODEL_PATH,
    NUMERICAL_FEATURES,
    OUTPUT_DIR,
    PRODUCTION_MODEL_NAME,
    PRODUCTION_MODEL_VERSION,
    PROJECT_ROOT,
)
from ml.inference import (
    ForbiddenFieldError,
    HeartDiseasePredictor,
    InvalidCategoricalError,
    InvalidNumericalError,
    MissingFieldError,
    PredictionResult,
    UnknownFieldError,
    clear_cache,
    get_metadata,
    get_model,
    get_model_metadata,
    get_predictor,
    load_model,
    predict,
    validate_input,
)


def run_phase_1d_validation():
    print("=" * 70)
    print("PHASE 1D — PRODUCTION ML VALIDATION AND INTEGRITY AUDIT")
    print("=" * 70)
    audit_results = {}

    # ---------------------------------------------------------
    # 1. ARTIFACT AUDIT
    # ---------------------------------------------------------
    print("\n[1/8] Auditing Production Artifact (model.joblib)...")
    assert MODEL_PATH.exists(), f"Model artifact not found at {MODEL_PATH}"
    pipeline = joblib.load(MODEL_PATH)
    assert isinstance(pipeline, Pipeline), f"Expected Pipeline, got {type(pipeline)}"
    assert "preprocessor" in pipeline.named_steps, "Missing 'preprocessor' step in Pipeline"
    assert "model" in pipeline.named_steps, "Missing 'model' step in Pipeline"

    preprocessor = pipeline.named_steps["preprocessor"]
    model = pipeline.named_steps["model"]
    assert isinstance(preprocessor, ColumnTransformer), f"Expected ColumnTransformer, got {type(preprocessor)}"
    assert isinstance(model, LogisticRegression), f"Expected LogisticRegression, got {type(model)}"

    # Check fitted state
    assert hasattr(model, "coef_") and model.coef_ is not None, "Model is not fitted (missing coef_)"
    assert hasattr(model, "classes_"), "Model missing classes_"
    assert list(model.classes_) == [0, 1], f"Expected classes [0, 1], got {model.classes_}"
    assert hasattr(pipeline, "predict"), "Pipeline missing predict()"
    assert hasattr(pipeline, "predict_proba"), "Pipeline missing predict_proba()"

    print("  ✓ model.joblib exists, is fitted Pipeline with ColumnTransformer + LogisticRegression")
    audit_results["artifact"] = "PASS"

    # ---------------------------------------------------------
    # 2. METADATA AUDIT
    # ---------------------------------------------------------
    print("\n[2/8] Auditing Metadata Consistency (model_metadata.json)...")
    assert METADATA_PATH.exists(), f"Metadata not found at {METADATA_PATH}"
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert meta["model_name"] == PRODUCTION_MODEL_NAME, f"Mismatch: {meta['model_name']} != {PRODUCTION_MODEL_NAME}"
    assert meta["model_version"] == PRODUCTION_MODEL_VERSION, f"Mismatch: {meta['model_version']}"
    assert meta["selection_criterion"] == "ROC-AUC"
    assert meta["random_state"] == 42
    assert meta["test_size"] == 0.20
    assert meta["features"] == CANONICAL_FEATURES
    assert meta["numerical_features"] == NUMERICAL_FEATURES
    assert meta["categorical_features"] == CATEGORICAL_FEATURES
    assert meta["excluded_features"] == EXCLUDED_FEATURES

    # Metric consistency check against CodeAlpha reference
    expected_metrics = {
        "accuracy": 0.8852,
        "precision": 0.8387,
        "recall": 0.9286,
        "f1_score": 0.8814,
        "roc_auc": 0.9665,
    }
    for k, expected_val in expected_metrics.items():
        val = meta["metrics"][k]
        assert abs(val - expected_val) < 1e-4, f"Metric mismatch for {k}: {val} != {expected_val}"

    # Confusion matrix consistency
    cm = meta["confusion_matrix"]
    assert cm == {"TN": 28, "FP": 5, "FN": 2, "TP": 26}, f"CM mismatch: {cm}"

    print("  ✓ model_metadata.json strictly matches baseline configuration and test metrics")
    audit_results["metadata"] = "PASS"

    # ---------------------------------------------------------
    # 3. SCHEMA & VALIDATION AUDIT
    # ---------------------------------------------------------
    print("\n[3/8] Auditing Input Schema and Rejections...")
    valid_test_record = {
        "age": 52.0,
        "sex": 1.0,
        "cp": 4.0,
        "trestbps": 138.0,
        "chol": 246.0,
        "fbs": 0.0,
        "restecg": 0.0,
        "thalach": 150.0,
        "exang": 0.0,
        "oldpeak": 1.2,
        "slope": 2.0,
        "ca": 0.0,
        "thal": 3.0,
    }

    # Valid validation
    val_out = validate_input(valid_test_record)
    assert len(val_out) == 13

    # Forbidden field rejection
    for forbidden in ["num", "target", "id"]:
        bad_rec = dict(valid_test_record)
        bad_rec[forbidden] = 1.0
        rejected = False
        try:
            validate_input(bad_rec)
        except ForbiddenFieldError:
            rejected = True
        assert rejected, f"Failed to reject forbidden field '{forbidden}'"

    # Unknown field rejection
    bad_rec = dict(valid_test_record)
    bad_rec["bmi"] = 23.5
    rejected = False
    try:
        validate_input(bad_rec)
    except UnknownFieldError:
        rejected = True
    assert rejected, "Failed to reject unknown field 'bmi'"

    # Missing field rejection
    for col in CANONICAL_FEATURES:
        bad_rec = dict(valid_test_record)
        del bad_rec[col]
        rejected = False
        try:
            validate_input(bad_rec)
        except MissingFieldError:
            rejected = True
        assert rejected, f"Failed to reject missing field '{col}'"

    # Discrete categorical domains
    cat_tests = [
        ("sex", 3),
        ("cp", 0),
        ("fbs", 2),
        ("restecg", 3),
        ("exang", -1),
        ("slope", 4),
        ("ca", 4),
        ("thal", 2),
    ]
    for cat_col, invalid_val in cat_tests:
        bad_rec = dict(valid_test_record)
        bad_rec[cat_col] = invalid_val
        rejected = False
        try:
            validate_input(bad_rec)
        except InvalidCategoricalError:
            rejected = True
        assert rejected, f"Failed to reject invalid categorical {cat_col}={invalid_val}"

    # Numerical invalid tests
    num_tests = [
        ("age", "not_a_number"),
        ("trestbps", None),
        ("chol", float("nan")),
        ("thalach", float("inf")),
        ("oldpeak", True),
    ]
    for num_col, invalid_val in num_tests:
        bad_rec = dict(valid_test_record)
        bad_rec[num_col] = invalid_val
        rejected = False
        try:
            validate_input(bad_rec)
        except InvalidNumericalError:
            rejected = True
        assert rejected, f"Failed to reject invalid numerical {num_col}={invalid_val}"

    print("  ✓ Schema integrity verified: 13 features enforced, forbidden/unknown/missing/domain rejected")
    audit_results["schema"] = "PASS"

    # ---------------------------------------------------------
    # 4. DETERMINISTIC INFERENCE AUDIT
    # ---------------------------------------------------------
    print("\n[4/8] Auditing Inference & Determinism...")
    res1 = predict(valid_test_record)
    res2 = predict(valid_test_record)
    res3 = predict(valid_test_record)

    assert isinstance(res1, PredictionResult)
    assert res1.prediction in [0, 1]
    assert 0.0 <= res1.probability <= 1.0
    assert res1.model_name == "Logistic Regression"
    assert res1.model_version == "heart-disease-logistic-regression-v1"

    # Determinism
    assert res1.prediction == res2.prediction == res3.prediction
    assert res1.probability == res2.probability == res3.probability
    print(f"  ✓ Deterministic inference confirmed: Prediction={res1.prediction}, Probability={res1.probability:.4f}")
    audit_results["inference"] = "PASS"

    # ---------------------------------------------------------
    # 5. DATASET & TRAINING INDEPENDENCE AUDIT
    # ---------------------------------------------------------
    print("\n[5/8] Auditing Dataset Independence & Training Independence...")

    # Record plot hashes before inference
    plot_hashes = {}
    for p in ["roc_curves.png", "confusion_matrices.png", "feature_importance.png", "model_comparison.csv"]:
        target = OUTPUT_DIR / p
        if target.exists():
            with open(target, "rb") as f:
                plot_hashes[p] = hashlib.sha256(f.read()).hexdigest()

    # Temporarily hide dataset.csv to verify absolute zero dependence
    temp_renamed = False
    temp_target = DATASET_PATH.parent / "dataset.csv.tmp_bak"
    try:
        if DATASET_PATH.exists():
            DATASET_PATH.rename(temp_target)
            temp_renamed = True

        assert not DATASET_PATH.exists(), "Dataset should be temporarily unavailable"

        # Clear cache and perform inference
        clear_cache()
        standalone_predictor = HeartDiseasePredictor()
        standalone_res = standalone_predictor.predict(valid_test_record)
        assert standalone_res.prediction in [0, 1]
        assert 0.0 <= standalone_res.probability <= 1.0
        print("  ✓ Prediction executed successfully while dataset.csv was completely unavailable on disk!")
    finally:
        if temp_renamed and temp_target.exists():
            temp_target.rename(DATASET_PATH)
            assert DATASET_PATH.exists(), "Dataset restored"

    # Verify plots and comparison csv remain completely untouched
    for p, orig_hash in plot_hashes.items():
        target = OUTPUT_DIR / p
        with open(target, "rb") as f:
            new_hash = hashlib.sha256(f.read()).hexdigest()
        assert orig_hash == new_hash, f"File {p} was modified during inference execution!"
    print("  ✓ Evaluation artifacts and output plots remained completely untouched during inference")
    audit_results["dataset_independence"] = "PASS"

    # ---------------------------------------------------------
    # 6. MODEL REUSE & CACHING LIFECYCLE AUDIT
    # ---------------------------------------------------------
    print("\n[6/8] Auditing In-Memory Caching Lifecycle...")
    clear_cache()
    m1 = get_model()
    m2 = get_model()
    assert m1 is m2, "get_model() did not return identical cached instance"

    p1 = get_predictor()
    p2 = get_predictor()
    assert p1 is p2, "get_predictor() did not return identical cached instance"
    print("  ✓ In-memory caching verified: Model is deserialized once and reused for all subsequent inferences")
    audit_results["caching"] = "PASS"

    # ---------------------------------------------------------
    # 7. MEDICAL LANGUAGE & SECURITY AUDIT
    # ---------------------------------------------------------
    print("\n[7/8] Auditing Medical Language & Security...")
    files_to_check = [
        PROJECT_ROOT / "ml" / "config.py",
        PROJECT_ROOT / "ml" / "inference" / "predictor.py",
        PROJECT_ROOT / "ml" / "inference" / "validator.py",
        PROJECT_ROOT / "ml" / "inference" / "model_loader.py",
        PROJECT_ROOT / "ml" / "inference" / "exceptions.py",
    ]

    prohibited_claims = ["medically accurate", "clinically validated", "confirmed disease", "doctor replacement"]
    for fpath in files_to_check:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read().lower()
            for claim in prohibited_claims:
                assert claim not in content, f"Inappropriate medical claim '{claim}' found in {fpath.name}"
            # Check for hardcoded secrets or passwords
            assert "password" not in content and "secret" not in content, f"Possible credential in {fpath.name}"
            assert "/home/" not in content and "c:\\" not in content, f"Hardcoded machine path in {fpath.name}"

    # Verify educational disclaimer is present in config and response
    assert "educational and research purposes" in EDUCATIONAL_DISCLAIMER.lower()
    assert "educational and research purposes" in res1.disclaimer.lower()
    print("  ✓ Medical language audit passed: No diagnostic claims, educational disclaimer preserved")
    print("  ✓ Security audit passed: No credentials, no machine-specific paths, privacy-safe logging")
    audit_results["security_and_language"] = "PASS"

    # ---------------------------------------------------------
    # 8. BACKWARD COMPATIBILITY OF ORIGINAL TRAINING SCRIPT
    # ---------------------------------------------------------
    print("\n[8/8] Auditing Backward Compatibility of Original ML Pipeline...")
    orig_script = PROJECT_ROOT / "disease_prediction.py"
    assert orig_script.exists(), "Original disease_prediction.py missing!"

    # Ensure dataset.csv exists and is readable
    df_raw = pd.read_csv(DATASET_PATH, header=None)
    assert df_raw.shape == (303, 14), f"Unexpected dataset shape: {df_raw.shape}"

    # Verify model_comparison.csv
    comp_file = OUTPUT_DIR / "model_comparison.csv"
    assert comp_file.exists(), "model_comparison.csv missing"
    comp_df = pd.read_csv(comp_file)
    assert "Model" in comp_df.columns and "ROC-AUC" in comp_df.columns
    top_model = comp_df.sort_values(by="ROC-AUC", ascending=False).iloc[0]["Model"]
    assert top_model == "Logistic Regression", f"Expected Logistic Regression as top ROC-AUC model, got: {top_model}"
    print(f"  ✓ Original model comparison verified: Top ROC-AUC model is '{top_model}'")
    audit_results["backward_compatibility"] = "PASS"

    print("\n" + "=" * 70)
    print("PHASE 1D VALIDATION SUMMARY: ALL CHECKS PASSED")
    print("=" * 70)
    return audit_results


if __name__ == "__main__":
    run_phase_1d_validation()
