import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, HeartPulse, Mail, ShieldCheck } from 'lucide-react';

export function Footer() {
  return (
    <footer id="contact" className="w-full bg-white border-t border-[#E2ECE8] mt-auto scroll-mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-10">
          {/* Brand & mission */}
          <div className="md:col-span-2 space-y-3.5">
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-lg bg-linear-to-br from-[#087F5B] to-[#14B8A6] text-white flex items-center justify-center">
                <HeartPulse className="w-4 h-4 stroke-[2.5]" />
              </div>
              <span className="font-extrabold text-base tracking-tight text-[#087F5B]">
                HeartCare AI
              </span>
              <span className="text-[10px] text-[#65756F] font-semibold border-l border-[#E2ECE8] pl-2">
                Educational ML App
              </span>
            </div>

            <p className="text-xs text-[#65756F] leading-relaxed max-w-md">
              An educational clinical machine learning platform demonstrating rigorous schema validation,
              calibrated logistic probability estimation, and privacy-preserving cloud health data
              engineering based on the UCI Cleveland benchmark.
            </p>

            <div className="flex items-center gap-2 text-xs text-[#087F5B] font-medium pt-1">
              <ShieldCheck className="w-4 h-4 shrink-0 text-[#14B8A6]" />
              <span>Token-authorized inference & zero-trust Firestore persistence</span>
            </div>
          </div>

          {/* Platform links */}
          <div>
            <h4 className="text-xs font-bold text-[#12231E] uppercase tracking-wider mb-3">
              Navigation
            </h4>
            <ul className="space-y-2 text-xs text-[#65756F]">
              <li>
                <Link to="/" className="hover:text-[#087F5B] transition-colors">
                  Home
                </Link>
              </li>
              <li>
                <a href="#how-it-works" className="hover:text-[#087F5B] transition-colors">
                  How It Works
                </a>
              </li>
              <li>
                <Link to="/about-model" className="hover:text-[#087F5B] transition-colors">
                  About Model & Architecture
                </Link>
              </li>
              <li>
                <a href="#product-preview" className="hover:text-[#087F5B] transition-colors">
                  Features & Preview
                </a>
              </li>
              <li>
                <Link to="/assessment" className="hover:text-[#F4B942] transition-colors font-semibold">
                  Start Assessment →
                </Link>
              </li>
            </ul>
          </div>

          {/* Research & Contact */}
          <div>
            <h4 className="text-xs font-bold text-[#12231E] uppercase tracking-wider mb-3">
              Research & Contact
            </h4>
            <ul className="space-y-2 text-xs text-[#65756F]">
              <li>UCI Cleveland Dataset (303 records)</li>
              <li>scikit-learn ColumnTransformer</li>
              <li>FastAPI Microservice Engine</li>
              <li className="pt-1">
                <a
                  href="mailto:contact@heartcare-ai.org"
                  className="inline-flex items-center gap-1.5 text-xs text-[#087F5B] hover:text-[#066749] font-medium"
                >
                  <Mail className="w-3.5 h-3.5 text-[#F4B942]" />
                  <span>support@heartcare-ai.org</span>
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Mandatory medical research disclaimer */}
        <div className="pt-6 border-t border-[#E2ECE8] flex flex-col sm:flex-row items-center justify-between gap-4 text-[11px] text-[#65756F]">
          <p className="text-center sm:text-left max-w-2xl leading-relaxed">
            <strong className="text-[#12231E]">Medical Research Notice:</strong> For educational,
            demonstrational, and research purposes only. Not intended to replace clinical judgment,
            diagnosis, or treatment by qualified healthcare professionals.
          </p>
          <p className="shrink-0 font-medium">
            &copy; {new Date().getFullYear()} HeartCare AI. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
