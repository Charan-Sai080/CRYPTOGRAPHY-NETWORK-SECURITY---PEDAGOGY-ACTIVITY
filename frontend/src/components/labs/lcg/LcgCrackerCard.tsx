import React, { useState } from 'react';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { AlertBanner } from '../../common/AlertBanner';
import { crackLcg } from '../../../api/lcgApi';
import { parseApiError } from '../../../api/client';
import { LCGCrackResponse } from '../../../types/lcg';
import { Unlock, ShieldAlert, Cpu } from 'lucide-react';
import { MathFormula } from '../../common/MathFormula';

interface LcgCrackerCardProps {
  currentParams: { m: number; a: number; c: number; seed: number };
  sampleOutputs: number[];
}

export const LcgCrackerCard: React.FC<LcgCrackerCardProps> = ({
  currentParams,
  sampleOutputs,
}) => {
  const [observedOutputs, setObservedOutputs] = useState<string>(() => {
    if (sampleOutputs.length >= 3) {
      return sampleOutputs.slice(0, 5).join(', ');
    }
    return '1, 8, 11, 10, 5';
  });
  const [modulusInput, setModulusInput] = useState<string>(String(currentParams.m));
  const [crackResult, setCrackResult] = useState<LCGCrackResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleCrack = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const numbers = observedOutputs
        .split(/[,;\s]+/)
        .map((s) => s.trim())
        .filter(Boolean)
        .map(Number);

      if (numbers.length < 3) {
        setError('At least 3 consecutive outputs (X_0, X_1, X_2) are required to crack LCG.');
        setIsLoading(false);
        return;
      }

      const mVal = modulusInput.trim() ? Number(modulusInput) : currentParams.m;
      if (!mVal || mVal < 2) {
        setError('Modulus m >= 2 is required.');
        setIsLoading(false);
        return;
      }

      const res = await crackLcg({
        outputs: numbers,
        m: mVal,
      });
      setCrackResult(res);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card
      title="Algebraic State Cracker &amp; Predictability Exploit"
      subtitle="Reconstruct hidden parameters (a, c) and predict future outputs from consecutive values"
      icon={<Unlock className="w-5 h-5 text-rose-500" />}
      className="border-rose-200 dark:border-rose-900/60"
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
        {/* Mathematical Attack Foundation */}
        <div className="p-3.5 bg-rose-50/50 dark:bg-rose-950/30 rounded-xl border border-rose-200 dark:border-rose-900/50 text-xs">
          <div className="flex items-center gap-2 font-semibold text-rose-800 dark:text-rose-300 mb-1">
            <ShieldAlert className="w-4 h-4 text-rose-600 dark:text-rose-400" />
            <span>Why LCGs are Insecure for Cryptography:</span>
          </div>
          <p className="text-rose-900 dark:text-rose-200 leading-relaxed mb-2">
            Given three consecutive outputs <MathFormula math="X_0, X_1, X_2" />, the constant increment <MathFormula math="c" /> cancels out via differencing:
          </p>
          <div className="font-mono text-center my-1">
            <MathFormula
              math="X_2 - X_1 \equiv a(X_1 - X_0) \pmod m \implies a \equiv (X_2 - X_1)(X_1 - X_0)^{-1} \pmod m"
              block
            />
          </div>
          <p className="text-[11px] text-rose-800 dark:text-rose-300 mt-1">
            Once <MathFormula math="a" /> is recovered, <MathFormula math="c \equiv X_1 - a X_0 \pmod m" /> is solved instantly, compromising all past and future pseudo-random values.
          </p>
        </div>

        {/* Inputs */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="md:col-span-2">
            <label htmlFor="observed-seq" className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Observed Consecutive Outputs (Comma separated, min 3):
            </label>
            <input
              id="observed-seq"
              type="text"
              value={observedOutputs}
              onChange={(e) => setObservedOutputs(e.target.value)}
              className="w-full p-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-rose-500 focus:outline-none"
              placeholder="e.g. 1, 8, 11, 10, 5"
            />
          </div>

          <div>
            <label htmlFor="modulus-input" className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Modulus m (Known or Guessed):
            </label>
            <input
              id="modulus-input"
              type="number"
              value={modulusInput}
              onChange={(e) => setModulusInput(e.target.value)}
              className="w-full p-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-rose-500 focus:outline-none"
              placeholder="m modulus"
            />
          </div>
        </div>

        <div>
          <Button
            variant="danger"
            onClick={handleCrack}
            isLoading={isLoading}
            icon={<Cpu className="w-4 h-4" />}
          >
            Execute Algebraic State Recovery
          </Button>
        </div>

        {/* Crack Result */}
        {crackResult && (
          <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-800 space-y-3">
            <div
              className={`p-3 rounded-lg border flex items-center justify-between text-xs font-mono font-bold ${
                crackResult.is_successful
                  ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-200 border-emerald-300 dark:border-emerald-700'
                  : 'bg-rose-50 dark:bg-rose-950/40 text-rose-800 dark:text-rose-200 border-rose-300 dark:border-rose-700'
              }`}
            >
              <span>{crackResult.is_successful ? 'STATE RECONSTRUCTION SUCCESSFUL' : 'CRACK FAILED'}</span>
              <span>{crackResult.notes}</span>
            </div>

            {crackResult.is_successful && (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-xs">
                <div className="p-2.5 rounded bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                  <span className="text-slate-400 block text-[10px]">Recovered Multiplier (a):</span>
                  <span className="text-lg font-bold text-indigo-600 dark:text-indigo-400">
                    {crackResult.recovered_a}
                  </span>
                </div>
                <div className="p-2.5 rounded bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                  <span className="text-slate-400 block text-[10px]">Recovered Increment (c):</span>
                  <span className="text-lg font-bold text-indigo-600 dark:text-indigo-400">
                    {crackResult.recovered_c}
                  </span>
                </div>
                <div className="p-2.5 rounded bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                  <span className="text-slate-400 block text-[10px]">Modulus (m):</span>
                  <span className="text-lg font-bold text-slate-800 dark:text-slate-200">
                    {crackResult.m}
                  </span>
                </div>
                <div className="p-2.5 rounded bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                  <span className="text-slate-400 block text-[10px]">Predicted Next Output:</span>
                  <span className="text-lg font-bold text-emerald-600 dark:text-emerald-400">
                    {crackResult.predicted_next ?? 'N/A'}
                  </span>
                </div>
              </div>
            )}

            {/* Step-by-step resolution logs */}
            {crackResult.steps && crackResult.steps.length > 0 && (
              <div className="p-3 bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 text-xs font-mono space-y-1">
                <span className="font-semibold text-slate-500 uppercase tracking-wide block mb-1">
                  Algebraic Derivation Trace:
                </span>
                {crackResult.steps.map((st: string, idx: number) => (
                  <div key={idx} className="text-slate-700 dark:text-slate-300">
                    &bull; {st}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  );
};
