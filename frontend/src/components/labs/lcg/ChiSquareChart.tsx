import React, { useState } from 'react';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { AlertBanner } from '../../common/AlertBanner';
import { runChiSquare } from '../../../api/lcgApi';
import { parseApiError } from '../../../api/client';
import { ChiSquareResponse } from '../../../types/lcg';
import { BarChart3, Play } from 'lucide-react';
import { MathFormula } from '../../common/MathFormula';

interface ChiSquareChartProps {
  params: { m: number; a: number; c: number; seed: number };
}

export const ChiSquareChart: React.FC<ChiSquareChartProps> = ({ params }) => {
  const [sampleSize, setSampleSize] = useState<number>(1000);
  const [bins, setBins] = useState<number>(10);
  const [testResult, setTestResult] = useState<ChiSquareResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleRunTest = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await runChiSquare({
        m: params.m,
        a: params.a,
        c: params.c,
        seed: params.seed,
        count: sampleSize,
        num_bins: bins,
      });
      setTestResult(res);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  // Find max observed count for SVG scaling
  const maxObserved = testResult
    ? Math.max(...testResult.bins.map((b) => Math.max(b.observed_count, b.expected_count)))
    : 1;

  return (
    <Card
      title="Chi-Square Goodness-of-Fit Uniformity Test"
      subtitle="Evaluates null hypothesis that LCG outputs are uniformly distributed across [0, 1)"
      icon={<BarChart3 className="w-5 h-5 text-indigo-500" />}
      action={
        <div className="flex items-center gap-2">
          <Button
            variant="primary"
            size="sm"
            onClick={handleRunTest}
            isLoading={isLoading}
            icon={<Play className="w-3.5 h-3.5" />}
          >
            Run Test
          </Button>
        </div>
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

      <div className="space-y-4">
        {/* Controls */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pb-2 border-b border-slate-100 dark:border-slate-800">
          <div>
            <label htmlFor="sample-size" className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Sample Size (N): {sampleSize.toLocaleString()}
            </label>
            <input
              id="sample-size"
              type="range"
              min={100}
              max={10000}
              step={100}
              value={sampleSize}
              onChange={(e) => setSampleSize(Number(e.target.value))}
              className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-600"
            />
          </div>

          <div>
            <label htmlFor="bins-count" className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Histogram Bins (k): {bins}
            </label>
            <input
              id="bins-count"
              type="range"
              min={5}
              max={30}
              value={bins}
              onChange={(e) => setBins(Number(e.target.value))}
              className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-600"
            />
          </div>
        </div>

        {testResult ? (
          <div className="space-y-4">
            {/* Statistical Metrics */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
              <div className="p-3 rounded-lg bg-indigo-50 dark:bg-indigo-950/50 border border-indigo-200 dark:border-indigo-900">
                <span className="text-slate-500 block text-[10px]">&chi;&sup2; Statistic:</span>
                <span className="text-lg font-bold text-indigo-600 dark:text-indigo-400">
                  {testResult.chi_square_stat.toFixed(3)}
                </span>
              </div>
              <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700">
                <span className="text-slate-500 block text-[10px]">Degrees of Freedom:</span>
                <span className="text-lg font-bold text-slate-800 dark:text-slate-200">
                  {testResult.degrees_of_freedom}
                </span>
              </div>
              <div className="p-3 rounded-lg bg-amber-50 dark:bg-amber-950/50 border border-amber-200 dark:border-amber-900">
                <span className="text-slate-500 block text-[10px]">p-value (approx):</span>
                <span className="text-lg font-bold text-amber-600 dark:text-amber-400">
                  {testResult.p_value_approx.toFixed(4)}
                </span>
              </div>
              <div className="p-3 rounded-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                <span className="text-slate-500 block text-[10px]">Critical Value:</span>
                <span className="text-lg font-bold text-slate-800 dark:text-slate-200">
                  {testResult.critical_value.toFixed(2)}
                </span>
              </div>
            </div>

            {/* Verdict */}
            <div
              className={`p-3 rounded-lg border text-xs font-semibold flex items-center justify-between ${
                testResult.is_uniform
                  ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800'
                  : 'bg-rose-50 dark:bg-rose-950/40 text-rose-800 dark:text-rose-300 border-rose-300 dark:border-rose-800'
              }`}
            >
              <span>{testResult.explanation}</span>
              <span className="font-mono text-[11px]">
                {testResult.is_uniform ? 'p > 0.05 (ACCEPT UNIFORM)' : 'p <= 0.05 (REJECT UNIFORM)'}
              </span>
            </div>

            {/* SVG Histogram */}
            <div className="p-4 bg-slate-50 dark:bg-slate-900/60 rounded-xl border border-slate-200 dark:border-slate-800">
              <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
                <span>Observed vs Expected Bin Counts</span>
                <div className="flex items-center gap-3">
                  <span className="flex items-center gap-1">
                    <span className="w-3 h-3 bg-indigo-500 rounded-xs inline-block" />
                    <span>Observed O_i</span>
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="w-3 h-0.5 bg-amber-500 inline-block border-b border-dashed border-amber-500" />
                    <span>Expected E_i</span>
                  </span>
                </div>
              </div>

              {/* Chart container */}
              <div className="h-44 w-full flex items-end gap-1.5 pt-6 pb-2 border-b border-slate-300 dark:border-slate-700">
                {testResult.bins.map((bin) => {
                  const barHeightPct = (bin.observed_count / (maxObserved * 1.15)) * 100;
                  const expHeightPct = (bin.expected_count / (maxObserved * 1.15)) * 100;

                  return (
                    <div
                      key={bin.bin_index}
                      className="flex-1 flex flex-col items-center h-full justify-end relative group"
                    >
                      {/* Expected line marker */}
                      <div
                        className="absolute w-full border-b-2 border-dashed border-amber-500 z-10 pointer-events-none"
                        style={{ bottom: `${expHeightPct}%` }}
                      />

                      {/* Observed bar */}
                      <div
                        style={{ height: `${barHeightPct}%` }}
                        className="w-full bg-indigo-500 hover:bg-indigo-600 dark:bg-indigo-600 dark:hover:bg-indigo-500 rounded-t transition-all"
                      />

                      {/* Tooltip on hover */}
                      <div className="hidden group-hover:block absolute -top-12 bg-slate-900 text-white text-[10px] font-mono px-2 py-1 rounded shadow-lg pointer-events-none z-20 whitespace-nowrap">
                        O: {bin.observed_count} | E: {bin.expected_count.toFixed(1)}
                        <br />
                        Deviation: {bin.deviation.toFixed(2)}
                      </div>

                      <span className="text-[9px] font-mono text-slate-400 mt-1">
                        [{bin.range_start.toFixed(2)}, {bin.range_end.toFixed(2)})
                      </span>
                    </div>
                  );
                })}
              </div>

              <div className="mt-2 text-center text-[10px] text-slate-400 font-mono">
                <MathFormula math="\chi^2 = \sum_{i=1}^k \frac{(O_i - E_i)^2}{E_i}" />
              </div>
            </div>
          </div>
        ) : (
          <div className="p-6 text-center text-xs text-slate-500 font-mono">
            Click &ldquo;Run Test&rdquo; to simulate {sampleSize.toLocaleString()} outputs and evaluate uniformity.
          </div>
        )}
      </div>
    </Card>
  );
};
