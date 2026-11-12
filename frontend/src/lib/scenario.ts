import type { Schema, Scenario } from '../api/client';

export const validUsers = (users: number) => Number.isInteger(users) && users >= 1 && users <= 100000;

// Normal mode always starts from Python defaults. Preset weights are resolved in Python.
export function normalScenario(defaults: Scenario, draft: Scenario): Scenario {
  return { ...defaults, workload: { ...defaults.workload, active_users: draft.workload.active_users },
    financials: { ...defaults.financials, cost_model: draft.financials.cost_model ?? 'enterprise' },
    decision: { ...defaults.decision, use_case: draft.decision.use_case, preset: draft.decision.preset, weights: null, method: 'saw' } };
}

export function expertScenario(scenario: Scenario, presets: Schema['SimulationOptions']['preset_weights']): Scenario {
  const weights = presets.find(([id]) => id === scenario.decision.preset)![1];
  return { ...scenario, decision: { ...scenario.decision, weights: { ...weights }, method: 'saw' } };
}

export const validFx = (value: string) => value.trim() === '' ||
  (/^(?:\d+(?:\.\d{0,6})?|\.\d{1,6})$/.test(value) && Number(value) >= .5 && Number(value) <= 2);

export const validWeights = (weights: Schema['CriterionWeights'] | null | undefined) => !!weights &&
  Object.values(weights).every(w => Number.isFinite(w) && w >= 0) &&
  Number.isFinite(Object.values(weights).reduce((a, b) => a + b, 0)) &&
  Object.values(weights).some(w => w > 0);
