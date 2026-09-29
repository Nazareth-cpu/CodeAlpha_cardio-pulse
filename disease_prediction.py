"""
Disease Prediction from Medical Data
CodeAlpha Machine Learning Internship Project

Author: CodeAlpha ML Intern
Description: End-to-end Machine Learning classification pipeline predicting heart disease presence
             using the UCI Cleveland Heart Disease dataset.
"""

import sys
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    ConfusionMatrixDisplay,
    roc_curve,
    classification_report,
)

# ============================================================
# CENTRALIZED CONFIGURATION
# ============================================================
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_PATH = PROJECT_ROOT / "data" / "dataset.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
RANDOM_STATE = 42
TEST_SIZE = 0.20

STANDARD_CLEVELAND_COLUMNS = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal", "num"
]

CATEGORICAL_ATTRIBUTES = ["sex", "cp", "fbs", "restecg", "exang", "slope", "ca", "thal"]
NUMERICAL_ATTRIBUTES = ["age", "trestbps", "chol", "thalach", "oldpeak"]


def load_data(data_path: Path = DATA_PATH) -> pd.DataFrame:
    """
    Load dataset from CSV path.
    Handles standard headerless UCI Cleveland format as well as header-included CSVs.
    """
    if not data_path.exists():
        print("\n" + "=" * 50)
        print("ERROR: DATASET NOT FOUND")
        print("=" * 50)
        raise FileNotFoundError(
            f"dataset.csv was not found. Please place the UCI Cleveland Heart Disease dataset at {data_path}."
        )

    try:
        # First attempt: Read without assuming headers
        df_raw = pd.read_csv(data_path, header=None, na_values=["?", "NA", "null", "none", ""])

        # Check if first row contained header strings
        first_row_strings = sum(isinstance(val, str) and not val.replace('.', '', 1).isdigit() for val in df_raw.iloc[0])
        if first_row_strings > 3:
            # Re-read with header
            df = pd.read_csv(data_path, na_values=["?", "NA", "null", "none", ""])
            df.columns = [str(col).strip().lower() for col in df.columns]
        else:
            df = df_raw
            if df.shape[1] == len(STANDARD_CLEVELAND_COLUMNS):
                df.columns = STANDARD_CLEVELAND_COLUMNS
            else:
                df.columns = [f"col_{i}" for i in range(df.shape[1])]

        if df.empty:
            raise ValueError(f"The dataset file at {data_path} is empty.")

        # Handle binary target transformation from original 'num' column (0 to 4)
        if "target" in df.columns:
            # Target already defined; ensure binary numeric
            df["target"] = pd.to_numeric(df["target"], errors="coerce")
            df["target"] = (df["target"] > 0).astype(int)
        elif "num" in df.columns:
            # Create binary target: 0 = No Disease, 1 = Presence of Heart Disease
            df["num"] = pd.to_numeric(df["num"], errors="coerce")
            df["target"] = (df["num"] > 0).astype(int)
        else:
            # Fallback: assume last column is target
            last_col = df.columns[-1]
            df[last_col] = pd.to_numeric(df[last_col], errors="coerce")
            df["target"] = (df[last_col] > 0).astype(int)

        print(f"Dataset successfully loaded from {data_path}")
        return df

    except Exception as e:
        if isinstance(e, FileNotFoundError):
            raise
        raise RuntimeError(f"Failed to read dataset at {data_path}: {e}") from e


def validate_data(df: pd.DataFrame) -> None:
    """
    Perform dataset validation and print initial inspection diagnostics.
    """
    print("\n" + "=" * 50)
    print("DATASET INFORMATION")
    print("=" * 50)
    print(f"Dataset shape: {df.shape[0]} rows, {df.shape[1]} columns")
    print("\nColumns:", list(df.columns))

    print("\nFirst 5 rows:")
    print(df.head())

    print("\nData types:")
    print(df.dtypes)

    print("\nMissing values check:")
    missing = df.isnull().sum()
    missing_cols = missing[missing > 0]
    if len(missing_cols) > 0:
        print(missing_cols)
    else:
        print("No missing values found.")

    print("\nDuplicate rows check:")
    duplicates = df.duplicated().sum()
    print(f"Duplicate rows count: {duplicates}")

    if "target" not in df.columns:
        raise ValueError("Target column could not be established.")

    unique_targets = sorted(df["target"].unique())
    print("\nTarget class distribution:")
    counts = df["target"].value_counts()
    props = df["target"].value_counts(normalize=True) * 100
    for cls in unique_targets:
        label = "Disease (1)" if cls == 1 else "No Disease (0)"
        print(f"  Class {cls} ({label}): {counts[cls]} samples ({props[cls]:.2f}%)")

    if len(unique_targets) != 2:
        raise ValueError(f"Target must contain exactly two classes after conversion. Found: {unique_targets}")

    print("\nData validation passed: Binary target established successfully.")


def prepare_data(df: pd.DataFrame) -> tuple:
    """
    Isolate predictor features X and target label y, preventing data leakage.
    Original 'num' column and any ID columns are explicitly removed from X.
    """
    print("\n" + "=" * 50)
    print("PREPROCESSING & FEATURE ISOLATION")
    print("=" * 50)

    # Exclude target and original 'num' source column to prevent data leakage
    drop_cols = ["target", "num", "id"]
    X = df.drop(columns=[col for col in drop_cols if col in df.columns], errors="ignore").copy()
    y = df["target"].copy()

    # Convert all predictor columns to numeric types
    for col in X.columns:
        X[col] = pd.to_numeric(X[col], errors="coerce")

    # Categorize attributes into categorical/discrete vs numerical
    cat_cols = [col for col in CATEGORICAL_ATTRIBUTES if col in X.columns]
    num_cols = [col for col in X.columns if col not in cat_cols]

    print(f"Target variable   : 'target' (0 = No Disease, 1 = Disease)")
    print(f"Predictor features: {X.shape[1]} columns")
    print(f"Numerical features ({len(num_cols)}): {num_cols}")
    print(f"Categorical features ({len(cat_cols)}): {cat_cols}")

    return X, y, num_cols, cat_cols


def build_preprocessor(numerical_cols: list, categorical_cols: list) -> ColumnTransformer:
    """
    Construct ColumnTransformer for numerical and categorical features.
    Learns preprocessing parameters strictly from training data.
    """
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
            ("num", num_transformer, numerical_cols),
            ("cat", cat_transformer, categorical_cols)
        ],
        remainder="drop"
    )


def build_models() -> dict:
    """
    Return dictionary of baseline classifiers: Logistic Regression, SVM, Random Forest, XGBoost.
    """
    return {
        "Logistic Regression": LogisticRegression(
            max_iter=2000,
            random_state=RANDOM_STATE
        ),
        "Support Vector Machine": SVC(
            probability=True,
            random_state=RANDOM_STATE
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=300,
            random_state=RANDOM_STATE
        ),
        "XGBoost": XGBClassifier(
            n_estimators=300,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric="logloss",
            random_state=RANDOM_STATE
        )
    }


def train_and_evaluate_models(
    models: dict,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    numerical_cols: list,
    categorical_cols: list
) -> tuple:
    """
    Fit preprocessing and model pipelines on X_train only and evaluate on X_test.
    """
    print("\n" + "=" * 50)
    print("MODEL TRAINING & EVALUATION")
    print("=" * 50)

    trained_pipelines = {}
    results = []
    test_preds = {}
    test_probs = {}

    for name, model in models.items():
        print(f"Training {name}...")

        preprocessor = build_preprocessor(numerical_cols, categorical_cols)
        pipeline = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("model", model)
        ])

        # Fit pipeline ONLY on training set
        pipeline.fit(X_train, y_train)
        trained_pipelines[name] = pipeline

        # Predictions on test set
        y_pred = pipeline.predict(X_test)
        y_prob = pipeline.predict_proba(X_test)[:, 1]

        test_preds[name] = y_pred
        test_probs[name] = y_prob

        # Evaluation metrics
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        roc_auc = roc_auc_score(y_test, y_prob)

        results.append({
            "Model": name,
            "Accuracy": round(acc, 4),
            "Precision": round(prec, 4),
            "Recall": round(rec, 4),
            "F1-Score": round(f1, 4),
            "ROC-AUC": round(roc_auc, 4)
        })

        print(f"  [{name}] Acc: {acc:.4f} | Prec: {prec:.4f} | Rec: {rec:.4f} | F1: {f1:.4f} | AUC: {roc_auc:.4f}")

    results_df = pd.DataFrame(results).sort_values(by="ROC-AUC", ascending=False).reset_index(drop=True)
    return trained_pipelines, results_df, test_preds, test_probs


def plot_confusion_matrices(models: dict, trained_pipelines: dict, X_test: pd.DataFrame, y_test: pd.Series, output_dir: Path) -> Path:
    """
    Generate single 2x2 multi-panel plot containing confusion matrices for all models.
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes_flat = axes.flatten()

    for idx, (name, _) in enumerate(models.items()):
        pipeline = trained_pipelines[name]
        y_pred = pipeline.predict(X_test)
        cm = confusion_matrix(y_test, y_pred)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["No Disease (0)", "Disease (1)"])
        disp.plot(ax=axes_flat[idx], cmap="Blues", colorbar=False)
        axes_flat[idx].set_title(f"{name}\nConfusion Matrix", fontsize=11, fontweight="bold")
        axes_flat[idx].set_xlabel("Predicted Label")
        axes_flat[idx].set_ylabel("True Label")

    plt.tight_layout()
    output_path = output_dir / "confusion_matrices.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Confusion matrices saved to {output_path}")
    return output_path


def plot_roc_curves(test_probs: dict, y_test: pd.Series, output_dir: Path) -> Path:
    """
    Plot ROC curves for all four models on a single figure.
    """
    plt.figure(figsize=(9, 7))

    for name, probs in test_probs.items():
        fpr, tpr, _ = roc_curve(y_test, probs)
        auc_val = roc_auc_score(y_test, probs)
        plt.plot(fpr, tpr, label=f"{name} (AUC = {auc_val:.4f})", linewidth=2)

    plt.plot([0, 1], [0, 1], "k--", label="Random Classifier (AUC = 0.5000)", linewidth=1.5)
    plt.xlabel("False Positive Rate", fontsize=11)
    plt.ylabel("True Positive Rate", fontsize=11)
    plt.title("Receiver Operating Characteristic (ROC) Curves", fontsize=13, fontweight="bold")
    plt.legend(loc="lower right", fontsize=10)
    plt.grid(True, linestyle="--", alpha=0.6)

    plt.tight_layout()
    output_path = output_dir / "roc_curves.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"ROC curves saved to {output_path}")
    return output_path


def plot_feature_importance(
    rf_pipeline: Pipeline,
    numerical_cols: list,
    categorical_cols: list,
    output_dir: Path,
    top_n: int = 15
) -> Path:
    """
    Extract and plot top N feature importances from Random Forest model using get_feature_names_out().
    """
    rf_model = rf_pipeline.named_steps["model"]
    preprocessor = rf_pipeline.named_steps["preprocessor"]

    cat_encoder = preprocessor.named_transformers_["cat"].named_steps["encoder"]
    if hasattr(cat_encoder, "get_feature_names_out"):
        cat_feature_names = list(cat_encoder.get_feature_names_out(categorical_cols))
    else:
        cat_feature_names = list(cat_encoder.get_feature_names(categorical_cols))

    feature_names = numerical_cols + cat_feature_names
    importances = rf_model.feature_importances_

    importance_df = pd.DataFrame({
        "Feature": feature_names,
        "Importance": importances
    }).sort_values(by="Importance", ascending=False).reset_index(drop=True)

    top_features = importance_df.head(top_n).sort_values(by="Importance", ascending=True)

    plt.figure(figsize=(10, 6))
    plt.barh(top_features["Feature"], top_features["Importance"], color="#2ca02c", edgecolor="black", alpha=0.85)
    plt.xlabel("Feature Importance (Gini Impurity Reduction)", fontsize=11)
    plt.ylabel("Transformed Feature", fontsize=11)
    plt.title(f"Top {top_n} Most Important Features (Random Forest)", fontsize=13, fontweight="bold")
    plt.grid(True, linestyle="--", alpha=0.5, axis="x")

    plt.tight_layout()
    output_path = output_dir / "feature_importance.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Feature importance plot saved to {output_path}")
    return output_path


def save_results(results_df: pd.DataFrame, output_dir: Path) -> Path:
    """
    Save model comparison table to CSV.
    """
    output_path = output_dir / "model_comparison.csv"
    results_df.to_csv(output_path, index=False)
    print(f"Model comparison saved to {output_path}")
    return output_path


def main():
    print("\n" + "=" * 50)
    print("DISEASE PREDICTION FROM MEDICAL DATA")
    print("=" * 50)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load data
    try:
        df = load_data(DATA_PATH)
    except FileNotFoundError as fnf_err:
        print(f"\n{fnf_err}")
        sys.exit(1)
    except Exception as err:
        print(f"\nExecution error while loading dataset: {err}")
        sys.exit(1)

    # 2. Validate data
    validate_data(df)

    # 3. Prepare features and target
    X, y, numerical_cols, categorical_cols = prepare_data(df)

    # 4. Stratified Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    print("\nTrain-Test Split Summary:")
    print(f"  Training set : {X_train.shape[0]} samples")
    print(f"  Testing set  : {X_test.shape[0]} samples")
    print(f"  Class Proportions (Full) : {y.value_counts(normalize=True).to_dict()}")
    print(f"  Class Proportions (Train): {y_train.value_counts(normalize=True).to_dict()}")
    print(f"  Class Proportions (Test) : {y_test.value_counts(normalize=True).to_dict()}")

    # 5. Build and train models
    models = build_models()
    trained_pipelines, results_df, test_preds, test_probs = train_and_evaluate_models(
        models, X_train, y_train, X_test, y_test, numerical_cols, categorical_cols
    )

    # 6. Display model performance summary
    print("\n" + "=" * 50)
    print("MODEL PERFORMANCE")
    print("=" * 50)
    print(results_df.to_string(index=False))

    save_results(results_df, OUTPUT_DIR)

    # 7. Identify best model based on ROC-AUC
    best_model_name = results_df.iloc[0]["Model"]
    best_auc = results_df.iloc[0]["ROC-AUC"]
    best_acc = results_df.iloc[0]["Accuracy"]
    best_prec = results_df.iloc[0]["Precision"]
    best_rec = results_df.iloc[0]["Recall"]
    best_f1 = results_df.iloc[0]["F1-Score"]

    print("\n" + "=" * 50)
    print("BEST MODEL")
    print("=" * 50)
    print(f"Best Model based on ROC-AUC: {best_model_name}")
    print(f"  Accuracy : {best_acc:.4f}")
    print(f"  Precision: {best_prec:.4f}")
    print(f"  Recall   : {best_rec:.4f}")
    print(f"  F1-Score : {best_f1:.4f}")
    print(f"  ROC-AUC  : {best_auc:.4f}")

    print("\nClassification Report for Best Model:")
    print(classification_report(y_test, test_preds[best_model_name], target_names=["No Disease (0)", "Disease (1)"]))

    # 8. Generate visualization artifacts
    print("\n" + "=" * 50)
    print("OUTPUT FILES")
    print("=" * 50)
    plot_confusion_matrices(models, trained_pipelines, X_test, y_test, OUTPUT_DIR)
    plot_roc_curves(test_probs, y_test, OUTPUT_DIR)

    if "Random Forest" in trained_pipelines:
        plot_feature_importance(
            trained_pipelines["Random Forest"], numerical_cols, categorical_cols, OUTPUT_DIR
        )

    print("\nPipeline execution successfully completed!")


if __name__ == "__main__":
    main()
