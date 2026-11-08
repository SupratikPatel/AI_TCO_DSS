import { render, screen, fireEvent, cleanup } from '@testing-library/react';
import { afterEach, describe, expect, it } from 'vitest';
import { Ranking } from '../src/components/Ranking';
import { normalScenario, validUsers } from '../src/lib/scenario';
import type { Schema, Scenario } from '../src/api/client';

afterEach(cleanup);
const fixture = {
  use_case: 'agentic-coding', method: 'saw', weights_normalised: null, ranked: [],
  rejected: [{ candidate_id: 'api:test', label: 'Fixture API', kind: 'api', eu_compliant: false,
    failures: [{ name: 'eu_sovereignty', measured: 'no EU-pinned endpoint', threshold: 'EU-pinned endpoint required' }], notes: [] }],
  explanation: null, ranking_error: null, warnings: [],
} as unknown as Schema['Recommendation'];

describe('Normal scenario and ranking states (33.1/2/7, 43.6/7)', () => {
  it('uses only three Normal inputs and ignores Expert values', () => {
    const defaults = { workload: { active_users: 25, min_acceptable_tps: 20 }, financials: { cooling_pue: 1.2 }, sizing: { target_context_length: 128000 }, decision: { method: 'saw', preset: 'best-fit', use_case: 'agentic-coding' }, fx_override: null } as Scenario;
    const draft = { ...defaults, workload: { ...defaults.workload, active_users: 70, min_acceptable_tps: 99 }, decision: { ...defaults.decision, preset: 'cheapest', method: 'topsis' }, fx_override: 1.5 } as Scenario;
    const normal = normalScenario(defaults, draft);
    expect(normal.workload.active_users).toBe(70);
    expect(normal.workload.min_acceptable_tps).toBe(20);
    expect(normal.decision.method).toBe('saw');
    expect(normal.decision.weights).toBeNull();
    expect(normal.fx_override).toBeNull();
    for (const value of [0, 100001, 1.5, NaN]) expect(validUsers(value)).toBe(false);
    expect(validUsers(100000)).toBe(true);
  });
  it('distinguishes loading, server error, empty ranking and rejection facts', () => {
    const { rerender } = render(<Ranking loading currency="USD" fx={1} />);
    expect(screen.getByRole('status').textContent).toContain('Calculating recommendations');
    rerender(<Ranking loading={false} error={new Error('Server failed')} currency="USD" fx={1} />);
    expect(screen.getByRole('alert').textContent).toContain('Server failed');
    expect(screen.queryByText('No feasible option')).toBeNull();
    rerender(<Ranking loading={false} data={fixture} currency="USD" fx={1} />);
    expect(screen.getByRole('heading', { name: 'No feasible option' })).toBeTruthy();
    fireEvent.click(screen.getByText(/Rejected candidates/));
    expect(screen.getByText('eu_sovereignty')).toBeTruthy();
    expect(screen.getByText('no EU-pinned endpoint')).toBeTruthy();
  });
});
