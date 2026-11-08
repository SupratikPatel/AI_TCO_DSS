import type { Data, Layout, Shape } from 'plotly.js';
import type { SizeResult, TcoProjection } from '../api/client';
import type { Currency } from './format';

export const series = [
  ['on_prem_cumulative', 'On-premise', '#0072B2', 'solid', 4],
  ['eu_dedicated_rental_cumulative', 'Dedicated EU rental', '#009E73', 'dashdot', 2.5],
  ['baseline_a_subscription_cumulative', 'A · Consumer sub [BLOCKED]', '#CC79A7', 'dash', 2],
  ['baseline_b_global_api_cumulative', 'B · Global API', '#000000', 'dot', 2],
  ['baseline_c_eu_sovereign_api_cumulative', 'C · EU-pinned API', '#E69F00', 'solid', 3],
  ['baseline_d_openrouter_value_cumulative', 'D · Output market value', '#000000', 'dot', 2],
  ['hybrid_split_cumulative', 'Hybrid split', '#E69F00', 'dash', 2.5],
] as const;

export function availableSeries(result?: TcoProjection) {
  return series.filter(([key]) => result?.timeline?.points.some(p => p[key] != null)).map(item => {
    if (item[0] !== 'on_prem_cumulative') return item;
    if (result?.candidate.archetype === 'Sovereign Per-Seat Workstation') return [item[0], item[1], '#56B4E9', 'solid', 3] as const;
    if (result?.candidate.archetype === 'Heterogeneous Modality / Scavenged Rig') return [item[0], item[1], '#F0E442', 'solid', 3] as const;
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
  const data: Data[] = availableSeries(result).map(([key, name, color, dash, width]) => ({
    type: 'scatter', mode: 'lines', name,
    x: points.map(p => p.month), y: points.map(p => p[key] == null ? null : p[key]! * scale),
    line: { color: dark && color === '#000000' ? '#bdc8d1' : color, dash, width },
    hovertemplate: `${name}<br>Month %{x}<br>${currency} %{y:,.0f}<extra></extra>`,
  }));
  const base = chartLayout(dark);
  const month = result.timeline?.break_even_months.find(([key]) => key === 'baseline_c_eu_sovereign_api_cumulative')?.[1];
  const shapes: Partial<Shape>[] = month == null ? [] : [{ type: 'line', x0: month, x1: month, y0: 0, y1: 1, yref: 'paper', line: { color: '#0072B2', dash: 'dash', width: 1 } }];
  return { data, layout: { ...base, hovermode: 'x unified', shapes, height: 440,
    xaxis: { ...base.xaxis, title: { text: 'Month' }, range: [1, 60], tickvals: [1, 12, 24, 36, 48, 60] },
    yaxis: { ...base.yaxis, title: { text: currency }, tickformat: '~s' },
    annotations: month == null ? [] : [{ x: month, y: 1, yref: 'paper', text: `Month ${month} · break-even vs C`, showarrow: false, yshift: 15, font: { color: dark ? '#8ed5ff' : '#00598c', size: 10 } }],
  } };
}

const segmentColors: Record<string, string> = { weights: '#0072B2', kv_cache_active: '#56B4E9', agent_state_parked: '#009E73', os_reserved: '#F0E442', runtime_overhead: '#CC79A7' };
export function memoryChart(result: SizeResult, dark: boolean): { data: Data[]; layout: Partial<Layout> } {
  const sizing = result.sizing;
  const base = chartLayout(dark);
  return { data: sizing.memory_breakdown.map(([name, value]) => ({
    type: 'bar', orientation: 'h', name: name.replaceAll('_', ' '), x: [value], y: ['Selected pairing'],
    marker: { color: segmentColors[name] }, hovertemplate: `${name.replaceAll('_', ' ')}: %{x:.2f} GB<extra></extra>`,
  })), layout: { ...base, height: 250, barmode: 'stack', bargap: 0.65,
    margin: { l: 12, r: 25, b: 55, t: 45 },
    yaxis: { visible: false }, xaxis: { ...base.xaxis, title: { text: 'Memory (GB) · cluster totals' }, rangemode: 'tozero' },
    shapes: [{ type: 'line', x0: sizing.usable_memory_gb, x1: sizing.usable_memory_gb, y0: 0, y1: 1, yref: 'paper', line: { color: dark ? '#dfe2ee' : '#141b2b', dash: 'dash', width: 2 } }],
    annotations: [{ x: sizing.usable_memory_gb, y: 1, yref: 'paper', text: `Usable ${sizing.usable_memory_gb.toFixed(1)} GB`, showarrow: false, yshift: 18 }],
  } };
}
