import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Activity,
  AlertCircle,
  ArrowRight,
  BarChart3,
  CheckCircle2,
  Cpu,
  HeartPulse,
  Info,
  Loader2,
  RotateCcw,
  Sparkles,
} from 'lucide-react';
import { PageContainer } from '../components/layout/PageContainer';
import { Section } from '../components/layout/Section';
import { Button } from '../components/ui/Button';
import { Alert } from '../components/ui/Alert';
import { Input } from '../components/ui/Input';
import { apiClient } from '../lib/api';
import { useAuth } from '../hooks/useAuth';
import type { ClinicalInputs, ModelInfoItem, ModelListResponse, PredictionResponse } from '../types/prediction';

// Canonical Cleveland Benchmark test case
const BENCHMARK_TEST_CASE: ClinicalInputs = {
  age: 52,
  sex: 1,
  cp: 4,
  trestbps: 138,
  chol: 246,
  fbs: 0,
  restecg: 0,
  thalach: 150,
  exang: 0,
  oldpeak: 1.2,
  slope: 2,
  ca: 0,
  thal: 3,
};

const DEFAULT_FORM: ClinicalInputs = {
  age: 50,
  sex: 1,
  cp: 4,
  trestbps: 120,
  chol: 200,
  fbs: 0,
  restecg: 0,
  thalach: 150,
  exang: 0,
  oldpeak: 0.0,
  slope: 2,
  ca: 0,
  thal: 3,
};

// Fallback catalog grounded directly in outputs/model_comparison.csv
const FALLBACK_MODELS: ModelInfoItem[] = [
  {
    id: 'logistic_regression',
    name: 'Logistic Regression',
    version: 'v1',
    description: 'Regularized linear classification model with standard scaling and calibrated probability estimation.',
    metrics: { accuracy: 0.8852, precision: 0.8387, recall: 0.9286, f1_score: 0.8814, roc_auc: 0.9665 },
    available: true,
  },
  {
    id: 'svm',
    name: 'Support Vector Machine',
    version: 'v1',
    description: 'Margin-based classifier with radial basis function kernel and calibrated probability estimation.',
    metrics: { accuracy: 0.8852, precision: 0.8387, recall: 0.9286, f1_score: 0.8814, roc_auc: 0.9643 },
    available: true,
  },
  {
    id: 'random_forest',
    name: 'Random Forest',
    version: 'v1',
    description: 'Ensemble of 300 decision trees trained with bootstrap aggregating.',
    metrics: { accuracy: 0.8689, precision: 0.8125, recall: 0.9286, f1_score: 0.8667, roc_auc: 0.9443 },
    available: true,
  },
  {
    id: 'xgboost',
    name: 'XGBoost',
    version: 'v1',
    description: 'Gradient-boosted decision trees with regularized objective optimization.',
    metrics: { accuracy: 0.9016, precision: 0.8438, recall: 0.9643, f1_score: 0.9000, roc_auc: 0.9437 },
    available: true,
  },
];

export function AssessmentPage() {
  const navigate = useNavigate();
  const { currentUser } = useAuth();

  const [models, setModels] = useState<ModelInfoItem[]>(FALLBACK_MODELS);
  const [selectedModelId, setSelectedModelId] = useState<string>('logistic_regression');
  const [form, setForm] = useState<ClinicalInputs>(DEFAULT_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [submissionStage, setSubmissionStage] = useState<'idle' | 'validating' | 'inference' | 'persisting'>('idle');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Fetch real model catalog on mount
  useEffect(() => {
    let isMounted = true;
    apiClient
      .get<ModelListResponse>('/api/v1/models', { requiresAuth: false })
      .then((res) => {
        if (isMounted && res?.models && res.models.length > 0) {
          setModels(res.models);
          if (res.default_model_id && !selectedModelId) {
            setSelectedModelId(res.default_model_id);
          }
        }
      })
      .catch((err) => {
        console.warn('Could not retrieve live models catalog, using verified baseline:', err);
      });
    return () => {
      isMounted = false;
    };
  }, []);

  const selectedModel = models.find((m) => m.id === selectedModelId) || models[0];

  const updateField = <K extends keyof ClinicalInputs>(field: K, value: ClinicalInputs[K]) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setErrorMsg(null);
  };

  const handleLoadBenchmark = () => {
    setForm(BENCHMARK_TEST_CASE);
    setErrorMsg(null);
  };

  const handleReset = () => {
    setForm(DEFAULT_FORM);
    setErrorMsg(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);

    if (!currentUser) {
      setErrorMsg('Authentication required. Please sign in to submit an assessment.');
      return;
    }

    if (form.age < 18 || form.age > 100) {
      setErrorMsg('Age must be between 18 and 100 years.');
      return;
    }
    if (form.trestbps < 80 || form.trestbps > 240) {
      setErrorMsg('Resting blood pressure must be between 80 and 240 mm Hg.');
      return;
    }
    if (form.chol < 100 || form.chol > 600) {
      setErrorMsg('Serum cholesterol must be between 100 and 600 mg/dl.');
      return;
    }
    if (form.thalach < 50 || form.thalach > 250) {
      setErrorMsg('Maximum heart rate achieved must be between 50 and 250 bpm.');
      return;
    }
    if (form.oldpeak < 0 || form.oldpeak > 8) {
      setErrorMsg('ST depression must be between 0.0 and 8.0 mm.');
      return;
    }

    if (selectedModel && selectedModel.available === false) {
      setErrorMsg(`The model '${selectedModel.name}' is currently unavailable on the server. Please select an available model.`);
      return;
    }

    try {
      setSubmitting(true);
      setSubmissionStage('validating');

      // Real API payload matching exact 13 features + explicit model_id
      const payload = {
        model_id: selectedModelId,
        age: Number(form.age),
        sex: Number(form.sex),
        cp: Number(form.cp),
        trestbps: Number(form.trestbps),
        chol: Number(form.chol),
        fbs: Number(form.fbs),
        restecg: Number(form.restecg),
        thalach: Number(form.thalach),
        exang: Number(form.exang),
        oldpeak: Number(form.oldpeak),
        slope: Number(form.slope),
        ca: Number(form.ca),
        thal: Number(form.thal),
      };

      setSubmissionStage('inference');

      // Authenticated POST /api/v1/predictions
      const response = await apiClient.post<PredictionResponse>('/api/v1/predictions', payload);

      setSubmissionStage('persisting');

      if (response && response.prediction_id) {
        navigate(`/result/${response.prediction_id}`);
      } else {
        throw new Error('Prediction response did not contain a valid record identifier.');
      }
    } catch (err: any) {
      console.error('Prediction submission error:', err);
      let msg = err?.message || 'An unexpected error occurred while executing inference.';
      if (err?.status === 401) {
        msg = 'Authentication session required or expired. Please sign in to generate and record assessments.';
      } else if (err?.status === 422) {
        msg = `Validation Error: ${err.message || 'Please check that all clinical inputs match accepted ranges.'}`;
      } else if (err?.status === 503) {
        msg = `Service Unavailable: The model pipeline for '${selectedModel?.name}' is currently offline. Please choose another model.`;
      } else if (err?.status === 500) {
        msg = `Server Error: ${err.message || 'Failed to complete prediction or save to Firestore history.'}`;
      }
      setErrorMsg(msg);
      setSubmitting(false);
      setSubmissionStage('idle');
    }
  };

  return (
    <PageContainer size="lg">
      <Section
        title="Clinical Risk Assessment"
        description="Select a machine learning classification model and provide patient clinical attributes to calculate calibrated heart disease likelihood."
        headerAction={
          <div className="flex items-center gap-2">
            <Button
              type="button"
              size="sm"
              variant="outline"
              leftIcon={<RotateCcw className="w-3.5 h-3.5" />}
              onClick={handleReset}
              disabled={submitting}
            >
              Reset Inputs
            </Button>
            <Button
              type="button"
              size="sm"
              variant="outline"
              leftIcon={<Sparkles className="w-3.5 h-3.5 text-[#DE9E27]" />}
              onClick={handleLoadBenchmark}
              disabled={submitting}
              className="border-[#F4B942]/60 hover:bg-[#FEF8EC] text-[#12231E]"
            >
              Load Benchmark Case
            </Button>
          </div>
        }
      >
        {errorMsg && (
          <div className="mb-6">
            <Alert
              variant="error"
              title="Submission Error"
              description={errorMsg}
              onClose={() => setErrorMsg(null)}
            />
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* ========================================================= */}
          {/* STEP 1: CHOOSE PREDICTION MODEL                          */}
          {/* ========================================================= */}
          <div className="bg-white rounded-2xl border border-[#E2ECE8] p-6 sm:p-7 shadow-xs space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[#E2ECE8] gap-2">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-xl bg-[#E6F3EF] text-[#087F5B] flex items-center justify-center font-bold text-xs">
                  01
                </div>
                <div>
                  <h3 className="text-sm font-bold text-[#12231E]">
                    Choose Prediction Model
                  </h3>
                  <p className="text-xs text-[#65756F]">
                    Inspect objective test-set metrics and select which fitted classifier will evaluate this patient.
                  </p>
                </div>
              </div>

              {/* Selected Model Sticky Indicator */}
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[#F6FAF8] border border-[#E2ECE8] text-xs">
                <span className="text-[#65756F]">Selected:</span>
                <span className="font-bold text-[#087F5B]">{selectedModel?.name}</span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-white border border-[#E2ECE8] text-[#12231E]">
                  {selectedModel?.version}
                </span>
              </div>
            </div>

            {/* 4 Model Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {models.map((m) => {
                const isSelected = selectedModelId === m.id;
                const isAvailable = m.available !== false;
                return (
                  <div
                    key={m.id}
                    onClick={() => !submitting && isAvailable && setSelectedModelId(m.id)}
                    className={`p-4 rounded-xl border transition-all ${
                      !isAvailable
                        ? 'opacity-60 bg-slate-50 border-slate-200 cursor-not-allowed'
                        : isSelected
                        ? 'bg-[#E6F3EF]/60 border-[#087F5B] shadow-xs ring-1 ring-[#087F5B] cursor-pointer'
                        : 'bg-white border-[#E2ECE8] hover:border-slate-300 hover:bg-slate-50/50 cursor-pointer'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div
                          className={`w-4 h-4 rounded-full border flex items-center justify-center ${
                            isSelected
                              ? 'border-[#087F5B] bg-[#087F5B]'
                              : 'border-slate-300 bg-white'
                          }`}
                        >
                          {isSelected && <div className="w-1.5 h-1.5 rounded-full bg-white" />}
                        </div>
                        <h4 className="text-sm font-bold text-[#12231E]">{m.name}</h4>
                      </div>
                      <div className="flex items-center gap-1.5">
                        {!isAvailable && (
                          <span className="text-[10px] font-semibold text-rose-700 bg-rose-50 border border-rose-200 px-1.5 py-0.5 rounded">
                            Unavailable
                          </span>
                        )}
                        <span className="text-[10px] font-mono text-[#65756F] bg-slate-100 px-1.5 py-0.5 rounded">
                          {m.version}
                        </span>
                      </div>
                    </div>

                    <p className="text-xs text-[#65756F] mb-3 leading-relaxed">
                      {m.description || 'Pre-trained supervised classifier with standardized pipeline.'}
                    </p>

                    {/* Test-Set Metric Pills (Neutral, non-ranked) */}
                    <div className="grid grid-cols-5 gap-1.5 pt-2 border-t border-[#E2ECE8] text-center">
                      <div className="bg-white/80 p-1.5 rounded border border-[#E2ECE8]">
                        <span className="text-[9px] uppercase font-bold text-[#65756F] block">Acc</span>
                        <span className="font-mono text-[11px] font-bold text-[#12231E]">
                          {(m.metrics.accuracy * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="bg-white/80 p-1.5 rounded border border-[#E2ECE8]">
                        <span className="text-[9px] uppercase font-bold text-[#65756F] block">Prec</span>
                        <span className="font-mono text-[11px] font-bold text-[#12231E]">
                          {(m.metrics.precision * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="bg-white/80 p-1.5 rounded border border-[#E2ECE8]">
                        <span className="text-[9px] uppercase font-bold text-[#65756F] block">Rec</span>
                        <span className="font-mono text-[11px] font-bold text-[#12231E]">
                          {(m.metrics.recall * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="bg-white/80 p-1.5 rounded border border-[#E2ECE8]">
                        <span className="text-[9px] uppercase font-bold text-[#65756F] block">F1</span>
                        <span className="font-mono text-[11px] font-bold text-[#12231E]">
                          {(m.metrics.f1_score * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="bg-white/80 p-1.5 rounded border border-[#E2ECE8]">
                        <span className="text-[9px] uppercase font-bold text-[#65756F] block">ROC-AUC</span>
                        <span className="font-mono text-[11px] font-bold text-[#12231E]">
                          {m.metrics.roc_auc.toFixed(4)}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Model Comparison Table */}
            <div className="pt-2">
              <div className="flex items-center gap-2 mb-2">
                <BarChart3 className="w-3.5 h-3.5 text-[#087F5B]" />
                <span className="text-xs font-bold text-[#12231E]">Model Evaluation — Test Set Comparison</span>
              </div>
              <div className="overflow-x-auto rounded-xl border border-[#E2ECE8]">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#F6FAF8] text-[#65756F] font-semibold border-b border-[#E2ECE8]">
                    <tr>
                      <th className="py-2.5 px-3">Model</th>
                      <th className="py-2.5 px-3 font-mono">Accuracy</th>
                      <th className="py-2.5 px-3 font-mono">Precision</th>
                      <th className="py-2.5 px-3 font-mono">Recall</th>
                      <th className="py-2.5 px-3 font-mono">F1-Score</th>
                      <th className="py-2.5 px-3 font-mono">ROC-AUC</th>
                      <th className="py-2.5 px-3 text-right">Select</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#E2ECE8]">
                    {models.map((m) => {
                      const isSelected = selectedModelId === m.id;
                      return (
                        <tr
                          key={m.id}
                          onClick={() => !submitting && setSelectedModelId(m.id)}
                          className={`cursor-pointer transition-colors ${
                            isSelected ? 'bg-[#E6F3EF]/40 font-semibold' : 'hover:bg-slate-50'
                          }`}
                        >
                          <td className="py-2.5 px-3 text-[#12231E] flex items-center gap-2">
                            <span>{m.name}</span>
                            <span className="text-[10px] font-mono text-[#65756F]">({m.version})</span>
                          </td>
                          <td className="py-2.5 px-3 font-mono text-[#12231E]">{(m.metrics.accuracy * 100).toFixed(2)}%</td>
                          <td className="py-2.5 px-3 font-mono text-[#12231E]">{(m.metrics.precision * 100).toFixed(2)}%</td>
                          <td className="py-2.5 px-3 font-mono text-[#12231E]">{(m.metrics.recall * 100).toFixed(2)}%</td>
                          <td className="py-2.5 px-3 font-mono text-[#12231E]">{(m.metrics.f1_score * 100).toFixed(2)}%</td>
                          <td className="py-2.5 px-3 font-mono text-[#12231E]">{m.metrics.roc_auc.toFixed(4)}</td>
                          <td className="py-2.5 px-3 text-right">
                            <input
                              type="radio"
                              name="model_selection"
                              checked={isSelected}
                              onChange={() => setSelectedModelId(m.id)}
                              className="accent-[#087F5B]"
                            />
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              <p className="text-[10px] text-[#65756F] mt-1.5">
                Note: Metrics reflect test-set evaluation on the 303-patient UCI Cleveland dataset split and are presented neutrally without automatic ranking.
              </p>
            </div>
          </div>

          {/* ========================================================= */}
          {/* STEP 2: DEMOGRAPHICS & RESTING VITALS                     */}
          {/* ========================================================= */}
          <div className="bg-white rounded-2xl border border-[#E2ECE8] p-6 sm:p-7 shadow-xs space-y-6">
            <div className="flex items-center gap-3 pb-4 border-b border-[#E2ECE8]">
              <div className="w-8 h-8 rounded-xl bg-[#E6F3EF] text-[#087F5B] flex items-center justify-center font-bold text-xs">
                02
              </div>
              <div>
                <h3 className="text-sm font-bold text-[#12231E]">
                  Patient Demographics & Resting Vitals
                </h3>
                <p className="text-xs text-[#65756F]">
                  Baseline physiological metrics measured at hospital admission.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
              {/* Age */}
              <div>
                <Input
                  id="age"
                  type="number"
                  label="Patient Age"
                  description="Years (18 – 95)"
                  min={18}
                  max={100}
                  required
                  value={form.age}
                  onChange={(e) => updateField('age', parseInt(e.target.value) || 0)}
                  disabled={submitting}
                />
              </div>

              {/* Sex */}
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-semibold text-[#12231E]">
                  Biological Sex <span className="text-rose-500">*</span>
                </label>
                <p className="text-xs text-[#65756F]">Demographic risk factor</p>
                <div className="grid grid-cols-2 gap-2 mt-auto">
                  <button
                    type="button"
                    onClick={() => updateField('sex', 0)}
                    disabled={submitting}
                    className={`py-2 px-3 rounded-xl text-xs font-semibold border transition-all ${
                      form.sex === 0
                        ? 'bg-[#E6F3EF] border-[#087F5B] text-[#087F5B] shadow-xs'
                        : 'bg-white border-[#E2ECE8] text-[#65756F] hover:bg-slate-50'
                    }`}
                  >
                    Female (0)
                  </button>
                  <button
                    type="button"
                    onClick={() => updateField('sex', 1)}
                    disabled={submitting}
                    className={`py-2 px-3 rounded-xl text-xs font-semibold border transition-all ${
                      form.sex === 1
                        ? 'bg-[#E6F3EF] border-[#087F5B] text-[#087F5B] shadow-xs'
                        : 'bg-white border-[#E2ECE8] text-[#65756F] hover:bg-slate-50'
                    }`}
                  >
                    Male (1)
                  </button>
                </div>
              </div>

              {/* Resting Blood Pressure */}
              <div>
                <Input
                  id="trestbps"
                  type="number"
                  label="Resting Blood Pressure"
                  description="mm Hg on hospital admission"
                  min={80}
                  max={240}
                  required
                  value={form.trestbps}
                  onChange={(e) => updateField('trestbps', parseInt(e.target.value) || 0)}
                  disabled={submitting}
                />
              </div>

              {/* Serum Cholesterol */}
              <div>
                <Input
                  id="chol"
                  type="number"
                  label="Serum Cholesterol"
                  description="mg/dl fast fasting state"
                  min={100}
                  max={600}
                  required
                  value={form.chol}
                  onChange={(e) => updateField('chol', parseInt(e.target.value) || 0)}
                  disabled={submitting}
                />
              </div>
            </div>
          </div>

          {/* ========================================================= */}
          {/* STEP 3: SYMPTOMS & EXERCISE STRESS TEST                   */}
          {/* ========================================================= */}
          <div className="bg-white rounded-2xl border border-[#E2ECE8] p-6 sm:p-7 shadow-xs space-y-6">
            <div className="flex items-center gap-3 pb-4 border-b border-[#E2ECE8]">
              <div className="w-8 h-8 rounded-xl bg-[#E6FFFA] text-[#14B8A6] flex items-center justify-center font-bold text-xs">
                03
              </div>
              <div>
                <h3 className="text-sm font-bold text-[#12231E]">
                  Symptoms & Exercise Stress Test
                </h3>
                <p className="text-xs text-[#65756F]">
                  Electrocardiographic and symptomatic response under treadmill exertion.
                </p>
              </div>
            </div>

            {/* Chest Pain Type (cp: 1, 2, 3, 4) */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-[#12231E] flex items-center justify-between">
                <span>
                  Chest Pain Classification (cp) <span className="text-rose-500">*</span>
                </span>
                <span className="text-[11px] font-normal text-[#65756F]">
                  Selected code: {form.cp}
                </span>
              </label>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                {[
                  { code: 1, title: 'Typical Angina', desc: 'Exertional retrosternal discomfort relieved by rest.' },
                  { code: 2, title: 'Atypical Angina', desc: 'Chest pain possessing two of three typical angina features.' },
                  { code: 3, title: 'Non-Anginal Pain', desc: 'Chest pain lacking typical exertional relationship.' },
                  { code: 4, title: 'Asymptomatic', desc: 'No subjective chest pain reported by patient.' },
                ].map((item) => (
                  <button
                    key={item.code}
                    type="button"
                    onClick={() => updateField('cp', item.code)}
                    disabled={submitting}
                    className={`p-3.5 rounded-xl border text-left transition-all ${
                      form.cp === item.code
                        ? 'bg-[#E6F3EF] border-[#087F5B] shadow-xs'
                        : 'bg-white border-[#E2ECE8] hover:bg-slate-50'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-bold text-[#12231E]">{item.title}</span>
                      <span
                        className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                          form.cp === item.code
                            ? 'bg-[#087F5B] text-white font-bold'
                            : 'bg-slate-100 text-[#65756F]'
                        }`}
                      >
                        Code {item.code}
                      </span>
                    </div>
                    <p className="text-[11px] text-[#65756F] leading-snug">{item.desc}</p>
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 pt-2">
              {/* Max Heart Rate (thalach) */}
              <div>
                <Input
                  id="thalach"
                  type="number"
                  label="Maximum Heart Rate"
                  description="Peak bpm achieved during stress"
                  min={50}
                  max={250}
                  required
                  value={form.thalach}
                  onChange={(e) => updateField('thalach', parseInt(e.target.value) || 0)}
                  disabled={submitting}
                />
              </div>

              {/* Exercise Induced Angina (exang: 0, 1) */}
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-semibold text-[#12231E]">
                  Exercise-Induced Angina (exang) <span className="text-rose-500">*</span>
                </label>
                <p className="text-xs text-[#65756F]">Angina during stress test</p>
                <div className="grid grid-cols-2 gap-2 mt-auto">
                  <button
                    type="button"
                    onClick={() => updateField('exang', 0)}
                    disabled={submitting}
                    className={`py-2 px-3 rounded-xl text-xs font-semibold border transition-all ${
                      form.exang === 0
                        ? 'bg-[#E6F3EF] border-[#087F5B] text-[#087F5B]'
                        : 'bg-white border-[#E2ECE8] text-[#65756F] hover:bg-slate-50'
                    }`}
                  >
                    No (0)
                  </button>
                  <button
                    type="button"
                    onClick={() => updateField('exang', 1)}
                    disabled={submitting}
                    className={`py-2 px-3 rounded-xl text-xs font-semibold border transition-all ${
                      form.exang === 1
                        ? 'bg-[#FEF8EC] border-[#F4B942] text-[#DE9E27]'
                        : 'bg-white border-[#E2ECE8] text-[#65756F] hover:bg-slate-50'
                    }`}
                  >
                    Yes (1)
                  </button>
                </div>
              </div>

              {/* ST Depression (oldpeak) */}
              <div>
                <Input
                  id="oldpeak"
                  type="number"
                  step="0.1"
                  label="ST Depression (oldpeak)"
                  description="mm induced by exercise relative to rest"
                  min={0.0}
                  max={8.0}
                  required
                  value={form.oldpeak}
                  onChange={(e) => updateField('oldpeak', parseFloat(e.target.value) || 0)}
                  disabled={submitting}
                />
              </div>
            </div>

            {/* Peak Exercise ST Slope (slope: 1, 2, 3) */}
            <div className="space-y-2 pt-1">
              <label className="text-xs font-semibold text-[#12231E]">
                ST Segment Slope (slope) <span className="text-rose-500">*</span>
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {[
                  { code: 1, title: 'Upsloping (1)', desc: 'Gradual upward recovery of ST segment.' },
                  { code: 2, title: 'Flat (2)', desc: 'Horizontal depression across peak exertion.' },
                  { code: 3, title: 'Downsloping (3)', desc: 'Downward deflection indicating ischemia.' },
                ].map((item) => (
                  <button
                    key={item.code}
                    type="button"
                    onClick={() => updateField('slope', item.code)}
                    disabled={submitting}
                    className={`p-3 rounded-xl border text-left transition-all ${
                      form.slope === item.code
                        ? 'bg-[#E6F3EF] border-[#087F5B] text-[#087F5B]'
                        : 'bg-white border-[#E2ECE8] text-[#65756F] hover:bg-slate-50'
                    }`}
                  >
                    <div className="font-bold text-xs text-[#12231E] mb-0.5">{item.title}</div>
                    <div className="text-[11px] text-[#65756F]">{item.desc}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* ========================================================= */}
          {/* STEP 4: METABOLIC & DIAGNOSTIC SCINTIGRAPHY               */}
          {/* ========================================================= */}
          <div className="bg-white rounded-2xl border border-[#E2ECE8] p-6 sm:p-7 shadow-xs space-y-6">
            <div className="flex items-center gap-3 pb-4 border-b border-[#E2ECE8]">
              <div className="w-8 h-8 rounded-xl bg-[#FEF8EC] text-[#DE9E27] flex items-center justify-center font-bold text-xs">
                04
              </div>
              <div>
                <h3 className="text-sm font-bold text-[#12231E]">
                  Metabolic & Diagnostic Scintigraphy
                </h3>
                <p className="text-xs text-[#65756F]">
                  Fasting blood glucose, resting ECG, fluoroscopy, and thallium scan results.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              {/* Fasting Blood Sugar (fbs: 0, 1) */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-[#12231E]">
                  Fasting Blood Sugar (fbs) <span className="text-rose-500">*</span>
                </label>
                <p className="text-xs text-[#65756F]">Threshold: &gt; 120 mg/dl</p>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => updateField('fbs', 0)}
                    disabled={submitting}
                    className={`py-2 px-3 rounded-xl text-xs font-semibold border transition-all ${
                      form.fbs === 0
                        ? 'bg-[#E6F3EF] border-[#087F5B] text-[#087F5B]'
                        : 'bg-white border-[#E2ECE8] text-[#65756F] hover:bg-slate-50'
                    }`}
                  >
                    &le; 120 mg/dl (0)
                  </button>
                  <button
                    type="button"
                    onClick={() => updateField('fbs', 1)}
                    disabled={submitting}
                    className={`py-2 px-3 rounded-xl text-xs font-semibold border transition-all ${
                      form.fbs === 1
                        ? 'bg-[#FEF8EC] border-[#F4B942] text-[#DE9E27]'
                        : 'bg-white border-[#E2ECE8] text-[#65756F] hover:bg-slate-50'
                    }`}
                  >
                    &gt; 120 mg/dl (1)
                  </button>
                </div>
              </div>

              {/* Resting ECG (restecg: 0, 1, 2) */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-[#12231E]">
                  Resting ECG (restecg) <span className="text-rose-500">*</span>
                </label>
                <p className="text-xs text-[#65756F]">Baseline cardiac electrical tracing</p>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { code: 0, label: 'Normal (0)' },
                    { code: 1, label: 'ST-T Abn (1)' },
                    { code: 2, label: 'LVH (2)' },
                  ].map((item) => (
                    <button
                      key={item.code}
                      type="button"
                      onClick={() => updateField('restecg', item.code)}
                      disabled={submitting}
                      className={`py-2 px-2 rounded-xl text-[11px] font-semibold border transition-all text-center ${
                        form.restecg === item.code
                          ? 'bg-[#E6F3EF] border-[#087F5B] text-[#087F5B]'
                          : 'bg-white border-[#E2ECE8] text-[#65756F] hover:bg-slate-50'
                      }`}
                    >
                      {item.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Number of Major Vessels Colored by Fluoroscopy (ca: 0, 1, 2, 3) */}
            <div className="space-y-2 pt-2">
              <label className="text-xs font-semibold text-[#12231E]">
                Major Vessels Colored by Fluoroscopy (ca: 0–3) <span className="text-rose-500">*</span>
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                {[0, 1, 2, 3].map((val) => (
                  <button
                    key={val}
                    type="button"
                    onClick={() => updateField('ca', val)}
                    disabled={submitting}
                    className={`py-2 px-3 rounded-xl text-xs font-semibold border text-center transition-all ${
                      form.ca === val
                        ? 'bg-[#E6F3EF] border-[#087F5B] text-[#087F5B] font-bold'
                        : 'bg-white border-[#E2ECE8] text-[#65756F] hover:bg-slate-50'
                    }`}
                  >
                    {val === 0 ? '0 Vessels' : `${val} Vessel${val > 1 ? 's' : ''}`} ({val})
                  </button>
                ))}
              </div>
            </div>

            {/* Thallium Stress Scintigraphy (thal: 3, 6, 7) */}
            <div className="space-y-2 pt-2">
              <label className="text-xs font-semibold text-[#12231E]">
                Thallium Stress Test Scintigraphy (thal: 3, 6, 7) <span className="text-rose-500">*</span>
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {[
                  { code: 3, title: 'Normal Uptake (3)', desc: 'Uniform radioactive tracer distribution across myocardium.' },
                  { code: 6, title: 'Fixed Defect (6)', desc: 'Non-reversible perfusion defect representing prior infarction.' },
                  { code: 7, title: 'Reversible Defect (7)', desc: 'Transient exercise defect that normalizes with rest.' },
                ].map((item) => (
                  <button
                    key={item.code}
                    type="button"
                    onClick={() => updateField('thal', item.code)}
                    disabled={submitting}
                    className={`p-3 rounded-xl border text-left transition-all ${
                      form.thal === item.code
                        ? 'bg-[#E6F3EF] border-[#087F5B] text-[#087F5B]'
                        : 'bg-white border-[#E2ECE8] text-[#65756F] hover:bg-slate-50'
                    }`}
                  >
                    <div className="font-bold text-xs text-[#12231E] mb-0.5">{item.title}</div>
                    <div className="text-[11px] text-[#65756F]">{item.desc}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* ========================================================= */}
          {/* SUBMISSION & EXECUTION WORKFLOW                          */}
          {/* ========================================================= */}
          <div className="bg-white rounded-2xl border border-[#E2ECE8] p-6 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-[#E6F3EF] text-[#087F5B] flex items-center justify-center shrink-0">
                <HeartPulse className="w-5 h-5 stroke-[2.2]" />
              </div>
              <div className="text-xs text-[#65756F]">
                <span className="font-bold text-[#12231E] block">
                  Executing: {selectedModel?.name} ({selectedModel?.version})
                </span>
                <span>
                  Calibrated probability estimation will be persisted to Cloud Firestore.
                </span>
              </div>
            </div>

            {/* Submission Button & Live Processing Indicator */}
            <div className="w-full sm:w-auto flex flex-col sm:flex-row items-center gap-3">
              {submitting && (
                <div className="text-xs font-mono text-[#087F5B] flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin text-[#F4B942]" />
                  <span>
                    {submissionStage === 'validating' && '01 VALIDATING INPUTS'}
                    {submissionStage === 'inference' && `02 RUNNING ${selectedModel?.name.toUpperCase()}`}
                    {submissionStage === 'persisting' && '03 PERSISTING TO FIRESTORE'}
                  </span>
                </div>
              )}

              <Button
                type="submit"
                size="lg"
                variant="amber"
                isLoading={submitting}
                disabled={submitting || selectedModel?.available === false}
                rightIcon={<ArrowRight className="w-4 h-4 text-[#12231E]" />}
                className="w-full sm:w-auto shadow-md"
              >
                Run Assessment with {selectedModel?.name}
              </Button>
            </div>
          </div>

          {/* Educational notice */}
          <div className="text-center pt-2">
            <p className="text-[11px] text-[#65756F]">
              <strong className="text-[#12231E]">Educational ML Model Notice:</strong> Output reflects statistical probability estimations based on benchmark clinical datasets and is not a medical diagnosis.
            </p>
          </div>
        </form>
      </Section>
    </PageContainer>
  );
}
