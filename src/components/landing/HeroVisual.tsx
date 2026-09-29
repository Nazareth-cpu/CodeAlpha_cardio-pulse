import React from 'react';
import {
  BarChart2,
  GraduationCap,
  Info,
  Lock,
  Shield,
  TrendingUp,
} from 'lucide-react';
import { HeroHeartAnimation } from './HeroHeartAnimation';

export function HeroVisual() {
  return (
    <div className="relative w-full max-w-lg mx-auto lg:max-w-none flex items-center justify-center">
      {/* Decorative Warm Amber and Teal background ambient glow */}
      <div
        className="absolute -inset-4 bg-radial from-[#F4B942]/15 via-[#14B8A6]/10 to-transparent rounded-full blur-3xl pointer-events-none"
        aria-hidden="true"
      />

      {/* Main Container hosting the Realistic Animated Heart & Orbital Telemetry */}
      <div className="relative w-[340px] h-[340px] sm:w-[440px] sm:h-[440px] rounded-full bg-linear-to-b from-[#E6F3EF]/60 via-white/80 to-[#E6FFFA]/60 p-2 sm:p-4 border border-[#087F5B]/15 shadow-xl backdrop-blur-xs flex items-center justify-center overflow-visible">
        {/* Realistic 3D Anatomical Heart with Natural Beating Pulse & Orbiting Rings */}
        <HeroHeartAnimation size={440} className="w-full h-full" />
      </div>

      {/* Floating Card: "Your Health, Our Technology" (Bottom Left, matching reference image) */}
      <div className="absolute -bottom-6 -left-2 sm:-left-6 z-20 bg-white/95 backdrop-blur-md rounded-2xl p-4 sm:p-5 border border-[#087F5B]/15 shadow-xl max-w-[250px] sm:max-w-[280px]">
        <div className="flex items-center gap-2.5 mb-3">
          <div className="w-7 h-7 rounded-lg bg-[#087F5B] text-white flex items-center justify-center shrink-0 shadow-xs">
            <Shield className="w-4 h-4 stroke-[2.4]" />
          </div>
          <h4 className="text-xs sm:text-sm font-bold text-[#087F5B] tracking-tight">
            Your Health, Our Technology
          </h4>
        </div>
        <ul className="space-y-2 text-xs text-[#12231E]">
          <li className="flex items-center gap-2.5">
            <BarChart2 className="w-4 h-4 text-[#14B8A6] shrink-0 stroke-[2.4]" />
            <span className="font-medium">Evidence-based model</span>
          </li>
          <li className="flex items-center gap-2.5">
            <Lock className="w-4 h-4 text-[#087F5B] shrink-0 stroke-[2.4]" />
            <span className="font-medium">Secure and private</span>
          </li>
          <li className="flex items-center gap-2.5">
            <GraduationCap className="w-4 h-4 text-[#DE9E27] shrink-0 stroke-[2.4]" />
            <span className="font-medium">Designed for learning</span>
          </li>
          <li className="flex items-center gap-2.5 pt-1.5 border-t border-slate-100 text-[11px] text-[#65756F]">
            <Info className="w-3.5 h-3.5 text-[#DE9E27] shrink-0 stroke-[2.2]" />
            <span>Not a medical diagnosis</span>
          </li>
        </ul>
      </div>

      {/* Floating Badge: "ANALYZE / Clinical Attributes" (Top Right, matching reference image) */}
      <div className="absolute -top-3 -right-2 sm:-right-4 z-20 bg-linear-to-r from-[#F4B942] to-[#E5A82D] text-[#12231E] rounded-2xl px-4 py-3 shadow-lg border border-[#DE9E27]/50 flex items-center gap-3">
        <div className="w-8 h-8 rounded-xl bg-[#033827] text-[#F4B942] flex items-center justify-center shrink-0 shadow-xs">
          <TrendingUp className="w-4.5 h-4.5 stroke-[2.5]" />
        </div>
        <div className="flex flex-col text-left">
          <span className="text-[10px] font-bold uppercase tracking-wider text-[#12231E]/80 leading-none mb-0.5">
            ANALYZE
          </span>
          <span className="text-xs sm:text-sm font-black tracking-tight leading-tight text-[#12231E]">
            Clinical Attributes
          </span>
        </div>
      </div>
    </div>
  );
}
