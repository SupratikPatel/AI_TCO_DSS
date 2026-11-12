import { useEffect, useRef, useState } from 'react';
import { ArrowDownToLine, ShieldCheck } from 'lucide-react';
import { ApiFailure, request, type Schema } from '../api/client';
import type { Currency } from '../lib/format';
import { number } from '../lib/format';
import { Button } from './ui/button';

const performanceLabels: Record<string, string> = { decode_tps: 'Decode TPS', prefill_tps: 'Prefill TPS', ttft_s: 'TTFT', effective_tps: 'Effective TPS', prefill_1m_minutes: '1M-token prefill time' };

function FxMetadata({ result }: { result: Schema['ScenarioResult'] }) {
  return <div className="audit-fx"><strong>{result.fx_rate.toFixed(6)} USD/EUR</strong><span>{result.fx_is_override ? 'Expert_Mode user override' : 'fx.json file rate'}</span><span>{result.fx_source_id} · rate date {result.fx_rate_date}</span></div>;
}

export function AuditDrawer({ result, selected, onSelect, currency, unavailable }: {
  result?: Schema['ScenarioResult']; selected?: string; onSelect: (id: string) => void; currency: Currency; unavailable?: string;
}) {
  const [open, setOpen] = useState(false);
  const [audit, setAudit] = useState<{ result: Schema['ScenarioResult']; id: string; data?: Schema['AuditResult']; error?: Error }>();
  const [download, setDownload] = useState<{ result: Schema['ScenarioResult']; currency: Currency; controller: AbortController; busy?: boolean; error?: Error }>();
  const transfer = useRef<AbortController | null>(null);
  useEffect(() => {
    // Cancel transfers on scenario/currency transitions, including unmount.
    return () => { transfer.current?.abort(); };
  }, [result, currency]);
  useEffect(() => {
    if (!open || !result || !selected) return;
    const controller = new AbortController();
    request<Schema['AuditResult']>('/audit', { result, candidate_id: selected }, controller.signal).then(data => {
      if (!controller.signal.aborted) setAudit({ result, id: selected, data });
    }).catch(error => { if (!controller.signal.aborted) setAudit({ result, id: selected, error }); });
    return () => controller.abort();
  }, [open, result, selected]);
  const active = audit?.result === result && audit?.id === selected ? audit : undefined;
  const candidate = result?.recommendation.ranked.find(r => r.evaluation.candidate_id === selected)?.evaluation;
  const downloading = download?.result === result && download?.currency === currency && !download.controller.signal.aborted && download.busy;
  const downloadError = download?.result === result && download?.currency === currency && !download.controller.signal.aborted ? download.error : undefined;
  const exportFile = async (kind: 'json' | 'csv') => {
    if (!result) return;
    transfer.current?.abort();
    const controller = new AbortController(); transfer.current = controller;
    setDownload({ result, currency, controller, busy: true });
    try {
      const response = await fetch(`/api/v1/export/${kind}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ result, currency }), signal: controller.signal });
      if (!response.ok) {
        const failure = await response.json() as Schema['ApiError'];
        throw new ApiFailure(failure.code, failure.message);
      }
      const blob = await response.blob();
      if (controller.signal.aborted) return;
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url; anchor.download = kind === 'json' ? 'scenario_USD.json' : `scenario_${currency}.zip`;
      document.body.append(anchor); anchor.click(); anchor.remove();
      // Give the browser time to consume the object URL before releasing it.
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      setDownload({ result, currency, controller });
    } catch (error) {
      if (!controller.signal.aborted) setDownload({ result, currency, controller, error: error as Error });
    }
  };
  return <section className="audit-section" aria-label="Audit and export">
    <details className="audit-drawer" onToggle={e => setOpen(e.currentTarget.open)}>
      <summary><ShieldCheck size={22} /><span>Audit & Export</span><small>Selected candidate · formulas, sources and value origins</small></summary>
      <div className="audit-body">
        {!candidate ? <><p role="status">No Candidate is available for audit. {unavailable ?? 'The result contains no ranked candidates.'}</p>{result && <FxMetadata result={result} />}</> : <>
          <label className="audit-picker">Audit candidate<select aria-label="Audit candidate" value={selected} onChange={e => onSelect(e.target.value)}>{result?.recommendation.ranked.map(r => <option key={r.evaluation.candidate_id} value={r.evaluation.candidate_id}>#{r.rank} · {r.evaluation.label}</option>)}</select></label>
          {!active && <p role="status">Loading selected candidate audit…</p>}
          {active?.error && <p className="notice error" role="alert">{active.error.message}</p>}
          {active?.data && <div className="audit-content">
            <h2>{candidate.label}</h2>
            <FxMetadata result={result!} />
            <p className="muted">Audit formulas and results use canonical USD. CSV uses {currency} at this result’s FX rate. JSON preserves the full Python scenario result in USD.</p>
            <h3>Performance value origins</h3>
            <dl className="audit-metrics">{Object.entries(active.data.performance).map(([name, metric]) => <div key={name}><dt>{performanceLabels[name] ?? name}</dt><dd>{metric ? <><strong>{number(metric.value, 2)} {metric.unit}</strong><span className="origin">{metric.origin.origin}</span><small>{metric.origin.source_ids.join(', ')}</small></> : <span>Unavailable · no value or formula returned</span>}</dd></div>)}</dl>
            <h3>Formulas & substitutions</h3>
            <p className="muted">Engine traces include measured selections. Component traces are labelled separately for hybrid deployments.</p>
            <div className="audit-formulas">{active.data.formulas.map((item, i) => <article key={`${item.section}-${item.trace.name}-${i}`}><div><span className="badge">{item.section}</span><strong>{item.trace.name}</strong></div><code>{item.trace.symbolic}</code><code>{item.trace.substituted}</code>{item.input_units && <p className="muted">Input units: {item.input_units}</p>}<strong className="audit-value">= {number(item.trace.result, 2)} {item.trace.unit}</strong></article>)}</div>
            <h3>Sources & catalog input provenance</h3>
            <p className="muted">Each source appears once. Expand its input records for field values, trust tiers and access dates; catalog metadata is included alongside contributing value origins.</p>
            <div className="audit-sources">{active.data.sources.map(source => <article key={source.source_id} data-source-id={source.source_id}><div><strong>{source.source_id}</strong><span>{source.tier}</span></div>{source.url ? <a href={source.url} target="_blank" rel="noreferrer">{source.title}</a> : <strong>{source.title}</strong>}{source.reference && <p>{source.reference}</p>}<p className="muted">Accessed: {[...new Set(source.provenance.map(p => p.accessed))].join(', ') || 'No provenance access date supplied'}</p><details><summary>Input provenance · {source.provenance.length} records</summary><ul>{source.provenance.map((p, i) => <li key={`${p.path}-${i}`}><code>{p.path}</code>{p.value != null && <strong>{p.value} {p.unit}</strong>}{p.tier === 'assumption' ? <span className="badge warning">assumption</span> : <span>{p.tier}</span>}<time>{p.accessed}</time></li>)}</ul></details></article>)}</div>
          </div>}
        </>}
      </div>
    </details>
    <div className="audit-downloads"><div><strong>Scenario downloads</strong><p>{result ? `Applied scenario result · ${currency} CSV / USD JSON` : unavailable ?? 'Awaiting a current Python result.'}</p>{result?.timeline ? <small>Scenario timeline anchor: {result.timeline.anchor_candidate_id}. Independent simulator projections are separate.</small> : result && <small>No scenario timeline is available. CSV requires a completed 60-month timeline.</small>}</div><Button disabled={!result || downloading} onClick={() => void exportFile('json')}><ArrowDownToLine size={16} />Export JSON</Button><Button disabled={!result?.timeline || downloading} onClick={() => void exportFile('csv')}>Export CSV (zip)</Button>{downloading && <p role="status">Preparing download…</p>}{downloadError && <p className="notice error" role="alert">{downloadError.message}</p>}</div>
  </section>;
}
