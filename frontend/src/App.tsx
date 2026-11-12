import { useEffect, useRef, useState, type FormEvent, type ReactNode } from 'react';
import { ChartNoAxesCombined, CircleHelp, Cpu, ListOrdered, MemoryStick, Moon, ShieldCheck, Sun, TriangleAlert } from 'lucide-react';
import { ApiFailure, request, type Schema, type Scenario, type SizeResult, type TcoProjection } from './api/client';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Ranking } from './components/Ranking';
import { KpiRibbon } from './components/KpiRibbon';
import { ExpertControls } from './components/ExpertControls';
import { TcoAccounting } from './components/TcoAccounting';
import { AuditDrawer } from './components/AuditDrawer';
import { expertScenario, normalScenario, validFx, validUsers, validWeights } from './lib/scenario';
import { Plot } from './components/Plot';
import { useCalculation } from './hooks/useCalculation';
import { availableSeries, memoryChart, seriesNote, seriesStatus, tcoChart } from './lib/charts';
import { money, number, type Currency } from './lib/format';

type Boot = { catalog: Schema['CatalogOverview']; scenario: Scenario; options: Schema['SimulationOptions'] };
type Pair = { hardware_id: string; model_id: string; nodes: number; precision: Schema['PrecisionFormat']; context: number; override: boolean };
const initialPair: Pair = { hardware_id: 'rtx-pro-6000-96gb', model_id: 'gpt-oss-120b', nodes: 4, precision: 'INT4', context: 128000, override: false };
const precisions: Schema['PrecisionFormat'][] = ['INT2', 'INT3', 'INT4', 'INT8', 'FP16'];
const label = (value: string) => value.replaceAll('_', ' ').replaceAll('-', ' ');

function Field({ name, children }: { name: string; children: ReactNode }) {
  return <div className="field"><span>{name}</span>{children}</div>;
}
function Message({ error }: { error?: Error }) {
  if (!error) return null;
  return <div className="notice error" role="alert"><TriangleAlert size={17} /><div>{error.message}{error instanceof ApiFailure && <small>{error.fields.join(', ')}</small>}</div></div>;
}
function PairControls({ boot, pair, setPair, prefix }: { boot: Boot; pair: Pair; setPair: (pair: Pair) => void; prefix: string }) {
  const nodes = boot.options.node_counts.find(([id]) => id === pair.hardware_id)?.[1] ?? [1];
  return <>
    <Field name="Hardware tier"><select aria-label={`${prefix} hardware`} value={pair.hardware_id} onChange={e => {
      const hardware_id = e.target.value;
      const allowed = boot.options.node_counts.find(([id]) => id === hardware_id)?.[1] ?? [1];
      setPair({ ...pair, hardware_id, nodes: allowed.includes(pair.nodes) ? pair.nodes : allowed[0] });
    }}>{boot.catalog.hardware.map(item => <option key={item.id} value={item.id}>{item.label}</option>)}</select></Field>
    <Field name="Cluster nodes"><div className="segmented node-options" role="group" aria-label={`${prefix} nodes`}>{nodes.map(n => <Button key={n} aria-pressed={pair.nodes === n} onClick={() => setPair({ ...pair, nodes: n })}>{n}</Button>)}</div></Field>
    <Field name="Model architecture"><select aria-label={`${prefix} model`} value={pair.model_id} onChange={e => setPair({ ...pair, model_id: e.target.value })}>{boot.catalog.models.filter(item => boot.options.open_model_ids.includes(item.id)).map(item => <option key={item.id} value={item.id}>{item.label}</option>)}</select></Field>
    <Field name="Precision"><select aria-label={`${prefix} precision`} value={pair.precision} onChange={e => setPair({ ...pair, precision: e.target.value as Pair['precision'] })}>{precisions.map(p => <option key={p}>{p}</option>)}</select></Field>
  </>;
}

export default function App() {
  const [boot, setBoot] = useState<Boot>();
  const [error, setError] = useState<Error>();
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    setError(undefined);
    Promise.all([request<Boot['catalog']>('/catalog', undefined, controller.signal), request<Scenario>('/scenario/default', undefined, controller.signal), request<Boot['options']>('/options', undefined, controller.signal)]).then(([catalog, scenario, options]) => setBoot({ catalog, scenario, options })).catch(e => { if (!controller.signal.aborted) setError(e); });
    return () => controller.abort();
  }, [attempt]);
  return boot ? <Dashboard boot={boot} /> : <Startup error={error} retry={() => setAttempt(attempt + 1)} />;
}

function Startup({ error, retry }: { error?: Error; retry: () => void }) {
  return <div className="app-shell startup-shell">
    <aside className="sidebar"><div className="brand"><div className="brand-icon"><Cpu size={22} /></div><div><strong>AI TCO DSS</strong><small>Sovereign AI Cost Advisor</small></div></div><p className="muted">{error ? 'Scenario controls unavailable until the catalog loads.' : 'Loading scenario controls…'}</p><div className="catalog-meta">Catalog metadata {error ? 'unavailable' : 'loading'}</div></aside>
    <div className="workspace"><header className="project-header"><div><ShieldCheck size={20} /><strong>Project: Sovereign Inference</strong></div></header><main><section className="kpi-grid" aria-label="Executive metrics">{['Recommended architecture', 'Break-even horizon', 'Monthly savings', 'Performance', 'Cluster utilization'].map(name => <article className="kpi" key={name}><div className="kpi-label">{name}</div><strong className="metric">—</strong><small>{error ? 'Catalog required' : 'Awaiting calculation'}</small></article>)}</section><section className="analysis-panel"><div className="tabbar"><span className="startup-tab">Cost Decision Matrix</span></div><div className="empty-state">{error ? <><TriangleAlert size={32} /><h2>Catalog unavailable</h2><Message error={error} /><p>No results can be calculated. Retry after restoring the catalog or server connection.</p><Button variant="default" onClick={retry}>Retry catalog</Button></> : <><Cpu size={32} /><h2>Preparing your workspace</h2><p role="status">Loading catalog and scenario defaults…</p></>}</div></section></main></div>
  </div>;
}

function Dashboard({ boot }: { boot: Boot }) {
  const [submitted, setSubmitted] = useState(false);
  const [scenario, setScenario] = useState(boot.scenario);
  const [draft, saveDraft] = useState(boot.scenario);
  const [fxText, saveFxText] = useState('');
  const validation = useRef<AbortController | null>(null);
  const cancelValidation = () => { validation.current?.abort(); setApplying(false); };
  const setDraft = (next: Scenario) => { cancelValidation(); saveDraft(next); setScenarioError(undefined); };
  const setFxText = (value: string) => { cancelValidation(); saveFxText(value); setScenarioError(undefined); };
  useEffect(() => () => validation.current?.abort(), []);
  const [expert, setExpert] = useState(false);
  const [currency, setCurrency] = useState<Currency>('USD');
  const [dark, setDark] = useState(false);
  const [tab, setTab] = useState('ranking');
  const [usersError, setUsersError] = useState<string>();
  const [scenarioError, setScenarioError] = useState<Error>();
  const [applying, setApplying] = useState(false);
  const [memoryDraft, setMemoryDraft] = useState(initialPair);
  const [memoryPair, setMemoryPair] = useState(initialPair);
  const [tcoDraft, setTcoDraft] = useState(initialPair);
  const [tcoPair, setTcoPair] = useState(initialPair);
  const [resaleDraft, setResaleDraft] = useState(false);
  const [resale, setResale] = useState(false);
  const [ratioDraft, setRatioDraft] = useState(0.7);
  const [ratio, setRatio] = useState(0.7);
  const memoryScenario = { ...scenario, sizing: { ...scenario.sizing, target_context_length: memoryPair.context, apply_mac_wired_memory_override: memoryPair.override } };
  const tcoScenario = { ...scenario, sizing: { ...scenario.sizing, target_context_length: tcoPair.context }, financials: { ...scenario.financials, include_resale_value: resale, local_offload_ratio: ratio } };
  const evaluation = useCalculation<Schema['ScenarioResult']>('/evaluate', { scenario }, submitted);
  const [selection, setSelection] = useState<{ result: Schema['ScenarioResult']; id: string }>();
  const currentResult = !evaluation.loading && !evaluation.error && evaluation.key === JSON.stringify({ scenario }) && !evaluation.data?.recommendation.ranking_error ? evaluation.data : undefined;
  const selected = selection?.result === currentResult ? selection?.id : currentResult?.recommendation.ranked[0]?.evaluation.candidate_id;
  const selectCandidate = (id: string) => { if (currentResult) setSelection({ result: currentResult, id }); };
  const memory = useCalculation<SizeResult>('/size', { scenario: memoryScenario, hardware_id: memoryPair.hardware_id, model_id: memoryPair.model_id, precision: memoryPair.precision, nodes: memoryPair.nodes });
  const tco = useCalculation<TcoProjection>('/tco', { scenario: tcoScenario, candidate_id: `onprem:${tcoPair.hardware_id}:${tcoPair.nodes}x:${tcoPair.model_id}:${tcoPair.precision}` });
  useEffect(() => { document.documentElement.dataset.theme = dark ? 'dark' : 'light'; }, [dark]);
  const fx = evaluation.data?.fx_rate ?? boot.catalog.fx.rate;
  const completedTco = tco.key ? JSON.parse(tco.key) as Schema['TcoRequest'] : undefined;
  const tcoFx = completedTco?.scenario.fx_override ?? boot.catalog.fx.rate;
  const tcoCash = (value: number | null | undefined) => money(value, currency, tcoFx);
  const completedMemory = memory.key ? JSON.parse(memory.key) as Schema['SizeRequest'] : undefined;
  const cost = tco.data?.candidate.tco;
  const applyScenario = async (event: FormEvent) => {
    event.preventDefault(); setScenarioError(undefined);
    if (!validUsers(draft.workload.active_users)) { setUsersError('Active users must be an integer from 1 to 100,000 (active_users).'); return; }
    if (expert && (!validFx(fxText) || !validWeights(draft.decision.weights))) return;
    validation.current?.abort();
    const controller = new AbortController(); validation.current = controller; setApplying(true);
    try {
      const next = expert ? { ...draft, fx_override: fxText.trim() === '' ? null : Number(fxText) } : normalScenario(boot.scenario, draft);
      const valid = await request<Scenario>('/scenario/validate', next, controller.signal);
      if (!controller.signal.aborted) { setScenario(valid); setSubmitted(true); }
    } catch (error) { if (!controller.signal.aborted) setScenarioError(error as Error); }
    finally { if (!controller.signal.aborted) setApplying(false); }
  };
  const updateNormal = (next: Scenario) => {
    if (expert && next.decision.preset !== draft.decision.preset) {
      next = { ...next, decision: { ...next.decision, weights: { ...boot.options.preset_weights.find(([id]) => id === next.decision.preset)![1] } } };
    }
    setDraft(next);
    if (validUsers(next.workload.active_users)) {
      setUsersError(undefined);
      if (!expert && submitted) setScenario(normalScenario(boot.scenario, next));
    } else setUsersError('Active users must be an integer from 1 to 100,000 (active_users).');
  };
  const switchMode = (next: boolean) => {
    if (next === expert) return;
    const shared = { ...draft, workload: { ...draft.workload, active_users: validUsers(draft.workload.active_users) ? draft.workload.active_users : scenario.workload.active_users } };
    const normal = normalScenario(boot.scenario, shared);
    setExpert(next); setUsersError(undefined); setScenarioError(undefined); setFxText('');
    setDraft(next ? expertScenario(normal, boot.options.preset_weights) : normal);
    if (!next) setScenario(normal);
  };
  const pairingName = (pair: Pair) => `${boot.catalog.hardware.find(h => h.id === pair.hardware_id)?.label} × ${pair.nodes} + ${boot.catalog.models.find(m => m.id === pair.model_id)?.label} ${pair.precision}`;
  const reviewRejected = () => {
    setTab('ranking');
    requestAnimationFrame(() => {
      const details = document.getElementById('rejected-candidates');
      if (details instanceof HTMLDetailsElement) { details.open = true; details.querySelector('summary')?.focus(); }
    });
  };
  return <div className="app-shell">
    <a className="skip-link" href={`#${tab}-tab`} onClick={e => { e.preventDefault(); document.getElementById(`${tab}-tab`)?.focus(); }}>Skip to analysis</a>
    <aside className="sidebar">
      <div className="brand"><div className="brand-icon"><Cpu size={22} /></div><div><strong>AI TCO DSS</strong><small>Sovereign AI Cost Advisor</small></div></div>
      <div className="segmented mode"><Button aria-pressed={!expert} onClick={() => switchMode(false)}>Normal</Button><Button aria-pressed={expert} onClick={() => switchMode(true)}>Expert</Button></div>
      <form noValidate onSubmit={applyScenario} className="scenario-form">
        <Field name="Use case"><select aria-label="Use case" value={draft.decision.use_case} onChange={e => updateNormal({ ...draft, decision: { ...draft.decision, use_case: e.target.value as Scenario['decision']['use_case'] } })}>{boot.catalog.use_cases.map(u => <option key={u.id} value={u.id}>{u.label}</option>)}</select></Field>
        <Field name="Active users"><Input aria-label="Active users" aria-invalid={!!usersError} aria-describedby={usersError ? "users-error" : undefined} type="number" value={draft.workload.active_users} onChange={e => updateNormal({ ...draft, workload: { ...draft.workload, active_users: Number(e.target.value) } })} />{usersError && <small id="users-error" role="alert">{usersError}</small>}</Field>
        <Field name="Cost assumptions"><select aria-label="Cost assumptions" value={draft.financials.cost_model ?? 'enterprise'} onChange={e => updateNormal({ ...draft, financials: { ...draft.financials, cost_model: e.target.value as Scenario['financials']['cost_model'] } })}><option value="self-managed">Self-managed</option><option value="enterprise">Enterprise</option></select><small className="muted">{draft.financials.cost_model === 'self-managed' ? 'Purchase once + electricity. No paid operations staff, NIM, resale credit or priced waiting time. Capacity and quality requirements still apply.' : `Includes ${draft.financials.devops_fte_allocation} operations FTE over five years, even for one user. Expert mode adjusts staffing and workload.`}</small></Field>
        <Field name="Preset"><div className="preset-grid">{boot.catalog.presets.map(p => <Button key={p.id} aria-pressed={draft.decision.preset === p.id} onClick={() => updateNormal({ ...draft, decision: { ...draft.decision, preset: p.id as Scenario['decision']['preset'] } })}>{label(p.label)}</Button>)}</div></Field>
        <Field name="Display currency"><div className="segmented">{(['USD', 'EUR'] as const).map(c => <Button key={c} aria-pressed={currency === c} onClick={() => setCurrency(c)}>{c}</Button>)}</div></Field>
        {expert && <ExpertControls draft={draft} update={setDraft} catalog={boot.catalog} fxText={fxText} setFxText={setFxText} />}
        <Button type="submit" variant="default" disabled={applying}>{applying ? 'Validating…' : 'Apply scenario'}</Button><Message error={scenarioError} />
        <p className="muted helper">Cheapest uses cost only; Expert weights can override it. Quality and capacity filters still apply. Other presets balance six criteria. Popular weights OpenRouter model usage (40%). Coding quality cutoffs are 40 and 55. Apply your first scenario to begin. Normal controls then update results; Expert edits require Apply.</p>
      </form>
      <div className="sidebar-nav"><span><ChartNoAxesCombined size={17} />Cost Decision Matrix</span></div>
      <footer className="catalog-meta"><span className="status-dot" />Python calculation engine<div>Catalog: {boot.catalog.counts.filter(([key]) => ['hardware', 'models', 'rentals'].includes(key)).map(([key, count]) => `${count} ${key}`).join(', ')}</div><div>FX {fx} USD/EUR{evaluation.data?.fx_is_override && ' (Expert override)'} · {boot.catalog.fx.source_id}<br />{boot.catalog.fx.rate_date}</div></footer>
    </aside>
    <div className="workspace">
      <header className="project-header"><div><ShieldCheck size={20} /><strong>Project: Sovereign Inference</strong><span className="header-divider" /><small>{tco.loading ? 'Calculating…' : tco.error ? 'Check calculation' : 'Calculated by Python'}</small></div><div className="segmented themes"><Button aria-label="Light theme" aria-pressed={!dark} onClick={() => setDark(false)}><Sun size={17} /></Button><Button aria-label="Dark theme" aria-pressed={dark} onClick={() => setDark(true)}><Moon size={17} /></Button></div></header>
      <main>
        {!submitted && <section className="notice"><div><h2>Set up your comparison</h2><p>Choose your use case, users and preferences, then Apply scenario. Recommendations reflect the workload and available evidence. Open Expert to set requests per day, token sizes, performance targets and a total budget.</p></div></section>}
        {submitted && <KpiRibbon data={evaluation.data} loading={evaluation.loading} error={evaluation.error} currency={currency} fx={fx} onRejected={reviewRejected} />}
        <section className="analysis-panel">
          <div className="tabbar" role="tablist" aria-label="Analysis views">{[['ranking', 'Ranking', ListOrdered], ['memory', 'View 1: Memory fit', MemoryStick], ['tco', 'View 2: 60-month TCO', ChartNoAxesCombined]].map(([id, title, Icon]) => <button key={id as string} id={`${id}-tab`} role="tab" aria-selected={tab === id} aria-controls={`${id}-panel`} tabIndex={tab === id ? 0 : -1} onKeyDown={e => {
            const ids = ['ranking', 'memory', 'tco']; const index = ids.indexOf(tab);
            const next = e.key === 'ArrowRight' ? ids[(index + 1) % 3] : e.key === 'ArrowLeft' ? ids[(index + 2) % 3] : e.key === 'Home' ? ids[0] : e.key === 'End' ? ids[2] : null;
            if (next) { e.preventDefault(); setTab(next); document.getElementById(`${next}-tab`)?.focus(); }
          }} onClick={() => setTab(id as string)}>{typeof Icon !== 'string' && <Icon size={18} />}{title as string}</button>)}<span className="tab-meta"><span className="status-dot" />USD calculation basis</span></div>
          <div id="tco-panel" role="tabpanel" aria-labelledby="tco-tab" hidden={tab !== 'tco'}>
            <form className="toolbar" onSubmit={e => { e.preventDefault(); setTcoPair(tcoDraft); setResale(resaleDraft); setRatio(ratioDraft); }}>
              <div className="pair-grid"><PairControls boot={boot} pair={tcoDraft} setPair={setTcoDraft} prefix="TCO" /></div>
              <div className="toolbar-extra"><Field name="TCO context (tokens)"><Input aria-label="TCO context (tokens)" type="number" value={tcoDraft.context} onChange={e => setTcoDraft({ ...tcoDraft, context: Number(e.target.value) })} /></Field><Field name="Local token share"><Input aria-label="Local token share" type="number" step="0.05" value={ratioDraft} onChange={e => setRatioDraft(Number(e.target.value))} /></Field><label className="checkbox"><input type="checkbox" checked={resaleDraft} onChange={e => setResaleDraft(e.target.checked)} />Include resale value</label><Button type="submit" variant="default">Run cost projection</Button></div>
            </form>
            {tco.loading && <p className="loading" role="status">Calculating TCO… {tco.data && 'Showing last valid projection.'}</p>}<Message error={tco.error} />
            {tco.error && tco.data && <p className="loading">Showing the previous valid projection.</p>}
            {tco.data && <div data-testid="tco-result"><div className="anchor-label"><strong>Selected anchor</strong><span>{tco.data.candidate.label}</span><span className="badge">{seriesStatus(tco.data, 'on_prem_cumulative')}</span></div><div className="tco-columns">
              <section className="chart-column"><div className="panel-heading"><div><h2>Cumulative Cost Trajectory (60 Months)</h2><p>CapEx, facility power, staffing and optional resale</p></div><small>Currency: <b>{currency}</b></small></div>
                <div className="chart-frame"><Plot {...tcoChart(tco.data, currency, tcoFx, dark)} label="60-month cumulative costs. Detailed values are available in the timeline table below." /></div>
                <ul className="chart-legend" aria-label="Timeline series and compliance">{availableSeries(tco.data).map(([key, name, color, dash]) => <li key={key}><svg className="legend-swatch" width="24" height="12" aria-hidden="true"><path d="M1 6H23" stroke={color} strokeWidth="3" strokeDasharray={dash === 'solid' ? undefined : dash === 'dash' ? '7 3' : dash === 'dashdot' ? '7 3 2 3' : '2 3'} /></svg><div>{name}<small>{seriesStatus(tco.data!, key)}</small><small>{seriesNote(tco.data!, key)}</small></div></li>)}</ul>
                <details className="data-table"><summary>Accessible timeline data · 60 months</summary><div className="table-scroll" role="region" tabIndex={0} aria-label="Scrollable timeline data"><table><caption>Monthly cumulative costs ({currency})</caption><thead><tr><th>Month</th>{availableSeries(tco.data).map(([key, name]) => <th key={key}>{name}<small>{seriesStatus(tco.data!, key)}</small></th>)}</tr></thead><tbody>{tco.data.timeline?.points.map(p => <tr key={p.month}><th>{p.month}</th>{availableSeries(tco.data).map(([key]) => <td key={key}>{tcoCash(p[key])}</td>)}</tr>)}</tbody></table></div></details>
              </section>
              <div>
                {tco.data.accounting ? <TcoAccounting data={tco.data.accounting} currency={currency} warnings={cost?.warnings ?? []} insufficient={cost?.capacity_insufficient ?? false} meetsThreshold={cost?.meets_70_percent_utilization_threshold ?? false} /> : <p>Detailed local accounting is unavailable for this deployment.</p>}
                <p className="muted">Rental: {tco.data.timeline?.rental_id}. Baseline D is output market value, not a deployment offer. Baseline A: {tco.data.baselines.baseline_a_eligible ? 'Compliant' : 'Non-compliant / BLOCKED'}.</p>
              </div>
            </div></div>}
          </div>
          <div id="memory-panel" role="tabpanel" aria-labelledby="memory-tab" hidden={tab !== 'memory'}>
            <div className="view-heading"><h1>Hardware VRAM & Unified Memory Allocation Matrix</h1><p>Memory sizing for LLM weights, KV cache and parked agent context</p></div>
            <form className="toolbar" onSubmit={e => { e.preventDefault(); setMemoryPair(memoryDraft); }}><div className="pair-grid"><PairControls boot={boot} pair={memoryDraft} setPair={setMemoryDraft} prefix="Memory" /></div><div className="toolbar-extra"><Field name="Memory context (tokens)"><Input aria-label="Memory context (tokens)" type="number" value={memoryDraft.context} onChange={e => setMemoryDraft({ ...memoryDraft, context: Number(e.target.value) })} /></Field><label className="checkbox"><input type="checkbox" checked={memoryDraft.override} onChange={e => setMemoryDraft({ ...memoryDraft, override: e.target.checked })} />Mac wired-memory override</label><Button type="submit" variant="default">Run memory simulation</Button></div></form>
            {memory.loading && <p className="loading" role="status">Calculating memory… {memory.data && 'Showing last valid simulation.'}</p>}<Message error={memory.error} />
            {memory.error && memory.data && <p className="loading">Showing the previous valid simulation.</p>}
            {memory.data && <div className="memory-body" data-testid="memory-result"><div className="panel-heading"><div><h2>Memory Allocation vs. Usable Capacity</h2><p>{pairingName({ ...memoryPair, hardware_id: memory.data.sizing.hardware_id, model_id: memory.data.sizing.model_id, precision: memory.data.sizing.precision, nodes: memory.data.sizing.requested_nodes })}</p><p>Context: <b>{number(completedMemory?.scenario.sizing.target_context_length, 0)} tokens</b> · Cluster totals</p></div><span className={`badge ${memory.data.sizing.is_feasible ? 'success' : 'warning'}`}>{memory.data.sizing.is_feasible ? 'Fits in memory' : 'OOM · Does not fit'}</span></div><div className="memory-status"><span className="badge">{memory.data.sizing.eu_commercial_license_valid ? 'Compliant - EU commercial license' : 'Non-compliant - EU commercial license'}</span><span className="badge">{memory.data.sizing.context_eviction_risk ? 'EVICTION RISK' : 'No context eviction risk detected'}</span></div><div className="chart-frame memory-chart"><Plot {...memoryChart(memory.data, dark)} label="Stacked memory breakdown with usable-memory threshold. Exact segment values follow." /></div>
              <div className="memory-details"><article><h3>Memory breakdown</h3><dl>{memory.data.sizing.memory_breakdown.map(([key, value]) => <div key={key}><dt>{label(key)}</dt><dd>{number(value, 2)} GB</dd></div>)}<div><dt>Usable memory</dt><dd>{number(memory.data.sizing.usable_memory_gb)} GB</dd></div>{memory.data.sizing.usable_system_ram_gb != null && <div><dt>System RAM</dt><dd>{number(memory.data.sizing.usable_system_ram_gb)} GB</dd></div>}</dl><p className="muted">Parked agent state and OS reservation are separate pools; the total bar is not a feasibility test. The Python engine determines fit.</p></article><article><h3>Pairing performance & capacity</h3><dl><div><dt>Concurrent users (U_max)</dt><dd>{number(memory.data.sizing.max_concurrent_users, 0)}</dd></div><div><dt>Decode</dt><dd>{number(memory.data.performance?.decode_tps?.value)} tok/s</dd></div><div><dt>Effective speed</dt><dd>{number(memory.data.performance?.effective_tps?.value)} tok/s</dd></div><div><dt>TTFT</dt><dd>{number(memory.data.performance?.ttft_s?.value)} s</dd></div><div><dt>Token agreement</dt><dd>{memory.data.sizing.token_agreement_rate == null ? 'n/a' : `${(memory.data.sizing.token_agreement_rate * 100).toFixed(1)}%`}</dd></div><div><dt>AA v5 quality</dt><dd>{number(memory.data.aa_index_v5?.value)}</dd></div></dl><Origin metric={memory.data.performance?.decode_tps} /><p className="badge warning">{memory.data.sizing.context_eviction_risk ? 'Context eviction risk' : 'No context eviction risk detected'}</p></article></div>
              {!memory.data.sizing.is_feasible && <div className="notice warning"><TriangleAlert size={19} /><div><strong>No feasible memory fit</strong><p>{memory.data.sizing.oom_reason}</p><p>Performance is unavailable for this pairing.</p></div></div>}{memory.data.sizing.warnings.map(w => <p className="notice warning" key={w}>{w}</p>)}
            </div>}
          </div>
          <div id="ranking-panel" role="tabpanel" aria-labelledby="ranking-tab" hidden={tab !== 'ranking'}><Ranking key={evaluation.key} data={evaluation.data?.recommendation} loading={evaluation.loading} error={evaluation.error} currency={currency} fx={fx} selectedId={selected} onSelect={selectCandidate} context={`${label(scenario.decision.use_case)} | ${scenario.workload.active_users} users | ${label(scenario.decision.preset)}`} /></div>
        </section>
        <AuditDrawer result={currentResult} selected={selected} onSelect={selectCandidate} currency={currency} unavailable={!submitted ? 'Apply a scenario to enable downloads.' : currentResult ? undefined : evaluation.error || evaluation.data?.recommendation.ranking_error ? 'Current scenario calculation failed.' : 'Calculating current scenario.'} />
        <p className="page-note"><CircleHelp size={14} />Estimates use the current catalog and engine assumptions. Calibration limitations remain recorded in the corrections ledger.</p>
      </main>
    </div>
  </div>;
}

function Origin({ metric }: { metric?: Schema['Metric'] | null }) {
  return metric ? <span className="metric-origin"><span className="origin">{metric.origin.origin}</span><small>{metric.origin.source_ids.join(', ')}</small></span> : <span className="muted">No benchmark / result</span>;
}
