import { expect, test } from '@playwright/test';

test('one user can compare purchase and electricity with a literal cheapest preset', async ({page}) => {
  await page.goto('/');
  await page.getByLabel('Active users').fill('1');
  await page.getByLabel('Cost assumptions').selectOption('self-managed');
  await page.getByRole('button', {name:'cheapest', exact:true}).click();
  const response = page.waitForResponse(r => r.url().endsWith('/evaluate') && r.status() === 200);
  await page.getByRole('button', {name:'Apply scenario', exact:true}).click();
  const result = await (await response).json();
  const ranked = result.recommendation.ranked;
  const top = ranked[0].evaluation;
  expect(top.cost_60m).toBe(Math.min(...ranked.map((r: {evaluation: {cost_60m:number}}) => r.evaluation.cost_60m)));
  expect(top.hardware_id).toContain('mac-');
  expect(top.tco.units).toBe(1);
  expect(top.cost_60m).toBeLessThan(10000);
  expect(Object.fromEntries(top.tco.monthly_opex).personnel).toBe(0);
  await expect(page.getByTestId('ranking-cost-breakdown')).toContainText('Monthly staffing: $0.00');
  for (const width of [1280, 390]) for (const theme of ['Light', 'Dark']) {
    await page.setViewportSize({width, height:1100});
    await page.getByRole('button', {name:`${theme} theme`}).click();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await expect(page).toHaveScreenshot(`self-managed-${theme.toLowerCase()}-${width}.png`, {fullPage:true});
  }
  await page.getByRole('button', {name:'Expert',exact:true}).click();
  await expect(page.getByLabel('Cost assumptions')).toHaveValue('self-managed');
  await page.getByRole('button', {name:'Normal',exact:true}).click();
  await expect(page.getByLabel('Cost assumptions')).toHaveValue('self-managed');
  const enterprise = page.waitForResponse(r => r.url().endsWith('/evaluate') && r.status() === 200);
  await page.getByLabel('Cost assumptions').selectOption('enterprise');
  const changed = await (await enterprise).json();
  expect(changed.recommendation.ranked[0].evaluation.cost_60m).toBeGreaterThan(200000);
  await expect(page.getByTestId('ranking-cost-breakdown')).toContainText('Monthly staffing: $3,567.57');
});
