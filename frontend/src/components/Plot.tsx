import { useEffect, useRef } from 'react';
import Plotly from 'plotly.js-basic-dist-min';
import type { Data, Layout } from 'plotly.js';

export function Plot({ data, layout, label }: { data: Data[]; layout: Partial<Layout>; label: string }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const element = ref.current!;
    void Plotly.react(element, data, layout, { responsive: true, displayModeBar: false });
    const observer = new ResizeObserver(() => { if (element.clientWidth) void Plotly.Plots.resize(element); });
    observer.observe(element);
    return () => { observer.disconnect(); Plotly.purge(element); };
  }, [data, layout]);
  return <div ref={ref} role="img" aria-label={label} className="plot" />;
}
