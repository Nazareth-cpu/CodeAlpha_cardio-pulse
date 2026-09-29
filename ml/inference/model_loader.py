"""
Model Loader for CardioPulse ML Multi-Model Inference Layer.

Responsible for safely loading the serialized Pipeline artifacts and metadata
from configured paths and registry using an in-memory caching pattern (singleton).
Never loads dataset.csv or executes training code at inference time.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
from sklearn.pipeline import Pipeline

from ml.config import (
    ARTIFACT_DIR,
    DEFAULT_MODEL_ID,
    METADATA_PATH,
    MODEL_PATH,
    REGISTRY_PATH,
    SUPPORTED_MODEL_IDS,
)
from ml.inference.exceptions import (
    CorruptedModelError,
    InvalidModelError,
    ModelNotFoundError,
)

logger = logging.getLogger("cardiopulse.model_loader")

# In-memory cached pipelines by model_id
_CACHED_PIPELINES: Dict[str, Pipeline] = {}
_CACHED_PIPELINE: Optional[Pipeline] = None  # Backward compatibility single pipeline
_CACHED_METADATA: Optional[Dict[str, Any]] = None
_CACHED_REGISTRY: Optional[Dict[str, Any]] = None
_CACHED_MODEL_METADATA: Dict[str, Dict[str, Any]] = {}


def load_registry(registry_path: Optional[Path] = None, force_reload: bool = False) -> Dict[str, Any]:
    """Load model registry containing configurations for all four models."""
    global _CACHED_REGISTRY

    if _CACHED_REGISTRY is not None and not force_reload:
        return _CACHED_REGISTRY

    target_path = Path(registry_path) if registry_path is not None else REGISTRY_PATH

    if not target_path.exists():
        logger.warning("Model registry file '%s' not found. Falling back to default configuration.", target_path.name)
        fallback_registry = {
            "models": {
                "logistic_regression": {
                    "id": "logistic_regression",
                    "display_name": "Logistic Regression",
                    "artifact": "logistic_regression.joblib",
                    "version": "v1",
                    "description": "Regularized linear classification model with standard scaling.",
                    "metrics": {"accuracy": 0.8852, "precision": 0.8387, "recall": 0.9286, "f1_score": 0.8814, "roc_auc": 0.9665}
                },
                "svm": {
                    "id": "svm",
                    "display_name": "Support Vector Machine",
                    "artifact": "svm.joblib",
                    "version": "v1",
                    "description": "Margin-based classifier with radial basis function kernel.",
                    "metrics": {"accuracy": 0.8852, "precision": 0.8387, "recall": 0.9286, "f1_score": 0.8814, "roc_auc": 0.9643}
                },
                "random_forest": {
                    "id": "random_forest",
                    "display_name": "Random Forest",
                    "artifact": "random_forest.joblib",
                    "version": "v1",
                    "description": "Ensemble of 300 decision trees trained with bootstrap aggregating.",
                    "metrics": {"accuracy": 0.8689, "precision": 0.8125, "recall": 0.9286, "f1_score": 0.8667, "roc_auc": 0.9443}
                },
                "xgboost": {
                    "id": "xgboost",
                    "display_name": "XGBoost",
                    "artifact": "xgboost.joblib",
                    "version": "v1",
                    "description": "Gradient-boosted decision trees with regularized objective optimization.",
                    "metrics": {"accuracy": 0.9016, "precision": 0.8438, "recall": 0.9643, "f1_score": 0.9000, "roc_auc": 0.9437}
                }
            },
            "default_model_id": DEFAULT_MODEL_ID
        }
        _CACHED_REGISTRY = fallback_registry
        return _CACHED_REGISTRY

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            registry = json.load(f)
        _CACHED_REGISTRY = registry
        logger.info("Model registry successfully loaded from %s", target_path.name)
        return _CACHED_REGISTRY
    except Exception as exc:
        logger.error("Failed to parse model registry JSON: %s", type(exc).__name__)
        raise CorruptedModelError(f"Model registry file '{target_path.name}' is damaged.") from exc


def get_registry() -> Dict[str, Any]:
    """Retrieve the cached model registry."""
    return load_registry()


def load_model(
    model_path: Optional[Path] = None,
    model_id: Optional[str] = None,
    force_reload: bool = False,
) -> Pipeline:
    """
    Load a serialized scikit-learn Pipeline artifact from disk by model_id or explicit path.
    Uses in-memory cache to ensure models are loaded once and reused across predictions.
    """
    global _CACHED_PIPELINES, _CACHED_PIPELINE

    # Resolve overloaded arguments cleanly
    if isinstance(model_id, Path):
        model_path = model_id
        model_id = None
    elif isinstance(model_path, str) and model_path in SUPPORTED_MODEL_IDS:
        model_id = model_path
        model_path = None

    # Resolve target model ID
    effective_id = model_id.strip().lower() if (model_id and isinstance(model_id, str)) else DEFAULT_MODEL_ID

    # Fast path: check in-memory cache if not forcing reload
    if not force_reload and model_path is None:
        if effective_id in _CACHED_PIPELINES:
            return _CACHED_PIPELINES[effective_id]

    # Determine artifact file path
    if model_path is not None:
        target_path = Path(model_path)
    else:
        registry = get_registry()
        models_dict = registry.get("models", {})
        if effective_id not in models_dict and effective_id not in SUPPORTED_MODEL_IDS:
            raise InvalidModelError(
                f"Unknown model identifier '{effective_id}'. Supported models: {', '.join(SUPPORTED_MODEL_IDS)}"
            )

        model_entry = models_dict.get(effective_id, {})
        artifact_filename = model_entry.get("artifact", f"{effective_id}.joblib")
        target_path = ARTIFACT_DIR / artifact_filename

        # Fallback to MODEL_PATH (model.joblib) if specific model artifact not found
        if not target_path.exists() and MODEL_PATH.exists() and effective_id == DEFAULT_MODEL_ID:
            target_path = MODEL_PATH

    logger.info("Loading model artifact for '%s' from: %s", effective_id, target_path.name)

    if not target_path.exists():
        logger.error("Model artifact file '%s' does not exist.", target_path.name)
        raise ModelNotFoundError(
            f"Production model artifact '{target_path.name}' could not be found. "
            "Please ensure the production model export pipeline has been executed."
        )

    try:
        loaded_obj = joblib.load(target_path)
    except Exception as exc:
        logger.error("Failed to deserialize model artifact '%s': %s", target_path.name, type(exc).__name__)
        raise CorruptedModelError(
            f"Production model artifact '{target_path.name}' is damaged or incompatible."
        ) from exc

    if not isinstance(loaded_obj, Pipeline):
        logger.error("Loaded artifact '%s' is not an sklearn Pipeline instance.", target_path.name)
        raise CorruptedModelError(
            f"Model artifact in '{target_path.name}' is invalid. Expected Pipeline, got {type(loaded_obj).__name__}."
        )

    if not hasattr(loaded_obj, "predict") or not hasattr(loaded_obj, "predict_proba"):
        logger.error("Loaded pipeline '%s' is missing required prediction methods.", target_path.name)
        raise CorruptedModelError(
            f"Model artifact in '{target_path.name}' lacks required prediction capabilities."
        )

    _CACHED_PIPELINES[effective_id] = loaded_obj
    _CACHED_PIPELINE = loaded_obj  # legacy alias
    logger.info("Model pipeline '%s' successfully loaded and cached in memory.", effective_id)
    return loaded_obj


def get_model(model_id: Optional[str] = None) -> Pipeline:
    """Retrieve the cached Pipeline for the specified model_id, loading it on first access."""
    effective_id = model_id.strip().lower() if model_id else DEFAULT_MODEL_ID
    if effective_id in _CACHED_PIPELINES:
        return _CACHED_PIPELINES[effective_id]
    return load_model(model_id=effective_id)


def load_all_models() -> Dict[str, Pipeline]:
    """Eagerly load all supported models from disk into memory cache."""
    registry = get_registry()
    models_dict = registry.get("models", {})
    results: Dict[str, Pipeline] = {}
    for m_id in models_dict.keys():
        try:
            results[m_id] = load_model(model_id=m_id)
        except Exception as exc:
            logger.warning("Could not pre-load model '%s': %s", m_id, exc)
    return results


def get_available_models() -> List[Dict[str, Any]]:
    """
    Verify each model in registry and return list of model summaries with live availability.
    Derives availability from whether the artifact exists and loads correctly.
    """
    registry = get_registry()
    models_dict = registry.get("models", {})
    available_list = []

    for m_id, m_cfg in models_dict.items():
        is_avail = False
        try:
            p = get_model(m_id)
            is_avail = p is not None and hasattr(p, "predict") and hasattr(p, "predict_proba")
        except Exception:
            is_avail = False

        available_list.append({
            "id": m_id,
            "name": m_cfg.get("display_name", m_id),
            "version": m_cfg.get("version", "v1"),
            "description": m_cfg.get("description", ""),
            "metrics": m_cfg.get("metrics", {}),
            "available": is_avail,
        })

    return available_list


def load_metadata(metadata_path: Optional[Path] = None, force_reload: bool = False) -> Dict[str, Any]:
    """Load model metadata JSON from disk, with in-memory caching."""
    global _CACHED_METADATA

    if _CACHED_METADATA is not None and not force_reload:
        return _CACHED_METADATA

    target_path = Path(metadata_path) if metadata_path is not None else METADATA_PATH

    if not target_path.exists():
        logger.error("Production model metadata file does not exist at target location.")
        raise ModelNotFoundError(
            f"Production model metadata '{target_path.name}' could not be found."
        )

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
    except Exception as exc:
        logger.error("Failed to parse model metadata JSON: %s", type(exc).__name__)
        raise CorruptedModelError(
            f"Model metadata file '{target_path.name}' is corrupted or contains invalid JSON."
        ) from exc

    _CACHED_METADATA = metadata
    logger.info("Production model metadata successfully loaded and cached in memory.")
    return _CACHED_METADATA


def get_metadata(model_id: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve metadata, enriched with model-specific entry if requested."""
    raw = load_metadata()
    if model_id is None or model_id == DEFAULT_MODEL_ID:
        return raw

    global _CACHED_MODEL_METADATA
    if model_id in _CACHED_MODEL_METADATA:
        return _CACHED_MODEL_METADATA[model_id]

    meta = dict(raw)
    registry = get_registry()
    models_dict = registry.get("models", {})

    if model_id and model_id in models_dict:
        m_cfg = models_dict[model_id]
        meta["model_name"] = m_cfg.get("display_name", meta.get("model_name"))
        meta["model_version"] = m_cfg.get("version", meta.get("model_version"))
        meta["metrics"] = m_cfg.get("metrics", meta.get("metrics"))
        meta["model_id"] = model_id

    _CACHED_MODEL_METADATA[model_id] = meta
    return meta


def clear_cache() -> None:
    """Clear in-memory cached models, registry, and metadata."""
    global _CACHED_PIPELINES, _CACHED_PIPELINE, _CACHED_METADATA, _CACHED_REGISTRY, _CACHED_MODEL_METADATA
    _CACHED_PIPELINES.clear()
    _CACHED_PIPELINE = None
    _CACHED_METADATA = None
    _CACHED_REGISTRY = None
    _CACHED_MODEL_METADATA.clear()
    logger.debug("In-memory model loader cache cleared.")
