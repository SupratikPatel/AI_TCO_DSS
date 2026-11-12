import type { ReactNode } from 'react';
import { Gauge } from 'lucide-react';
import type { Schema, Scenario } from '../api/client';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { validFx, validWeights } from '../lib/scenario';

const label = (value: string) => value.replaceAll('_', ' ').replaceAll('-', ' ');
function Field({ name, children }: { name: string; children: ReactNode }) {
  return <div className="field"><span>{name}</span>{children}</div>;
}

export function ExpertControls({ draft, update, catalog, fxText, setFxText }: {
  draft: Scenario; update: (scenario: Scenario) => void; catalog: Schema['CatalogOverview'];
  fxText: string; setFxText: (value: string) => void;
}) {
  const workload = (values: Partial<Scenario['workload']>) => update({ ...draft, workload: { ...draft.workload, ...values } });
  const financials = (values: Partial<Scenario['financials']>) => update({ ...draft, financials: { ...draft.financials, ...values } });
  const sizing = (values: Partial<Scenario['sizing']>) => update({ ...draft, sizing: { ...draft.sizing, ...values } });
  const numeric = (name: string, value: number | null | undefined, onChange: (value: number | null) => void, optional = false) => <Field name={name}><Input aria-label={name} type="number" step="any" value={value == null || Number.isNaN(value) ? '' : value} onChange={e => onChange(optional && e.target.value === '' ? null : e.target.value === '' ? NaN : Number(e.target.value))} /></Field>;
  const flag = (name: string, key: keyof Scenario['financials']) => <label className="checkbox"><input type="checkbox" checked={!!draft.financials[key]} onChange={e => financials({ [key]: e.target.checked })} />{name}</label>;
  return <section className="expert-settings" aria-label="Expert settings"><h3><Gauge size={15} />Expert settings</h3>
    {draft.financials.cost_model === 'self-managed' && <p className="muted">Self-managed costs use purchase and electricity at PUE 1. Staffing, licensing, economic costs and resale settings below apply in Enterprise mode.</p>}
    <Field name="Staffing hub"><select aria-label="Staffing hub" value={draft.financials.engineering_hub_location} onChange={e => financials({ engineering_hub_location: e.target.value as Scenario['financials']['engineering_hub_location'] })}>{catalog.hubs.map(h => <option key={h.id} value={h.id}>{label(h.label)}</option>)}</select></Field>
    <Field name="Electricity tariff"><select aria-label="Electricity tariff" value={draft.financials.electricity_tariff_tier} onChange={e => financials({ electricity_tariff_tier: e.target.value as Scenario['financials']['electricity_tariff_tier'] })}>{catalog.tariffs.map(t => <option key={t.id} value={t.id}>{label(t.label)}</option>)}</select></Field>
    <div className="two-fields">{numeric('Facility PUE', draft.financials.cooling_pue, v => financials({ cooling_pue: v! }))}{numeric('MLOps FTE', draft.financials.devops_fte_allocation, v => financials({ devops_fte_allocation: v! }))}</div>
    <div className="expert-flags"><h4>Constraint toggles</h4>{flag('NVIDIA NIM licensing', 'enable_nvidia_nim_licensing')}{flag('Wait-time penalty', 'include_wait_time_penalty')}{flag('Strict EU sovereignty', 'strict_eu_sovereignty')}{flag('Require third-party harness', 'require_third_party_harness')}{flag('Expert include resale value', 'include_resale_value')}</div>
    {numeric('Expert local token share', draft.financials.local_offload_ratio, v => financials({ local_offload_ratio: v! }))}
    <Field name="FX override (USD/EUR)"><Input aria-label="FX override (USD/EUR)" aria-invalid={!validFx(fxText)} aria-describedby="fx-help" inputMode="decimal" value={fxText} placeholder={`File rate: ${catalog.fx.rate}`} onChange={e => setFxText(e.target.value)} />{!validFx(fxText) ? <small id="fx-help" role="alert">Enter a rate from 0.50 to 2.00 with at most 6 decimals.</small> : <small id="fx-help" className="muted">Blank uses the file rate. Applies on submission to EUR input costs and currency display.</small>}</Field>
    <details className="expert-group" open><summary>Workload & sizing</summary><div className="expert-group-fields">
      {numeric('Requests per user per day', draft.workload.daily_requests_per_user, v => workload({daily_requests_per_user:v!}))}
      {numeric('Average input tokens', draft.workload.avg_input_tokens, v => workload({avg_input_tokens:v!}))}
      {numeric('Average output tokens', draft.workload.avg_output_tokens, v => workload({avg_output_tokens:v!}))}
      {numeric('Active hours per month', draft.workload.active_hours_per_month, v => workload({active_hours_per_month:v!}))}
      <div className="two-fields">{numeric('Target TPS', draft.workload.min_acceptable_tps, v => workload({ min_acceptable_tps: v }), true)}{numeric('Target TTFT (s)', draft.workload.max_acceptable_ttft_seconds, v => workload({ max_acceptable_ttft_seconds: v }), true)}</div>
      <small className="muted">Blank TPS or TTFT skips that threshold.</small>
      {numeric('Concurrent agents', draft.workload.concurrent_agent_instances, v => workload({ concurrent_agent_instances: v! }))}
      {numeric('Peak concurrent requests', draft.workload.peak_concurrent_requests, v => workload({ peak_concurrent_requests: v! }))}
      {numeric('Target context (tokens)', draft.sizing.target_context_length, v => sizing({ target_context_length: v! }))}
      <Field name="KV quantization precision"><select aria-label="KV quantization precision" value={draft.sizing.kv_precision} onChange={e => sizing({ kv_precision: e.target.value as Schema['PrecisionFormat'] })}>{(['INT2', 'INT3', 'INT4', 'INT8', 'FP8', 'FP16', 'BF16'] as const).map(p => <option key={p}>{p}</option>)}</select><small className="muted">Ranking compares all supported weight precisions. Simulator weight precision is selected in each panel.</small></Field>
      <Field name="Harness"><select aria-label="Harness" value={draft.workload.harness_type} onChange={e => workload({ harness_type: e.target.value as Schema['HarnessType'] })}>{(['claude-code', 'codex', 'opencode', 'deepseek-dsh', 'custom-lean'] as const).map(h => <option key={h} value={h}>{label(h)}</option>)}</select></Field>
      {draft.workload.harness_type === 'custom-lean' && numeric('Custom scaffolding tokens', draft.workload.custom_scaffolding_tokens, v => workload({ custom_scaffolding_tokens: v }), true)}
      <label className="checkbox"><input type="checkbox" checked={draft.workload.mcp_code_mode_pruning} onChange={e => workload({ mcp_code_mode_pruning: e.target.checked })} />MCP code mode pruning</label>
      <Field name="Thinking effort"><select aria-label="Thinking effort" value={draft.workload.thinking_effort_preset} onChange={e => workload({ thinking_effort_preset: e.target.value as Schema['ThinkingEffortPreset'] })}>{(['none', 'low', 'medium', 'extra-high'] as const).map(p => <option key={p} value={p}>{label(p)}</option>)}</select></Field>
      {numeric('60-month total budget (USD)', draft.financials.max_tco_budget_usd, v => financials({ max_tco_budget_usd: v }), true)}
      {numeric('CapEx budget (USD)', draft.financials.max_capex_budget_usd, v => financials({ max_capex_budget_usd: v }), true)}
    </div></details>
    <details className="expert-group" open><summary>Ranking method & weights</summary><div className="expert-group-fields">
      <div className="segmented" role="group" aria-label="Ranking method">{(['saw', 'topsis'] as const).map(method => <Button key={method} aria-pressed={draft.decision.method === method} onClick={() => update({ ...draft, decision: { ...draft.decision, method } })}>{method.toUpperCase()}</Button>)}</div>
      <label className="checkbox"><input type="checkbox" checked={draft.decision.reward_excess_performance} onChange={e => update({...draft, decision:{...draft.decision, reward_excess_performance:e.target.checked}})} />Reward performance beyond targets</label>
      <p className="muted">By default, extra speed earns no additional score once targets are met.</p>
      <p className="muted">Weights are normalized in Python. Preset selection initializes all six weights; hard filters always apply first.</p>
      <div className="two-fields">{draft.decision.weights && Object.entries(draft.decision.weights).map(([key, value]) => <Field name={label(key)} key={key}><Input aria-label={`Weight: ${label(key)}`} aria-invalid={!Number.isFinite(value) || value < 0} type="number" step="any" value={Number.isNaN(value) ? '' : value} onChange={e => update({ ...draft, decision: { ...draft.decision, weights: { ...draft.decision.weights!, [key]: e.target.value === '' ? NaN : Number(e.target.value) } } })} /></Field>)}</div>
      {!validWeights(draft.decision.weights) && <small role="alert">Weights must be finite, non-negative and have a positive sum.</small>}
    </div></details>
    <p className="muted">Apply scenario to validate these inputs and refresh results.</p>
  </section>;
}
