import React, { useState } from 'react';
import { FloydStepTraceSchema } from '../../types/lcg';
import { Play, RotateCcw, FastForward } from 'lucide-react';
import { Button } from '../common/Button';

interface CycleGraphProps {
  traces: FloydStepTraceSchema[];
  periodLambda: number;
  cycleStartMu: number;
}

export const CycleGraph: React.FC<CycleGraphProps> = ({
  traces,
  periodLambda,
  cycleStartMu,
}) => {
  const [currentStepIdx, setCurrentStepIdx] = useState<number>(0);

  if (!traces || traces.length === 0) {
    return (
      <div className="p-4 text-center text-sm text-slate-500 font-mono">
        No cycle trace data available.
      </div>
    );
  }

  const currentTrace = traces[Math.min(currentStepIdx, traces.length - 1)];
  const isMatch = currentTrace?.tortoise === currentTrace?.hare;

  const nextStep = () => {
    setCurrentStepIdx((prev) => Math.min(prev + 1, traces.length - 1));
  };

  const jumpToEnd = () => {
    setCurrentStepIdx(traces.length - 1);
  };

  const reset = () => {
    setCurrentStepIdx(0);
  };

  return (
    <div className="p-4 bg-slate-50 dark:bg-slate-900/60 rounded-xl border border-slate-200 dark:border-slate-800">
      <div className="flex flex-wrap items-center justify-between gap-4 pb-3 border-b border-slate-200 dark:border-slate-800">
        <div>
          <span className="text-xs uppercase tracking-wider font-semibold text-slate-500 dark:text-slate-400">
            Floyd Tortoise &amp; Hare Stepper
          </span>
          <div className="flex items-center gap-3 mt-1">
            <span className="text-sm font-mono font-medium">
              Step {currentTrace.step} / {traces[traces.length - 1].step}
            </span>
            {isMatch && (
              <span className="text-xs px-2 py-0.5 rounded-full font-bold bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-700">
                Tortoise == Hare (Meeting Point Found!)
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={reset} icon={<RotateCcw className="w-3.5 h-3.5" />}>
            Reset
          </Button>
          <Button variant="secondary" size="sm" onClick={nextStep} icon={<Play className="w-3.5 h-3.5" />}>
            Step
          </Button>
          <Button variant="primary" size="sm" onClick={jumpToEnd} icon={<FastForward className="w-3.5 h-3.5" />}>
            Fast-Forward
          </Button>
        </div>
      </div>

      {/* Visual Track */}
      <div className="my-6 grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Tortoise Pointer */}
        <div className="p-3 bg-white dark:bg-slate-800/80 rounded-xl border border-slate-200 dark:border-slate-700 shadow-xs">
          <div className="flex items-center justify-between text-xs font-semibold text-indigo-600 dark:text-indigo-400 mb-2">
            <span>🐢 Tortoise (Speed = 1 step)</span>
            <span className="font-mono text-slate-400">X_i</span>
          </div>
          <div className="text-2xl font-mono font-bold text-slate-900 dark:text-slate-100">
            {currentTrace.tortoise.toLocaleString()}
          </div>
          <div className="mt-2 text-[11px] text-slate-500 dark:text-slate-400">
            Advances single step per iteration: X_{'{i+1}'} = f(X_i)
          </div>
        </div>

        {/* Hare Pointer */}
        <div className="p-3 bg-white dark:bg-slate-800/80 rounded-xl border border-slate-200 dark:border-slate-700 shadow-xs">
          <div className="flex items-center justify-between text-xs font-semibold text-amber-600 dark:text-amber-400 mb-2">
            <span>🐇 Hare (Speed = 2 steps)</span>
            <span className="font-mono text-slate-400">X_2i</span>
          </div>
          <div className="text-2xl font-mono font-bold text-slate-900 dark:text-slate-100">
            {currentTrace.hare.toLocaleString()}
          </div>
          <div className="mt-2 text-[11px] text-slate-500 dark:text-slate-400">
            Advances two steps per iteration: X_{'{2i+2}'} = f(f(X_{'{2i}'}))
          </div>
        </div>
      </div>

      {/* Summary Chips */}
      <div className="flex flex-wrap items-center justify-between gap-2 text-xs font-mono bg-white dark:bg-slate-950 p-3 rounded-lg border border-slate-200 dark:border-slate-800">
        <div>
          Cycle Period <span className="font-bold text-indigo-600 dark:text-indigo-400">&lambda; = {periodLambda.toLocaleString()}</span>
        </div>
        <div>
          Transient Tail <span className="font-bold text-amber-600 dark:text-amber-400">&mu; = {cycleStartMu.toLocaleString()}</span>
        </div>
        <div className="text-slate-500">
          Memory Complexity: <span className="text-emerald-600 font-bold">O(1)</span>
        </div>
      </div>
    </div>
  );
};
