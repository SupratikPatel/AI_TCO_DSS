import { expect, test } from '@playwright/test';

test('recommendations wait for the first applied scenario', async ({page}) => {
  const calls: string[] = [];
  page.on('request', r => { if (r.url().endsWith('/evaluate')) calls.push(r.url()); });
  await page.goto('/');
  await expect(page.getByRole('heading', {name:'Set up your comparison'})).toBeVisible();
  await expect(page).toHaveScreenshot('setup.png', {fullPage:true});
  await page.getByLabel('Active users').fill('40');
  expect(calls).toHaveLength(0);
  await expect(page.getByTestId('ranking-result')).toHaveCount(0);
  await page.getByRole('button', {name:'Apply scenario',exact:true}).click();
  await expect(page.getByTestId('ranking-result')).toBeVisible();
  await expect(page.locator('.ranking-meta')).toContainText('40 users');
});
