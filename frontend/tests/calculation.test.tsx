// Requirement 43.7: abort, stale results, errors and independent request identities.
import { act, renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useCalculation } from '../src/hooks/useCalculation';
import { request } from '../src/api/client';

vi.mock('../src/api/client', () => ({ request: vi.fn() }));
const mockedRequest = vi.mocked(request);

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (error: Error) => void;
  const promise = new Promise<T>((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}
beforeEach(() => { mockedRequest.mockReset(); });

describe('calculation lifecycle', () => {
  it('ignores a superseded response even if its transport does not honor cancellation', async () => {
    const old = deferred<string>(); const fresh = deferred<string>();
    mockedRequest.mockReturnValueOnce(old.promise).mockReturnValueOnce(fresh.promise);
    const hook = renderHook(({ value }) => useCalculation<string>('/size', { value }), { initialProps: { value: 1 } });
    expect(hook.result.current.loading).toBe(true);
    const oldSignal = mockedRequest.mock.calls[0][2];
    hook.rerender({ value: 2 });
    expect(oldSignal?.aborted).toBe(true);
    await act(async () => fresh.resolve('new'));
    await act(async () => old.resolve('old'));
    expect(hook.result.current.data).toBe('new');
    expect(hook.result.current.key).toBe('{"value":2}');
  });
  it('retains the last valid data and its inputs when the server rejects a change', async () => {
    mockedRequest.mockResolvedValueOnce('valid').mockRejectedValueOnce(new Error('validation'));
    const hook = renderHook(({ value }) => useCalculation<string>('/size', { value }), { initialProps: { value: 1 } });
    await waitFor(() => expect(hook.result.current.data).toBe('valid'));
    hook.rerender({ value: 0 });
    await waitFor(() => expect(hook.result.current.error?.message).toBe('validation'));
    expect(hook.result.current.data).toBe('valid');
    expect(hook.result.current.key).toBe('{"value":1}');
  });
  it('does not recompute for an equal input object and cancels on unmount', async () => {
    mockedRequest.mockReturnValue(new Promise(() => {}));
    const hook = renderHook(() => useCalculation('/tco', { value: 1 }));
    hook.rerender();
    expect(mockedRequest).toHaveBeenCalledTimes(1);
    const signal = mockedRequest.mock.calls[0][2];
    hook.unmount();
    expect(signal?.aborted).toBe(true);
  });
});

 it('waits for explicit submission before requesting a recommendation', async () => {
   mockedRequest.mockResolvedValue('result');
   const hook = renderHook(({enabled}) => useCalculation('/evaluate', {}, enabled), {initialProps:{enabled:false}});
   expect(mockedRequest).not.toHaveBeenCalled();
   expect(hook.result.current.loading).toBe(false);
   hook.rerender({enabled:true});
   await waitFor(() => expect(hook.result.current.data).toBe('result'));
 });
