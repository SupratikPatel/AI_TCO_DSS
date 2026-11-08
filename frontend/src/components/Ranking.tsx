import { useState } from 'react';
import { ListOrdered, ShieldCheck, TrendingUp, TriangleAlert } from 'lucide-react';
import type { Schema } from '../api/client';
import { money, number, type Currency } from '../lib/format';
import { Button } from './ui/button';

const label = (value: string) => value.replaceAll('_', ' ').replaceAll('-', ' ');
const kinds = { onprem: 'On-premise', api: 'Cloud API', rental: 'EU rental', hybrid: 'Hybrid' };

export function Ranking({ data, loading, error, currency, fx, context }: {
  data?: Schema['Recommendation']; loading: boolean; error?: Error; currency: Currency; fx: number; context?: string;
}) {
  const [selected, setSelected] = useState<string>();
  const [page, setPage] = useState(0);
  const [rejectedPage, setRejectedPage] = useState(0);
  const cash = (value: number) => money(value, currency, fx);
  const row = data?.ranked.find(r => r.evaluation.candidate_id === selected) ?? data?.ranked[0];
  const top = data?.ranked[0];
  const topsis = data?.method === 'topsis';
  const currentPage = Math.min(page, Math.max(0, Math.ceil((data?.ranked.length ?? 0) / 8) - 1));
  const currentRejectedPage = Math.min(rejectedPage, Math.max(0, Math.ceil((data?.rejected.length ?? 0) / 10) - 1));
  return <div className="ranking-body" aria-busy={loading}>
    {loading && <p role="status" className="loading">Calculating recommendations… {data && 'Updating the current scenario.'}</p>}
    {error && <div role="alert" className="notice error"><TriangleAlert size={20} /><p>{error.message}</p></div>}
    {!loading && !error && data && <div data-testid="ranking-result">
      <div className="ranking-meta"><span><span className="status-dot" />{data.method.toUpperCase()} · {context}</span><span>{data.ranked.length} admissible · {data.rejected.length} rejected</span></div>
      {data.ranking_error ? <div role="alert" className="notice error">{data.ranking_error}</div> : top ? <article className="recommendation-card">
        <div className="recommendation-icon"><TrendingUp size={24} /></div>
        <div className="recommendation-copy"><h2>{top.evaluation.label} ranks first.</h2><span className="badge success"><ShieldCheck size={12} /> Recommended by DSS</span>
          <p>{data.explanation}</p>
          <div className="contribution-chips"><small>{topsis ? 'SAW contributions for comparison' : 'Largest contributions'}</small>{[...top.criteria].sort((a, b) => b.contribution - a.contribution).slice(0, 2).map(c => <span className="origin" key={c.criterion}>{label(c.criterion)}: {number(c.contribution, 3)}</span>)}</div>
        </div><div className="recommendation-score"><small>{topsis ? 'TOPSIS closeness' : 'Weighted SAW score'}</small><strong>{topsis ? top.topsis_closeness?.toFixed(3) : number(top.saw_score, 3)}</strong><span>/ 1.000</span>{topsis && <small>D+ {number(top.d_plus, 3)} · D− {number(top.d_minus, 3)}</small>}</div>
      </article> : <div className="empty-state"><ListOrdered size={32} /><h2>No feasible option</h2><p>Every candidate failed one or more hard filters. Review the measured values and thresholds below. Changing ranking weights cannot remedy a hard-filter failure.</p><a href="#rejected-candidates" onClick={() => { const details = document.getElementById('rejected-candidates'); if (details instanceof HTMLDetailsElement) details.open = true; }}>Review rejected candidates</a></div>}
      {top && <>
        <div className={`table-scroll ranking-table${topsis ? " topsis-table" : ""}`} tabIndex={0} role="region" aria-label="Scrollable candidate ranking"><table><caption>Admissible candidates · {data.method.toUpperCase()} ranking · monetary values in {currency}</caption><thead><tr>{topsis ? <><th>SAW rank</th><th>TOPSIS rank</th><th>Closeness</th></> : <th>Rank</th>}<th>Candidate architecture & quantization</th><th>Type</th><th>60M TCO ({currency})</th><th>Quality</th><th>Speed tok/s</th><th>TTFT s</th><th>Risk</th><th>Popularity</th><th>SAW</th></tr></thead><tbody>{data.ranked.slice(currentPage * 8, currentPage * 8 + 8).map(r => {
          const c = r.evaluation;
          return <tr key={c.candidate_id} className={row?.evaluation.candidate_id === c.candidate_id ? 'selected' : ''}>{topsis ? <><td>{r.saw_rank}</td><td><span className="rank-number">{r.topsis_rank}</span></td><td>{r.topsis_closeness?.toFixed(3)}</td></> : <td><span className="rank-number">{r.rank}</span></td>}<td><Button variant="ghost" aria-pressed={row?.evaluation.candidate_id === c.candidate_id} onClick={() => setSelected(c.candidate_id)}>{c.label}</Button><small>{c.eu_compliant ? 'Compliant' : 'Non-compliant'} · {c.precision ?? 'API'}{c.quality?.fallback_note && ' · Quality fallback'}</small></td><td><span className={`badge kind-${c.kind}`}>{kinds[c.kind]}</span></td><td>{cash(c.cost_60m)}</td><td>{number(c.quality?.value)}<small>{c.quality ? label(c.quality.benchmark) : 'No benchmark'}</small></td><td>{number(c.performance?.effective_tps?.value)}</td><td>{number(c.performance?.ttft_s?.value)}</td><td>{number(c.risk, 3)}</td><td>{number(c.popularity)}</td><td>{number(r.saw_score, 3)}</td></tr>;
        })}</tbody></table></div>
        <div className="ranking-pagination"><span>{topsis ? 'Closeness = D- / (D+ + D-)' : 'Score = Σ normalized weight × normalized criterion'} · {currentPage * 8 + 1}–{Math.min(currentPage * 8 + 8, data.ranked.length)} of {data.ranked.length}</span><div><Button disabled={currentPage === 0} onClick={() => setPage(currentPage - 1)}>Previous ranks</Button><Button disabled={(currentPage + 1) * 8 >= data.ranked.length} onClick={() => setPage(currentPage + 1)}>Next ranks</Button></div></div>
        {row && <details className="contribution-details" key={row.evaluation.candidate_id} open><summary>Selected candidate {topsis ? 'SAW ' : ''}contributions · rank {row.rank}</summary><p>{row.evaluation.label}</p><div className="table-scroll"><table aria-label="Selected candidate contributions"><thead><tr><th>Criterion</th><th>Raw value</th><th>Normalized</th><th>Weight</th><th>Contribution</th></tr></thead><tbody>{row.criteria.map(c => <tr key={c.criterion}><th>{label(c.criterion)}</th><td>{c.missing ? 'Not available' : c.criterion === 'tco_60m' ? cash(c.raw!) : number(c.raw, 3)}</td><td>{number(c.normalised, 3)}</td><td>{number(c.weight, 3)}</td><td>{number(c.contribution, 3)}</td></tr>)}</tbody></table></div>{row.evaluation.notes.map(n => <p className="muted" key={n}>{n}</p>)}</details>}
      </>}
      <details className="rejected-candidates" id="rejected-candidates"><summary>Rejected candidates <span className="badge">{data.rejected.length}</span><span className="muted">All failed filters, measured values and thresholds</span></summary><div className="rejected-list">{data.rejected.slice(currentRejectedPage * 10, currentRejectedPage * 10 + 10).map(c => <article key={c.candidate_id}><div><h3>{c.label}</h3><small>{c.eu_compliant ? 'Compliant' : 'Non-compliant'}{c.failures.some(f => f.name === 'memory_fit') && ' · OOM'}</small></div><div className="failure-list">{c.failures.map(f => <span className="filter-failure" key={f.name}><b>{f.name}</b><span>{f.measured}</span><small>Required: {f.threshold}</small></span>)}</div></article>)}<div className="ranking-pagination"><span>{data.rejected.length ? `${currentRejectedPage * 10 + 1}–${Math.min(currentRejectedPage * 10 + 10, data.rejected.length)} of ${data.rejected.length}` : 'No rejected candidates'}</span><div><Button disabled={currentRejectedPage === 0} onClick={() => setRejectedPage(currentRejectedPage - 1)}>Previous rejections</Button><Button disabled={(currentRejectedPage + 1) * 10 >= data.rejected.length} onClick={() => setRejectedPage(currentRejectedPage + 1)}>Next rejections</Button></div></div></div></details>
      {data.warnings.map(w => <p key={w} className="notice warning">{w}</p>)}
    </div>}
  </div>;
}
