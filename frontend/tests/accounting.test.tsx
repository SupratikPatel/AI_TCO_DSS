import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, expect, it } from 'vitest';
import { TcoAccounting } from '../src/components/TcoAccounting';
import json from './fixtures/accounting.json';
import type { Schema } from '../src/api/client';
const fixture = json as Schema['TcoAccounting'];

afterEach(cleanup);
it('explains simulator costs, assumptions and disabled zero values without asserting APIs are cheaper', () => {
  render(<TcoAccounting data={fixture} currency="USD" warnings={[]} insufficient={false} meetsThreshold={false} />);
  expect(screen.getByText('Monthly cash operating costs')).toBeTruthy();
  expect(screen.getByText('Monthly modeled economic costs')).toBeTruthy();
  expect(screen.getByText('before resale; resale disabled')).toBeTruthy();
  expect(screen.getByText(/Utilization: 4.7%/)).toBeTruthy();
  expect(screen.getByText('$308,347.20')).toBeTruthy();
  expect(screen.getByText('$17,322.31')).toBeTruthy();
  expect(screen.getByText(/49 months/)).toBeTruthy();
  fireEvent.click(screen.getByRole('button', { name: 'Show calculation for Hardware CapEx' }));
  expect(screen.getByText(/4 \* 17864/)).toBeTruthy();
  expect(screen.getAllByText('assumption').length).toBeGreaterThan(0);
  expect(screen.getAllByText(/2026-11-07/).length).toBeGreaterThan(0);
  fireEvent.click(screen.getByRole('button', { name: 'Show calculation for NIM licensing' }));
  expect(screen.getByText('Disabled in this projection.')).toBeTruthy();
});
it('uses the retained result FX and resale state with display-only conversion', () => {
  const { rerender } = render(<TcoAccounting data={fixture} currency="EUR" warnings={[]} insufficient={false} meetsThreshold={false} />);
  expect(screen.getByText('€276,173.04')).toBeTruthy();
  expect(screen.getByText(/1.116500 USD\/EUR/)).toBeTruthy();
  const data = { ...fixture, includes_resale: true, rows: fixture.rows.map(r => r.key === 'cost_60m' ? { ...r, note: 'after resale deduction' } : r) };
  rerender(<TcoAccounting data={data} currency="USD" warnings={[]} insufficient={false} meetsThreshold={false} />);
  expect(screen.getByText('after resale deduction')).toBeTruthy();
  expect(screen.queryByText('before resale; resale disabled')).toBeNull();
});
