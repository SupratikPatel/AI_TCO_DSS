import type { components } from './generated';
export type Schema = components['schemas'];
export type Scenario = Schema['Scenario'];
export type SizeResult = Schema['SizeResult'];
export type TcoProjection = Schema['TcoProjection'];

export class ApiFailure extends Error {
  constructor(public code: string, message: string, public fields: string[] = []) { super(message); }
}
export async function request<T>(path: string, body?: unknown, signal?: AbortSignal): Promise<T> {
  let response: Response;
  try {
    response = await fetch('/api/v1' + path, { signal, ...(body === undefined ? {} : { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }) });
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') throw error;
    throw new ApiFailure('connection_error', 'API connection unavailable. Check that the Python server is running.');
  }
  if (!response.ok) {
    const error = await response.json().catch(() => ({ code: 'server_error', message: 'Server returned an unreadable response.' })) as Schema['ApiError'];
    throw new ApiFailure(error.code, error.message, error.fields ?? []);
  }
  return response.json() as Promise<T>;
}
