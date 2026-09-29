import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import {
  Activity,
  AlertCircle,
  ArrowLeft,
  BarChart3,
  Calendar,
  CheckCircle2,
  Clock,
  Cpu,
  FileText,
  HeartPulse,
  Info,
  Loader2,
  PlusCircle,
  Printer,
  ShieldAlert,
  ShieldCheck,
} from 'lucide-react';
import { PageContainer } from '../components/layout/PageContainer';
import { Section } from '../components/layout/Section';
import { Button } from '../components/ui/Button';
import { Alert } from '../components/ui/Alert';
import { apiClient } from '../lib/api';
import { formatDateTime, formatPercent } from '../lib/utils';
import { useAuth } from '../hooks/useAuth';
import type { PredictionDetailResponse } from '../types/prediction';

// Baseline test-set reference metrics from outputs/model_comparison.csv
const MODEL_BENCHMARK_METRICS: Record<string, { accuracy: number; precision: number; recall: number; f1_score: number; roc_auc: number; desc: string }> = {
  'Logistic Regression': {
    accuracy: 0.8852,
    precision: 0.8387,
    recall: 0.9286,
    f1_score: 0.8814,
    roc_auc: 0.9665,
    desc: 'Regularized linear classification model with standard scaling.',
  },
  'logistic_regression': {
    accuracy: 0.8852,
    precision: 0.8387,
    recall: 0.9286,
    f1_score: 0.8814,
    roc_auc: 0.9665,
    desc: 'Regularized linear classification model with standard scaling.',
  },
  'Support Vector Machine': {
    accuracy: 0.8852,
    precision: 0.8387,
    recall: 0.9286,
    f1_score: 0.8814,
    roc_auc: 0.9643,
    desc: 'Margin-based classifier with radial basis function kernel and probability estimation.',
  },
  'svm': {
    accuracy: 0.8852,
    precision: 0.8387,
    recall: 0.9286,
    f1_score: 0.8814,
    roc_auc: 0.9643,
    desc: 'Margin-based classifier with radial basis function kernel and probability estimation.',
  },
  'Random Forest': {
    accuracy: 0.8689,
    precision: 0.8125,
    recall: 0.9286,
    f1_score: 0.8667,
    roc_auc: 0.9443,
    desc: 'Ensemble of 300 decision trees with bootstrap aggregation.',
  },
  'random_forest': {
    accuracy: 0.8689,
    precision: 0.8125,
    recall: 0.9286,
    f1_score: 0.8667,
    roc_auc: 0.9443,
    desc: 'Ensemble of 300 decision trees with bootstrap aggregation.',
  },
  'XGBoost': {
    accuracy: 0.9016,
    precision: 0.8438,
    recall: 0.9643,
    f1_score: 0.9000,
    roc_auc: 0.9437,
    desc: 'Gradient-boosted decision-tree model with regularized loss optimization.',
  },
  'xgboost': {
    accuracy: 0.9016,
    precision: 0.8438,
    recall: 0.9643,
    f1_score: 0.9000,
    roc_auc: 0.9437,
    desc: 'Gradient-boosted decision-tree model with regularized loss optimization.',
  },
};

export function ResultPage() {
  const { id } = useParams<{ id: string }>();
  const { currentUser, loading: authLoading } = useAuth();

  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [record, setRecord] = useState<PredictionDetailResponse | null>(null);

  useEffect(() => {
    if (!id) {
      setErrorMsg('No prediction identifier provided in route.');
      setLoading(false);
      return;
    }

    if (authLoading) return;
    if (!currentUser) {
      setLoading(false);
      return;
    }

    let isMounted = true;

    async function fetchRecord() {
      try {
        setLoading(true);
        setErrorMsg(null);

        // Authenticated GET /api/v1/predictions/{id}
        const data = await apiClient.get<PredictionDetailResponse>(`/api/v1/predictions/${id}`);
        if (isMounted) {
          setRecord(data);
        }
      } catch (err: any) {
        if (isMounted) {
          console.error('Failed to load prediction record:', err);
          setErrorMsg(err?.message || 'Unable to retrieve prediction record.');
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    fetchRecord();

    return () => {
      isMounted = false;
    };
  }, [id, authLoading, currentUser]);

  if (loading) {
    return (
      <PageContainer size="md">
        <div className="py-24 flex flex-col items-center justify-center text-center space-y-4">
          <Loader2 className="w-8 h-8 animate-spin text-[#087F5B]" />
          <p className="text-sm font-semibold text-[#12231E]">
            Retrieving clinical assessment record...
          </p>
          <span className="text-xs font-mono text-[#65756F]">
            Querying persistent Firestore database
          </span>
        </div>
      </PageContainer>
    );
  }

  if (errorMsg || !record) {
    return (
      <PageContainer size="md">
        <div className="space-y-6">
          <Alert
            variant="error"
            title="Assessment Record Unavailable"
            description={errorMsg || 'The requested clinical assessment was not found.'}
          />
          <div className="flex items-center gap-3">
            <Link to="/history">
              <Button size="sm" variant="outline" leftIcon={<ArrowLeft className="w-3.5 h-3.5" />}>
                Back to History
              </Button>
            </Link>
            <Link to="/assessment">
              <Button size="sm" variant="amber" leftIcon={<PlusCircle className="w-3.5 h-3.5" />}>
                Start New Assessment
              </Button>
            </Link>
          </div>
        </div>
      </PageContainer>
    );
  }

  const { result, model, input, created_at } = record;
  const isElevated = result.prediction === 1;
  const probPercent = (result.probability * 100).toFixed(1);

  // Look up model test-set metrics
  const benchmark =
    MODEL_BENCHMARK_METRICS[model.model_name] ||
    (model.model_id ? MODEL_BENCHMARK_METRICS[model.model_id] : null) || {
      accuracy: 0.8852,
      precision: 0.8387,
      recall: 0.9286,
      f1_score: 0.8814,
      roc_auc: 0.9665,
      desc: 'Trained supervised classifier evaluated on benchmark dataset.',
    };

  // Human readable translations for display
  const chestPainLabels: Record<number, string> = {
    1: 'Typical Angina',
    2: 'Atypical Angina',
    3: 'Non-Anginal Pain',
    4: 'Asymptomatic',
  };

  const slopeLabels: Record<number, string> = {
    1: 'Upsloping',
    2: 'Flat',
    3: 'Downsloping',
  };

  const thalLabels: Record<number, string> = {
    3: 'Normal Uptake',
    6: 'Fixed Defect',
    7: 'Reversible Defect',
  };

  const restecgLabels: Record<number, string> = {
    0: 'Normal',
    1: 'ST-T Wave Abnormality',
    2: 'Left Ventricular Hypertrophy',
  };

  return (
    <PageContainer size="lg">
      <Section
        title="Assessment Result"
        description="Machine learning statistical risk evaluation based on your selected predictive model."
        headerAction={
          <div className="flex items-center gap-2.5">
            <Button
              size="sm"
              variant="outline"
              leftIcon={<Printer className="w-3.5 h-3.5" />}
              onClick={() => window.print()}
            >
              Print Report
            </Button>
            <Link to="/assessment">
              <Button size="sm" variant="amber" leftIcon={<PlusCircle className="w-3.5 h-3.5" />}>
                New Assessment
              </Button>
            </Link>
          </div>
        }
      >
        <div className="space-y-8">
          {/* ========================================================= */}
          {/* PRIMARY ASSESSMENT CARD                                   */}
          {/* ========================================================= */}
          <div className="bg-white rounded-2xl border border-[#E2ECE8] p-6 sm:p-8 shadow-sm">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
              {/* Left Column: Result Outcome & Calibrated Probability */}
              <div className="lg:col-span-7 space-y-4">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#E6F3EF] border border-[#087F5B]/20 text-[11px] font-bold text-[#087F5B] uppercase tracking-wider">
                  <Cpu className="w-3.5 h-3.5 text-[#14B8A6]" />
                  <span>MODEL ASSESSMENT • {model.model_name}</span>
                </div>

                <div className="space-y-1">
                  <h2 className="text-2xl sm:text-3xl font-extrabold text-[#12231E] tracking-tight">
                    {isElevated ? (
                      <span className="text-[#DE9E27]">
                        Elevated Estimated Likelihood
                      </span>
                    ) : (
                      <span className="text-[#087F5B]">
                        Lower Estimated Likelihood
                      </span>
                    )}
                  </h2>
                  <p className="text-xs text-[#65756F]">
                    The calibrated model estimated a probability of{' '}
                    <strong className="text-[#12231E] font-semibold">{probPercent}%</strong> for
                    presence of heart disease based on the provided clinical features.
                  </p>
                </div>

                {/* Risk Probability Spectrum Bar */}
                <div className="space-y-2 pt-2">
                  <div className="flex justify-between items-baseline text-xs">
                    <span className="font-semibold text-[#65756F]">Estimated Individual Probability</span>
                    <span className="font-mono text-sm font-black text-[#12231E]">
                      {probPercent}% ({result.probability.toFixed(4)})
                    </span>
                  </div>

                  <div className="relative h-3.5 w-full rounded-full bg-slate-100 overflow-hidden flex">
                    <div className="h-full bg-[#087F5B] w-1/3" title="Lower Range" />
                    <div className="h-full bg-[#14B8A6] w-1/3" title="Mid Range" />
                    <div className="h-full bg-[#F4B942] w-1/3" title="Elevated Range" />
                  </div>

                  {/* Marker pointer */}
                  <div className="relative w-full h-3">
                    <div
                      className="absolute -top-1 w-3 h-3 bg-[#12231E] rotate-45 rounded-[2px] border-2 border-white shadow-xs"
                      style={{
                        left: `clamp(0%, ${result.probability * 100}%, calc(100% - 12px))`,
                      }}
                    />
                  </div>

                  <div className="flex justify-between text-[10px] text-[#65756F] font-mono">
                    <span>0.00 (Lower Probability)</span>
                    <span className="text-[#14B8A6] font-semibold">0.50 (Classification Threshold)</span>
                    <span className="text-[#F4B942] font-semibold">1.00 (Elevated Probability)</span>
                  </div>
                </div>
              </div>

              {/* Right Column: Metadata Box */}
              <div className="lg:col-span-5 bg-[#F6FAF8] rounded-xl border border-[#E2ECE8] p-5 space-y-3 text-xs">
                <div className="flex items-center justify-between pb-2 border-b border-[#E2ECE8]">
                  <span className="text-[#65756F]">Record ID</span>
                  <span className="font-mono text-[11px] font-bold text-[#12231E] truncate max-w-[170px]">
                    {record.prediction_id}
                  </span>
                </div>

                <div className="flex items-center justify-between pb-2 border-b border-[#E2ECE8]">
                  <span className="text-[#65756F]">Selected Model</span>
                  <span className="font-bold text-[#087F5B]">{model.model_name}</span>
                </div>

                <div className="flex items-center justify-between pb-2 border-b border-[#E2ECE8]">
                  <span className="text-[#65756F]">Model Version</span>
                  <span className="font-mono text-[11px] text-[#12231E]">
                    {model.model_version}
                  </span>
                </div>

                <div className="flex items-center justify-between pb-2 border-b border-[#E2ECE8]">
                  <span className="text-[#65756F]">Evaluation Date</span>
                  <span className="font-medium text-[#12231E]">
                    {created_at ? formatDateTime(created_at) : 'Just now'}
                  </span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-[#65756F]">Storage Scope</span>
                  <span className="inline-flex items-center gap-1 font-semibold text-[#087F5B]">
                    <ShieldCheck className="w-3.5 h-3.5 text-[#14B8A6]" />
                    <span>Cloud Firestore Isolated</span>
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* ========================================================= */}
          {/* MODEL EVALUATION METRICS (TEST SET REFERENCE)             */}
          {/* ========================================================= */}
          <div className="bg-white rounded-2xl border border-[#E2ECE8] p-6 shadow-xs space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-[#E2ECE8]">
              <div className="flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-[#087F5B]" />
                <h3 className="text-sm font-bold text-[#12231E]">
                  Model Evaluation Reference — Test Set Performance
                </h3>
              </div>
              <span className="text-[11px] font-mono text-[#65756F]">
                Algorithm: {model.model_name} ({model.model_version})
              </span>
            </div>

            <p className="text-xs text-[#65756F]">
              {benchmark.desc} The metrics below represent general model performance on the held-out test split of the UCI Cleveland benchmark dataset.
            </p>

            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-center">
              <div className="p-3 rounded-xl bg-[#F6FAF8] border border-[#E2ECE8]">
                <span className="text-[10px] uppercase font-bold text-[#65756F] block">Accuracy</span>
                <span className="text-sm font-extrabold text-[#12231E] mt-0.5 block">
                  {(benchmark.accuracy * 100).toFixed(2)}%
                </span>
                <span className="text-[9px] text-[#65756F]">Test split</span>
              </div>
              <div className="p-3 rounded-xl bg-[#F6FAF8] border border-[#E2ECE8]">
                <span className="text-[10px] uppercase font-bold text-[#65756F] block">Precision</span>
                <span className="text-sm font-extrabold text-[#12231E] mt-0.5 block">
                  {(benchmark.precision * 100).toFixed(2)}%
                </span>
                <span className="text-[9px] text-[#65756F]">Positive predictive</span>
              </div>
              <div className="p-3 rounded-xl bg-[#F6FAF8] border border-[#E2ECE8]">
                <span className="text-[10px] uppercase font-bold text-[#65756F] block">Recall</span>
                <span className="text-sm font-extrabold text-[#12231E] mt-0.5 block">
                  {(benchmark.recall * 100).toFixed(2)}%
                </span>
                <span className="text-[9px] text-[#65756F]">Sensitivity</span>
              </div>
              <div className="p-3 rounded-xl bg-[#F6FAF8] border border-[#E2ECE8]">
                <span className="text-[10px] uppercase font-bold text-[#65756F] block">F1-Score</span>
                <span className="text-sm font-extrabold text-[#12231E] mt-0.5 block">
                  {(benchmark.f1_score * 100).toFixed(2)}%
                </span>
                <span className="text-[9px] text-[#65756F]">Harmonic mean</span>
              </div>
              <div className="p-3 rounded-xl bg-[#F6FAF8] border border-[#E2ECE8] col-span-2 sm:col-span-1">
                <span className="text-[10px] uppercase font-bold text-[#65756F] block">ROC-AUC</span>
                <span className="text-sm font-extrabold text-[#12231E] mt-0.5 block">
                  {benchmark.roc_auc.toFixed(4)}
                </span>
                <span className="text-[9px] text-[#65756F]">Discrimination</span>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-[#F6FAF8] border border-[#E2ECE8] text-[11px] text-[#65756F] flex items-start gap-2">
              <Info className="w-4 h-4 text-[#087F5B] shrink-0 mt-0.5" />
              <span>
                <strong className="text-[#12231E]">Distinction:</strong> These benchmark evaluation metrics measure the overall historical generalization of the model on the test dataset. They are strictly separate from the individual patient probability estimate ({(result.probability * 100).toFixed(1)}%) calculated above.
              </span>
            </div>
          </div>

          {/* ========================================================= */}
          {/* CLINICAL INPUTS BREAKDOWN                                 */}
          {/* ========================================================= */}
          <div className="bg-white rounded-2xl border border-[#E2ECE8] p-6 sm:p-7 shadow-xs space-y-6">
            <div className="flex items-center gap-3 pb-3 border-b border-[#E2ECE8]">
              <div className="w-8 h-8 rounded-xl bg-[#E6F3EF] text-[#087F5B] flex items-center justify-center font-bold text-xs">
                <FileText className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-[#12231E]">
                  Submitted Clinical Attributes (13 Canonical Features)
                </h3>
                <p className="text-xs text-[#65756F]">
                  Exact values processed through the {model.model_name} pipeline.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 text-xs">
              <div className="p-3 rounded-xl bg-[#F6FAF8] border border-[#E2ECE8]">
                <span className="text-[10px] uppercase font-bold text-[#65756F] block">Age</span>
                <span className="text-sm font-extrabold text-[#12231E] mt-0.5 block">{input.age} years</span>
              </div>

              <div className="p-3 rounded-xl bg-[#F6FAF8] border border-[#E2ECE8]">
                <span className="text-[10px] uppercase font-bold text-[#65756F] block">Biological Sex</span>
                <span className="text-sm font-extrabold text-[#12231E] mt-0.5 block">
                  {input.sex === 1 ? 'Male (1)' : 'Female (0)'}
                </span>
              </div>

              <div className="p-3 rounded-xl bg-[#F6FAF8] border border-[#E2ECE8]">
                <span className="text-[10px] uppercase font-bold text-[#65756F] block">Chest Pain Type</span>
                <span className="text-sm font-extrabold text-[#12231E] mt-0.5 block truncate">
                  {chestPainLabels[input.cp] || `Code ${input.cp}`}
                </span>
              </div>

              <div className="p-3 rounded-xl bg-[#F6FAF8] border border-[#E2ECE8]">
                <span className="text-[10px] uppercase font-bold text-[#65756F] block">Resting BP</span>
                <span className="text-sm font-extrabold text-[#12231E] mt-0.5 block">{input.trestbps} mm Hg</span>
              </div>

              <div className="p-3 rounded-xl bg-[#F6FAF8] border border-[#E2ECE8]">
                <span className="text-[10px] uppercase font-bold text-[#65756F] block">Serum Cholesterol</span>
                <span className="text-sm font-extrabold text-[#12231E] mt-0.5 block">{input.chol} mg/dl</span>
              </div>

              <div className="p-3 rounded-xl bg-[#F6FAF8] border border-[#E2ECE8]">
                <span className="text-[10px] uppercase font-bold text-[#65756F] block">Fasting Blood Sugar</span>
                <span className="text-sm font-extrabold text-[#12231E] mt-0.5 block">
                  {input.fbs === 1 ? '> 120 mg/dl (1)' : '≤ 120 mg/dl (0)'}
                </span>
              </div>

              <div className="p-3 rounded-xl bg-[#F6FAF8] border border-[#E2ECE8]">
                <span className="text-[10px] uppercase font-bold text-[#65756F] block">Resting ECG</span>
                <span className="text-sm font-extrabold text-[#12231E] mt-0.5 block truncate">
                  {restecgLabels[input.restecg] || `Code ${input.restecg}`}
                </span>
              </div>

              <div className="p-3 rounded-xl bg-[#F6FAF8] border border-[#E2ECE8]">
                <span className="text-[10px] uppercase font-bold text-[#65756F] block">Max Heart Rate</span>
                <span className="text-sm font-extrabold text-[#12231E] mt-0.5 block">{input.thalach} bpm</span>
              </div>

              <div className="p-3 rounded-xl bg-[#F6FAF8] border border-[#E2ECE8]">
                <span className="text-[10px] uppercase font-bold text-[#65756F] block">Exercise Angina</span>
                <span className="text-sm font-extrabold text-[#12231E] mt-0.5 block">
                  {input.exang === 1 ? 'Yes (1)' : 'No (0)'}
                </span>
              </div>

              <div className="p-3 rounded-xl bg-[#F6FAF8] border border-[#E2ECE8]">
                <span className="text-[10px] uppercase font-bold text-[#65756F] block">ST Depression (oldpeak)</span>
                <span className="text-sm font-extrabold text-[#12231E] mt-0.5 block">{input.oldpeak.toFixed(1)} mm</span>
              </div>

              <div className="p-3 rounded-xl bg-[#F6FAF8] border border-[#E2ECE8]">
                <span className="text-[10px] uppercase font-bold text-[#65756F] block">ST Segment Slope</span>
                <span className="text-sm font-extrabold text-[#12231E] mt-0.5 block">
                  {slopeLabels[input.slope] || `Code ${input.slope}`}
                </span>
              </div>

              <div className="p-3 rounded-xl bg-[#F6FAF8] border border-[#E2ECE8]">
                <span className="text-[10px] uppercase font-bold text-[#65756F] block">Fluoroscopy Vessels</span>
                <span className="text-sm font-extrabold text-[#12231E] mt-0.5 block">
                  {input.ca} major vessel{input.ca === 1 ? '' : 's'}
                </span>
              </div>

              <div className="p-3 rounded-xl bg-[#F6FAF8] border border-[#E2ECE8] sm:col-span-2">
                <span className="text-[10px] uppercase font-bold text-[#65756F] block">Thallium Scintigraphy</span>
                <span className="text-sm font-extrabold text-[#12231E] mt-0.5 block">
                  {thalLabels[input.thal] || `Code ${input.thal}`}
                </span>
              </div>
            </div>
          </div>

          {/* ========================================================= */}
          {/* MANDATORY MEDICAL DISCLAIMER                             */}
          {/* ========================================================= */}
          <div className="p-4 rounded-xl bg-[#FEF8EC] border border-[#F4B942]/40 text-xs text-[#DE9E27] flex items-start gap-3">
            <ShieldAlert className="w-5 h-5 shrink-0 mt-0.5 text-[#DE9E27]" />
            <div className="space-y-1 text-[#12231E]">
              <span className="font-bold text-xs block">
                Educational Model Assessment Notice
              </span>
              <p className="text-[11px] text-[#65756F] leading-relaxed">
                This assessment is generated by a statistical machine learning algorithm ({model.model_name}) trained on the
                UCI Cleveland benchmark dataset. It provides an estimated statistical probability for
                educational, instructional, and research exploration only. It is{' '}
                <strong className="text-[#12231E]">not a medical diagnosis</strong> and should never
                replace formal clinical judgment, medical examinations, or consultation with a
                certified physician or cardiologist.
              </p>
            </div>
          </div>
        </div>
      </Section>
    </PageContainer>
  );
}
