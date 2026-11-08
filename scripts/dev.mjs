import { spawn, execFile } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { resolve, dirname } from 'node:path';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
export function startDev({ open = false } = {}) {
  const windows = process.platform === 'win32';
  const python = resolve(root, '.venv', windows ? 'Scripts/python.exe' : 'bin/python');
  const children = [
    spawn(python, ['-m', 'uvicorn', 'ai_tco_dss.api.app:app', '--host', '127.0.0.1', '--port', '8000'], { cwd: root, stdio: 'inherit', windowsHide: true }),
    spawn(process.execPath, [resolve(root, 'node_modules/vite/bin/vite.js'), '--host', '127.0.0.1', '--port', '5173', '--strictPort', ...(open ? ['--open'] : [])], { cwd: resolve(root, 'frontend'), stdio: 'inherit', windowsHide: true }),
  ];
  let stopping;
  const stop = () => stopping ??= Promise.all(children.map(child => new Promise(resolve => {
    if (!child.pid || child.exitCode !== null) return resolve();
    child.once('exit', resolve);
    if (windows) execFile('taskkill', ['/pid', String(child.pid), '/T', '/F'], { windowsHide: true }, () => {});
    else child.kill('SIGTERM');
  })));
  for (const child of children) {
    child.once('error', error => { console.error(error.message); process.exitCode = 1; void stop(); });
    child.once('exit', code => { if (!stopping) { process.exitCode = code || 1; void stop(); } });
  }
  return { stop };
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const dev = startDev({ open: process.argv.includes('--open') });
  for (const signal of ['SIGINT', 'SIGTERM']) process.once(signal, () => { void dev.stop(); });
}
