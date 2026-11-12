import { expect, test } from '@playwright/test';

test('43.4/43.7 real size/TCO controls, display currency and validation', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Apply scenario', exact: true }).click();
  await page.getByRole('tab', { name: /60-month TCO/ }).click();
  await expect(page.getByTestId('tco-result')).toBeVisible();
  await expect(page.locator('.kpi').first()).not.toContainText('Calculating');
  const requests: string[] = [];
  page.on('request', r => { if (r.url().includes('/api/v1/')) requests.push(r.url()); });
  await page.getByRole('button', { name: 'EUR', exact: true }).click();
  await expect(page.getByTestId('tco-result')).toContainText('EUR');
  expect(requests).toHaveLength(0);
  await page.getByRole('tab', { name: /Memory fit/ }).click();
  await expect(page.getByTestId('memory-result')).toBeVisible();
  await page.getByLabel('Memory context (tokens)').fill('8192');
  await page.getByRole('button', { name: 'Run memory simulation' }).click();
  await expect(page.getByTestId('memory-result')).toContainText('8,192');
  expect(requests.every(url => !url.endsWith('/tco'))).toBe(true);
  await page.getByLabel('Active users').fill('0');
  await page.getByRole('button', { name: 'Apply scenario' }).click();
  await expect(page.getByRole('alert')).toContainText('active_users');
  await expect(page.getByTestId('memory-result')).toBeVisible();
});

test('43.7 catalog error, retry, loading and server error retain distinct states', async ({ page }) => {
  await page.route('**/api/v1/catalog', route => route.fulfill({ status: 503, json: { code: 'catalog_error', message: 'Catalog unavailable. Check server logs.', fields: [] } }));
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Catalog unavailable' })).toBeVisible();
  await expect(page).toHaveScreenshot('catalog-error.png');
  await page.unroute('**/api/v1/catalog');
  await page.getByRole('button', { name: 'Retry catalog' }).click();
  await page.getByRole('button', { name: 'Apply scenario', exact: true }).click();
  await page.getByRole('tab', { name: /60-month TCO/ }).click();
  await expect(page.getByTestId('tco-result')).toBeVisible();
  await expect(page.locator('.kpi').first()).not.toContainText('Calculating');
  let release!: () => void;
  const gate = new Promise<void>(resolve => { release = resolve; });
  await page.route('**/api/v1/tco', async route => {
    await gate;
    await route.fulfill({ status: 500, json: { code: 'server_error', message: 'Calculation failed. Please retry.', fields: [] } });
  });
  await page.getByLabel('Include resale value').check();
  await page.getByRole('button', { name: 'Run cost projection' }).click();
  await expect(page.getByRole('status')).toContainText('Calculating TCO');
  await page.getByRole('button', { name: 'Apply scenario', exact: true }).click();
  await page.getByRole('tab', { name: /60-month TCO/ }).click();
  await expect(page.getByTestId('tco-result')).toBeVisible();
  await expect(page.locator('.kpi').first()).not.toContainText('Calculating');
  release();
  await expect(page.getByRole('alert')).toContainText('Calculation failed');
  await page.getByRole('button', { name: 'Apply scenario', exact: true }).click();
  await page.getByRole('tab', { name: /60-month TCO/ }).click();
  await expect(page.getByTestId('tco-result')).toBeVisible();
  await expect(page.locator('.kpi').first()).not.toContainText('Calculating');
  await expect(page.getByText('Showing the previous valid projection.')).toBeVisible();
});

test('43.7 initial loading keeps the reference shell and no invented results', async ({ page }) => {
  let release!: () => void;
  const gate = new Promise<void>(resolve => { release = resolve; });
  await page.route('**/api/v1/catalog', async route => { await gate; await route.continue(); });
  await page.goto('/');
  await expect(page.getByRole('status')).toContainText('Loading catalog');
  await expect(page).toHaveScreenshot('catalog-loading.png');
  release();
  await page.getByRole('button', { name: 'Apply scenario', exact: true }).click();
  await page.getByRole('tab', { name: /60-month TCO/ }).click();
  await expect(page.getByTestId('tco-result')).toBeVisible();
  await expect(page.locator('.kpi').first()).not.toContainText('Calculating');
});

test('43.7 infeasible memory is a result, keyboard tabs and expert disclosure work', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Apply scenario', exact: true }).click();
  await page.getByRole('tab', { name: /60-month TCO/ }).click();
  await expect(page.getByTestId('tco-result')).toBeVisible();
  await expect(page.locator('.kpi').first()).not.toContainText('Calculating');
  await page.getByRole('button', { name: 'Expert', exact: true }).click();
  await expect(page.getByLabel('Staffing hub')).toBeVisible();
  await page.getByRole('button', { name: 'Normal', exact: true }).click();
  await expect(page.getByLabel('Staffing hub')).not.toBeVisible();
  await page.getByRole('tab', { name: /60-month TCO/ }).focus();
  await page.keyboard.press('ArrowLeft');
  await expect(page.getByRole('tab', { name: /Memory fit/ })).toBeFocused();
  await page.getByLabel('Memory hardware').selectOption('mac-mini-m5-pro-64gb');
  await page.getByLabel('Memory model').selectOption('qwen-3-8-flash-next');
  await page.getByRole('button', { name: 'Run memory simulation' }).click();
  await expect(page.getByText('No feasible memory fit', { exact: true })).toBeVisible();
  await expect(page.getByTestId('memory-result')).toContainText('Performance is unavailable');
  await expect(page).toHaveScreenshot('memory-oom.png', { fullPage: true });
  await page.getByRole('tab', { name: 'Ranking', exact: true }).click();
  await expect(page.getByTestId('ranking-result')).toBeVisible();
});

for (const width of [1280, 1440, 768, 390]) {
  for (const theme of ['light', 'dark']) {
    test(`43.3/43.4 ${theme} reference at ${width}`, async ({ page }) => {
      await page.setViewportSize({ width, height: 1100 });
      await page.goto('/');
      await page.getByRole('button', { name: 'Apply scenario', exact: true }).click();
  await page.getByRole('tab', { name: /60-month TCO/ }).click();
  await expect(page.getByTestId('tco-result')).toBeVisible();
  await expect(page.locator('.kpi').first()).not.toContainText('Calculating');
      if (theme === 'dark') await page.getByRole('button', { name: 'Dark theme' }).click();
      await page.evaluate(() => document.fonts.ready);
      await expect(page.locator('.chart-column .js-plotly-plot')).toBeVisible();
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
      await expect(page).toHaveScreenshot(`tco-${theme}-${width}.png`, { fullPage: true, animations: 'disabled' });
      await page.getByRole('tab', { name: /Memory fit/ }).click();
      await expect(page.locator('.memory-chart .js-plotly-plot')).toBeVisible();
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
      await expect(page).toHaveScreenshot(`memory-${theme}-${width}.png`, { fullPage: true, animations: 'disabled' });
    });
  }
}
