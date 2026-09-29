import React from 'react';
import { ArrowRight, BarChart3, Binary, BookOpen, ClipboardEdit } from 'lucide-react';

export function HowItWorks() {
  const steps = [
    {
      num: '01',
      title: 'Enter Clinical Attributes',
      description:
        'Provide basic health information such as age, cholesterol, blood pressure, and other model inputs.',
      icon: <ClipboardEdit className="w-6 h-6 text-[#087F5B]" />,
      accentBg: 'bg-[#E6F3EF]',
      accentBorder: 'border-[#087F5B]/20',
    },
    {
      num: '02',
      title: 'AI Model Analysis',
      description:
        'The machine learning model standardizes features and executes inference with strict bounds checking.',
      icon: <Binary className="w-6 h-6 text-[#14B8A6]" />,
      accentBg: 'bg-[#E6FFFA]',
      accentBorder: 'border-[#14B8A6]/20',
    },
    {
      num: '03',
      title: 'Get Your Result',
      description:
        'Receive an educational model assessment with its calibrated probability output and stratification.',
      icon: <BarChart3 className="w-6 h-6 text-[#087F5B]" />,
      accentBg: 'bg-[#E6F3EF]',
      accentBorder: 'border-[#087F5B]/20',
    },
    {
      num: '04',
      title: 'Learn & Explore',
      description:
        'Explore model coefficients, research benchmark metrics, and educational cardiology resources.',
      icon: <BookOpen className="w-6 h-6 text-[#DE9E27]" />,
      accentBg: 'bg-[#FEF8EC]',
      accentBorder: 'border-[#F4B942]/30',
    },
  ];

  return (
    <section id="how-it-works" className="py-16 sm:py-24 bg-transparent scroll-mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-2xl mx-auto mb-16 space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#E6F3EF] border border-[#087F5B]/20 text-[11px] font-bold text-[#087F5B] uppercase tracking-wider">
            <span className="w-1.5 h-1.5 rounded-full bg-[#F4B942]" />
            <span>SIMPLE PROCESS</span>
          </div>

          <h2 className="text-3xl sm:text-4xl font-extrabold text-[#087F5B] tracking-tight">
            How It Works
          </h2>

          <p className="text-sm sm:text-base text-[#65756F] leading-relaxed">
            Get your heart health risk estimate in a few simple steps.
          </p>
        </div>

        {/* 4 Connected Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 relative">
          {steps.map((step, idx) => (
            <div
              key={step.num}
              className="relative flex flex-col bg-white rounded-2xl p-6 sm:p-7 border border-[#E2ECE8] shadow-sm hover:shadow-md hover:border-[#F4B942]/60 transition-all duration-200 group"
            >
              {/* Step number badge in prominent Warm Amber */}
              <div className="flex items-center justify-between mb-5">
                <div
                  className={`w-12 h-12 rounded-xl ${step.accentBg} ${step.accentBorder} border flex items-center justify-center`}
                >
                  {step.icon}
                </div>
                <span className="font-mono text-2xl font-black text-[#F4B942] group-hover:scale-110 transition-transform">
                  {step.num}
                </span>
              </div>

              {/* Title & Description */}
              <h3 className="text-base font-bold text-[#12231E] mb-2 group-hover:text-[#087F5B] transition-colors">
                {step.title}
              </h3>
              <p className="text-xs text-[#65756F] leading-relaxed flex-1">
                {step.description}
              </p>

              {/* Connecting arrow for desktop between cards */}
              {idx < steps.length - 1 && (
                <div
                  className="hidden lg:flex absolute -right-3 top-1/2 -translate-y-1/2 z-10 w-6 h-6 rounded-full bg-[#FEF8EC] border border-[#F4B942]/40 items-center justify-center text-[#F4B942] shadow-xs"
                  aria-hidden="true"
                >
                  <ArrowRight className="w-3.5 h-3.5" />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Educational Note */}
        <div className="mt-8 text-center">
          <p className="text-xs text-[#65756F]">
            Outputs reflect machine learning probability estimations based on benchmark datasets and
            are <strong className="text-[#12231E]">never a substitute for clinical diagnostics</strong>.
          </p>
        </div>
      </div>
    </section>
  );
}
