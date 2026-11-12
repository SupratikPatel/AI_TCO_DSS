import { expect, test } from '@playwright/test';
import { readFile } from 'node:fs/promises';

test('Task 12 selected audit, exact JSON and active-currency ZIP downloads', async ({ page, request }) => {
  const responsePromise = page.waitForResponse('**/api/v1/evaluate');
  await page.goto('/');
  await page.getByRole('button', { name: 'Apply scenario', exact: true }).click();
  const result = await (await responsePromise).json();
  await expect(page.getByTestId('ranking-result')).toBeVisible();
  const drawer = page.locator('.audit-drawer');
  await expect(drawer).not.toHaveAttribute('open', '');
  await drawer.locator('summary').first().click();
  await expect(page.getByLabel('Audit candidate')).toHaveValue(result.recommendation.ranked[0].evaluation.candidate_id);
  await expect(drawer.getByRole('heading', { name: 'Formulas & substitutions' })).toBeVisible();
  await page.locator('.ranking-table tbody tr').nth(1).getByRole('button').click();
  await expect(page.getByLabel('Audit candidate')).toHaveValue(result.recommendation.ranked[1].evaluation.candidate_id);
  await expect(drawer.locator('.audit-content')).toContainText(result.recommendation.ranked[1].evaluation.label);
  await page.getByLabel('Audit candidate').selectOption(result.recommendation.ranked[0].evaluation.candidate_id);
  await expect(page.locator('.ranking-table tbody tr').first().getByRole('button')).toHaveAttribute('aria-pressed', 'true');
  await page.getByRole('button', { name: 'EUR', exact: true }).click();
  const jsonEvent = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Export JSON', exact: true }).click();
  const json = await jsonEvent;
  expect(json.suggestedFilename()).toBe('scenario_USD.json');
  expect(JSON.parse(await readFile((await json.path())!, 'utf8'))).toEqual(result);
  const zipEvent = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Export CSV (zip)', exact: true }).click();
  const zip = await zipEvent;
  expect(zip.suggestedFilename()).toBe('scenario_EUR.zip');
  const expectedZip = await request.post('/api/v1/export/csv', { data: { result, currency: 'EUR' } });
  expect(await readFile((await zip.path())!)).toEqual(await expectedZip.body());
  const newResponse = page.waitForResponse('**/api/v1/evaluate');
  await page.getByRole('button', { name: 'cheapest', exact: true }).click();
  const next = await (await newResponse).json();
  await expect(page.getByLabel('Audit candidate')).toHaveValue(next.recommendation.ranked[0].evaluation.candidate_id);
});

test('Task 12 pending, failed, empty and failed downloads cannot export stale results', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Apply scenario', exact: true }).click();
  await expect(page.getByTestId('ranking-result')).toBeVisible();
  await page.locator('.audit-drawer summary').first().click();
  await page.route('**/api/v1/export/json', route => route.fulfill({ status: 500, json: { code: 'server_error', message: 'Download failed', fields: [] } }));
  await page.getByRole('button', { name: 'Export JSON', exact: true }).click();
  await expect(page.locator('.audit-downloads').getByRole('alert')).toContainText('Download failed');
  await page.route('**/api/v1/audit', route => route.fulfill({ status: 500, json: { code: 'server_error', message: 'Audit failed', fields: [] } }));
  await page.locator('.ranking-table tbody tr').nth(1).getByRole('button').click();
  await expect(page.locator('.audit-drawer').getByRole('alert')).toContainText('Audit failed');
  await expect(page.locator('.audit-content')).not.toBeVisible();
  await page.route('**/api/v1/evaluate', async route => {
    await new Promise(resolve => setTimeout(resolve, 700));
    await route.fulfill({ status: 500, json: { code: 'server_error', message: 'Current result failed', fields: [] } });
  });
  await page.getByRole('button', { name: 'cheapest', exact: true }).click();
  await expect(page.getByRole('button', { name: 'Export JSON', exact: true })).toBeDisabled();
  await expect(page.getByRole('button', { name: 'Export CSV (zip)', exact: true })).toBeDisabled();
  await expect(page.locator('.ranking-body').getByRole('alert')).toContainText('Current result failed');
  await expect(page.locator('.audit-drawer')).toContainText('No Candidate is available for audit');
  await expect(page.getByRole('button', { name: 'Export JSON', exact: true })).toBeDisabled();
  await page.unroute('**/api/v1/evaluate');
  await page.route('**/api/v1/evaluate', async route => {
    const response = await route.fetch(); const result = await response.json();
    result.recommendation.ranked = []; result.timeline = null;
    await route.fulfill({ json: result });
  });
  await page.getByRole('button', { name: 'popular', exact: true }).click();
  await expect(page.getByTestId('ranking-result')).toBeVisible();
  await expect(page.locator('.audit-drawer')).toContainText('No Candidate is available for audit');
  await expect(page.getByRole('button', { name: 'Export JSON', exact: true })).toBeEnabled();
  await expect(page.getByRole('button', { name: 'Export CSV (zip)', exact: true })).toBeDisabled();
});

for (const width of [1280, 1440, 768, 390]) for (const theme of ['light', 'dark']) {
  test(`Task 12 audit reference ${theme} ${width}`, async ({ page }) => {
    await page.setViewportSize({ width, height: 1100 });
    await page.goto('/');
  await page.getByRole('button', { name: 'Apply scenario', exact: true }).click();
    await expect(page.getByTestId('ranking-result')).toBeVisible();
    if (theme === 'dark') await page.getByRole('button', { name: 'Dark theme' }).click();
    const summary = page.locator('.audit-drawer summary').first();
    await summary.focus(); await page.keyboard.press('Enter');
    await expect(page.locator('.audit-content')).toBeVisible();
    await expect(page.getByLabel('Audit candidate')).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await page.evaluate(() => document.fonts.ready);
    await page.locator('.audit-drawer').scrollIntoViewIfNeeded();
    await expect(page.locator('.audit-drawer')).toHaveScreenshot(`audit-${theme}-${width}.png`);
    await summary.focus(); await page.keyboard.press('Enter');
    await expect(page.locator('.audit-content')).not.toBeVisible();
  });
}

test('Task 12 ignores delayed audit selection and cancels obsolete downloads', async ({ page }) => {
  const evaluation = page.waitForResponse('**/api/v1/evaluate');
  await page.goto('/');
  await page.getByRole('button', { name: 'Apply scenario', exact: true }).click();
  const result = await (await evaluation).json();
  await expect(page.getByTestId('ranking-result')).toBeVisible();
  const first = result.recommendation.ranked[0].evaluation;
  const second = result.recommendation.ranked[1].evaluation;
  await page.route('**/api/v1/audit', async route => {
    const response = await route.fetch();
    if (route.request().postDataJSON().candidate_id === first.candidate_id) await new Promise(resolve => setTimeout(resolve, 800));
    await route.fulfill({ response });
  });
  const auditStarted = page.waitForRequest('**/api/v1/audit');
  await page.locator('.audit-drawer summary').first().click();
  await auditStarted;
  await page.getByLabel('Audit candidate').selectOption(second.candidate_id);
  await expect(page.locator('.audit-content h2')).toHaveText(second.label);
  await page.waitForTimeout(1000);
  await expect(page.locator('.audit-content h2')).toHaveText(second.label);
  const downloads: string[] = [];
  page.on('download', d => downloads.push(d.suggestedFilename()));
  await page.route('**/api/v1/export/json', async route => {
    const response = await route.fetch();
    await new Promise(resolve => setTimeout(resolve, 800));
    await route.fulfill({ response });
  });
  const exportStarted = page.waitForRequest('**/api/v1/export/json');
  await page.getByRole('button', { name: 'Export JSON', exact: true }).click();
  await exportStarted;
  await page.getByRole('button', { name: 'cheapest', exact: true }).click();
  await expect(page.getByTestId('ranking-result')).toBeVisible();
  await page.waitForTimeout(1000);
  expect(downloads).toEqual([]);
  await expect(page.getByRole('button', { name: 'Export JSON', exact: true })).toBeEnabled();
});
