import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  AlertCircle,
  ArrowRight,
  Clock,
  ExternalLink,
  HeartPulse,
  Loader2,
  PlusCircle,
  RefreshCw,
  ShieldCheck,
} from 'lucide-react';
import { PageContainer } from '../components/layout/PageContainer';
import { Section } from '../components/layout/Section';
import { Button } from '../components/ui/Button';
import { EmptyState } from '../components/feedback/EmptyState';
import { Alert } from '../components/ui/Alert';
import { apiClient } from '../lib/api';
import { formatDateTime } from '../lib/utils';
import { useAuth } from '../hooks/useAuth';
import type { PredictionHistoryResponse, PredictionSummaryItem } from '../types/prediction';

export function HistoryPage() {
  const { currentUser, loading: authLoading } = useAuth();
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [history, setHistory] = useState<PredictionSummaryItem[]>([]);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      setErrorMsg(null);
      // Real authenticated GET /api/v1/predictions
      const response = await apiClient.get<PredictionHistoryResponse>('/api/v1/predictions?limit=50');
      setHistory(response?.predictions || []);
    } catch (err: any) {
      console.error('Failed to load history:', err);
      setErrorMsg(err?.message || 'Unable to retrieve prediction history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!authLoading) {
      if (currentUser) {
        fetchHistory();
      } else {
        setLoading(false);
      }
    }
  }, [authLoading, currentUser]);

  return (
    <PageContainer size="lg">
      <Section
        title="Prediction History"
        description="Historical risk assessment records retrieved authoritatively from your isolated Cloud Firestore subcollection."
        headerAction={
          <div className="flex items-center gap-2.5">
            <Button
              size="sm"
              variant="outline"
              leftIcon={<RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />}
              onClick={fetchHistory}
              disabled={loading}
            >
              Refresh
            </Button>
            <Link to="/assessment">
              <Button size="sm" variant="amber" leftIcon={<PlusCircle className="w-3.5 h-3.5" />}>
                New Assessment
              </Button>
            </Link>
          </div>
        }
      >
        {errorMsg && (
          <div className="mb-6 space-y-3">
            <Alert
              variant="error"
              title="Unable to Retrieve History"
              description={errorMsg}
              onClose={() => setErrorMsg(null)}
            />
            <div className="flex items-center gap-2">
              <Button
                size="sm"
                variant="outline"
                leftIcon={<RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />}
                onClick={fetchHistory}
                disabled={loading}
              >
                Retry Loading History
              </Button>
              <Link to="/assessment">
                <Button size="sm" variant="amber" leftIcon={<PlusCircle className="w-3.5 h-3.5" />}>
                  Start New Assessment
                </Button>
              </Link>
            </div>
          </div>
        )}

        {loading ? (
          <div className="py-20 flex flex-col items-center justify-center text-center space-y-3">
            <Loader2 className="w-8 h-8 animate-spin text-[#087F5B]" />
            <p className="text-sm font-semibold text-[#12231E]">
              Loading historical assessment records...
            </p>
            <span className="text-xs text-[#65756F]">
              Querying users/&#123;uid&#125;/predictions
            </span>
          </div>
        ) : history.length === 0 ? (
          <EmptyState
            icon={<Clock className="w-6 h-6 stroke-[1.5] text-[#087F5B]" />}
            title="No Assessments Yet"
            description="You have not completed any cardiovascular risk evaluations yet. Run your first assessment using the 13 clinical attributes."
            actionText="Start First Assessment"
            onAction={() => window.location.assign('/assessment')}
          />
        ) : (
          <div className="bg-white rounded-2xl border border-[#E2ECE8] shadow-xs overflow-hidden">
            <div className="px-6 py-4 border-b border-[#E2ECE8] flex items-center justify-between bg-[#F6FAF8]">
              <span className="text-xs font-bold text-[#12231E]">
                {history.length} Assessment{history.length > 1 ? 's' : ''} on Record
              </span>
              <span className="inline-flex items-center gap-1.5 text-xs text-[#087F5B] font-semibold">
                <ShieldCheck className="w-3.5 h-3.5 text-[#14B8A6]" />
                <span>Isolated Firestore Tenant</span>
              </span>
            </div>

            <div className="divide-y divide-[#E2ECE8]">
              {history.map((item) => {
                const isElevated = item.prediction === 1;
                const prob = (item.probability * 100).toFixed(1);

                return (
                  <div
                    key={item.prediction_id}
                    className="p-5 sm:px-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-50/60 transition-colors"
                  >
                    <div className="space-y-1.5">
                      <div className="flex items-center gap-3">
                        <span
                          className={`w-2.5 h-2.5 rounded-full shrink-0 ${
                            isElevated ? 'bg-[#F4B942]' : 'bg-[#087F5B]'
                          }`}
                        />
                        <h4 className="text-sm font-bold text-[#12231E]">
                          {isElevated ? 'Elevated Estimated Likelihood' : 'Lower Estimated Likelihood'}
                        </h4>
                        <span className="font-mono text-xs font-black text-[#12231E] bg-[#F6FAF8] px-2 py-0.5 rounded border border-[#E2ECE8]">
                          {prob}% Prob
                        </span>
                      </div>

                      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-[#65756F]">
                        <span>{formatDateTime(item.created_at)}</span>
                        <span>•</span>
                        <span className="font-medium text-[#087F5B]">{item.model_name}</span>
                        <span>•</span>
                        <span className="font-mono text-[11px]">{item.model_version}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 shrink-0">
                      <Link to={`/result/${item.prediction_id}`}>
                        <Button
                          size="sm"
                          variant="outline"
                          rightIcon={<ArrowRight className="w-3.5 h-3.5" />}
                        >
                          View Assessment
                        </Button>
                      </Link>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </Section>
    </PageContainer>
  );
}
