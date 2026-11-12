import { expect, test } from '@playwright/test';

test('Task 13 43.7 two independent browsers keep scenario, selection and currency isolated', async ({ browser }) => {
  const left = await browser.newContext();
  const right = await browser.newContext();
  try {
    const a = await left.newPage(); const b = await right.newPage();
    const start = performance.now();
    await Promise.all([a.goto('/'), b.goto('/')]);
    await Promise.all([a.getByRole('button', {name:'Apply scenario',exact:true}).click(), b.getByRole('button', {name:'Apply scenario',exact:true}).click()]);
    await expect(a.getByTestId('ranking-result')).toBeVisible();
    await expect(b.getByTestId('ranking-result')).toBeVisible();
    expect(performance.now() - start).toBeLessThan(5000);
    const original = await b.getByTestId('ranking-result').innerText();
    await a.getByRole('button', { name: 'EUR', exact: true }).click();
    await a.getByLabel('Active users').fill('10');
    await a.getByRole('button', { name: 'Apply scenario' }).click();
    await expect(a.getByLabel('Active users')).toHaveValue('10');
    await expect(a.getByLabel('Executive metrics')).toHaveAttribute('aria-busy', 'false');
    await expect(b.getByLabel('Active users')).toHaveValue('25');
    expect(await b.getByTestId('ranking-result').innerText()).toBe(original);
    await expect(b.getByRole('button', { name: 'USD', exact: true })).toHaveAttribute('aria-pressed', 'true');
  } finally { await left.close(); await right.close(); }
});
