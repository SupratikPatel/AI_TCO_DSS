import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: './tests', testMatch: '**/*.spec.ts', workers: 1,
  use: { baseURL: 'http://127.0.0.1:5173', viewport: { width: 1280, height: 1100 }, deviceScaleFactor: 1, trace: 'retain-on-failure' },
  webServer: { command: 'node scripts/dev.mjs', cwd: '..', url: 'http://127.0.0.1:5173/api/v1/health', reuseExistingServer: !process.env.CI, timeout: 30000 },
});
