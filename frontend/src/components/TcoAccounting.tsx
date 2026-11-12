import { useState } from 'react';
import { TriangleAlert } from 'lucide-react';
import type { Schema } from '../api/client';
import { money, type Currency } from '../lib/format';

export function TcoAccounting({ data, currency, warnings, insufficient, meetsThreshold }: {
  data: Schema['TcoAccounting']; currency: Currency; warnings: string[]; insufficient: boolean; meetsThreshold: boolean;
}) {
  const [expanded, setExpanded] = useState<string>();
  const cash = (value: number) => money(value, currency, data.fx.rate);
  const totals = new Set(['monthly_total', 'cost_60m', 'savings_60m']);
  return <section className="accounting" aria-label="Simulator cost accounting">
    <h2>60-Month Cost Accounting Matrix</h2>
    <p className="accounting-context">This simulator’s selected anchor. Calculated amounts use catalog inputs and scenario assumptions.</p>
    <div className="table-scroll" role="region" tabIndex={0} aria-label="Scrollable cost accounting"><table>
      <thead><tr><th>Item</th><th>Value ({currency})</th><th>Calculation</th></tr></thead>
      <tbody>{data.rows.map(row => <AccountingRows key={row.key} row={row} amount={cash(row.value)} expanded={expanded === row.key} onToggle={() => setExpanded(expanded === row.key ? undefined : row.key)} total={totals.has(row.key)} />)}</tbody>
    </table></div>
    <p className="accounting-context"><strong>{data.fx.rate.toFixed(6)} USD/EUR</strong> · {data.fx.is_override ? 'Original Expert FX override' : 'Original catalog FX'} · {data.fx.source_id} · {data.fx.rate_date}. Display currency changes presentation only. Equations retain USD; totals use unrounded inputs.</p>
    <div className={`notice ${insufficient || !meetsThreshold ? 'warning' : ''}`}><TriangleAlert size={20} /><div>
      <strong>{insufficient ? 'CAPACITY DEFICIT' : meetsThreshold ? 'UTILIZATION THRESHOLD MET' : 'LOW UTILIZATION'}</strong>
      <p>Utilization: {data.utilization_text}. Low utilization alone does not establish which option is cheaper.</p>
      {warnings.length > 0 && <p>{warnings.join(' ')}</p>}
    </div></div>
    <p className="accounting-comparison">Break-even vs Baseline C: <strong>{data.break_even_month === null ? 'No break-even within 60 months' : `${data.break_even_month} months`}</strong>. Positive 60-month savings favor local; negative savings favor the API, under these assumptions.</p>
    <p className="muted">Cash and economic subtotals explain the components; they are not additional charges.</p>
  </section>;
}

function AccountingRows({ row, amount, expanded, onToggle, total }: {
  row: Schema['AccountingRow']; amount: string; expanded: boolean; onToggle: () => void; total: boolean;
}) {
  const monthly = ['energy', 'personnel', 'nim_licensing', 'capital_opportunity', 'wait_penalty', 'eviction_loss', 'baseline_c'].includes(row.key);
  const assumption = row.sources.some(s => s.provenance.some(p => p.tier === 'assumption'));
  return <>
    <tr className={total ? 'total' : undefined}><td>{row.label}{monthly && <small>monthly</small>}{row.key === 'cost_60m' && <small>{row.note}</small>}</td><td>{amount}</td><td>
      <button className="calculation-toggle" aria-expanded={expanded} aria-controls={`cost-detail-${row.key}`} aria-label={`${expanded ? 'Hide' : 'Show'} calculation for ${row.label}`} onClick={onToggle}>Calculated {expanded ? '−' : '+'}</button>
      {assumption && <small className="assumption-label">Assumption inputs</small>}
    </td></tr>
    {expanded && <tr className="accounting-detail" id={`cost-detail-${row.key}`}><td colSpan={3}>
      <p>{row.note}</p><code>{row.trace.symbolic}</code><code>{row.trace.substituted}</code>
      <strong>Result: {money(row.trace.result, 'USD', 1)} {row.trace.unit === 'USD/month' ? '/ month' : ''}</strong>
      {!row.sources.length && <p>Scenario settings / model assumptions; no measured cost is claimed.</p>}
      {row.sources.map(source => <article key={source.source_id}>
        {source.url ? <a href={source.url} target="_blank" rel="noreferrer">{source.source_id}: {source.title}</a> : <strong>{source.source_id}: {source.title}</strong>}
        {source.reference && <p>{source.reference}</p>}
        <ul>{source.provenance.map((p, i) => <li key={i}><span className="badge">{p.tier}</span> {p.path}: {p.value} {p.unit} · accessed {p.accessed}</li>)}</ul>
      </article>)}
    </td></tr>}
  </>;
}
