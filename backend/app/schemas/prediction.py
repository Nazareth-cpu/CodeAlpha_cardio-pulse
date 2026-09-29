"""
Prediction request and response schemas for CardioPulse FastAPI Backend.

Enforces strict Pydantic validation:
  - Rejects forbidden fields ('num', 'target', 'id')
  - Rejects unknown fields
  - Enforces exact canonical types and values
  - Supports explicit model selection across all four production models
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class PredictionRequest(BaseModel):
    """
    Standard clinical observation payload containing the 13 canonical features
    and optional explicit model selection.
    Any extra fields (e.g. 'num', 'target', 'id', 'bmi') are strictly forbidden.
    """
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "model_id": "logistic_regression",
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
        },
    )

    model_id: Optional[str] = Field(
        default=None,
        description="Selected model identifier: 'logistic_regression', 'svm', 'random_forest', or 'xgboost'",
    )
    age: float = Field(..., description="Age in years (e.g. 52)")
    sex: float = Field(..., description="Biological sex (0.0 = female, 1.0 = male)")
    cp: float = Field(..., description="Chest pain type (1.0 = typical angina, 2.0 = atypical angina, 3.0 = non-anginal pain, 4.0 = asymptomatic)")
    trestbps: float = Field(..., description="Resting blood pressure in mm Hg on hospital admission")
    chol: float = Field(..., description="Serum cholesterol in mg/dl")
    fbs: float = Field(..., description="Fasting blood sugar > 120 mg/dl (1.0 = true, 0.0 = false)")
    restecg: float = Field(..., description="Resting electrocardiographic results (0.0 = normal, 1.0 = ST-T wave abnormality, 2.0 = LV hypertrophy)")
    thalach: float = Field(..., description="Maximum heart rate achieved")
    exang: float = Field(..., description="Exercise-induced angina (1.0 = yes, 0.0 = no)")
    oldpeak: float = Field(..., description="ST depression induced by exercise relative to rest")
    slope: float = Field(..., description="Slope of the peak exercise ST segment (1.0 = upsloping, 2.0 = flat, 3.0 = downsloping)")
    ca: float = Field(..., description="Number of major vessels (0.0 - 3.0) colored by fluoroscopy")
    thal: float = Field(..., description="Thallium stress test result (3.0 = normal, 6.0 = fixed defect, 7.0 = reversible defect)")

    @model_validator(mode="before")
    @classmethod
    def handle_nested_features(cls, data: Any) -> Any:
        """Allow requests with nested {'model_id': '...', 'features': {...}} structure cleanly."""
        if isinstance(data, dict) and "features" in data and isinstance(data["features"], dict):
            flattened = dict(data["features"])
            if "model_id" in data:
                flattened["model_id"] = data["model_id"]
            return flattened
        return data

    def model_dump(self, *args, **kwargs):
        """Custom dump that omits model_id when unset to preserve exact canonical feature schema."""
        d = super().model_dump(*args, **kwargs)
        if self.model_id is None and "model_id" in d:
            del d["model_id"]
        return d


class PredictionResponse(BaseModel):
    """Structured production prediction response including persistent record identifier and model identity."""
    prediction_id: str = Field(..., description="Unique persistent identifier of the stored prediction record")
    model_id: str = Field(..., description="Identifier of the model used: logistic_regression, svm, random_forest, or xgboost")
    model_name: str = Field(..., description="Display name of the machine learning model")
    model_version: str = Field(..., description="Version identifier of the deployed model artifact")
    prediction: int = Field(..., description="Predicted class label: 0 (No Heart Disease) or 1 (Presence of Heart Disease)")
    probability: float = Field(..., description="Estimated model probability for class 1 (range 0.0 to 1.0)")
    disclaimer: str = Field(..., description="Mandatory medical research and educational use disclaimer")


class PredictionSummaryItem(BaseModel):
    """Summary of a historical prediction record without bulky input data."""
    prediction_id: str = Field(..., description="Unique prediction record identifier")
    model_id: Optional[str] = Field("logistic_regression", description="Identifier of model used")
    prediction: int = Field(..., description="Predicted class label: 0 or 1")
    probability: float = Field(..., description="Estimated model probability (0.0 to 1.0)")
    model_name: str = Field(..., description="Name of the production machine learning model")
    model_version: str = Field(..., description="Version identifier of the deployed model artifact")
    created_at: str = Field(..., description="Server timestamp formatted in ISO 8601")


class PredictionHistoryResponse(BaseModel):
    """Paginated list of prediction history for the authenticated user."""
    predictions: List[PredictionSummaryItem] = Field(..., description="List of user's historical predictions")
    total: int = Field(..., description="Number of prediction records returned in this batch")
    limit: int = Field(..., description="Applied pagination query limit")


class PredictionDetailResponse(BaseModel):
    """Detailed prediction record including full clinical inputs, model metadata, and outcomes."""
    prediction_id: str = Field(..., description="Unique prediction identifier")
    user_id: str = Field(..., description="Owning user Firebase UID")
    input: Dict[str, float] = Field(..., description="Clinical observation inputs")
    result: Dict[str, Any] = Field(..., description="Inference outcome and probability")
    model: Dict[str, str] = Field(..., description="Model architecture, identifier, and version metadata")
    created_at: str = Field(..., description="Server timestamp formatted in ISO 8601")


class DeletePredictionResponse(BaseModel):
    """Status confirmation following successful deletion of a prediction record."""
    success: bool = Field(True, description="Whether record was deleted successfully")
    message: str = Field("Prediction record deleted successfully.", description="Operation status message")
    prediction_id: str = Field(..., description="Identifier of the deleted prediction record")


class ModelInfoItem(BaseModel):
    """Single model information item in the multi-model catalog."""
    id: str = Field(..., description="Unique model identifier (e.g. 'logistic_regression', 'svm', 'random_forest', 'xgboost')")
    name: str = Field(..., description="Human-readable model name")
    version: str = Field(..., description="Model artifact version")
    description: Optional[str] = Field(None, description="Technical summary of the algorithm")
    metrics: Dict[str, float] = Field(..., description="Test-set evaluation metrics (accuracy, precision, recall, f1_score, roc_auc)")
    available: bool = Field(..., description="Whether artifact is currently verified and loadable in runtime")


class ModelListResponse(BaseModel):
    """Multi-model catalog listing all four trained models."""
    models: List[ModelInfoItem] = Field(..., description="List of all available machine-learning models")
    default_model_id: str = Field("logistic_regression", description="Default model identifier")


class ModelMetadataResponse(BaseModel):
    """Production model evaluation metadata and operational parameters."""
    model_name: str = Field(..., description="Production model architecture name")
    model_version: str = Field(..., description="Production artifact version")
    task: str = Field(..., description="Machine learning task type")
    dataset: str = Field(..., description="Source dataset")
    selection_criterion: str = Field(..., description="Criterion used to select production model")
    metrics: Dict[str, float] = Field(..., description="Model evaluation benchmark metrics on test set")
    features: List[str] = Field(..., description="Canonical 13 input features in fixed order")
    numerical_features: List[str] = Field(..., description="List of continuous numerical features")
    categorical_features: List[str] = Field(..., description="List of discrete categorical features")
    confusion_matrix: Dict[str, int] = Field(..., description="Test set confusion matrix counts (TN, FP, FN, TP)")
    disclaimer: str = Field(..., description="Educational use disclaimer")
