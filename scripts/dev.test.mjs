// Requirement 43.9: real child-process startup and cleanup.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import net from 'node:net';
import { startDev } from './dev.mjs';

async function ready(url) {
  for (let attempt = 0; attempt < 300; attempt++) {
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

test('startup failure cleans sibling without stopping the process owning the occupied API port', async () => {
  const { spawn } = await import('node:child_process');
  const { createServer } = await import('node:http');
  const owner = createServer((_request, response) => response.end('owned'));
  await new Promise(resolve => owner.listen(8000, '127.0.0.1', resolve));
  const child = spawn(process.execPath, ['scripts/dev.mjs'], { stdio: 'inherit', windowsHide: true });
  try {
    const exit = await new Promise((resolve, reject) => {
      const timer = setTimeout(() => { child.kill(); reject(Error('Startup failure did not terminate launcher')); }, 15000);
      child.once('exit', code => { clearTimeout(timer); resolve(code); });
    });
    assert.notEqual(exit, 0);
    assert.equal((await fetch('http://127.0.0.1:8000')).status, 200);
    await new Promise((resolve, reject) => {
      const port = net.createServer();
      port.once('error', reject);
      port.listen(5173, '127.0.0.1', () => port.close(resolve));
    });
  } finally { owner.closeAllConnections(); await new Promise(resolve => owner.close(resolve)); }
});
