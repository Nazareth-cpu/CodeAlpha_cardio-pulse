import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, BookOpen, Database, Lock, Play, ShieldAlert } from 'lucide-react';
import { Button } from '../ui/Button';
import { HeroVisual } from './HeroVisual';

export function Hero() {
  return (
    <section className="relative pt-8 pb-16 sm:pt-12 sm:pb-24 overflow-hidden">
      {/* Subtle organic background gradient accents */}
      <div
        className="absolute top-0 right-1/4 w-96 h-96 bg-radial from-[#14B8A6]/10 to-transparent rounded-full blur-3xl pointer-events-none"
        aria-hidden="true"
      />
      <div
        className="absolute top-20 left-10 w-72 h-72 bg-radial from-[#F4B942]/10 to-transparent rounded-full blur-3xl pointer-events-none"
        aria-hidden="true"
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
          {/* Left Column: Copy & Actions */}
          <div className="lg:col-span-7 flex flex-col items-start text-left space-y-6">
            {/* Eyebrow */}
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#E6F3EF] border border-[#087F5B]/20 text-[11px] font-bold text-[#087F5B] uppercase tracking-wider">
              <span>AI POWERED</span>
              <span className="text-[#F4B942] font-black">•</span>
              <span>EDUCATIONAL</span>
              <span className="text-[#F4B942] font-black">•</span>
              <span className="text-[#14B8A6]">EVIDENCE-BASED</span>
            </div>

            {/* Headline with Deep Emerald and Warm Amber Highlight */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-[#087F5B] tracking-tight leading-[1.12]">
              Understand Your <br />
              <span className="text-[#F4B942] drop-shadow-xs">Heart Health</span> with AI
            </h1>

            {/* Subheading */}
            <p className="text-base sm:text-lg text-[#65756F] leading-relaxed max-w-xl">
              An educational tool that uses machine learning to estimate heart disease risk based on
              clinical attributes.{' '}
              <strong className="text-[#12231E] font-semibold">Not a medical diagnosis.</strong>
            </p>

            {/* CTA Row */}
            <div className="flex flex-wrap items-center gap-4 pt-2 w-full sm:w-auto">
              <Link to="/assessment" className="w-full sm:w-auto">
                <Button
                  size="lg"
                  variant="amber"
                  rightIcon={<ArrowRight className="w-4 h-4 text-[#12231E]" />}
                  className="w-full sm:w-auto shadow-md"
                >
                  Start Assessment
                </Button>
              </Link>

              <a href="#how-it-works" className="w-full sm:w-auto">
                <Button
                  size="lg"
                  variant="outline"
                  leftIcon={<Play className="w-4 h-4 text-[#087F5B] fill-[#087F5B]/20" />}
                  className="w-full sm:w-auto"
                >
                  Learn More
                </Button>
              </a>
            </div>

            {/* Trust / Value Indicators */}
            <div className="pt-6 border-t border-[#E2ECE8] grid grid-cols-1 sm:grid-cols-3 gap-4 w-full">
              {/* Indicator 1 */}
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-[#E6F3EF] text-[#087F5B] flex items-center justify-center shrink-0 border border-[#087F5B]/20">
                  <ShieldAlert className="w-4 h-4 stroke-[2.2]" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-[#12231E] leading-snug">
                    Educational <br />
                    <span className="text-[#65756F] font-normal">Purpose Only</span>
                  </h4>
                </div>
              </div>

              {/* Indicator 2 */}
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-[#E6FFFA] text-[#14B8A6] flex items-center justify-center shrink-0 border border-[#14B8A6]/20">
                  <Lock className="w-4 h-4 stroke-[2.2]" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-[#12231E] leading-snug">
                    Your Data <br />
                    <span className="text-[#65756F] font-normal">Stays Private</span>
                  </h4>
                </div>
              </div>

              {/* Indicator 3 */}
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-[#FEF8EC] text-[#DE9E27] flex items-center justify-center shrink-0 border border-[#F4B942]/30">
                  <Database className="w-4 h-4 stroke-[2.2]" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-[#12231E] leading-snug">
                    Built on Trusted <br />
                    <span className="text-[#65756F] font-normal">ML Models</span>
                  </h4>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: Hero Visual Graphic */}
          <div className="lg:col-span-5 flex justify-center lg:justify-end">
            <HeroVisual />
          </div>
        </div>
      </div>
    </section>
  );
}
