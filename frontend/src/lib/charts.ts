import type { Data, Layout, Shape } from 'plotly.js';
import type { SizeResult, TcoProjection } from '../api/client';
import type { Currency } from './format';
import { OKABE_ITO as colors } from './theme';

export const series = [
  ['on_prem_cumulative', 'On-premise', colors.blue, 'solid', 4],
  ['eu_dedicated_rental_cumulative', 'Dedicated EU rental', colors.green, 'dashdot', 2.5],
  ['baseline_a_subscription_cumulative', 'A · Consumer sub', colors.purple, 'dash', 2],
  ['baseline_b_global_api_cumulative', 'B · Global API', colors.black, 'dot', 2],
  ['baseline_c_eu_sovereign_api_cumulative', 'C · EU-pinned API', colors.orange, 'solid', 3],
  ['baseline_d_openrouter_value_cumulative', 'D · Output market value', colors.black, 'dot', 2],
  ['hybrid_split_cumulative', 'Hybrid split', colors.orange, 'dash', 2.5],
] as const;
type SeriesKey = typeof series[number][0];

export function seriesStatus(result: TcoProjection, key: SeriesKey) {
  if (key === 'on_prem_cumulative') return `${result.candidate.eu_compliant ? 'Compliant' : 'Non-compliant'}${result.candidate.sizing && !result.candidate.sizing.is_feasible ? ' · OOM' : ''}`;
  if (key === 'baseline_a_subscription_cumulative') return result.baselines.baseline_a_eligible ? 'Compliant' : 'Non-compliant / BLOCKED';
  if (key === 'baseline_b_global_api_cumulative') return 'Non-compliant · global endpoint';
  if (key === 'baseline_d_openrouter_value_cumulative') return 'Output value · not a deployment';
  if (key === 'hybrid_split_cumulative') return 'See component compliance';
  return 'Compliant · EU-hosted';
}

export function seriesNote(result: TcoProjection, key: SeriesKey) {
  if (key === 'on_prem_cumulative' || key === 'baseline_a_subscription_cumulative' && !result.baselines.baseline_a_eligible) return '';
  const month = result.timeline?.break_even_months.find(([field]) => field === key)?.[1];
  return month == null ? 'No break-even within 60 months' : `t* = ${month} vs on-premise`;
}

export function availableSeries(result?: TcoProjection) {
  return series.filter(([key]) => result?.timeline?.points.some(p => p[key] != null)).map(item => {
    if (item[0] === 'baseline_a_subscription_cumulative' && result?.baselines.baseline_a_eligible) return [item[0], item[1], item[2], 'solid', item[4]] as const;
    if (item[0] !== 'on_prem_cumulative') return item;
    if (result?.candidate.archetype === 'Sovereign Per-Seat Workstation') return [item[0], item[1], colors.skyBlue, 'solid', 3] as const;
    if (result?.candidate.archetype === 'Heterogeneous Modality / Scavenged Rig') return [item[0], item[1], colors.yellow, 'solid', 3] as const;
    return item;
  });
}

export function chartLayout(dark: boolean): Partial<Layout> {
  return { autosize: true, paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
    font: { family: 'JetBrains Mono', size: 10, color: dark ? '#bdc8d1' : '#404750' },
    margin: { l: 60, r: 16, t: 30, b: 48 }, showlegend: false,
    xaxis: { gridcolor: dark ? '#283347' : '#e5e7ef', zeroline: false },
    yaxis: { gridcolor: dark ? '#283347' : '#e5e7ef', zeroline: false },
    hoverlabel: { font: { family: 'JetBrains Mono', size: 11 } },
  };
}

export function tcoChart(result: TcoProjection, currency: Currency, fx: number, dark: boolean): { data: Data[]; layout: Partial<Layout> } {
  const points = result.timeline?.points ?? [];
  const scale = currency === 'EUR' ? 1 / fx : 1; // display conversion only
  const symbol = currency === 'EUR' ? '€' : '$';
  const data: Data[] = availableSeries(result).map(([key, name, color, dash, width]) => ({
    type: 'scatter', mode: key === 'baseline_d_openrouter_value_cumulative' ? 'lines+markers' : 'lines', name: `${name} · ${seriesStatus(result, key)}`,
    x: points.map(p => p.month), y: points.map(p => p[key] == null ? null : p[key]! * scale),
    line: { color, dash, width }, marker: { symbol: 'diamond', size: 4, color },
    hovertemplate: `${name} · ${seriesStatus(result, key)}<br>Month %{x}<br>${symbol}%{y:,.2f} ${currency}<extra></extra>`,
  }));
  const base = chartLayout(dark);
  if (!data.length) return { data, layout: { ...base, annotations: [{ text: 'No data available', x: .5, y: .5, xref: 'paper', yref: 'paper', showarrow: false }] } };
  const annotations: Partial<Layout>['annotations'] = [];
  for (const [key, name, color] of availableSeries(result)) {
    if (key === 'on_prem_cumulative' || key === 'baseline_a_subscription_cumulative' && !result.baselines.baseline_a_eligible) continue;
    const month = result.timeline?.break_even_months.find(([field]) => field === key)?.[1];
    const point = points.find(p => p.month === month);
    if (month != null && point) {
      data.push({ type: 'scatter', mode: 'markers', name: `t* = ${month} · ${name}`, x: [month], y: [point.on_prem_cumulative * scale], line: { color }, marker: { color, symbol: 'diamond', size: 9 }, hovertemplate: `${name}<br>t* = ${month}<br>${symbol}%{y:,.2f} ${currency}<extra></extra>` });
      annotations.push({ x: month, y: point.on_prem_cumulative * scale, text: `t* = ${month}`, showarrow: true, arrowcolor: color, ay: -25 - (annotations.length % 3) * 18, font: { size: 10 } });
    }
  }
  const danger = result.candidate.utilization != null && result.candidate.utilization < .7;
  const shapes: Partial<Shape>[] = danger ? [{ type: 'rect', x0: 0, x1: 1, y0: 0, y1: 1, xref: 'paper', yref: 'paper', fillcolor: colors.orange, opacity: .06, line: { width: 0 }, layer: 'below' }] : [];
  if (danger) annotations.push({ text: 'Utilization Danger Zone (<70%)', x: 0, y: 1.05, xref: 'paper', yref: 'paper', xanchor: 'left', showarrow: false, font: { size: 10 } });
  return { data, layout: { ...base, hovermode: 'x unified', shapes, height: 440,
    margin: { l: 100, r: 18, t: 35, b: 48 },
    xaxis: { ...base.xaxis, title: { text: 'Month' }, range: [1, 60], tickvals: [1, 12, 24, 36, 48, 60] },
    yaxis: { ...base.yaxis, title: { text: currency }, tickprefix: symbol, tickformat: ',.2f', automargin: true }, annotations,
  } };
}

const segments = [['weights', colors.blue], ['kv_cache_active', colors.skyBlue], ['agent_state_parked', colors.green], ['os_reserved', colors.yellow], ['runtime_overhead', colors.purple]] as const;
export function memoryChart(result: SizeResult, dark: boolean): { data: Data[]; layout: Partial<Layout> } {
  const sizing = result.sizing;
  const base = chartLayout(dark);
  const breakdown = Object.fromEntries(sizing.memory_breakdown);
  const max = Math.max(sizing.usable_memory_gb, sizing.usable_system_ram_gb ?? 0, sizing.memory_breakdown.reduce((sum, [, value]) => sum + value, 0)) * 1.15;
  const thresholds = [['Usable memory', sizing.usable_memory_gb, 'dash'], ['System RAM', sizing.usable_system_ram_gb, 'dot']] as const;
  const agreement = sizing.token_agreement_rate == null ? 'n/a' : `${(sizing.token_agreement_rate * 100).toFixed(1)}%`;
  return { data: segments.map(([name, color]) => ({
    type: 'bar', orientation: 'h', name: name.replaceAll('_', ' '), x: [breakdown[name] ?? 0], y: ['Selected pairing'],
    marker: { color, line: { color: colors.black, width: .5 }, pattern: { shape: sizing.context_eviction_risk ? '/' : '', fgcolor: colors.vermillion } }, hovertemplate: `${name.replaceAll('_', ' ')}: %{x:.2f} GB<extra></extra>`,
  })), layout: { ...base, height: 250, barmode: 'stack', bargap: 0.65,
    margin: { l: 12, r: 25, b: 65, t: 70 },
    yaxis: { visible: false }, xaxis: { ...base.xaxis, title: { text: 'Memory (GB) · cluster totals' }, range: [0, max] },
    shapes: thresholds.filter(([, value]) => value != null).map(([, value, dash]) => ({ type: 'line', x0: value!, x1: value!, y0: 0, y1: 1, yref: 'paper', line: { color: colors.black, dash, width: 2 } })),
    annotations: [
      ...thresholds.filter(([, value]) => value != null).map(([name, value], index) => ({ x: value!, y: 1, yref: 'paper' as const, text: `${name} ${value!.toFixed(1)} GB`, showarrow: false, yshift: 18 + index * 18 })),
      { x: 0, y: -.3, xref: 'paper', yref: 'paper', xanchor: 'left', text: `AA v5 ${result.aa_index_v5?.value.toFixed(1) ?? 'n/a'} · agreement ${agreement}`, showarrow: false },
      ...(sizing.context_eviction_risk ? [{ x: 0, y: 1.45, xref: 'paper' as const, yref: 'paper' as const, xanchor: 'left' as const, text: 'EVICTION RISK', showarrow: false }] : []),
    ],
  } };
}
