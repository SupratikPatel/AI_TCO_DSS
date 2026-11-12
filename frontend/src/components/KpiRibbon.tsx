import { Activity, ChartNoAxesCombined, Cpu, Gauge, TrendingDown } from 'lucide-react';
import type { Schema } from '../api/client';
import { money, number, type Currency } from '../lib/format';
import { Button } from './ui/button';

export function KpiRibbon({ data, loading, error, currency, fx, onRejected }: {
  data?: Schema['ScenarioResult']; loading: boolean; error?: Error; currency: Currency; fx: number; onRejected: () => void;
}) {
  const candidate = !loading && !error && !data?.recommendation.ranking_error ? data?.recommendation.ranked[0]?.evaluation : undefined;
  const state = loading ? 'Calculating…' : error || data?.recommendation.ranking_error ? 'Unavailable' : 'No feasible option';
  const missing = candidate ? 'Not applicable' : 'Not available';
  const cash = (value: number | null | undefined) => value == null ? missing : money(value, currency, fx);
  const metric = (value: number | null | undefined, unit: string) => value == null ? missing : `${number(value)} ${unit}`;
  const perf = candidate?.performance;
  const utilization = candidate?.utilization;
  const badge = utilization == null ? missing : utilization > 1 ? 'Capacity insufficient' : utilization >= .7 ? 'Viable' : utilization < .55 ? 'Idle capacity warning' : 'Below threshold';
  const month = data?.timeline?.break_even_months.find(([key]) => key === 'baseline_c_eu_sovereign_api_cumulative')?.[1];
  const anchor = candidate && data?.timeline && candidate.candidate_id !== data.timeline.anchor_candidate_id;
  return <>
    <section className="kpi-grid" aria-label="Executive metrics" aria-busy={loading}>
      <article className="kpi"><div className="kpi-label">Recommended architecture<Cpu size={17} /></div><h3>{candidate?.label ?? state}</h3><p>{candidate ? `${candidate.kind} | ${data?.recommendation.method.toUpperCase()} rank 1` : 'Recommendation engine'}</p>{!candidate && !loading && !error && !data?.recommendation.ranking_error && <Button onClick={onRejected}>Review rejected candidates</Button>}<small>Hard filters applied before ranking</small></article>
      <article className="kpi"><div className="kpi-label">Break-even horizon<ChartNoAxesCombined size={17} /></div><strong className={`metric${month == null ? ' metric-text' : ''}`}>{!candidate ? missing : !data?.timeline ? 'Not applicable' : month == null ? 'No break-even within 60 months' : `Month ${month}`}</strong><p>vs Baseline C (EU-pinned API)</p><small>{anchor ? `On-premise comparison anchor: ${data?.timeline?.anchor_candidate_id}` : 'Rank-one on-premise anchor · 60 months'}</small></article>
      <article className="kpi"><div className="kpi-label">Monthly staffing savings<TrendingDown size={17} /></div><strong className="metric compact">{cash(candidate?.tco?.munich_vs_romania_personnel_savings_monthly)}</strong><p>Munich vs Romania staffing</p><small>Compliance tax delta: {cash(candidate ? data?.baselines.compliance_tax_delta_monthly : null)}<br />Baseline C − Baseline A / month</small></article>
      <article className="kpi"><div className="kpi-label">Performance<Gauge size={17} /></div><strong className="metric compact">{metric(perf?.effective_tps?.value, 'tok/s')}</strong><p>TTFT: {metric(perf?.ttft_s?.value, 's')}</p><small>Decode: {metric(perf?.decode_tps?.value, 'tok/s')}</small></article>
      <article className="kpi"><div className="kpi-label">Cluster utilization<Activity size={17} /></div><strong className="metric">{utilization == null ? missing : `${(utilization * 100).toFixed(1)}%`}</strong><p className={`badge ${badge === 'Viable' ? 'success' : 'warning'}`}>{badge}</p><small>Demand / aggregate capacity</small></article>
    </section>
    {(error || data?.recommendation.ranking_error) && !loading && <p role="alert" className="notice error">KPIs could not be computed. Check the scenario or retry the calculation.</p>}
  </>;
}
