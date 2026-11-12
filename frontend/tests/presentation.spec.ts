import { expect, test } from '@playwright/test';

for (const width of [1280, 1440, 768, 390]) for (const theme of ['light', 'dark']) {
  test(`Task 11 34.1/37.4/43.3/4/6/7 accessible ${theme} ${width}`, async ({ page }) => {
    await page.setViewportSize({ width, height: 1100 });
    await page.goto('/');
  await page.getByRole('button', { name: 'Apply scenario', exact: true }).click();
    await expect(page.getByTestId('ranking-result')).toBeVisible();
    if (theme === 'dark') await page.getByRole('button', { name: 'Dark theme' }).click();
    await expect(page.locator('.kpi')).toHaveCount(5);
    const kpis = await page.getByLabel('Executive metrics').innerText();
    await page.getByRole('link', { name: 'Skip to analysis' }).focus();
    await page.keyboard.press('Enter');
    await expect(page.getByRole('tab', { name: 'Ranking', exact: true })).toBeFocused();
    await page.keyboard.press('End');
    await expect(page.getByRole('tab', { name: /60-month TCO/ })).toBeFocused();
    await expect(page.getByTestId('tco-result')).toBeVisible();
    expect(await page.getByLabel('Executive metrics').innerText()).toBe(kpis);
    await expect(page.getByLabel('Timeline series and compliance')).toContainText('Non-compliant');
    await page.getByText('Accessible timeline data').click();
    await page.getByRole('region', { name: 'Scrollable timeline data' }).focus();
    await expect(page.getByRole('region', { name: 'Scrollable timeline data' })).toBeFocused();
    const chart = page.locator('.chart-column .js-plotly-plot');
    await expect(chart).toBeVisible();
    const traces = await chart.evaluate(el => (el as unknown as { data: { hovertemplate: string }[] }).data.map(d => d.hovertemplate));
    expect(traces.every(t => t.includes('$%{y:,.2f}'))).toBe(true);
    await page.getByRole('tab', { name: /Memory fit/ }).click();
    await expect(page.getByTestId('memory-result')).toContainText('Compliant');
    await expect(page.getByTestId('memory-result')).toContainText('Token agreement');
    expect(await page.getByLabel('Executive metrics').innerText()).toBe(kpis);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    // WCAG AA normal text against its nearest opaque surface, and control boundaries (1.4.3/1.4.11).
    const contrast = await page.evaluate(() => {
      const rgb = (s: string) => (s.match(/[\d.]+/g) ?? []).map(Number);
      const lum = (c: number[]) => c.slice(0, 3).map(v => v / 255).map(v => v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4).reduce((s, v, i) => s + v * [.2126, .7152, .0722][i], 0);
      const ratio = (a: string, b: string) => { const x = lum(rgb(a)), y = lum(rgb(b)); return (Math.max(x, y) + .05) / (Math.min(x, y) + .05); };
      return [...document.querySelectorAll('.kpi-label,.kpi small,.kpi p,.field>span,.page-note,select,.input')].filter(el => (el as HTMLElement).offsetWidth).map(el => {
        let parent: Element | null = el; let bg = 'rgb(249,249,255)';
        while (parent) { const color = getComputedStyle(parent).backgroundColor; if (color !== 'rgba(0, 0, 0, 0)' && color !== 'transparent') { bg = color; break; } parent = parent.parentElement; }
        const style = getComputedStyle(el);
        return { text: el.textContent?.slice(0, 40), textRatio: ratio(style.color, bg), borderRatio: el.matches('select,.input') ? ratio(style.borderTopColor, bg) : 3 };
      });
    });
    for (const item of contrast) { expect(item.textRatio, item.text).toBeGreaterThanOrEqual(4.5); expect(item.borderRatio, item.text).toBeGreaterThanOrEqual(3); }
  });
}

test('Task 11 34.5/6/7 missing, empty, loading and error KPI semantics', async ({ page }) => {
  await page.route('**/api/v1/evaluate', async route => {
    const response = await route.fetch(); const data = await response.json();
    data.recommendation.ranked[0].evaluation.performance = null;
    data.recommendation.ranked[0].evaluation.utilization = null;
    await route.fulfill({ json: data });
  });
  await page.goto('/');
  await page.getByRole('button', { name: 'Apply scenario', exact: true }).click(); await expect(page.getByTestId('ranking-result')).toBeVisible();
  await expect(page.locator('.kpi').nth(3)).toContainText('Not applicable');
  await expect(page.locator('.kpi').nth(4)).toContainText('Not applicable');
  await page.unroute('**/api/v1/evaluate');
  await page.route('**/api/v1/evaluate', async route => {
    const response = await route.fetch(); const data = await response.json(); data.recommendation.ranked = [];
    await route.fulfill({ json: data });
  });
  await page.getByRole('button', { name: 'popular', exact: true }).click();
  await expect(page.locator('.kpi').first()).toContainText('No feasible option');
  await page.getByRole('tab', { name: /Memory fit/ }).click();
  await page.locator('.kpi').getByRole('button', { name: 'Review rejected candidates' }).click();
  await expect(page.locator('#rejected-candidates')).toHaveAttribute('open', '');
  await expect(page.locator('#rejected-candidates>summary')).toBeFocused();
  await page.unroute('**/api/v1/evaluate');
  await page.route('**/api/v1/evaluate', async route => {
    await new Promise(resolve => setTimeout(resolve, 500));
    await route.fulfill({ status: 500, json: { code: 'server_error', message: 'Failed', fields: [] } });
  });
  await page.getByRole('button', { name: 'cheapest', exact: true }).click();
  await expect(page.getByLabel('Executive metrics')).toHaveAttribute('aria-busy', 'true');
  await expect(page.getByRole('alert').filter({ hasText: 'KPIs could not be computed' })).toBeVisible();
  for (const card of await page.locator('.kpi').all()) await expect(card).not.toContainText(/\$|tok\/s|\d%/);
});

test('Task 11 43.7 TCO and memory preserve each other and rank-one KPIs', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Apply scenario', exact: true }).click(); await expect(page.getByTestId('ranking-result')).toBeVisible();
  await page.getByRole('tab', { name: /Memory fit/ }).click();
  await expect(page.getByTestId('memory-result')).toBeVisible();
  const memory = await page.getByTestId('memory-result').innerText();
  const kpis = await page.getByLabel('Executive metrics').innerText();
  const calls: string[] = [];
  page.on('request', r => { if (/\/(size|tco|evaluate)$/.test(r.url())) calls.push(r.url().split('/').at(-1)!); });
  await page.getByRole('tab', { name: /60-month TCO/ }).click();
  await page.getByLabel('TCO context (tokens)').fill('8192');
  await page.getByRole('button', { name: 'Run cost projection' }).click();
  await expect(page.getByTestId('tco-result')).toBeVisible();
  await expect(page.getByRole('status')).toHaveCount(0);
  expect(calls).toEqual(['tco']);
  const tco = await page.getByTestId('tco-result').innerText();
  await page.getByRole('tab', { name: /Memory fit/ }).click();
  expect(await page.getByTestId('memory-result').innerText()).toBe(memory);
  await page.getByLabel('Memory context (tokens)').fill('16384');
  await page.getByRole('button', { name: 'Run memory simulation' }).click();
  await expect(page.getByTestId('memory-result')).toContainText('16,384');
  expect(calls).toEqual(['tco', 'size']);
  expect(await page.getByLabel('Executive metrics').innerText()).toBe(kpis);
  await page.getByRole('tab', { name: /60-month TCO/ }).click();
  expect(await page.getByTestId('tco-result').innerText()).toBe(tco);
});
