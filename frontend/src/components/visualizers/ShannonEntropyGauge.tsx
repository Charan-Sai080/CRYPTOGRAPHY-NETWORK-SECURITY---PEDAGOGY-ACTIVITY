import React from 'react';
import { MathFormula } from '../common/MathFormula';

interface ShannonEntropyGaugeProps {
  entropy: number;
  maxEntropy?: number;
  label?: string;
  interpretation?: string;
  size?: number;
}

export const ShannonEntropyGauge: React.FC<ShannonEntropyGaugeProps> = ({
  entropy,
  maxEntropy = 8.0,
  label = 'Shannon Entropy',
  interpretation,
  size = 180,
}) => {
  // Clamp entropy
  const clamped = Math.max(0, Math.min(entropy, maxEntropy));
  const fraction = maxEntropy > 0 ? clamped / maxEntropy : 0;
  const percentage = Math.round(fraction * 100);

  // SVG Gauge Calculations (Semi-circle from 180 to 0 degrees)
  const strokeWidth = 14;
  const radius = (size - strokeWidth * 2) / 2;
  const circumference = Math.PI * radius;
  const strokeDashoffset = circumference * (1 - fraction);

  // Color mapping
  let strokeColor = '#f43f5e'; // rose (poor)
  let badgeClass = 'text-rose-600 bg-rose-50 dark:bg-rose-950/60 border-rose-200 dark:border-rose-800';
  if (fraction >= 0.93) {
    strokeColor = '#10b981'; // emerald (excellent uniform CSPRNG)
    badgeClass = 'text-emerald-600 bg-emerald-50 dark:bg-emerald-950/60 border-emerald-200 dark:border-emerald-800';
  } else if (fraction >= 0.6) {
    strokeColor = '#f59e0b'; // amber (moderate)
    badgeClass = 'text-amber-600 bg-amber-50 dark:bg-amber-950/60 border-amber-200 dark:border-amber-800';
  }

  return (
    <div className="flex flex-col items-center justify-center p-4 bg-slate-50 dark:bg-slate-900/60 rounded-xl border border-slate-200 dark:border-slate-800">
      <div className="relative flex items-center justify-center" style={{ width: size, height: size / 2 + 30 }}>
        <svg
          width={size}
          height={size / 2 + strokeWidth}
          viewBox={`0 0 ${size} ${size / 2 + strokeWidth}`}
          className="overflow-visible"
        >
          {/* Background track */}
          <path
            d={`M ${strokeWidth} ${size / 2} A ${radius} ${radius} 0 0 1 ${size - strokeWidth} ${size / 2}`}
            fill="none"
            stroke="currentColor"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            className="text-slate-200 dark:text-slate-800"
          />
          {/* Active arc */}
          <path
            d={`M ${strokeWidth} ${size / 2} A ${radius} ${radius} 0 0 1 ${size - strokeWidth} ${size / 2}`}
            fill="none"
            stroke={strokeColor}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            className="transition-all duration-700 ease-out"
          />
        </svg>

        {/* Center reading */}
        <div className="absolute top-[40%] flex flex-col items-center text-center">
          <span className="text-2xl font-black font-mono tracking-tight text-slate-900 dark:text-slate-100">
            {clamped.toFixed(2)}
          </span>
          <span className="text-[11px] font-mono text-slate-500 dark:text-slate-400">
            / {maxEntropy.toFixed(1)} bits/byte
          </span>
        </div>
      </div>

      <div className="mt-2 text-center">
        <div className="text-xs font-semibold text-slate-700 dark:text-slate-300">
          {label}
        </div>
        <div className="my-1">
          <span className={`text-[11px] px-2 py-0.5 rounded-full font-medium border ${badgeClass}`}>
            {percentage}% Uniformity
          </span>
        </div>
        {interpretation && (
          <p className="text-[11px] text-slate-500 dark:text-slate-400 max-w-[200px] mt-1 leading-snug">
            {interpretation}
          </p>
        )}
      </div>

      <div className="mt-2 text-[10px] text-slate-400 dark:text-slate-500 font-mono">
        <MathFormula math="H(X) = -\sum p(x) \log_2 p(x)" />
      </div>
    </div>
  );
};
