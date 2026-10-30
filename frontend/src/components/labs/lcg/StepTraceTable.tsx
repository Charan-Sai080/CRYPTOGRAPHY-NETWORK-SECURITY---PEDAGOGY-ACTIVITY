import React, { useState } from 'react';
import { Card } from '../../common/Card';
import { LCGStepTraceSchema } from '../../../types/lcg';
import { ListOrdered } from 'lucide-react';

interface StepTraceTableProps {
  traces: LCGStepTraceSchema[];
  m: number;
}

export const StepTraceTable: React.FC<StepTraceTableProps> = ({ traces, m }) => {
  const [displayCount, setDisplayCount] = useState<number>(10);

  if (!traces || traces.length === 0) return null;

  const visibleTraces = traces.slice(0, displayCount);

  return (
    <Card
      title="Arithmetic Step-by-Step Calculation Trace"
      subtitle="Examine quotient, remainder, and normalization for each step"
      icon={<ListOrdered className="w-5 h-5 text-indigo-500" />}
      action={
        traces.length > 10 && (
          <select
            value={displayCount}
            onChange={(e) => setDisplayCount(Number(e.target.value))}
            className="text-xs p-1.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-mono"
          >
            <option value={10}>Show 10 steps</option>
            <option value={25}>Show 25 steps</option>
            <option value={50}>Show 50 steps</option>
            <option value={traces.length}>Show All ({traces.length})</option>
          </select>
        )
      }
    >
      <div className="overflow-x-auto">
        <table className="w-full text-xs font-mono text-center">
          <thead>
            <tr className="bg-slate-50 dark:bg-slate-800/60 text-slate-600 dark:text-slate-400 border-b border-slate-200 dark:border-slate-800">
              <th className="py-2.5 px-3 text-left">Step (n)</th>
              <th className="py-2.5 px-3">State X_n</th>
              <th className="py-2.5 px-3">Product a &middot; X_n</th>
              <th className="py-2.5 px-3">Sum + c</th>
              <th className="py-2.5 px-3">Quotient &lfloor;S/m&rfloor;</th>
              <th className="py-2.5 px-3 text-indigo-600 dark:text-indigo-400 font-bold">Next X_{'{n+1}'}</th>
              <th className="py-2.5 px-3 text-right">Normalized U_n &isin; [0, 1)</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
            {visibleTraces.map((trace) => {
              const quotient = Math.floor(trace.product_plus_c / m);
              return (
                <tr
                  key={trace.step}
                  className="hover:bg-slate-50/50 dark:hover:bg-slate-800/40 transition-colors"
                >
                  <td className="py-2 px-3 text-left font-semibold text-slate-500">
                    #{trace.step}
                  </td>
                  <td className="py-2 px-3 text-slate-800 dark:text-slate-200">
                    {trace.x_prev.toLocaleString()}
                  </td>
                  <td className="py-2 px-3 text-slate-500">
                    {trace.product.toLocaleString()}
                  </td>
                  <td className="py-2 px-3 text-slate-500">
                    {trace.product_plus_c.toLocaleString()}
                  </td>
                  <td className="py-2 px-3 text-slate-400">
                    {quotient.toLocaleString()}
                  </td>
                  <td className="py-2 px-3">
                    <span className="font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950 px-2 py-0.5 rounded">
                      {trace.x_next.toLocaleString()}
                    </span>
                  </td>
                  <td className="py-2 px-3 text-right text-emerald-600 dark:text-emerald-400 font-bold">
                    {trace.normalized.toFixed(6)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="mt-3 text-[11px] text-slate-500 flex items-center justify-between">
        <span>Modulus m = {m.toLocaleString()}</span>
        <span>
          Showing {visibleTraces.length} of {traces.length} steps
        </span>
      </div>
    </Card>
  );
};
