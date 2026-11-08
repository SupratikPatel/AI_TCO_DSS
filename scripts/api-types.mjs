import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync, mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import openapiTS, { astToString } from 'openapi-typescript';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const temp = mkdtempSync(resolve(tmpdir(), 'ai-tco-openapi-'));
try {
  const schema = resolve(temp, 'openapi.json');
  execFileSync(resolve(root, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python'), [resolve(root, 'scripts/export_openapi.py'), schema], { cwd: root });
  const generated = '// Generated from FastAPI OpenAPI. Run npm run types:generate.\n' + astToString(await openapiTS(JSON.parse(readFileSync(schema, 'utf8'))));
  const target = resolve(root, 'frontend/src/api/generated.ts');
  if (process.argv.includes('--check')) {
    if (readFileSync(target, 'utf8').replaceAll('\r\n', '\n') !== generated) throw Error('API types drifted. Run npm run types:generate.');
    console.log('API types match OpenAPI.');
  } else writeFileSync(target, generated);
} finally { rmSync(temp, { recursive: true }); }
