# Disease Prediction from Medical Data

## Project Overview

This repository contains an end-to-end Machine Learning classification project designed to predict whether a patient is likely to have heart disease based on clinical and demographic attributes. The project implements a complete pipeline covering dataset validation, missing value imputation, categorical encoding, feature scaling, stratified train-test splitting, baseline model training (Logistic Regression, Support Vector Machine, Random Forest, XGBoost), model comparison, and visualization artifact generation.

## Dataset

**Dataset Name:** UCI Heart Disease Dataset (Cleveland subset)  
**Source:** UCI Machine Learning Repository  

### Attribute Information
- **`age`**: Age in years
- **`sex`**: Sex (1 = male, 0 = female)
- **`cp`**: Chest pain type (1 = typical angina, 2 = atypical angina, 3 = non-anginal pain, 4 = asymptomatic)
- **`trestbps`**: Resting blood pressure (in mm Hg on admission to the hospital)
- **`chol`**: Serum cholesterol in mg/dl
- **`fbs`**: Fasting blood sugar > 120 mg/dl (1 = true, 0 = false)
- **`restecg`**: Resting electrocardiographic results (0 = normal, 1 = ST-T wave abnormality, 2 = left ventricular hypertrophy)
- **`thalach`**: Maximum heart rate achieved
- **`exang`**: Exercise-induced angina (1 = yes, 0 = no)
- **`oldpeak`**: ST depression induced by exercise relative to rest
- **`slope`**: Slope of peak exercise ST segment (1 = upsloping, 2 = flat, 3 = downsloping)
- **`ca`**: Number of major vessels (0–3) colored by fluoroscopy
- **`thal`**: Thalassemia type (3 = normal, 6 = fixed defect, 7 = reversible defect)
- **`num`**: Original heart disease diagnosis target (0 = no disease, 1–4 = presence of heart disease)

### Target Transformation
To convert the multi-class diagnosis into a binary classification problem:
- `num = 0` $\rightarrow$ `target = 0` (No Heart Disease)
- `num = 1, 2, 3, 4` $\rightarrow$ `target = 1` (Presence of Heart Disease)

> [!IMPORTANT]
> The original `num` column is strictly excluded from predictor features $X$ to prevent target leakage.

## Algorithms Used

Four classical machine learning models are trained and compared:
1. **Logistic Regression:** Regularized linear classifier with feature standardization.
2. **Support Vector Machine (SVM):** Non-linear kernel classifier with probability estimation enabled.
3. **Random Forest:** Ensemble of 300 decision trees.
4. **XGBoost:** Gradient boosted decision trees using log-loss evaluation.

## Preprocessing

- **Data Validation:** Checks data shape, column names, missing values, duplicates, and binary class balance.
- **Train-Test Split:** 80/20 stratified split (`test_size=0.20`, `random_state=42`, `stratify=y`).
- **Numerical Pipeline:** Median imputation (`SimpleImputer(strategy="median")`) followed by standardization (`StandardScaler()`).
- **Categorical Pipeline:** Mode imputation (`SimpleImputer(strategy="most_frequent")`) followed by One-Hot Encoding (`OneHotEncoder(handle_unknown="ignore")`).
- **Leakage Prevention:** Pipelines are fit exclusively on the training set (`X_train`).

## Evaluation Metrics

- **Accuracy:** Proportion of correct predictions.
- **Precision:** Ratio of true positive heart disease cases to total predicted positive cases.
- **Recall:** Sensitivity / true positive rate in detecting heart disease cases.
- **F1-Score:** Harmonic mean of Precision and Recall.
- **ROC-AUC:** Area under the Receiver Operating Characteristic curve evaluated using predicted probabilities.

## Project Structure

```text
Disease-Prediction-Model/
│
├── data/
│   └── dataset.csv
│
├── outputs/
│   ├── confusion_matrices.png
│   ├── roc_curves.png
│   ├── feature_importance.png
│   └── model_comparison.csv
│
├── disease_prediction.py
├── requirements.txt
└── README.md
```

## Installation

```bash
python -m pip install -r requirements.txt
```

## Dataset Setup

Download the UCI Cleveland Heart Disease dataset and place the CSV file at:

```text
data/dataset.csv
```

## Running the Project

```bash
python disease_prediction.py
```

## Generated Outputs

Upon execution, the script generates the following artifacts in `outputs/`:

- `outputs/model_comparison.csv`: Summary CSV table comparing Accuracy, Precision, Recall, F1-Score, and ROC-AUC.
- `outputs/confusion_matrices.png`: 2x2 multi-panel plot of confusion matrices for all 4 models.
- `outputs/roc_curves.png`: Combined ROC curves plot for all models with AUC legend scores.
- `outputs/feature_importance.png`: Horizontal bar chart displaying the top 15 features by Random Forest Gini importance.

## Results

*The evaluation metrics below are computed dynamically upon runtime execution on `data/dataset.csv`:*

| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
|---|---|---|---|---|---|
| Logistic Regression | 0.8852 | 0.8387 | 0.9286 | 0.8814 | 0.9665 |
| Support Vector Machine | 0.8852 | 0.8387 | 0.9286 | 0.8814 | 0.9643 |
| Random Forest | 0.8689 | 0.8125 | 0.9286 | 0.8667 | 0.9443 |
| XGBoost | 0.9016 | 0.8438 | 0.9643 | 0.9000 | 0.9437 |

## Important Medical Disclaimer

> [!CAUTION]
> This project is intended for educational and research purposes only. The predictions generated by this machine-learning model should not be interpreted as medical advice, diagnosis, or a substitute for evaluation by a qualified healthcare professional.
