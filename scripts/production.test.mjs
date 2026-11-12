import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawn, execFile } from 'node:child_process';
import net from 'node:net';
import { gzipSync } from 'node:zlib';
import { readFileSync } from 'node:fs';

const ready = async url => {
  for (let i = 0; i < 150; i++) {
    try { if ((await fetch(url)).ok) return; } catch { /* starting */ }
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  throw Error('Not ready: ' + url);
};

test('production serves built assets and API on one origin; termination releases port', async () => {
  const python = process.platform === 'win32' ? '.venv/Scripts/python.exe' : '.venv/bin/python';
  const child = spawn(python, ['-m', 'uvicorn', 'ai_tco_dss.api.production:create_app', '--factory', '--port', '8000'], { stdio: 'inherit', windowsHide: true });
  const exited = new Promise(resolve => child.once('exit', resolve));
  try {
    await ready('http://127.0.0.1:8000/api/v1/health');
    const html = await (await fetch('http://127.0.0.1:8000/')).text();
    assert.match(html, /id="root"/);
    const assets = [...html.matchAll(/(?:src|href)="(\/assets\/[^\"]+)"/g)];
    assert.ok(assets.length > 0);
    let javascript = 0; let compressed = 0;
    for (const [, asset] of assets) {
      assert.equal((await fetch('http://127.0.0.1:8000' + asset)).status, 200);
      if (asset.endsWith('.js')) {
        const bytes = readFileSync('frontend/dist' + asset);
        javascript += bytes.length; compressed += gzipSync(bytes).length;
      }
    }
    // Measured basic Plotly + React baseline: 1.46 MB raw / 480 KB gzip.
    // Explicit regression budgets keep dependency growth visible.
    assert.ok(javascript < 1_600_000, `Initial JS grew to ${javascript} bytes`);
    assert.ok(compressed < 512_000, `Initial gzip JS grew to ${compressed} bytes`);
    assert.equal((await fetch('http://127.0.0.1:8000/api/v1/missing')).status, 404);
  } finally {
    if (process.platform === 'win32') await new Promise(resolve => execFile('taskkill', ['/pid', String(child.pid), '/T', '/F'], { windowsHide: true }, resolve));
    else child.kill('SIGTERM');
    await exited;
  }
  await new Promise((resolve, reject) => {
    const server = net.createServer();
    server.once('error', reject);
    server.listen(8000, '127.0.0.1', () => server.close(resolve));
  });
});
