import React from 'react';
import { Card } from '../../common/Card';
import { HullDobellResponse } from '../../../types/lcg';
import { MathFormula } from '../../common/MathFormula';
import { CheckCircle2, XCircle, Award } from 'lucide-react';

interface HullDobellCardProps {
  analysis: HullDobellResponse | null;
}

export const HullDobellCard: React.FC<HullDobellCardProps> = ({ analysis }) => {
  if (!analysis) {
    return (
      <Card
        title="Hull-Dobell Theorem Periodicity Validator"
        subtitle="Mathematical criteria for full period (length m)"
        icon={<Award className="w-5 h-5 text-indigo-500" />}
      >
        <div className="p-4 text-center text-xs text-slate-500 font-mono">
          Generate a sequence to evaluate the Hull-Dobell criteria.
        </div>
      </Card>
    );
  }

  const isFull = analysis.is_full_period;
  const conditions = [
    { id: 1, ...analysis.condition_1 },
    { id: 2, ...analysis.condition_2 },
    { id: 3, ...analysis.condition_3 },
  ];

  return (
    <Card
      title="Hull-Dobell Theorem Periodicity Validator"
      subtitle="Evaluates necessary and sufficient conditions for full period m"
      icon={<Award className="w-5 h-5 text-indigo-500" />}
      action={
        <span
          className={`px-3 py-1 rounded-full text-xs font-bold font-mono border ${
            isFull
              ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 border-emerald-300 dark:border-emerald-700'
              : 'bg-rose-50 text-rose-700 dark:bg-rose-950 dark:text-rose-300 border-rose-300 dark:border-rose-700'
          }`}
        >
          {isFull ? 'FULL PERIOD GUARANTEED' : 'DEFECTIVE / SHORT PERIOD'}
        </span>
      }
    >
      <div className="space-y-4">
        {/* Theorem Statement */}
        <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700 text-xs">
          <span className="font-semibold text-slate-700 dark:text-slate-300 block mb-1">
            Hull-Dobell Theorem (1962):
          </span>
          <div className="font-mono text-center my-1 text-slate-800 dark:text-slate-200">
            <MathFormula
              math="X_{n+1} \equiv (a X_n + c) \pmod m \text{ has full period } m \iff \begin{cases} 1.\; \gcd(c, m) = 1 \\ 2.\; \forall p \in \mathbb{P}, p \mid m \implies p \mid (a - 1) \\ 3.\; 4 \mid m \implies 4 \mid (a - 1) \end{cases}"
              block
            />
          </div>
        </div>

        {/* Condition Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {conditions.map((cond) => (
            <div
              key={cond.id}
              className={`p-3.5 rounded-xl border transition-all ${
                cond.satisfied
                  ? 'bg-emerald-50/40 dark:bg-emerald-950/20 border-emerald-200 dark:border-emerald-800'
                  : 'bg-rose-50/40 dark:bg-rose-950/20 border-rose-200 dark:border-rose-800'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold font-mono text-slate-700 dark:text-slate-300">
                  Condition {cond.id}
                </span>
                {cond.satisfied ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                ) : (
                  <XCircle className="w-4 h-4 text-rose-600 dark:text-rose-400" />
                )}
              </div>
              <h5 className="font-semibold text-xs text-slate-900 dark:text-slate-100 mb-1">
                {cond.description}
              </h5>
              <p className="text-[11px] text-slate-600 dark:text-slate-400 leading-snug">
                {cond.detail}
              </p>
            </div>
          ))}
        </div>

        {/* Prime Factors Decomposition */}
        <div className="flex flex-wrap items-center justify-between gap-2 p-3 bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 text-xs font-mono">
          <div className="flex items-center gap-2">
            <span className="text-slate-500">Prime factors of m ({analysis.m}):</span>
            <div className="flex gap-1">
              {analysis.prime_factors_m.map((prime) => (
                <span
                  key={prime}
                  className="px-2 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 font-bold"
                >
                  {prime}
                </span>
              ))}
            </div>
          </div>
          <span className="text-slate-500">
            Explanation: <span className="font-semibold text-slate-800 dark:text-slate-200">{analysis.explanation}</span>
          </span>
        </div>
      </div>
    </Card>
  );
};
