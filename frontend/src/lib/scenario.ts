import type { Scenario } from '../api/client';

export const validUsers = (users: number) => Number.isInteger(users) && users >= 1 && users <= 100000;

// Normal mode always starts from Python defaults. Preset weights are resolved in Python.
export function normalScenario(defaults: Scenario, draft: Scenario): Scenario {
  return { ...defaults, workload: { ...defaults.workload, active_users: draft.workload.active_users },
    decision: { ...defaults.decision, use_case: draft.decision.use_case, preset: draft.decision.preset, weights: null, method: 'saw' } };
}
