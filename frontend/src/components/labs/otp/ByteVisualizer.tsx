import React, { useState } from 'react';
import { ByteOTPTraceSchema } from '../../../types/otp';
import { BitTruthTable } from '../../visualizers/BitTruthTable';

interface ByteVisualizerProps {
  traces: ByteOTPTraceSchema[];
}

export const ByteVisualizer: React.FC<ByteVisualizerProps> = ({ traces }) => {
  const [selectedByteIdx, setSelectedByteIdx] = useState<number | null>(0);

  if (!traces || traces.length === 0) return null;

  const selectedTrace =
    selectedByteIdx !== null ? traces.find((t) => t.byte_index === selectedByteIdx) : null;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between text-xs text-slate-500">
        <span className="font-semibold uppercase tracking-wider">
          Byte Stream Alignment (Click byte for bitwise XOR view):
        </span>
        <span>{traces.length} Total Bytes</span>
      </div>

      {/* Interactive Horizontal Byte Stream */}
      <div className="overflow-x-auto pb-2">
        <div className="flex gap-2 min-w-max">
          {traces.map((trace) => {
            const isSelected = selectedByteIdx === trace.byte_index;
            return (
              <div
                key={trace.byte_index}
                onClick={() => setSelectedByteIdx(trace.byte_index)}
                className={`p-2 rounded-lg border cursor-pointer font-mono text-center transition-all ${
                  isSelected
                    ? 'ring-2 ring-indigo-500 bg-indigo-50/50 dark:bg-indigo-950/40 border-indigo-300 dark:border-indigo-700 shadow-sm'
                    : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-slate-400 dark:hover:border-slate-600'
                }`}
              >
                <div className="text-[10px] text-slate-400 mb-1">
                  #{trace.byte_index}
                </div>
                {/* Plain char */}
                <div className="text-xs font-bold text-indigo-600 dark:text-indigo-400">
                  {trace.char_m === ' ' ? '␣' : trace.char_m}
                </div>
                {/* Plain Hex */}
                <div className="text-[11px] text-slate-500">
                  0x{trace.byte_m_val.toString(16).padStart(2, '0')}
                </div>
                {/* XOR symbol */}
                <div className="text-[9px] text-slate-400 my-0.5">&oplus;</div>
                {/* Key Hex */}
                <div className="text-[11px] text-amber-600 dark:text-amber-400">
                  0x{trace.byte_k_val.toString(16).padStart(2, '0')}
                </div>
                {/* Equals symbol */}
                <div className="text-[9px] text-slate-400 my-0.5">=</div>
                {/* Cipher Hex */}
                <div className="text-[11px] font-bold text-emerald-600 dark:text-emerald-400">
                  0x{trace.byte_c_hex}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Selected Byte Truth Table Drawer */}
      {selectedTrace && (
        <BitTruthTable
          trace={selectedTrace}
          onClose={() => setSelectedByteIdx(null)}
        />
      )}
    </div>
  );
};
