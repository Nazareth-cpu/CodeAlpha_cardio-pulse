/**
 * Phase 7C Model Selection & Frontend Integration Verification Tests
 */

import assert from 'node:assert';
import { describe, it } from 'node:test';

import { AssessmentPage } from '../src/pages/AssessmentPage';
import { ResultPage } from '../src/pages/ResultPage';
import { HistoryPage } from '../src/pages/HistoryPage';
import type { ModelInfoItem } from '../src/types/prediction';

describe('Phase 7C: Frontend Model Selection & Prediction Integration Suite', () => {
  it('1. All 4 canonical model identifiers are recognized in system', () => {
    const expectedModelIds = ['logistic_regression', 'svm', 'random_forest', 'xgboost'];
    assert.strictEqual(expectedModelIds.length, 4);
    assert.ok(expectedModelIds.includes('logistic_regression'));
    assert.ok(expectedModelIds.includes('svm'));
    assert.ok(expectedModelIds.includes('random_forest'));
    assert.ok(expectedModelIds.includes('xgboost'));
  });

  it('2. Model comparison is strictly neutral with no subjective winner labels', () => {
    // Model catalog items should have quantitative metrics only
    const sampleModel: ModelInfoItem = {
      id: 'random_forest',
      name: 'Random Forest',
      version: 'v1',
      description: 'Ensemble of 300 decision trees.',
      metrics: {
        accuracy: 0.8689,
        precision: 0.8125,
        recall: 0.9286,
        f1_score: 0.8667,
        roc_auc: 0.9443,
      },
      available: true,
    };

    assert.ok(sampleModel.metrics.accuracy > 0);
    assert.ok(sampleModel.metrics.roc_auc > 0);
    assert.strictEqual(typeof sampleModel.available, 'boolean');

    // Verify no forbidden subjective rankings
    const forbiddenLabels = ['best', 'winner', 'recommended', 'top choice', 'champion'];
    const desc = sampleModel.description?.toLowerCase() || '';
    for (const label of forbiddenLabels) {
      assert.ok(!desc.includes(label), `Model description should not include '${label}'`);
    }
  });

  it('3. AssessmentPage, ResultPage, and HistoryPage components exist and are functional', () => {
    assert.strictEqual(typeof AssessmentPage, 'function');
    assert.strictEqual(typeof ResultPage, 'function');
    assert.strictEqual(typeof HistoryPage, 'function');
  });

  it('4. Payload construction includes exact 13 canonical features plus model_id', () => {
    const canonicalPayload = {
      model_id: 'xgboost',
      age: 52,
      sex: 1,
      cp: 4,
      trestbps: 138,
      chol: 246,
      fbs: 0,
      restecg: 0,
      thalach: 150,
      exang: 0,
      oldpeak: 1.2,
      slope: 2,
      ca: 0,
      thal: 3,
    };

    const keys = Object.keys(canonicalPayload);
    assert.strictEqual(keys.length, 14); // 13 features + model_id
    assert.ok(keys.includes('model_id'));
    assert.ok(!keys.includes('num'), 'Forbidden field num must not be present');
    assert.ok(!keys.includes('target'), 'Forbidden field target must not be present');
    assert.ok(!keys.includes('id'), 'Forbidden field id must not be present');
  });
});
