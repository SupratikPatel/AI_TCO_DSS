// Requirement 43.9: real child-process startup and cleanup.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import net from 'node:net';
import { startDev } from './dev.mjs';

async function ready(url) {
  for (let attempt = 0; attempt < 100; attempt++) {
    try { if ((await fetch(url)).ok) return; } catch { /* starting */ }
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  throw Error('Server did not start: ' + url);
}

test('starts API and Vite and releases both ports on stop', async () => {
  const dev = startDev();
  try {
    await Promise.all([ready('http://127.0.0.1:8000/api/v1/health'), ready('http://127.0.0.1:5173')]);
    assert.equal((await fetch('http://127.0.0.1:5173/api/v1/health')).status, 200);
  } finally { await dev.stop(); }
  for (const port of [8000, 5173]) {
    await new Promise((resolve, reject) => {
      const server = net.createServer();
      server.once('error', reject);
      server.listen(port, '127.0.0.1', () => server.close(resolve));
    });
  }
});
