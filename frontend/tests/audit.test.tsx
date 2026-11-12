import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import { AuditDrawer } from '../src/components/AuditDrawer';
import type { Schema } from '../src/api/client';

afterEach(() => { cleanup(); vi.unstubAllGlobals(); });
const result = { recommendation: { ranked: [
  { rank: 1, evaluation: { candidate_id: 'first', label: 'First candidate' } },
  { rank: 2, evaluation: { candidate_id: 'second', label: 'Second candidate' } },
] }, timeline: { anchor_candidate_id: 'first' }, fx_rate: 1.1165, fx_source_id: 'ECB-FX', fx_rate_date: '2026-11-07' } as unknown as Schema['ScenarioResult'];

it('36.6/7: starts collapsed, reflects selection, disables unavailable/currently updating exports', () => {
  const select = vi.fn();
  const { rerender } = render(<AuditDrawer result={result} selected="first" onSelect={select} currency="USD" />);
  expect(screen.getByText('Audit & Export').closest('details')?.open).toBe(false);
  fireEvent.click(screen.getByText('Audit & Export'));
  fireEvent.change(screen.getByLabelText('Audit candidate'), { target: { value: 'second' } });
  expect(select).toHaveBeenCalledWith('second');
  rerender(<AuditDrawer onSelect={select} currency="USD" unavailable="Calculating current scenario" />);
  expect(screen.getByText(/No Candidate is available for audit/)).toBeTruthy();
  expect(screen.getByRole('button', { name: 'Export JSON' }).hasAttribute('disabled')).toBe(true);
  expect(screen.getByRole('button', { name: 'Export CSV (zip)' }).hasAttribute('disabled')).toBe(true);
});

it('36.1/2/3 and 43.6: renders real formulas, origins, assumption badges, sources and FX', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({
    candidate_id: 'first', formulas: [{ section: 'sizing', trace: { name: 'weights', symbolic: 'P * bits / 8', substituted: '27e9 * 4 / 8 bytes', result: 13.5, unit: 'GB' } }],
    performance: { decode_tps: { value: 14.7, unit: 'tok/s', origin: { origin: 'measured', source_ids: ['YT-18'] } }, prefill_tps: null, ttft_s: null, effective_tps: null, prefill_1m_minutes: null },
    sources: [{ source_id: 'YT-18', title: 'Real benchmark', url: 'https://example.org/benchmark', reference: null, tier: 'community', provenance: [{ accessed: '2026-11-07', tier: 'community', path: 'decode' }] }, { source_id: 'SPEC-03', title: 'Price assumption', reference: 'spec 03', tier: 'assumption', provenance: [{ accessed: '2026-11-07', tier: 'assumption', path: 'street_price', value: 100 }] }],
    fx: { rate: 1.1165, source_id: 'ECB-FX', rate_date: '2026-11-07', is_override: false },
  }))));
  render(<AuditDrawer result={result} selected="first" onSelect={() => {}} currency="EUR" />);
  fireEvent.click(screen.getByText('Audit & Export'));
  await waitFor(() => expect(screen.getByText('P * bits / 8')).toBeTruthy());
  expect(screen.getByText('27e9 * 4 / 8 bytes')).toBeTruthy();
  expect(screen.getByText('measured')).toBeTruthy();
  expect(screen.getByRole('link', { name: 'Real benchmark' }).getAttribute('href')).toBe('https://example.org/benchmark');
  expect(screen.getAllByText('assumption').filter(el => el.classList.contains('badge'))).toHaveLength(1);
  expect(screen.getByText(/1.116500 USD\/EUR/)).toBeTruthy();
});

it('cancelled currency transitions never leave a download stuck busy', async () => {
  vi.stubGlobal('fetch', vi.fn(() => new Promise(() => {})));
  const { rerender } = render(<AuditDrawer result={result} selected="first" onSelect={() => {}} currency="EUR" />);
  fireEvent.click(screen.getByRole('button', { name: 'Export JSON' }));
  expect(screen.getByRole('button', { name: 'Export JSON' }).hasAttribute('disabled')).toBe(true);
  rerender(<AuditDrawer result={result} selected="first" onSelect={() => {}} currency="USD" />);
  rerender(<AuditDrawer result={result} selected="first" onSelect={() => {}} currency="EUR" />);
  expect(screen.getByRole('button', { name: 'Export JSON' }).hasAttribute('disabled')).toBe(false);
});
