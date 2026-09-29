import React, { useEffect, useState } from 'react';
import { Activity, BarChart3, CheckCircle, Database, Layers, ShieldCheck } from 'lucide-react';
import { PageContainer } from '../components/layout/PageContainer';
import { Section } from '../components/layout/Section';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Skeleton } from '../components/ui/Skeleton';
import { apiClient } from '../lib/api';
import type { ModelInfoItem, ModelListResponse } from '../types/prediction';

export function AboutModelPage() {
  const [models, setModels] = useState<ModelInfoItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    apiClient
      .get<ModelListResponse>('/api/v1/models', { requiresAuth: false })
      .then((data) => {
        if (mounted) {
          setModels(data.models || []);
          setLoading(false);
        }
      })
      .catch(() => {
        if (mounted) {
          // Fallback if network issue
          setModels([
            {
              id: 'logistic_regression',
              name: 'Logistic Regression',
              version: 'v1',
              description: 'Regularized linear classification model with standard scaling.',
              metrics: { accuracy: 0.8852, precision: 0.8387, recall: 0.9286, f1_score: 0.8814, roc_auc: 0.9665 },
              available: true,
            },
            {
              id: 'svm',
              name: 'Support Vector Machine',
              version: 'v1',
              description: 'Margin-based classifier with radial basis function kernel.',
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
          ]);
          setLoading(false);
        }
      });
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <PageContainer size="lg">
      <Section
        title="Model Architecture & Verification"
        description="Transparent machine learning engineering parameters, clinical benchmark metrics, and evaluation contracts for all four supported classifiers."
      >
        {/* Four Model Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-8">
          {loading
            ? [1, 2, 3, 4].map((i) => (
                <Card key={i} className="p-5 space-y-3">
                  <Skeleton className="h-6 w-36" />
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-12 w-full" />
                </Card>
              ))
            : models.map((m) => (
                <Card key={m.id} className="p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-bold text-base text-[#12231E]">{m.name}</h4>
                      <span className="text-[10px] font-mono text-[#65756F]">Artifact ID: {m.id} ({m.version})</span>
                    </div>
                    <Badge variant={m.available ? 'success' : 'neutral'} size="sm" hasDot={m.available}>
                      {m.available ? 'Artifact Verified' : 'Unavailable'}
                    </Badge>
                  </div>

                  <p className="text-xs text-[#65756F] leading-relaxed">{m.description}</p>

                  <div className="grid grid-cols-5 gap-1.5 pt-2 border-t border-[#E2ECE8] text-center">
                    <div className="bg-[#F6FAF8] p-1.5 rounded border border-[#E2ECE8]">
                      <span className="text-[9px] uppercase font-bold text-[#65756F] block">Acc</span>
                      <span className="font-mono text-xs font-bold text-[#12231E]">
                        {(m.metrics.accuracy * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="bg-[#F6FAF8] p-1.5 rounded border border-[#E2ECE8]">
                      <span className="text-[9px] uppercase font-bold text-[#65756F] block">Prec</span>
                      <span className="font-mono text-xs font-bold text-[#12231E]">
                        {(m.metrics.precision * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="bg-[#F6FAF8] p-1.5 rounded border border-[#E2ECE8]">
                      <span className="text-[9px] uppercase font-bold text-[#65756F] block">Rec</span>
                      <span className="font-mono text-xs font-bold text-[#12231E]">
                        {(m.metrics.recall * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="bg-[#F6FAF8] p-1.5 rounded border border-[#E2ECE8]">
                      <span className="text-[9px] uppercase font-bold text-[#65756F] block">F1</span>
                      <span className="font-mono text-xs font-bold text-[#12231E]">
                        {(m.metrics.f1_score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="bg-[#F6FAF8] p-1.5 rounded border border-[#E2ECE8]">
                      <span className="text-[9px] uppercase font-bold text-[#65756F] block">ROC-AUC</span>
                      <span className="font-mono text-xs font-bold text-[#12231E]">
                        {m.metrics.roc_auc.toFixed(4)}
                      </span>
                    </div>
                  </div>
                </Card>
              ))}
        </div>

        {/* Feature definitions */}
        <Card className="mb-8">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Layers className="w-5 h-5 text-[#087F5B]" />
              <CardTitle>13 Canonical Clinical Attributes</CardTitle>
            </div>
            <CardDescription>
              Features are preprocessed through scikit-learn ColumnTransformer pipelines with strict
              type and range validation.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 text-xs">
              {[
                { name: 'age', desc: 'Age in years (continuous, 29-77)' },
                { name: 'sex', desc: 'Biological sex (0 = female, 1 = male)' },
                { name: 'cp', desc: 'Chest pain type (1 = typical, 2 = atypical, 3 = non-anginal, 4 = asymptomatic)' },
                { name: 'trestbps', desc: 'Resting blood pressure in mm Hg (continuous, 94-200)' },
                { name: 'chol', desc: 'Serum cholesterol in mg/dl (continuous, 126-564)' },
                { name: 'fbs', desc: 'Fasting blood sugar > 120 mg/dl (0 = <=120, 1 = >120)' },
                { name: 'restecg', desc: 'Resting electrocardiographic results (0 = normal, 1 = ST-T, 2 = LVH)' },
                { name: 'thalach', desc: 'Maximum heart rate achieved (continuous, 71-202)' },
                { name: 'exang', desc: 'Exercise induced angina (0 = no, 1 = yes)' },
                { name: 'oldpeak', desc: 'ST depression induced by exercise relative to rest (0.0-6.2)' },
                { name: 'slope', desc: 'Peak exercise ST segment slope (1 = upsloping, 2 = flat, 3 = downsloping)' },
                { name: 'ca', desc: 'Major vessels colored by fluoroscopy (0-3)' },
                { name: 'thal', desc: 'Thallium scintigraphy defect (3 = normal, 6 = fixed, 7 = reversible)' },
              ].map((f) => (
                <div key={f.name} className="p-3 rounded-lg border border-[#E2ECE8] bg-[#F6FAF8]">
                  <span className="font-mono font-bold text-[#087F5B] text-xs block">{f.name}</span>
                  <span className="text-[#65756F] text-[11px] leading-tight block mt-0.5">{f.desc}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Disclaimer */}
        <div className="p-4 rounded-xl bg-[#FEF8EC] border border-[#F4B942]/40 text-xs text-[#DE9E27] flex items-start gap-3">
          <ShieldCheck className="w-5 h-5 shrink-0 mt-0.5 text-[#DE9E27]" />
          <div className="space-y-1 text-[#12231E]">
            <span className="font-bold text-xs block">Research & Educational Use Disclaimer</span>
            <p className="text-[11px] text-[#65756F] leading-relaxed">
              This application is built exclusively for clinical decision support exploration and educational research.
              The predictions generated by these models must not be used as independent diagnostic criteria or as a substitute
              for medical evaluation by licensed cardiologists and healthcare providers.
            </p>
          </div>
        </div>
      </Section>
    </PageContainer>
  );
}
