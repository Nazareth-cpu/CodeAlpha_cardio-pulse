import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Activity,
  ArrowRight,
  Clock,
  Cpu,
  FileText,
  HeartPulse,
  PlusCircle,
  ShieldCheck,
  TrendingUp,
} from 'lucide-react';
import { PageContainer } from '../components/layout/PageContainer';
import { Section } from '../components/layout/Section';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { useAuth } from '../hooks/useAuth';
import { apiClient } from '../lib/api';
import { formatDateTime } from '../lib/utils';
import type { PredictionHistoryResponse, PredictionSummaryItem } from '../types/prediction';

export function DashboardPage() {
  const { currentUser } = useAuth();
  const [recentAssessments, setRecentAssessments] = useState<PredictionSummaryItem[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  useEffect(() => {
    async function loadRecent() {
      try {
        setLoadingHistory(true);
        const res = await apiClient.get<PredictionHistoryResponse>('/api/v1/predictions?limit=3');
        setRecentAssessments(res?.predictions || []);
      } catch (err) {
        // Quiet fallback on initial load if not yet populated
      } finally {
        setLoadingHistory(false);
      }
    }

    if (currentUser) {
      loadRecent();
    }
  }, [currentUser]);

  return (
    <PageContainer size="lg">
      <Section
        title="Clinical Intelligence Dashboard"
        description="Authenticated workspace for real-time risk stratification and patient prediction history."
        headerAction={
          <Link to="/assessment">
            <Button size="sm" variant="amber" leftIcon={<PlusCircle className="w-4 h-4" />}>
              New Assessment
            </Button>
          </Link>
        }
      >
        {/* Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <span className="text-xs font-semibold text-[#65756F]">Active Session</span>
              <CardTitle className="text-lg text-[#087F5B]">Verified Clinician</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-[#65756F] truncate">{currentUser?.email}</p>
              <Badge variant="success" size="sm" hasDot className="mt-2">
                Firebase Token Active
              </Badge>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <span className="text-xs font-semibold text-[#65756F]">Model Catalog</span>
              <CardTitle className="text-lg">4 Supervised Models</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-[#65756F]">Logistic Regression, SVM, RF, XGBoost</p>
              <Badge variant="default" size="sm" className="mt-2">
                User-Selectable Pipeline
              </Badge>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <span className="text-xs font-semibold text-[#65756F]">Persistence Scoping</span>
              <CardTitle className="text-lg">Cloud Firestore</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-[#65756F] font-mono text-[11px] truncate">
                users/{currentUser?.uid?.substring(0, 10)}.../predictions
              </p>
              <Badge variant="info" size="sm" className="mt-2">
                Subcollection Isolated
              </Badge>
            </CardContent>
          </Card>
        </div>

        {/* Action Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <Card variant="bordered" className="p-6 flex flex-col justify-between">
            <div className="space-y-2 mb-4">
              <div className="w-8 h-8 rounded-lg bg-[#E6F3EF] text-[#087F5B] flex items-center justify-center">
                <Activity className="w-4 h-4" />
              </div>
              <h4 className="font-bold text-base text-[#12231E]">Risk Assessment Engine</h4>
              <p className="text-xs text-[#65756F] leading-relaxed">
                Input 13 canonical clinical attributes to execute ML risk inference with immediate
                authoritative persistence in Cloud Firestore.
              </p>
            </div>
            <Link to="/assessment">
              <Button size="sm" variant="amber" rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
                Launch Assessment Workflow
              </Button>
            </Link>
          </Card>

          <Card variant="bordered" className="p-6 flex flex-col justify-between">
            <div className="space-y-2 mb-4">
              <div className="w-8 h-8 rounded-lg bg-[#E6FFFA] text-[#14B8A6] flex items-center justify-center">
                <Clock className="w-4 h-4" />
              </div>
              <h4 className="font-bold text-base text-[#12231E]">Assessment History</h4>
              <p className="text-xs text-[#65756F] leading-relaxed">
                Query paginated historical predictions, review probabilistic risk trends, and inspect
                stored records securely.
              </p>
            </div>
            <Link to="/history">
              <Button size="sm" variant="outline" rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
                View Prediction Records
              </Button>
            </Link>
          </Card>
        </div>

        {/* Recent Assessments Section */}
        {recentAssessments.length > 0 && (
          <div className="bg-white rounded-2xl border border-[#E2ECE8] p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-[#E2ECE8]">
              <div className="flex items-center gap-2">
                <HeartPulse className="w-4 h-4 text-[#087F5B]" />
                <h3 className="text-sm font-bold text-[#12231E]">Recent Assessments</h3>
              </div>
              <Link to="/history" className="text-xs text-[#087F5B] hover:underline font-semibold">
                View All →
              </Link>
            </div>

            <div className="divide-y divide-[#E2ECE8]">
              {recentAssessments.map((item) => (
                <div key={item.prediction_id} className="py-3 flex items-center justify-between text-xs">
                  <div className="space-y-0.5">
                    <span className="font-bold text-[#12231E] block">
                      {item.prediction === 1 ? 'Elevated Estimated Likelihood' : 'Lower Estimated Likelihood'}
                    </span>
                    <span className="text-[#65756F] text-[11px]">
                      {formatDateTime(item.created_at)} · {item.model_name}
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="font-mono font-bold text-[#12231E]">
                      {(item.probability * 100).toFixed(1)}% Prob
                    </span>
                    <Link to={`/result/${item.prediction_id}`}>
                      <Button size="sm" variant="outline">
                        View
                      </Button>
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </Section>
    </PageContainer>
  );
}
