import React from 'react';
import { Link } from 'react-router-dom';
import {
  Activity,
  ArrowRight,
  BarChart2,
  CheckCircle2,
  Clock,
  Database,
  FileText,
  HeartPulse,
  Layers,
  Play,
  ShieldCheck,
  TrendingDown,
  User,
} from 'lucide-react';
import { Button } from '../ui/Button';

export function ProductPreview() {
  return (
    <section id="product-preview" className="py-16 sm:py-24 bg-white/70 border-y border-[#E2ECE8] scroll-mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-10 items-center">
          {/* Left Column: Context & Action */}
          <div className="lg:col-span-5 space-y-6 text-left">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#E6FFFA] border border-[#14B8A6]/20 text-[11px] font-bold text-[#14B8A6] uppercase tracking-wider">
              <span className="w-1.5 h-1.5 rounded-full bg-[#F4B942]" />
              <span>INSIGHTS FOR A HEALTHIER TOMORROW</span>
            </div>

            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-[#087F5B] tracking-tight leading-[1.15]">
              Make Informed Decisions <br />
              <span className="text-[#F4B942]">About Your Heart Health</span>
            </h2>

            <p className="text-sm sm:text-base text-[#65756F] leading-relaxed">
              Explore how 13 non-invasive clinical attributes interact with calibrated machine
              learning models. Review real-time probability estimates, historical trends, and model
              coefficients in a clean, intuitive clinical interface.
            </p>

            <div className="space-y-3 pt-1">
              <div className="flex items-center gap-3 text-xs text-[#12231E]">
                <div className="w-5 h-5 rounded-full bg-[#E6F3EF] text-[#087F5B] flex items-center justify-center shrink-0">
                  <CheckCircle2 className="w-3.5 h-3.5 stroke-[2.5]" />
                </div>
                <span>Standardized feature normalization and continuous risk estimation</span>
              </div>
              <div className="flex items-center gap-3 text-xs text-[#12231E]">
                <div className="w-5 h-5 rounded-full bg-[#FEF8EC] text-[#DE9E27] flex items-center justify-center shrink-0">
                  <CheckCircle2 className="w-3.5 h-3.5 stroke-[2.5]" />
                </div>
                <span>User-isolated Cloud Firestore persistence with strict privacy boundaries</span>
              </div>
              <div className="flex items-center gap-3 text-xs text-[#12231E]">
                <div className="w-5 h-5 rounded-full bg-[#E6FFFA] text-[#14B8A6] flex items-center justify-center shrink-0">
                  <CheckCircle2 className="w-3.5 h-3.5 stroke-[2.5]" />
                </div>
                <span>Transparent model metadata and benchmark evaluation metrics</span>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3.5 pt-4">
              <Link to="/assessment">
                <Button
                  size="md"
                  variant="amber"
                  rightIcon={<ArrowRight className="w-4 h-4 text-[#12231E]" />}
                >
                  Start Assessment
                </Button>
              </Link>
              <Link to="/about-model">
                <Button
                  size="md"
                  variant="outline"
                  leftIcon={<Play className="w-3.5 h-3.5 text-[#087F5B]" />}
                >
                  Watch Demo
                </Button>
              </Link>
            </div>
          </div>

          {/* Right Column: High-Fidelity Dashboard Preview Card */}
          <div className="lg:col-span-7">
            <div className="relative rounded-2xl bg-white border border-[#E2ECE8] shadow-2xl overflow-hidden text-[#12231E]">
              {/* Window Header Bar */}
              <div className="bg-[#F6FAF8] border-b border-[#E2ECE8] px-4 py-3 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-slate-300" />
                  <div className="w-2.5 h-2.5 rounded-full bg-slate-300" />
                  <div className="w-2.5 h-2.5 rounded-full bg-slate-300" />
                  <span className="text-[11px] font-mono text-[#65756F] ml-2">
                    cardiopulse.app/dashboard
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-[#E6F3EF] text-[10px] font-bold text-[#087F5B]">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#087F5B] animate-pulse" />
                    LIVE MODEL v1
                  </span>
                  <div className="w-6 h-6 rounded-full bg-[#E6F3EF] text-[#087F5B] flex items-center justify-center text-[10px] font-bold">
                    DR
                  </div>
                </div>
              </div>

              {/* Dashboard Layout inside Window */}
              <div className="flex flex-col sm:flex-row min-h-[380px]">
                {/* Mini Sidebar */}
                <div className="w-full sm:w-44 bg-[#F6FAF8] border-r border-[#E2ECE8] p-3 flex sm:flex-col justify-between sm:justify-start gap-1">
                  <div className="space-y-1 w-full">
                    <div className="px-2.5 py-1.5 rounded-lg bg-[#E6F3EF] text-[#087F5B] text-xs font-bold flex items-center gap-2">
                      <Activity className="w-3.5 h-3.5" />
                      <span>Overview</span>
                    </div>
                    <div className="px-2.5 py-1.5 rounded-lg text-[#65756F] hover:bg-white text-xs font-medium flex items-center gap-2 transition-colors">
                      <HeartPulse className="w-3.5 h-3.5" />
                      <span>Assessment</span>
                    </div>
                    <div className="px-2.5 py-1.5 rounded-lg text-[#65756F] hover:bg-white text-xs font-medium flex items-center gap-2 transition-colors">
                      <Clock className="w-3.5 h-3.5" />
                      <span>History</span>
                    </div>
                    <div className="px-2.5 py-1.5 rounded-lg text-[#65756F] hover:bg-white text-xs font-medium flex items-center gap-2 transition-colors">
                      <Layers className="w-3.5 h-3.5" />
                      <span>Model Metrics</span>
                    </div>
                  </div>

                  <div className="hidden sm:block mt-auto p-2.5 rounded-xl bg-white border border-[#E2ECE8] text-[10px] space-y-1">
                    <span className="font-bold text-[#087F5B] block">Cloud Firestore</span>
                    <span className="text-[#65756F] block truncate">Isolated User DB</span>
                  </div>
                </div>

                {/* Dashboard Main Workspace */}
                <div className="flex-1 p-5 space-y-5 bg-white">
                  {/* Top Stats Cards */}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <div className="p-3.5 rounded-xl border border-[#E2ECE8] bg-[#F6FAF8]/50">
                      <span className="text-[10px] font-bold text-[#65756F] uppercase tracking-wider block">
                        Estimated Risk
                      </span>
                      <div className="flex items-baseline gap-1 mt-1">
                        <span className="text-xl font-extrabold text-[#087F5B]">24.8%</span>
                        <span className="text-[10px] font-bold text-[#14B8A6]">(Low)</span>
                      </div>
                    </div>

                    <div className="p-3.5 rounded-xl border border-[#E2ECE8] bg-[#F6FAF8]/50">
                      <span className="text-[10px] font-bold text-[#65756F] uppercase tracking-wider block">
                        Blood Pressure
                      </span>
                      <div className="flex items-baseline gap-1 mt-1">
                        <span className="text-xl font-extrabold text-[#12231E]">122</span>
                        <span className="text-[10px] text-[#65756F]">mm Hg</span>
                      </div>
                    </div>

                    <div className="p-3.5 rounded-xl border border-[#F4B942]/40 bg-[#FEF8EC]/50">
                      <span className="text-[10px] font-bold text-[#DE9E27] uppercase tracking-wider block">
                        Cholesterol
                      </span>
                      <div className="flex items-baseline gap-1 mt-1">
                        <span className="text-xl font-extrabold text-[#F4B942]">204</span>
                        <span className="text-[10px] text-[#DE9E27]">mg/dl</span>
                      </div>
                    </div>
                  </div>

                  {/* Risk Stratification Graphic & Feature Contribution */}
                  <div className="p-4 rounded-xl border border-[#E2ECE8] bg-white">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="text-xs font-bold text-[#12231E] flex items-center gap-1.5">
                        <BarChart2 className="w-3.5 h-3.5 text-[#087F5B]" />
                        <span>Clinical Risk Stratification</span>
                      </h4>
                      <span className="text-[10px] font-mono text-[#F4B942] font-bold bg-[#FEF8EC] px-2 py-0.5 rounded border border-[#F4B942]/30">
                        P = 0.248
                      </span>
                    </div>

                    {/* Calibrated Risk Bar (Emerald -> Teal -> Warm Amber) */}
                    <div className="space-y-1.5">
                      <div className="relative h-3 w-full rounded-full bg-slate-100 overflow-hidden flex">
                        <div className="h-full bg-[#087F5B] w-1/3" title="Low Risk Zone" />
                        <div className="h-full bg-[#14B8A6] w-1/3" title="Moderate Risk Zone" />
                        <div className="h-full bg-[#F4B942] w-1/3" title="Elevated Risk Zone" />
                      </div>
                      {/* Active Pointer Marker */}
                      <div className="relative w-full h-3">
                        <div
                          className="absolute -top-1 w-2.5 h-2.5 bg-[#12231E] rotate-45 rounded-[1px] border border-white"
                          style={{ left: '24.8%' }}
                        />
                      </div>
                      <div className="flex justify-between text-[10px] text-[#65756F] font-mono">
                        <span>0.0 (Low)</span>
                        <span className="text-[#14B8A6] font-semibold">0.5 (Threshold)</span>
                        <span className="text-[#F4B942] font-semibold">1.0 (High)</span>
                      </div>
                    </div>
                  </div>

                  {/* Recent Predictions List Snippet */}
                  <div className="space-y-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-[#65756F]">
                      Recent Patient Assessments
                    </span>
                    <div className="space-y-1.5 text-xs">
                      <div className="p-2.5 rounded-lg border border-[#E2ECE8] bg-[#F6FAF8] flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="w-2 h-2 rounded-full bg-[#087F5B]" />
                          <span className="font-semibold text-[#12231E]">Subject #303</span>
                          <span className="text-[11px] text-[#65756F] hidden sm:inline">
                            · Age 54 · Male · Asymptomatic
                          </span>
                        </div>
                        <span className="font-mono text-xs font-bold text-[#087F5B] bg-[#E6F3EF] px-2 py-0.5 rounded">
                          0.18 Prob
                        </span>
                      </div>

                      <div className="p-2.5 rounded-lg border border-[#F4B942]/30 bg-[#FEF8EC]/40 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="w-2 h-2 rounded-full bg-[#F4B942]" />
                          <span className="font-semibold text-[#12231E]">Subject #302</span>
                          <span className="text-[11px] text-[#65756F] hidden sm:inline">
                            · Age 67 · Female · Typical Angina
                          </span>
                        </div>
                        <span className="font-mono text-xs font-bold text-[#DE9E27] bg-[#FEF8EC] px-2 py-0.5 rounded border border-[#F4B942]/30">
                          0.64 Prob
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
