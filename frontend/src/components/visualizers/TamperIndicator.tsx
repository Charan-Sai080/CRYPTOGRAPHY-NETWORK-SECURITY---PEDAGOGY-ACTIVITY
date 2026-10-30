import React from 'react';
import { CheckCircle2, XCircle, AlertTriangle, Cpu } from 'lucide-react';
import { DSATamperResponse } from '../../types/dsa';

interface TamperIndicatorProps {
  result: DSATamperResponse;
}

export const TamperIndicator: React.FC<TamperIndicatorProps> = ({ result }) => {
  const isValid = result.tampered_verification;
  const tamperDetected = result.tamper_detected;

  return (
    <div
      className={`p-5 rounded-xl border transition-all ${
        isValid && !tamperDetected
          ? 'bg-emerald-50/50 dark:bg-emerald-950/30 border-emerald-300 dark:border-emerald-800'
          : 'bg-rose-50/50 dark:bg-rose-950/30 border-rose-300 dark:border-rose-800'
      }`}
    >
      <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800">
        <div className="flex items-center gap-3">
          {isValid && !tamperDetected ? (
            <div className="p-2 rounded-lg bg-emerald-100 dark:bg-emerald-900/60 text-emerald-600 dark:text-emerald-300">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          ) : (
            <div className="p-2 rounded-lg bg-rose-100 dark:bg-rose-900/60 text-rose-600 dark:text-rose-300">
              <XCircle className="w-5 h-5" />
            </div>
          )}
          <div>
            <h4
              className={`font-bold text-base ${
                isValid && !tamperDetected
                  ? 'text-emerald-900 dark:text-emerald-200'
                  : 'text-rose-900 dark:text-rose-200'
              }`}
            >
              {tamperDetected ? 'TAMPER DETECTED / SIGNATURE REJECTED' : 'AUTHENTIC INTEGRITY VERIFIED'}
            </h4>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Tamper Type: {result.tamper_type} &bull; Bit #{result.bit_flipped} flipped
            </p>
          </div>
        </div>

        <span
          className={`text-xs px-2.5 py-1 rounded-full font-mono font-bold border ${
            isValid && !tamperDetected
              ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200 border-emerald-300 dark:border-emerald-700'
              : 'bg-rose-100 text-rose-800 dark:bg-rose-900 dark:text-rose-200 border-rose-300 dark:border-rose-700'
          }`}
        >
          {tamperDetected ? 'VERIFICATION FAILED (REJECTED)' : 'VERIFIED (ACCEPTED)'}
        </span>
      </div>

      {/* Comparison Grid */}
      <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
        <div className="p-3 rounded-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
          <span className="text-[11px] font-sans font-semibold text-slate-500 uppercase tracking-wide block mb-1">
            Message Comparison
          </span>
          <div className="space-y-1">
            <div>
              <span className="text-slate-400">Original: </span>
              <span className="text-indigo-600 dark:text-indigo-400 font-bold break-all">
                &ldquo;{result.original_message}&rdquo;
              </span>
            </div>
            <div>
              <span className="text-slate-400">Tampered: </span>
              <span
                className={`font-bold break-all ${
                  result.original_message === result.tampered_message
                    ? 'text-indigo-600 dark:text-indigo-400'
                    : 'text-rose-600 dark:text-rose-400'
                }`}
              >
                &ldquo;{result.tampered_message}&rdquo;
              </span>
            </div>
          </div>
          {result.original_message !== result.tampered_message && (
            <div className="mt-2 text-[10px] font-sans text-rose-600 dark:text-rose-400 flex items-center gap-1">
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>Avalanche Effect: 1 bit altered changed the SHA-256 digest completely!</span>
            </div>
          )}
        </div>

        <div className="p-3 rounded-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
          <span className="text-[11px] font-sans font-semibold text-slate-500 uppercase tracking-wide block mb-1">
            Signature Components (r, s)
          </span>
          <div className="space-y-1">
            <div>
              <span className="text-slate-400">Original: </span>
              <span className="text-slate-800 dark:text-slate-200 font-bold break-all">
                r={result.original_signature.r}, s={result.original_signature.s}
              </span>
            </div>
            <div>
              <span className="text-slate-400">Tampered: </span>
              <span
                className={`font-bold break-all ${
                  result.original_signature.r === result.tampered_signature.r &&
                  result.original_signature.s === result.tampered_signature.s
                    ? 'text-emerald-600 dark:text-emerald-400'
                    : 'text-rose-600 dark:text-rose-400'
                }`}
              >
                r={result.tampered_signature.r}, s={result.tampered_signature.s}
              </span>
            </div>
          </div>
          <div className="mt-2 text-[10px] font-sans text-slate-500 flex items-center gap-1">
            <Cpu className="w-3.5 h-3.5" />
            <span>Verification: Original={result.original_verification ? 'Valid' : 'Invalid'}, Tampered={result.tampered_verification ? 'Valid' : 'Invalid'}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
