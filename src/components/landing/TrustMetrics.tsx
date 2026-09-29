import React from 'react';
import { Activity, Award, GraduationCap, Lock, ShieldCheck } from 'lucide-react';

export function TrustMetrics() {
  const metrics = [
    {
      value: '300+',
      label: 'Benchmark Records',
      description: 'UCI Cleveland clinical cohort',
      icon: <Activity className="w-5 h-5 text-[#087F5B]" />,
      valueColor: 'text-[#087F5B]',
    },
    {
      value: '13',
      label: 'Clinical Attributes',
      description: 'Zero target leakage schema',
      icon: <ShieldCheck className="w-5 h-5 text-[#14B8A6]" />,
      valueColor: 'text-[#F4B942]',
    },
    {
      value: '100%',
      label: 'Data Privacy',
      description: 'Token-scoped cloud Firestore',
      icon: <Lock className="w-5 h-5 text-[#087F5B]" />,
      valueColor: 'text-[#087F5B]',
    },
    {
      value: 'Educational',
      label: 'Research Architecture',
      description: 'For students, learners & researchers',
      icon: <GraduationCap className="w-5 h-5 text-[#DE9E27]" />,
      valueColor: 'text-[#F4B942]',
    },
  ];

  return (
    <section className="relative -mt-4 mb-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="bg-white rounded-2xl border border-[#E2ECE8] shadow-sm p-6 sm:p-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-0">
          {metrics.map((item, idx) => (
            <div
              key={item.label}
              className={`flex items-center gap-4 ${
                idx !== 0 ? 'lg:border-l lg:border-[#F4B942]/30 lg:pl-8' : ''
              } ${idx !== metrics.length - 1 ? 'lg:pr-8' : ''}`}
            >
              <div className="w-12 h-12 rounded-xl bg-[#F6FAF8] border border-[#E2ECE8] flex items-center justify-center shrink-0">
                {item.icon}
              </div>
              <div className="flex flex-col">
                <span
                  className={`text-2xl sm:text-3xl font-extrabold tracking-tight ${item.valueColor}`}
                >
                  {item.value}
                </span>
                <span className="text-xs font-bold text-[#12231E] leading-tight">
                  {item.label}
                </span>
                <span className="text-[11px] text-[#65756F] leading-tight mt-0.5">
                  {item.description}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
