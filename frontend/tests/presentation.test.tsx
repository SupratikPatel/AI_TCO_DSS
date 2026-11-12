import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import type { Schema, SizeResult, TcoProjection } from '../src/api/client';
import { KpiRibbon } from '../src/components/KpiRibbon';
import { availableSeries, memoryChart, tcoChart } from '../src/lib/charts';
import { money } from '../src/lib/format';

afterEach(cleanup);
const result = {
  recommendation: { method: 'saw', ranked: [{ evaluation: {
    candidate_id: 'local', label: 'Hardware x4 + Model INT4', kind: 'onprem', eu_compliant: true,
    utilization: .7, tco: { munich_vs_romania_personnel_savings_monthly: 1234.567 },
    performance: { effective_tps: { value: 51.2 }, ttft_s: null },
  } }] },
  baselines: { compliance_tax_delta_monthly: -12.345 },
  timeline: { anchor_candidate_id: 'local', break_even_months: [['baseline_c_eu_sovereign_api_cumulative', null]] },
} as unknown as Schema['ScenarioResult'];

describe('12.5, 34.1-7, 43.6 shared executive presentation', () => {
  it('formats all monetary displays with two decimals, signs and display-only FX', () => {
    expect(money(111.65, 'USD', 1.1165)).toBe('$111.65');
    expect(money(111.65, 'EUR', 1.1165)).toBe('€100.00');
    expect(money(-12.345, 'USD', 1)).toBe('-$12.35');
    expect(money(0, 'EUR', 1)).toBe('€0.00');
  });
  it('shows exactly five ordered rank-one cards with missing metrics and both savings', () => {
    const { container } = render(<KpiRibbon data={result} loading={false} currency="USD" fx={1} onRejected={() => {}} />);
    expect([...container.querySelectorAll('.kpi-label')].map(e => e.textContent)).toEqual(['Recommended architecture', 'Break-even horizon', 'Monthly staffing savings', 'Performance', 'Cluster utilization']);
    expect(screen.getByText('No break-even within 60 months')).toBeTruthy();
    expect(screen.getByText('$1,234.57')).toBeTruthy();
    expect(screen.getByText(/Compliance tax delta: -\$12.35/)).toBeTruthy();
    expect(screen.getByText('TTFT: Not applicable')).toBeTruthy();
    expect(screen.getByText('70.0%')).toBeTruthy();
    expect(screen.getByText('Viable')).toBeTruthy();
  });
  it.each([['loading', 'Calculating…'], ['error', 'Unavailable'], ['empty', 'No feasible option']] as const)('clears numeric values for %s and exposes rejected results on empty', (state, title) => {
    const onRejected = vi.fn();
    const data = state === 'empty' ? { ...result, recommendation: { ...result.recommendation, ranked: [] } } : result;
    const { container } = render(<KpiRibbon data={data} loading={state === 'loading'} error={state === 'error' ? new Error('Failed') : undefined} currency="USD" fx={1} onRejected={onRejected} />);
    expect(screen.getByText(title)).toBeTruthy();
    expect(container.textContent).not.toContain('$1,234.57');
    expect(container.textContent).not.toContain('70.0%');
    if (state === 'empty') { fireEvent.click(screen.getByRole('button', { name: 'Review rejected candidates' })); expect(onRejected).toHaveBeenCalledOnce(); }
  });
  it.each([[.54, 'Idle capacity warning'], [.55, 'Below threshold'], [.699, 'Below threshold'], [1, 'Viable'], [1.01, 'Capacity insufficient'], [null, 'Not applicable']] as const)('classifies utilization %s without relying on colour', (utilization, badge) => {
    const data = structuredClone(result); data.recommendation.ranked[0].evaluation.utilization = utilization;
    render(<KpiRibbon data={data} loading={false} currency="EUR" fx={1.2} onRejected={() => {}} />);
    expect(screen.getAllByText(badge).length).toBeGreaterThan(0);
  });
  it('does not attribute the D-09 fallback anchor break-even to an API winner', () => {
    const data = structuredClone(result); data.recommendation.ranked[0].evaluation.kind = 'api'; data.recommendation.ranked[0].evaluation.candidate_id = 'remote';
    render(<KpiRibbon data={data} loading={false} currency="USD" fx={1} onRejected={() => {}} />);
    expect(screen.getByText(/On-premise comparison anchor/)).toBeTruthy();
  });
});

const projection = {
  candidate: { archetype: 'Sovereign Centralized Server / PD-Disagg', eu_compliant: true, utilization: .4, sizing: { is_feasible: false } },
  baselines: { baseline_a_eligible: false },
  timeline: { points: [{ month: 1, on_prem_cumulative: 100.125, baseline_a_subscription_cumulative: 10, baseline_b_global_api_cumulative: 20, baseline_c_eu_sovereign_api_cumulative: 30, baseline_d_openrouter_value_cumulative: null, eu_dedicated_rental_cumulative: 40, hybrid_split_cumulative: 50 }], break_even_months: [['baseline_a_subscription_cumulative', 1], ['baseline_c_eu_sovereign_api_cumulative', 1]] },
} as unknown as TcoProjection;

describe('35.4, 37.1/4, 43.3/6 typed chart semantics', () => {
  it('keeps Okabe-Ito trace colours in both themes, shows compliance and omits absent series', () => {
    const palette = ['#E69F00', '#56B4E9', '#009E73', '#F0E442', '#0072B2', '#D55E00', '#CC79A7', '#000000'];
    for (const dark of [false, true]) {
      const figure = tcoChart(projection, 'EUR', 1.25, dark);
      for (const trace of figure.data) expect(palette).toContain((trace as { line: { color: string } }).line.color);
      expect(availableSeries(projection).map(s => s[0])).not.toContain('baseline_d_openrouter_value_cumulative');
      expect(figure.data[0].name).toContain('Compliant · OOM');
      expect(figure.data[0]).toHaveProperty('hovertemplate', expect.stringContaining('€%{y:,.2f}'));
      expect(figure.layout.yaxis?.tickprefix).toBe('€');
      expect(figure.layout.yaxis?.tickformat).toBe(',.2f');
      expect(figure.layout.shapes?.some(s => s.type === 'rect')).toBe(true);
      expect(figure.data.some(t => t.name === 't* = 1 · C · EU-pinned API')).toBe(true);
      expect(figure.data.some(t => t.name?.startsWith('t*') && t.name.includes('Consumer'))).toBe(false);
    }
    expect(tcoChart(projection, 'USD', 1, false).data[0]).toHaveProperty('y', [100.125]);
    expect(projection.timeline?.points[0].on_prem_cumulative).toBe(100.125);
  });
  it('renders diamond market-value markers and eligible A solid without blocked text', () => {
    const data = structuredClone(projection); data.baselines.baseline_a_eligible = true;
    data.timeline!.points[0].baseline_d_openrouter_value_cumulative = 12;
    const traces = tcoChart(data, 'USD', 1, true).data;
    expect(traces.find(t => t.name?.startsWith('A ·'))).toHaveProperty('line.dash', 'solid');
    expect(traces.find(t => t.name?.startsWith('D ·'))).toHaveProperty('marker.symbol', 'diamond');
  });
  it('has a no-data annotation for missing timelines', () => {
    const chart = tcoChart({ ...projection, timeline: null }, 'USD', 1, false);
    expect(chart.data).toEqual([]); expect(chart.layout.annotations?.[0].text).toBe('No data available');
  });
  it('shows ordered memory segments, both capacity lines, agreement and eviction hatch', () => {
    const data = { sizing: { memory_breakdown: [['runtime_overhead', 2], ['weights', 3], ['os_reserved', 4], ['agent_state_parked', 5], ['kv_cache_active', 6]], usable_memory_gb: 12, usable_system_ram_gb: 32, context_eviction_risk: true, token_agreement_rate: .956 }, aa_index_v5: null } as unknown as SizeResult;
    const chart = memoryChart(data, true);
    expect(chart.data.map(t => t.name)).toEqual(['weights', 'kv cache active', 'agent state parked', 'os reserved', 'runtime overhead']);
    expect(chart.data[0]).toHaveProperty('marker.pattern.shape', '/');
    expect(chart.layout.shapes).toHaveLength(2);
    expect(chart.layout.xaxis?.range?.[1]).toBeGreaterThan(32);
    expect(chart.layout.annotations?.map(a => a.text).join(' ')).toContain('AA v5 n/a · agreement 95.6%');
    expect(chart.layout.annotations?.some(a => a.text === 'EVICTION RISK')).toBe(true);
  });
});
