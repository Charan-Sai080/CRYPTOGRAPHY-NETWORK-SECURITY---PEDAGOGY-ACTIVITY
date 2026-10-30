import React, { useState } from 'react';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { AlertBanner } from '../../common/AlertBanner';
import { CycleGraph } from '../../visualizers/CycleGraph';
import { detectCycle } from '../../../api/lcgApi';
import { parseApiError } from '../../../api/client';
import { CycleDetectResponse } from '../../../types/lcg';
import { Repeat, Play } from 'lucide-react';

interface FloydCycleCardProps {
  params: { m: number; a: number; c: number; seed: number };
}

export const FloydCycleCard: React.FC<FloydCycleCardProps> = ({ params }) => {
  const [cycleData, setCycleData] = useState<CycleDetectResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleRunDetection = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await detectCycle({
        m: params.m,
        a: params.a,
        c: params.c,
        seed: params.seed,
        max_steps: 10000,
      });
      setCycleData(res);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card
      title="Floyd's Cycle Detection (Tortoise and Hare Algorithm)"
      subtitle="Empirically find repeating sequence period λ and transient start μ in O(1) space"
      icon={<Repeat className="w-5 h-5 text-indigo-500" />}
      action={
        <Button
          variant="primary"
          size="sm"
          onClick={handleRunDetection}
          isLoading={isLoading}
          icon={<Play className="w-3.5 h-3.5" />}
        >
          Run Cycle Detection
        </Button>
      }
    >
      {error && (
        <AlertBanner
          type="error"
          message={error}
          onClose={() => setError(null)}
          className="mb-4"
        />
      )}

      {cycleData ? (
        <div className="space-y-4">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
            <div className="p-3 rounded-lg bg-indigo-50 dark:bg-indigo-950/50 border border-indigo-200 dark:border-indigo-900">
              <span className="text-slate-500 block text-[10px]">Empirical Period (&lambda;):</span>
              <span className="text-lg font-bold text-indigo-600 dark:text-indigo-400">
                {cycleData.period.toLocaleString()}
              </span>
            </div>
            <div className="p-3 rounded-lg bg-amber-50 dark:bg-amber-950/50 border border-amber-200 dark:border-amber-900">
              <span className="text-slate-500 block text-[10px]">Transient Start (&mu;):</span>
              <span className="text-lg font-bold text-amber-600 dark:text-amber-400">
                {cycleData.cycle_start.toLocaleString()}
              </span>
            </div>
            <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700">
              <span className="text-slate-500 block text-[10px]">Max Period (m):</span>
              <span className="text-lg font-bold text-slate-800 dark:text-slate-200">
                {params.m.toLocaleString()}
              </span>
            </div>
            <div className="p-3 rounded-lg bg-emerald-50 dark:bg-emerald-950/50 border border-emerald-200 dark:border-emerald-900">
              <span className="text-slate-500 block text-[10px]">Full Period Ratio:</span>
              <span className="text-lg font-bold text-emerald-600 dark:text-emerald-400">
                {((cycleData.period / params.m) * 100).toFixed(1)}%
              </span>
            </div>
          </div>

          <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 text-xs text-slate-600 dark:text-slate-400">
            Detected period {cycleData.period} with cycle start at index {cycleData.cycle_start} (Total steps evaluated: {cycleData.total_steps}). Full period: {cycleData.is_full_period ? 'Yes' : 'No'}.
          </div>

          {/* Stepper Visualizer */}
          {cycleData.traces && cycleData.traces.length > 0 && (
            <CycleGraph
              traces={cycleData.traces}
              periodLambda={cycleData.period}
              cycleStartMu={cycleData.cycle_start}
            />
          )}
        </div>
      ) : (
        <div className="p-6 text-center text-xs text-slate-500 font-mono">
          Click &ldquo;Run Cycle Detection&rdquo; to launch Floyd&apos;s algorithm on parameters (m={params.m}, a={params.a}, c={params.c}, seed={params.seed}).
        </div>
      )}
    </Card>
  );
};
