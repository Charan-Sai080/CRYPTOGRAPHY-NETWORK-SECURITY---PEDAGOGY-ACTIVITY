import React, { useState } from 'react';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { AlertBanner } from '../../common/AlertBanner';
import { runCribDrag } from '../../../api/otpApi';
import { parseApiError } from '../../../api/client';
import { CribDragCandidateSchema, CribDragResponse } from '../../../types/otp';
import { BookOpen, Sparkles, CheckCircle2 } from 'lucide-react';

interface DictionaryAttackViewProps {
  c1XorC2Hex: string;
}

const COMMON_CRIBS = [' the ', 'that', 'with', 'attack', 'retreat', 'from'];

export const DictionaryAttackView: React.FC<DictionaryAttackViewProps> = ({
  c1XorC2Hex,
}) => {
  const [selectedCrib, setSelectedCrib] = useState<string>(' the ');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [result, setResult] = useState<CribDragResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleRunAttack = async (cribToTest?: string) => {
    if (!c1XorC2Hex) {
      setError('Please compute C1 ⊕ C2 stream in the Two-Time Pad sandbox first.');
      return;
    }
    const crib = (cribToTest ?? selectedCrib).trim() || ' the ';
    setIsLoading(true);
    setError(null);
    try {
      // XOR difference C1 ^ C2 against all-zero stream produces the exact XOR stream
      const zeroPad = '00'.repeat(Math.ceil(c1XorC2Hex.length / 2));
      const res = await runCribDrag({
        c1: c1XorC2Hex,
        c2: zeroPad,
        input_format: 'hex',
        crib,
        min_readability_score: 0.1,
      });
      setResult(res);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card
      title="Automated Dictionary Crib-Dragging Attack"
      subtitle="Dispatches English n-gram frequency and dictionary searches to uncover both plaintexts"
      icon={<BookOpen className="w-5 h-5 text-indigo-500" />}
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
        <div>
          <p className="text-xs text-slate-600 dark:text-slate-400 mb-2">
            Automated cryptanalysis tests frequent English cribs across all byte offsets, scoring output readability using character frequency analysis.
          </p>
          <div className="flex flex-wrap gap-2 items-center mb-3">
            <span className="text-xs font-semibold text-slate-500">Popular Cribs:</span>
            {COMMON_CRIBS.map((c) => (
              <button
                key={c}
                type="button"
                onClick={() => {
                  setSelectedCrib(c);
                  handleRunAttack(c);
                }}
                className={`px-2.5 py-1 rounded text-xs font-mono font-medium border transition-colors ${
                  selectedCrib === c
                    ? 'bg-indigo-50 border-indigo-300 text-indigo-700 dark:bg-indigo-950 dark:border-indigo-800 dark:text-indigo-300'
                    : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50 dark:bg-slate-800 dark:border-slate-700 dark:text-slate-300'
                }`}
              >
                &ldquo;{c}&rdquo;
              </button>
            ))}
          </div>

          <div className="flex gap-2">
            <input
              type="text"
              value={selectedCrib}
              onChange={(e) => setSelectedCrib(e.target.value)}
              placeholder="Or enter custom crib..."
              className="flex-1 p-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            />
            <Button
              variant="primary"
              onClick={() => handleRunAttack()}
              isLoading={isLoading}
              disabled={!c1XorC2Hex}
              icon={<Sparkles className="w-4 h-4" />}
            >
              Drag Crib
            </Button>
          </div>
        </div>

        {/* Best Match Highlight */}
        {result?.best_candidate && (
          <div className="p-4 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-300 dark:border-emerald-800">
            <div className="flex items-center gap-2 text-emerald-800 dark:text-emerald-300 font-bold text-xs uppercase tracking-wider mb-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              <span>Highest Confidence Plaintext Match</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 font-mono text-xs">
              <div className="p-2.5 rounded bg-white dark:bg-slate-900 border border-emerald-200 dark:border-emerald-900/50">
                <span className="text-slate-400 block text-[10px]">Crib Tested:</span>
                <span className="font-bold text-indigo-600 dark:text-indigo-400">
                  &ldquo;{result.best_candidate.crib}&rdquo;
                </span>
              </div>
              <div className="p-2.5 rounded bg-white dark:bg-slate-900 border border-emerald-200 dark:border-emerald-900/50">
                <span className="text-slate-400 block text-[10px]">At Byte Offset:</span>
                <span className="font-bold text-slate-800 dark:text-slate-200">
                  #{result.best_candidate.position}
                </span>
              </div>
              <div className="p-2.5 rounded bg-white dark:bg-slate-900 border border-emerald-200 dark:border-emerald-900/50">
                <span className="text-slate-400 block text-[10px]">Recovered In Other Message:</span>
                <span className="font-bold text-emerald-600 dark:text-emerald-400">
                  &ldquo;{result.best_candidate.revealed_text}&rdquo;
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Candidates List */}
        {result && result.candidates.length > 0 && (
          <div className="space-y-2 mt-4">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide block">
              Ranked Candidates ({result.candidates.length} Found):
            </span>
            <div className="divide-y divide-slate-100 dark:divide-slate-800 max-h-60 overflow-y-auto rounded-lg border border-slate-200 dark:border-slate-800">
              {result.candidates.map((cand: CribDragCandidateSchema, idx: number) => (
                <div
                  key={idx}
                  className="p-3 bg-white dark:bg-slate-900 flex items-center justify-between text-xs font-mono hover:bg-slate-50 dark:hover:bg-slate-850"
                >
                  <div className="flex items-center gap-4">
                    <span className="text-slate-400 w-6">#{idx + 1}</span>
                    <div>
                      <span className="text-indigo-600 dark:text-indigo-400 font-bold">
                        &ldquo;{cand.crib}&rdquo;
                      </span>
                      <span className="text-slate-400 mx-2">&rarr;</span>
                      <span className="text-emerald-600 dark:text-emerald-400 font-bold">
                        &ldquo;{cand.revealed_text}&rdquo;
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-[11px] text-slate-400">Pos {cand.position}</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
                      Score: {cand.readability_score.toFixed(2)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};
