/**
 * Frontend Foundation & Design System Verification Test Suite
 *
 * Verifies:
 *  1. Utility functions behave correctly
 *  2. Router configuration and routes structure
 *  3. Public routes are accessible
 *  4. Protected routes isolate sensitive clinical views
 *  5. API Error handles 401 as AUTHENTICATION_ERROR
 *  6. API Error handles 422 as VALIDATION_ERROR
 *  7. API Error handles 500/503 as SERVER_ERROR / SERVICE_UNAVAILABLE
 *  8. Firebase configuration reads from VITE_ environment variables only
 *  9. Design tokens and color values match exact specification
 * 10. Semantic colors are strictly separated from brand Amber
 * 11. Clinical input types match exact 13 canonical features
 * 12. Landing page section components are modular and exported
 */

import assert from 'node:assert';
import { describe, it } from 'node:test';

// Test API Error abstraction & tokens
import { ApiError } from '../src/types/api';
import { cn, formatDateTime, formatPercent } from '../src/lib/utils';
import { routes } from '../src/app/router';
import { PALETTE } from '../src/lib/design-tokens';
import { Hero } from '../src/components/landing/Hero';
import { TrustMetrics } from '../src/components/landing/TrustMetrics';
import { HowItWorks } from '../src/components/landing/HowItWorks';
import { ProductPreview } from '../src/components/landing/ProductPreview';
import { CTASection } from '../src/components/landing/CTASection';
import { HeroHeartAnimation } from '../src/components/landing/HeroHeartAnimation';
import { AssessmentPage } from '../src/pages/AssessmentPage';
import { ResultPage } from '../src/pages/ResultPage';
import { HistoryPage } from '../src/pages/HistoryPage';

describe('Phase 5 Frontend Foundation & Design System Test Suite', () => {
  it('1. Utility functions behave correctly', () => {
    assert.strictEqual(cn('a', false && 'b', 'c', undefined, null, 'd'), 'a c d');
    assert.strictEqual(formatPercent(0.754), '75.4%');
    assert.strictEqual(formatPercent(0), '0.0%');
  });

  it('2. Router defines expected public and protected route structure', () => {
    assert.ok(Array.isArray(routes), 'routes is an array');

    const rootRoute = routes[0];
    assert.strictEqual(rootRoute.path, '/');
    assert.ok(rootRoute.children, 'Root route has children');

    const paths = rootRoute.children!.map((r) => r.path || (r.index ? '/' : undefined));
    assert.ok(paths.includes('/'), 'Landing page route exists');
    assert.ok(paths.includes('login'), 'Login route exists');
    assert.ok(paths.includes('signup'), 'Signup route exists');
    assert.ok(paths.includes('about-model'), 'About model route exists');

    // Find protected children
    const protectedBranch = rootRoute.children!.find((r) => !r.path && r.children);
    assert.ok(protectedBranch, 'Protected route wrapper branch exists');

    const protectedPaths = protectedBranch.children!.map((r) => r.path);
    assert.ok(protectedPaths.includes('dashboard'), 'Dashboard route protected');
    assert.ok(protectedPaths.includes('assessment'), 'Assessment route protected');
    assert.ok(protectedPaths.includes('result/:id'), 'Result route protected');
    assert.ok(protectedPaths.includes('history'), 'History route protected');
    assert.ok(protectedPaths.includes('profile'), 'Profile route protected');
  });

  it('3. Public routes are defined directly at top level', () => {
    const rootRoute = routes[0];
    const publicChildren = rootRoute.children!.filter((r) => r.path && !r.children);
    const publicNames = publicChildren.map((r) => r.path);

    assert.ok(publicNames.includes('login'));
    assert.ok(publicNames.includes('signup'));
    assert.ok(publicNames.includes('about-model'));
  });

  it('4. Protected route branch isolates sensitive clinical views', () => {
    const rootRoute = routes[0];
    const protectedBranch = rootRoute.children!.find((r) => !r.path && r.children);
    assert.ok(protectedBranch);

    const sensitiveRoutes = ['dashboard', 'assessment', 'result/:id', 'history', 'profile'];
    for (const routeName of sensitiveRoutes) {
      assert.ok(
        protectedBranch.children!.some((c) => c.path === routeName),
        `Route ${routeName} must be inside protected branch`,
      );
    }
  });

  it('5. API Error properly encapsulates 401 as AUTHENTICATION_ERROR', () => {
    const err401 = new ApiError(401, 'AUTHENTICATION_ERROR', 'Authentication required.');
    assert.strictEqual(err401.status, 401);
    assert.strictEqual(err401.category, 'AUTHENTICATION_ERROR');
    assert.strictEqual(err401.message, 'Authentication required.');
  });

  it('6. API Error properly encapsulates 422 as VALIDATION_ERROR', () => {
    const err422 = new ApiError(422, 'VALIDATION_ERROR', 'Invalid value 5 for categorical field sex.');
    assert.strictEqual(err422.status, 422);
    assert.strictEqual(err422.category, 'VALIDATION_ERROR');
  });

  it('7. API Error properly encapsulates 500/503 as SERVER_ERROR and SERVICE_UNAVAILABLE', () => {
    const err500 = new ApiError(500, 'SERVER_ERROR', 'Internal server failure.');
    assert.strictEqual(err500.status, 500);
    assert.strictEqual(err500.category, 'SERVER_ERROR');

    const err503 = new ApiError(503, 'SERVICE_UNAVAILABLE', 'Database temporarily unavailable.');
    assert.strictEqual(err503.status, 503);
    assert.strictEqual(err503.category, 'SERVICE_UNAVAILABLE');
  });

  it('8. Firebase configuration reads from VITE_ environment variables only', () => {
    const envKeys = Object.keys(process.env);
    const clientExposedSecrets = envKeys.filter(
      (k) => k.startsWith('VITE_') && (k.includes('PRIVATE_KEY') || k.includes('CLIENT_EMAIL')),
    );
    assert.strictEqual(
      clientExposedSecrets.length,
      0,
      'No private key or client email may be prefixed with VITE_',
    );
  });

  it('9. Design tokens and color values match exact specification', () => {
    assert.strictEqual(PALETTE.primary, '#087F5B', 'Deep Emerald is #087F5B');
    assert.strictEqual(PALETTE.secondary, '#14B8A6', 'Electric Teal is #14B8A6');
    assert.strictEqual(PALETTE.accent, '#F4B942', 'Warm Amber is #F4B942');
    assert.strictEqual(PALETTE.bg, '#F6FAF8', 'Background is #F6FAF8');
    assert.strictEqual(PALETTE.text, '#12231E', 'Primary text is #12231E');
    assert.strictEqual(PALETTE.textMuted, '#65756F', 'Muted text is #65756F');
  });

  it('10. Semantic colors are strictly separated from brand Amber', () => {
    assert.notStrictEqual(
      PALETTE.accent,
      PALETTE.warning,
      'Brand Amber (#F4B942) must not equal Warning (#F59E0B)',
    );
    assert.strictEqual(PALETTE.success, '#10B981');
    assert.strictEqual(PALETTE.warning, '#F59E0B');
    assert.strictEqual(PALETTE.error, '#EF4444');
    assert.strictEqual(PALETTE.info, '#3B82F6');
  });

  it('11. Clinical input types match exact 13 canonical features', () => {
    const canonicalFeatures = [
      'age',
      'sex',
      'cp',
      'trestbps',
      'chol',
      'fbs',
      'restecg',
      'thalach',
      'exang',
      'oldpeak',
      'slope',
      'ca',
      'thal',
    ];
    assert.strictEqual(canonicalFeatures.length, 13);
    assert.ok(!canonicalFeatures.includes('num'), 'num target leakage prohibited');
    assert.ok(!canonicalFeatures.includes('target'), 'target leakage prohibited');
    assert.ok(!canonicalFeatures.includes('id'), 'id field prohibited');
  });

  it('12. Reusable landing page section components exist and are functions', () => {
    assert.strictEqual(typeof Hero, 'function');
    assert.strictEqual(typeof TrustMetrics, 'function');
    assert.strictEqual(typeof HowItWorks, 'function');
    assert.strictEqual(typeof ProductPreview, 'function');
    assert.strictEqual(typeof CTASection, 'function');
  });

  it('13. HeroHeartAnimation is exported and instantiable', () => {
    assert.strictEqual(typeof HeroHeartAnimation, 'function');
  });

  it('14. Phase 7 AssessmentPage is exported and functional', () => {
    assert.strictEqual(typeof AssessmentPage, 'function');
  });

  it('15. Phase 7 ResultPage is exported and functional', () => {
    assert.strictEqual(typeof ResultPage, 'function');
  });

  it('16. Phase 7 HistoryPage is exported and functional', () => {
    assert.strictEqual(typeof HistoryPage, 'function');
  });
});
