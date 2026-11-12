import { expect, test } from '@playwright/test';

test('Task 9 Normal controls, Python ranking, rejection reasons and currency', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Apply scenario', exact: true }).click();
  await expect(page.getByRole('tab', { name: 'Ranking', exact: true })).toHaveAttribute('aria-selected', 'true');
  await expect(page.getByTestId('ranking-result')).toBeVisible();
  await expect(page.locator('.recommendation-card')).toContainText('ranks first');
  await expect(page.getByLabel('Use case')).toHaveValue('agentic-coding');
  await expect(page.getByLabel('Active users')).toHaveValue('25');
  await expect(page.getByRole('button', { name: 'best fit', exact: true })).toHaveAttribute('aria-pressed', 'true');
  await page.getByRole('button', { name: 'cheapest', exact: true }).click();
  await expect(page.locator('.ranking-meta')).toContainText('cheapest');
  await page.getByLabel('Use case').selectOption('writing-email');
  await expect(page.locator('.ranking-meta')).toContainText('writing email');
  await page.getByLabel('Active users').fill('80');
  await expect(page.locator('.ranking-meta')).toContainText('80 users');
  const before = await page.locator('.recommendation-card h2').textContent();
  const calls: string[] = [];
  page.on('request', r => { if (r.url().includes('/api/v1/evaluate')) calls.push(r.url()); });
  await page.getByLabel('Active users').fill('0');
  await expect(page.getByRole('alert')).toContainText('1 to 100,000');
  await page.waitForTimeout(400);
  expect(calls).toHaveLength(0);
  await expect(page.locator('.recommendation-card h2')).toHaveText(before!);
  await page.getByRole('button', { name: 'EUR', exact: true }).click();
  await expect(page.locator('.ranking-table')).toContainText('EUR');
  expect(calls).toHaveLength(0);
  await page.getByText(/Rejected candidates/).click();
  await expect(page.locator('.rejected-list')).toBeVisible();
  await expect(page.locator('.rejected-list').getByText('quality_floor', { exact: true }).first()).toBeVisible();
  await page.locator('.ranking-table tbody tr').nth(1).getByRole('button').click();
  await expect(page.getByLabel('Selected candidate contributions')).toContainText('Normalized');
});

for (const width of [1280, 1440, 768, 390]) for (const theme of ['light', 'dark']) {
  test(`Task 9 ranking reference ${theme} ${width}`, async ({ page }) => {
    await page.setViewportSize({ width, height: 1100 });
    await page.goto('/');
  await page.getByRole('button', { name: 'Apply scenario', exact: true }).click();
    await page.getByRole('tab', { name: 'Ranking', exact: true }).click();
    await expect(page.getByTestId('ranking-result')).toBeVisible();
    if (theme === 'dark') await page.getByRole('button', { name: 'Dark theme' }).click();
    await page.evaluate(() => document.fonts.ready);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await expect(page).toHaveScreenshot(`ranking-${theme}-${width}.png`, { fullPage: true });
  });
}

test('Task 9 loading, server error, empty and stale results are distinct', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Apply scenario', exact: true }).click();
  await page.getByRole('tab', { name: 'Ranking', exact: true }).click();
  await expect(page.getByTestId('ranking-result')).toBeVisible();
  await page.route('**/api/v1/evaluate', async route => {
    await route.fulfill({ status: 500, json: { code: 'server_error', message: 'Ranking calculation failed', fields: [] } });
  });
  await page.getByRole('button', { name: 'popular', exact: true }).click();
  await expect(page.locator('.ranking-body').getByRole('alert')).toContainText('Ranking calculation failed');
  await expect(page.getByTestId('ranking-result')).not.toBeVisible();
  await expect(page.locator('.kpi').first()).toContainText('Unavailable');
  await page.unroute('**/api/v1/evaluate');
  await page.route('**/api/v1/evaluate', async route => {
    const response = await route.fetch();
    const result = await response.json();
    result.recommendation.ranked = [];
    result.recommendation.explanation = null;
    await route.fulfill({ json: result });
  });
  await page.getByRole('button', { name: 'cheapest', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'No feasible option', level: 2 })).toBeVisible();
  await expect(page.locator('.kpi').first()).toContainText('No feasible option');
});

test('Task 9 slow superseded recommendations and independent memory inputs', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Apply scenario', exact: true }).click();
  await page.getByRole('tab', { name: 'Ranking', exact: true }).click();
  await expect(page.getByTestId('ranking-result')).toBeVisible();
  let release!: () => void;
  let ready!: () => void;
  const gate = new Promise<void>(resolve => { release = resolve; });
  const oldReady = new Promise<void>(resolve => { ready = resolve; });
  await page.route('**/api/v1/evaluate', async route => {
    if (route.request().postDataJSON().scenario.workload.active_users !== 26) return route.continue();
    const response = await route.fetch();
    ready();
    await gate;
    await route.fulfill({ response });
  });
  await page.getByLabel('Active users').fill('26');
  await expect(page.getByRole('status')).toContainText('Calculating recommendations');
  await oldReady;
  await page.getByLabel('Active users').fill('100000');
  await expect(page.getByRole('heading', { name: 'No feasible option', level: 2 })).toBeVisible();
  release();
  await page.waitForTimeout(400);
  await expect(page.getByRole('heading', { name: 'No feasible option', level: 2 })).toBeVisible();
  const calls: string[] = [];
  page.on('request', r => { if (r.url().endsWith('/evaluate')) calls.push(r.url()); });
  await page.getByRole('tab', { name: /Memory fit/ }).click();
  await page.getByLabel('Memory context (tokens)').fill('8192');
  await page.getByRole('button', { name: 'Run memory simulation' }).click();
  await expect(page.getByTestId('memory-result')).toContainText('8,192');
  expect(calls).toHaveLength(0);
});
