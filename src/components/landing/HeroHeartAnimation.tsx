import React from 'react';

const realisticHeartImg = '/realistic_heart.jpg';

export interface HeroHeartAnimationProps {
  className?: string;
  size?: number;
}

export function HeroHeartAnimation({ className = '', size = 460 }: HeroHeartAnimationProps) {
  return (
    <div
      className={`relative flex items-center justify-center select-none ${className}`}
      style={{ width: '100%', maxWidth: `${size}px`, aspectRatio: '1 / 1' }}
      aria-label="Realistic 3D anatomical heart visualization with heartbeat pulse and rotating orbital telemetry"
      role="img"
    >
      {/* 1. Ambient Background Glows in Warm Amber, Teal and Emerald */}
      <div
        className="absolute inset-2 rounded-full bg-radial from-[#F4B942]/15 via-[#14B8A6]/10 to-transparent blur-3xl pointer-events-none"
        aria-hidden="true"
      />
      <div
        className="absolute inset-8 rounded-full bg-radial from-[#087F5B]/15 via-transparent to-transparent blur-2xl pointer-events-none"
        aria-hidden="true"
      />

      {/* Subtle decorative concentric orbital arcs (matching the reference background) */}
      <svg
        className="absolute inset-0 w-full h-full pointer-events-none opacity-40"
        viewBox="0 0 500 500"
        fill="none"
        aria-hidden="true"
      >
        <circle cx="250" cy="250" r="230" stroke="#087F5B" strokeWidth="1" strokeDasharray="3 6" />
        <circle cx="250" cy="250" r="200" stroke="#F4B942" strokeWidth="1.5" strokeDasharray="14 10 30 10" opacity="0.6" />
        <circle cx="250" cy="250" r="170" stroke="#14B8A6" strokeWidth="1" strokeDasharray="6 8" opacity="0.4" />
      </svg>

      {/* 2. Floating Assembly with Natural Lub-Dub Beating Motion */}
      <div className="relative w-full h-full flex items-center justify-center animate-gentle-float">
        {/* ========================================================= */}
        {/* REALISTIC 3D ANATOMICAL HEART WITH NATURAL BEAT PULSE     */}
        {/* ========================================================= */}
        <div className="relative z-10 w-[84%] h-[84%] flex items-center justify-center">
          {/* Main Beating Container */}
          <div className="relative w-full h-full flex items-center justify-center animate-heartbeat">
            {/* The Realistic 3D Anatomical Heart with smooth organic blend */}
            <div className="relative w-full h-full rounded-full overflow-hidden shadow-2xl border border-[#087F5B]/15">
              <img
                src={realisticHeartImg}
                alt="Realistic 3D Anatomical Heart in Emerald, Teal and Amber"
                className="w-full h-full object-cover object-center scale-105"
                referrerPolicy="no-referrer"
              />
              {/* Soft radial vignette so it blends seamlessly */}
              <div
                className="absolute inset-0 rounded-full bg-radial from-transparent via-transparent to-[#F6FAF8]/25 pointer-events-none"
                aria-hidden="true"
              />
            </div>

            {/* Glowing amber vascular specular pulse overlay */}
            <div
              className="absolute inset-0 rounded-full bg-radial from-[#F4B942]/10 via-transparent to-transparent pointer-events-none animate-vascular"
              aria-hidden="true"
            />
          </div>
        </div>

        {/* ========================================================= */}
        {/* DYNAMIC 3D ORBITAL TELEMETRY RINGS (Matching Reference)   */}
        {/* ========================================================= */}

        {/* Ring 1: Clockwise Primary Amber Orbital Ring with Glowing Bead */}
        <svg
          className="absolute inset-0 w-full h-full pointer-events-none animate-orbital-1"
          viewBox="0 0 500 500"
          fill="none"
          aria-hidden="true"
        >
          <defs>
            <linearGradient id="orbit-grad-amber-1" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#F4B942" stopOpacity="0.95" />
              <stop offset="40%" stopColor="#DE9E27" stopOpacity="0.8" />
              <stop offset="75%" stopColor="#14B8A6" stopOpacity="0.5" />
              <stop offset="100%" stopColor="#087F5B" stopOpacity="0.2" />
            </linearGradient>
            <radialGradient id="satellite-amber-glow">
              <stop offset="0%" stopColor="#F4B942" stopOpacity="1" />
              <stop offset="50%" stopColor="#F4B942" stopOpacity="0.5" />
              <stop offset="100%" stopColor="#F4B942" stopOpacity="0" />
            </radialGradient>
          </defs>

          {/* Ellipse tilted at 32 degrees */}
          <g transform="rotate(32 250 250)">
            <ellipse
              cx="250"
              cy="250"
              rx="232"
              ry="110"
              stroke="url(#orbit-grad-amber-1)"
              strokeWidth="2"
              strokeDasharray="28 12 120 16 12 8"
              className="opacity-90"
            />
            {/* Glowing Amber Orbital Satellite Node */}
            <g transform="translate(482, 250)" className="animate-particle">
              <circle cx="0" cy="0" r="11" fill="url(#satellite-amber-glow)" />
              <circle cx="0" cy="0" r="5" fill="#F4B942" stroke="#FFFFFF" strokeWidth="1.5" />
              <circle cx="0" cy="0" r="8" fill="none" stroke="#F4B942" strokeWidth="1" strokeDasharray="2 2" />
            </g>
            {/* Secondary Golden bead on left orbit */}
            <g transform="translate(18, 250)">
              <circle cx="0" cy="0" r="4" fill="#F4B942" stroke="#FFFFFF" strokeWidth="1" />
            </g>
          </g>
        </svg>

        {/* Ring 2: Counter-Clockwise Teal & Amber Ring with Teal Bead */}
        <svg
          className="absolute inset-0 w-full h-full pointer-events-none animate-orbital-2"
          viewBox="0 0 500 500"
          fill="none"
          aria-hidden="true"
        >
          <defs>
            <linearGradient id="orbit-grad-teal-2" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#14B8A6" stopOpacity="0.9" />
              <stop offset="50%" stopColor="#F4B942" stopOpacity="0.7" />
              <stop offset="100%" stopColor="#087F5B" stopOpacity="0.3" />
            </linearGradient>
            <radialGradient id="satellite-teal-glow">
              <stop offset="0%" stopColor="#14B8A6" stopOpacity="1" />
              <stop offset="60%" stopColor="#14B8A6" stopOpacity="0.4" />
              <stop offset="100%" stopColor="#14B8A6" stopOpacity="0" />
            </radialGradient>
          </defs>

          {/* Ellipse tilted at -36 degrees */}
          <g transform="rotate(-36 250 250)">
            <ellipse
              cx="250"
              cy="250"
              rx="224"
              ry="98"
              stroke="url(#orbit-grad-teal-2)"
              strokeWidth="1.8"
              strokeDasharray="20 10 80 14 10 8"
              className="opacity-85"
            />
            {/* Glowing Teal/Emerald Satellite Node */}
            <g transform="translate(474, 250)" className="animate-particle">
              <circle cx="0" cy="0" r="10" fill="url(#satellite-teal-glow)" />
              <circle cx="0" cy="0" r="5" fill="#087F5B" stroke="#14B8A6" strokeWidth="1.5" />
            </g>
          </g>
        </svg>

        {/* Ring 3: Faint Golden Outer Trajectory */}
        <svg
          className="absolute inset-0 w-full h-full pointer-events-none animate-orbital-3"
          viewBox="0 0 500 500"
          fill="none"
          aria-hidden="true"
        >
          <ellipse
            cx="250"
            cy="250"
            rx="240"
            ry="125"
            stroke="#F4B942"
            strokeWidth="1.2"
            strokeDasharray="4 8 16 8"
            transform="rotate(65 250 250)"
            className="opacity-30"
          />
        </svg>

        {/* ECG Rhythm Wave Trail on Right (Matching the Reference Image) */}
        <svg
          className="absolute right-[-24px] top-1/2 -translate-y-1/2 w-32 h-16 pointer-events-none hidden sm:block"
          viewBox="0 0 120 60"
          fill="none"
          aria-hidden="true"
        >
          <path
            d="M0 30 L30 30 L36 12 L44 48 L52 4 L60 56 L68 24 L76 36 L84 30 L120 30"
            stroke="#087F5B"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="opacity-80"
          />
        </svg>
      </div>
    </div>
  );
}
