/**
 * Types representing the CardioPulse Machine Learning API Contracts
 * Based on the UCI Cleveland Heart Disease dataset (13 canonical features)
 * and Multi-Model Selection across all 4 production models.
 */

export interface ClinicalInputs {
  age: number;      // Age in years (29 - 77)
  sex: number;      // 0 = female, 1 = male
  cp: number;       // Chest pain type (1 = typical angina, 2 = atypical angina, 3 = non-anginal, 4 = asymptomatic)
  trestbps: number; // Resting blood pressure in mm Hg
  chol: number;     // Serum cholesterol in mg/dl
  fbs: number;      // Fasting blood sugar > 120 mg/dl (1 = true, 0 = false)
  restecg: number;  // Resting ECG results (0 = normal, 1 = ST-T abnormality, 2 = LV hypertrophy)
  thalach: number;  // Maximum heart rate achieved
  exang: number;    // Exercise-induced angina (1 = yes, 0 = no)
  oldpeak: number;  // ST depression induced by exercise relative to rest
  slope: number;    // Slope of the peak exercise ST segment (1 = upsloping, 2 = flat, 3 = downsloping)
  ca: number;       // Number of major vessels (0 - 3) colored by fluoroscopy
  thal: number;     // Thallium stress test (3 = normal, 6 = fixed defect, 7 = reversible defect)
}

export interface PredictionRequest extends ClinicalInputs {
  model_id?: string; // Optional: 'logistic_regression', 'svm', 'random_forest', 'xgboost'
}

export interface PredictionResponse {
  prediction_id: string;
  model_id: string;
  model_name: string;
  model_version: string;
  prediction: 0 | 1;
  probability: number;
  disclaimer: string;
}

export interface PredictionSummaryItem {
  prediction_id: string;
  model_id?: string;
  model_name: string;
  model_version: string;
  prediction: 0 | 1;
  probability: number;
  created_at: string;
}

export interface PredictionHistoryResponse {
  predictions: PredictionSummaryItem[];
  total: number;
  limit: number;
}

export interface PredictionDetailResponse {
  prediction_id: string;
  user_id: string;
  input: ClinicalInputs;
  result: {
    prediction: 0 | 1;
    probability: number;
  };
  model: {
    model_id?: string;
    model_name: string;
    model_version: string;
  };
  created_at: string;
}

export interface DeletePredictionResponse {
  success: boolean;
  message: string;
  prediction_id: string;
}

export interface ModelInfoItem {
  id: string;
  name: string;
  version: string;
  description?: string;
  metrics: {
    accuracy: number;
    precision: number;
    recall: number;
    f1_score: number;
    roc_auc: number;
    [key: string]: number;
  };
  available: boolean;
}

export interface ModelListResponse {
  models: ModelInfoItem[];
  default_model_id: string;
}

export interface ModelMetadataResponse {
  model_name: string;
  model_version: string;
  task: string;
  dataset: string;
  selection_criterion: string;
  metrics: {
    accuracy?: number;
    roc_auc?: number;
    f1?: number;
    f1_score?: number;
    precision?: number;
    recall?: number;
    [key: string]: number | undefined;
  };
  features: string[];
  numerical_features: string[];
  categorical_features: string[];
  confusion_matrix: {
    TN?: number;
    FP?: number;
    FN?: number;
    TP?: number;
    [key: string]: number | undefined;
  };
  disclaimer: string;
}

export interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unavailable';
  service: string;
  model_loaded: boolean;
  model_name?: string;
  model_version?: string;
}
