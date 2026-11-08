import { expect, test } from '@playwright/test';

async function expert(page: import('@playwright/test').Page) {
  await page.goto('/');
  await expect(page.getByTestId('ranking-result')).toBeVisible();
  await page.getByRole('button', { name: 'Expert', exact: true }).click();
}

test('Task 10 full Expert inputs, preset initialization, paired ranks and Normal reset (30.1/3/4, 33.3-5)', async ({ page }) => {
  await expert(page);
  for (const name of ['Target TPS', 'Target TTFT (s)', 'Concurrent agents', 'Peak concurrent requests', 'Target context (tokens)', 'KV quantization precision', 'Harness', 'Thinking effort', 'FX override (USD/EUR)', 'Expert local token share', 'Weight: tco 60m']) await expect(page.getByLabel(name, { exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'SAW', exact: true })).toHaveAttribute('aria-pressed', 'true');
  await page.getByRole('button', { name: 'cheapest', exact: true }).click();
  const options = await (await page.request.get('/api/v1/options')).json();
  await expect(page.getByLabel('Weight: tco 60m', { exact: true })).toHaveValue(String(options.preset_weights.find(([id]: [string]) => id === 'cheapest')[1].tco_60m));
  await page.getByRole('button', { name: 'TOPSIS', exact: true }).click();
  await page.getByLabel('FX override (USD/EUR)', { exact: true }).fill('1.2');
  await page.getByRole('button', { name: 'Apply scenario', exact: true }).click();
  await expect(page.locator('.ranking-meta')).toContainText('TOPSIS');
  await expect(page.locator('.ranking-table th').filter({ hasText: /^SAW rank$/ })).toBeVisible();
  await expect(page.locator('.ranking-table th').filter({ hasText: /^TOPSIS rank$/ })).toBeVisible();
  await expect(page.locator('.ranking-table th').filter({ hasText: /^Closeness$/ })).toBeVisible();
  await expect(page.locator('.recommendation-score')).toContainText('D+');
  await page.getByRole('button', { name: 'Normal', exact: true }).click();
  await expect(page.getByLabel('FX override (USD/EUR)', { exact: true })).not.toBeVisible();
  await expect(page.locator('.ranking-meta')).toContainText('SAW');
  await expect(page.getByRole('button', { name: 'cheapest', exact: true })).toHaveAttribute('aria-pressed', 'true');
  await page.getByRole('button', { name: 'Expert', exact: true }).click();
  await expect(page.getByRole('button', { name: 'SAW', exact: true })).toHaveAttribute('aria-pressed', 'true');
  await expect(page.getByLabel('FX override (USD/EUR)', { exact: true })).toHaveValue('');
});

test('Task 10 invalid FX and weights retain valid results; currency never recomputes (12.4/8, 43.7)', async ({ page }) => {
  await expert(page);
  const before = await page.locator('.recommendation-card').textContent();
  let evaluations = 0;
  page.on('request', r => { if (r.url().endsWith('/evaluate')) evaluations++; });
  for (const fx of ['bad', '0.49', '2.000001', '1.1234567']) {
    await page.getByLabel('FX override (USD/EUR)', { exact: true }).fill(fx);
    await page.getByRole('button', { name: 'Apply scenario', exact: true }).click();
    await expect(page.getByText('Enter a rate from 0.50 to 2.00 with at most 6 decimals.')).toBeVisible();
    await expect(page.locator('.recommendation-card')).toHaveText(before!);
  }
  await page.getByLabel('FX override (USD/EUR)', { exact: true }).fill('1.2');
  await page.getByLabel('Weight: tco 60m', { exact: true }).fill('-1');
  await page.getByRole('button', { name: 'Apply scenario', exact: true }).click();
  await expect(page.getByText('Weights must be finite, non-negative and have a positive sum.')).toBeVisible();
  await page.getByRole('button', { name: 'EUR', exact: true }).click();
  await expect(page.locator('.ranking-table')).toContainText('EUR');
  expect(evaluations).toBe(0);
});

for (const width of [1280, 1440, 768, 390]) for (const theme of ['light', 'dark']) {
  test(`Task 10 Expert reference ${theme} ${width}`, async ({ page }) => {
    await page.setViewportSize({ width, height: 1100 });
    await expert(page);
    await page.getByRole('button', { name: 'TOPSIS', exact: true }).click();
    await page.getByRole('button', { name: 'Apply scenario', exact: true }).click();
    await expect(page.locator('.ranking-meta')).toContainText('TOPSIS');
    if (theme === 'dark') await page.getByRole('button', { name: 'Dark theme' }).click();
    await page.evaluate(() => { document.querySelector('.sidebar')!.scrollTop = 0; return document.fonts.ready; });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await expect(page).toHaveScreenshot(`expert-${theme}-${width}.png`, { fullPage: true });
  });
}

test('Task 10 Expert payload and server validation retain inputs (33.3, 43.7)', async ({ page }) => {
  await expert(page);
  await page.getByLabel('Target TPS', { exact: true }).fill('');
  await page.getByLabel('Target TTFT (s)', { exact: true }).fill('');
  await page.getByLabel('Concurrent agents', { exact: true }).fill('3');
  await page.getByLabel('Peak concurrent requests', { exact: true }).fill('2');
  await page.getByLabel('Target context (tokens)', { exact: true }).fill('64000');
  await page.getByLabel('KV quantization precision', { exact: true }).selectOption('INT4');
  await page.getByLabel('Harness', { exact: true }).selectOption('opencode');
  await page.getByLabel('Thinking effort', { exact: true }).selectOption('low');
  await page.getByLabel('MCP code mode pruning', { exact: true }).check();
  await page.getByLabel('Expert local token share', { exact: true }).fill('0.4');
  await page.getByLabel('Expert include resale value', { exact: true }).check();
  const sent = page.waitForRequest(r => r.url().endsWith('/evaluate'));
  await page.getByRole('button', { name: 'Apply scenario', exact: true }).click();
  const scenario = (await sent).postDataJSON().scenario;
  expect(scenario.workload).toMatchObject({ min_acceptable_tps: null, max_acceptable_ttft_seconds: null, concurrent_agent_instances: 3, peak_concurrent_requests: 2, harness_type: 'opencode', thinking_effort_preset: 'low', mcp_code_mode_pruning: true });
  expect(scenario.sizing).toMatchObject({ target_context_length: 64000, kv_precision: 'INT4' });
  expect(scenario.financials).toMatchObject({ local_offload_ratio: .4, include_resale_value: true });
  await expect(page.getByTestId('ranking-result')).toBeVisible();
  const before = await page.locator('.recommendation-card').textContent();
  await page.getByLabel('Facility PUE', { exact: true }).fill('.9');
  await page.getByRole('button', { name: 'Apply scenario', exact: true }).click();
  await expect(page.getByRole('alert')).toContainText('financials.cooling_pue');
  await expect(page.getByLabel('Target context (tokens)', { exact: true })).toHaveValue('64000');
  await expect(page.locator('.recommendation-card')).toHaveText(before!);
});

test('Task 10 active FX display, USD ranking/break-even invariants and delayed mode transitions', async ({ page }) => {
  await expert(page);
  await page.getByLabel('FX override (USD/EUR)', { exact: true }).fill('1.2');
  const result = page.waitForResponse(r => r.url().endsWith('/evaluate'));
  await page.getByRole('button', { name: 'Apply scenario', exact: true }).click();
  const usd = await (await result).json();
  await expect(page.getByTestId('ranking-result')).toBeVisible();
  const first = usd.recommendation.ranked[0];
  const breakEven = await page.locator('.kpi').nth(1).textContent();
  const usdTable = await page.locator('.ranking-table').textContent();
  let calls = 0;
  page.on('request', r => { if (r.url().endsWith('/evaluate')) calls++; });
  await page.getByRole('button', { name: 'EUR', exact: true }).click();
  await expect(page.locator('.ranking-table tbody tr').first()).toContainText(new Intl.NumberFormat('en-US', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(first.evaluation.cost_60m / 1.2));
  await expect(page.locator('.kpi').nth(1)).toHaveText(breakEven!);
  await page.getByRole('button', { name: 'USD', exact: true }).click();
  await expect(page.locator('.ranking-table')).toHaveText(usdTable!);
  expect(calls).toBe(0);

  let release!: () => void;
  const gate = new Promise<void>(resolve => { release = resolve; });
  await page.route('**/api/v1/scenario/validate', async route => {
    const response = await route.fetch();
    await gate;
    await route.fulfill({ response });
  });
  await page.getByLabel('Active users', { exact: true }).fill('31');
  await page.getByRole('button', { name: 'TOPSIS', exact: true }).click();
  await page.getByRole('button', { name: 'Apply scenario', exact: true }).click();
  await expect(page.getByRole('button', { name: /Validating/ })).toBeVisible();
  await page.getByRole('button', { name: 'Normal', exact: true }).click();
  await expect(page.locator('.ranking-meta')).toContainText('31 users');
  release();
  await page.waitForTimeout(400);
  await expect(page.locator('.ranking-meta')).toContainText('SAW');
  await expect(page.locator('.ranking-table th').filter({ hasText: /^Closeness$/ })).toHaveCount(0);
});

test('Task 10 retained TCO projection keeps its own FX after a failed recalculation', async ({ page }) => {
  await expert(page);
  await page.getByLabel('FX override (USD/EUR)', { exact: true }).fill('1.2');
  const tcoReady = page.waitForResponse(r => r.url().endsWith('/tco'));
  await page.getByRole('button', { name: 'Apply scenario', exact: true }).click();
  await tcoReady;
  await page.getByRole('tab', { name: /60-month TCO/ }).click();
  await expect(page.getByTestId('tco-result')).toBeVisible();
  await page.getByRole('button', { name: 'EUR', exact: true }).click();
  const before = await page.getByTestId('tco-result').textContent();
  await page.route('**/api/v1/tco', route => route.fulfill({ status: 500, json: { code: 'server_error', message: 'Projection failed', fields: [] } }));
  await page.getByLabel('FX override (USD/EUR)', { exact: true }).fill('1.3');
  const evaluated = page.waitForResponse(r => r.url().endsWith('/evaluate'));
  await page.getByRole('button', { name: 'Apply scenario', exact: true }).click();
  await evaluated;
  await expect(page.getByRole('alert')).toContainText('Projection failed');
  await expect(page.getByTestId('tco-result')).toHaveText(before!);
});

for (const theme of ['light', 'dark']) test(`Task 10 inline validation reference ${theme}`, async ({ page }) => {
  await expert(page);
  await page.getByRole('button', { name: 'TOPSIS', exact: true }).click();
  await page.getByRole('button', { name: 'Apply scenario', exact: true }).click();
  await expect(page.locator('.ranking-meta')).toContainText('TOPSIS');
  await page.getByLabel('Active users', { exact: true }).fill('0');
  await page.getByLabel('FX override (USD/EUR)', { exact: true }).fill('2.4591928');
  if (theme === 'dark') await page.getByRole('button', { name: 'Dark theme' }).click();
  await expect(page.getByLabel('Active users', { exact: true })).toHaveAttribute('aria-invalid', 'true');
  await expect(page.getByLabel('FX override (USD/EUR)', { exact: true })).toHaveAttribute('aria-invalid', 'true');
  await page.evaluate(() => { document.querySelector('.sidebar')!.scrollTop = 0; return document.fonts.ready; });
  await expect(page.getByLabel('FX override (USD/EUR)', { exact: true })).toHaveCSS('border-color', theme === 'dark' ? 'rgb(252, 165, 165)' : 'rgb(180, 35, 24)');
  await expect(page).toHaveScreenshot(`expert-validation-${theme}.png`, { fullPage: true, threshold: .05 });
});
