import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, BookOpen, HeartPulse, Sparkles } from 'lucide-react';
import { Button } from '../ui/Button';

export function CTASection() {
  return (
    <section className="py-16 sm:py-24 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="relative rounded-3xl bg-linear-to-br from-[#087F5B] via-[#066749] to-[#05543c] p-8 sm:p-14 text-white overflow-hidden shadow-2xl">
        {/* Decorative Amber glow and botanical leaves SVG */}
        <div
          className="absolute -top-24 -right-24 w-96 h-96 bg-[#F4B942]/15 rounded-full blur-3xl pointer-events-none"
          aria-hidden="true"
        />
        <svg
          className="absolute -bottom-10 -right-10 w-80 h-80 opacity-15 pointer-events-none"
          viewBox="0 0 300 300"
          fill="none"
          aria-hidden="true"
        >
          <path
            d="M50 250 C100 200 180 200 250 120 C230 70 170 80 120 130 C70 180 40 220 50 250 Z"
            fill="#F4B942"
          />
          <path
            d="M120 280 C160 230 220 230 280 180 C260 140 220 150 180 190 Z"
            fill="#14B8A6"
          />
        </svg>

        <div className="relative z-10 max-w-3xl mx-auto text-center space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 border border-white/20 text-xs font-semibold text-[#F4B942]">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Interactive Educational Platform</span>
          </div>

          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white leading-tight">
            Ready to Explore Heart Health <br />
            <span className="text-[#F4B942]">Risk Assessment?</span>
          </h2>

          <p className="text-sm sm:text-base text-white/85 max-w-xl mx-auto leading-relaxed">
            Experience the interactive machine learning model with real clinical features in seconds.
            Understand how predictive algorithms calibrate risk without compromising personal data.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 pt-3">
            <Link to="/assessment">
              <Button
                size="lg"
                variant="amber"
                rightIcon={<ArrowRight className="w-4 h-4 text-[#12231E]" />}
                className="shadow-lg hover:scale-105"
              >
                Start Assessment Now
              </Button>
            </Link>

            <Link to="/about-model">
              <Button
                size="lg"
                variant="outline"
                leftIcon={<BookOpen className="w-4 h-4 text-white" />}
                className="bg-white/10 border-white/30 text-white hover:bg-white/20 hover:border-white focus-visible:ring-white"
              >
                Explore Model Architecture
              </Button>
            </Link>
          </div>

          <p className="text-[11px] text-white/70 pt-2">
            No credit card or setup required · Instant private browser session · Open educational research
          </p>
        </div>
      </div>
    </section>
  );
}
