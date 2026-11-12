import { useEffect, useState } from 'react';
import { request } from '../api/client';

export function useCalculation<T>(path: string, body: unknown, enabled = true) {
  const [state, setState] = useState<{ data?: T; loading: boolean; error?: Error; key?: string }>({ loading: enabled });
  const serialized = JSON.stringify(body);
  useEffect(() => {
    if (!enabled) return;
    const controller = new AbortController();
    let current = true;
    setState(old => ({ ...old, loading: true, error: undefined }));
    request<T>(path, JSON.parse(serialized), controller.signal).then(data => {
      if (current) setState({ data, loading: false, key: serialized });
    }).catch(error => {
      if (current) setState(old => ({ ...old, error, loading: false }));
    });
    return () => { current = false; controller.abort(); };
  }, [path, serialized, enabled]);
  return state;
}
