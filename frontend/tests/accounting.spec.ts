import { expect, test } from '@playwright/test';

test('simulator calculations explain source assumptions, zero costs and resale without changing ranking', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Apply scenario', exact: true }).click();
  await expect(page.getByTestId('ranking-result')).toBeVisible();
  const ranking = await page.getByTestId('ranking-result').innerText();
  await page.getByRole('tab', { name: /60-month TCO/ }).click();
  const panel = page.getByRole('region', { name: 'Simulator cost accounting' });
  await expect(panel).toContainText('$308,347.20');
  await expect(panel).toContainText('$17,322.31');
  await expect(panel).toContainText('Utilization: 4.7%');
  await expect(panel).not.toContainText('likely to exceed');
  await panel.getByRole('button', { name: 'Show calculation for Hardware CapEx' }).focus();
  await page.keyboard.press('Enter');
  await expect(panel.locator('#cost-detail-capex')).toContainText('17864');
  await expect(panel.locator('#cost-detail-capex')).toContainText('assumption');
  await expect(panel.locator('#cost-detail-capex')).toContainText('2026-11-07');
  await panel.getByRole('button', { name: 'Show calculation for NIM licensing' }).click();
  await expect(panel.locator('#cost-detail-nim_licensing')).toContainText('Disabled');
  await panel.getByRole('button', { name: 'Show calculation for Baseline C monthly' }).click();
  await expect(panel.locator('#cost-detail-baseline_c')).toContainText('gateway');
  await expect(panel.locator('#cost-detail-baseline_c')).toContainText('1.10');
  await page.getByLabel('Include resale value').check();
  await page.getByRole('button', { name: 'Run cost projection' }).click();
  await expect(panel).toContainText('after resale deduction');
  await expect(panel).not.toContainText('before resale');
  const original = await panel.innerText();
  const calls: string[] = [];
  page.on('request', r => { if (r.url().includes('/api/v1/')) calls.push(r.url()); });
  await page.getByRole('button', { name: 'EUR', exact: true }).click();
  await expect(panel).toContainText('€');
  await expect(panel).toContainText('1.116500 USD/EUR');
  await page.getByRole('button', { name: 'USD', exact: true }).click();
  expect(await panel.innerText()).toBe(original);
  expect(calls).toEqual([]);
  await page.getByRole('tab', { name: 'Ranking', exact: true }).click();
  expect(await page.getByTestId('ranking-result').innerText()).toBe(ranking);
});

for (const width of [1280, 1440, 768, 390]) for (const theme of ['light', 'dark']) {
  test(`accounting calculation disclosure ${theme} ${width}`, async ({ page }) => {
    await page.setViewportSize({ width, height: 1100 });
    await page.goto('/');
  await page.getByRole('button', { name: 'Apply scenario', exact: true }).click();
    if (theme === 'dark') await page.getByRole('button', { name: 'Dark theme' }).click();
    await page.getByRole('tab', { name: /60-month TCO/ }).click();
    const panel = page.getByRole('region', { name: 'Simulator cost accounting' });
    await panel.getByRole('button', { name: 'Show calculation for Hardware CapEx' }).click();
    await expect(panel.locator('#cost-detail-capex')).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await expect(panel).toHaveScreenshot(`accounting-${theme}-${width}.png`, { animations: 'disabled' });
  });
}
