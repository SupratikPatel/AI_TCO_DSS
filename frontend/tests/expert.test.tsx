import { describe, expect, it } from 'vitest';
import { expertScenario, validFx, validWeights } from '../src/lib/scenario';
import type { Scenario } from '../src/api/client';

describe('Expert initialization and validation (12.4/8, 29.11, 33.5)', () => {
  it('initializes weights from the selected preset and resets the method', () => {
    const weights = { tco_60m: .5, quality: .1, effective_tps: .1, ttft: .1, risk: .1, popularity: .1 };
    const scenario = { decision: { preset: 'cheapest', method: 'topsis', weights: null }, workload: { active_users: 71 } } as Scenario;
    const expert = expertScenario(scenario, [['cheapest', weights]]);
    expect(expert.workload.active_users).toBe(71);
    expect(expert.decision.weights).toEqual(weights);
    expect(expert.decision.method).toBe('saw');
  });
  it('validates FX range/precision and weights without ranking math', () => {
    for (const value of ['', '.5', '2', '1.234567']) expect(validFx(value)).toBe(true);
    for (const value of ['bad', '0.49', '2.1', '1.0000001', 'NaN', 'Infinity']) expect(validFx(value)).toBe(false);
    expect(validWeights({ tco_60m: 2, quality: 0, effective_tps: 0, ttft: 0, risk: 0, popularity: 0 })).toBe(true);
    for (const value of [-1, NaN, Infinity, 0]) expect(validWeights({ tco_60m: value, quality: 0, effective_tps: 0, ttft: 0, risk: 0, popularity: 0 })).toBe(false);
  });
});
