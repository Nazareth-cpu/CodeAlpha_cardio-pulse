import React from 'react';
import { Hero } from '../components/landing/Hero';
import { TrustMetrics } from '../components/landing/TrustMetrics';
import { HowItWorks } from '../components/landing/HowItWorks';
import { ProductPreview } from '../components/landing/ProductPreview';
import { CTASection } from '../components/landing/CTASection';

export function LandingPage() {
  return (
    <div className="w-full">
      {/* 1. Two-Column Hero with Clean Visual, Floating Cards & Amber CTAs */}
      <Hero />

      {/* 2. Horizontal Information / Metrics Strip */}
      <TrustMetrics />

      {/* 3. Four-Step Connected Process with Amber Step Numbers and Arrows */}
      <HowItWorks />

      {/* 4. Insights & High-Fidelity Dashboard Preview Section */}
      <ProductPreview />

      {/* 5. Pre-Footer Action Banner with Botanical Accents */}
      <CTASection />
    </div>
  );
}
