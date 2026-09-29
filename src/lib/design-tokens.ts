/**
 * Centralized Design System Tokens for HeartCare AI / CardioPulse.
 *
 * EXACT PALETTE SPECIFICATION:
 * - Primary: Deep Emerald (#087F5B) — brand / trust / primary identity
 * - Secondary: Electric Teal (#14B8A6) — supporting health-tech / secondary interaction
 * - Accent: Warm Amber (#F4B942) — CTA / emphasis / highlights / important interactive elements
 * - Background: (#F6FAF8) — soft, clean, warm-white canvas
 * - Primary Text: (#12231E) — dark green-black rather than pure black
 * - Muted Text: (#65756F) — comfortable reading width supporting copy
 *
 * SEMANTIC COLORS (strictly separated from brand palette):
 * - Success: #10B981
 * - Warning: #F59E0B (distinct from Brand Amber #F4B942)
 * - Error: #EF4444
 * - Info: #3B82F6
 */

export const PALETTE = {
  // Brand
  primary: '#087F5B',
  primaryHover: '#066749',
  primaryActive: '#05543C',
  primaryLight: '#E6F3EF',

  secondary: '#14B8A6',
  secondaryHover: '#0D9488',
  secondaryLight: '#E6FFFA',

  accent: '#F4B942',
  accentHover: '#DE9E27',
  accentActive: '#C98B1B',
  accentLight: '#FEF8EC',

  // Neutrals
  bg: '#F6FAF8',
  cardBg: '#FFFFFF',
  text: '#12231E',
  textMuted: '#65756F',
  border: '#E2ECE8',
  borderSubtle: '#EDF4F1',

  // Semantics
  success: '#10B981',
  successLight: '#ECFDF5',
  warning: '#F59E0B',
  warningLight: '#FFFBEB',
  error: '#EF4444',
  errorLight: '#FEF2F2',
  info: '#3B82F6',
  infoLight: '#EFF6FF',
} as const;

export const TYPOGRAPHY = {
  fontSans: "'Plus Jakarta Sans', system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
  fontMono: "'JetBrains Mono', monospace",
} as const;
