import { expect, test } from '@playwright/test';

test('simultaneous peak capacity rejects a three-slot local option with a visible reason', async ({ page }) => {
  await page.goto('/');
  await page.getByLabel('Active users').fill('1');
  await page.getByLabel('Cost assumptions').selectOption('self-managed');
  await page.getByRole('button', { name: 'cheapest', exact: true }).click();
  const response = page.waitForResponse(r => r.url().endsWith('/evaluate') && r.status() === 200);
  await page.getByRole('button', { name: 'Apply scenario', exact: true }).click();
  const result = await (await response).json();
  const id = 'onprem:mac-studio-m5-max-128gb:1x:qwen-3-8-flash-next:INT3';
  const rejected = result.recommendation.rejected.find((c: { candidate_id: string }) => c.candidate_id === id);
  expect(rejected.sizing.max_concurrent_users).toBe(3);
  expect(rejected.failures).toContainEqual({
    name: 'peak_capacity',
    measured: '3 resident request slots',
    threshold: '>= 5 simultaneous requests at target context',
  });
  expect(result.recommendation.ranked.some((c: { evaluation: { candidate_id: string } }) => c.evaluation.candidate_id === id)).toBe(false);
  await page.getByText(/Rejected candidates/).click();
  const index = result.recommendation.rejected.findIndex((c: { candidate_id: string }) => c.candidate_id === id);
  for (let current = 0; current < Math.floor(index / 10); current++) {
    await page.getByRole('button', { name: 'Next rejections', exact: true }).click();
  }
  const card = page.locator('.rejected-list article').filter({ has: page.getByRole('heading', { name: rejected.label, exact: true }) });
  await expect(card.getByText('peak_capacity', { exact: true })).toBeVisible();
  await expect(card).toContainText('3 resident request slots');
  await expect(card).toContainText('>= 5 simultaneous requests at target context');
});
