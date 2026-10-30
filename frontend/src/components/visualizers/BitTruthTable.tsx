import React from 'react';
import { ByteOTPTraceSchema } from '../../types/otp';
import { MathFormula } from '../common/MathFormula';

interface BitTruthTableProps {
  trace: ByteOTPTraceSchema;
  onClose?: () => void;
}

export const BitTruthTable: React.FC<BitTruthTableProps> = ({ trace, onClose }) => {
  const plainHex = trace.byte_m_val.toString(16).padStart(2, '0');
  const keyHex = trace.byte_k_val.toString(16).padStart(2, '0');

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-md">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
        <div>
          <h4 className="font-semibold text-slate-900 dark:text-slate-100 text-sm">
            Byte {trace.byte_index} Bitwise XOR Breakdown
          </h4>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Plaintext Char: <span className="font-mono font-semibold text-indigo-600 dark:text-indigo-400">&apos;{trace.char_m}&apos;</span> (0x{plainHex}) &oplus; Key (0x{keyHex}) = Cipher (0x{trace.byte_c_hex})
          </p>
        </div>
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 px-2 py-1 rounded"
          >
            Close
          </button>
        )}
      </div>

      <div className="mt-3 overflow-x-auto">
        <table className="w-full text-xs font-mono text-center">
          <thead>
            <tr className="bg-slate-50 dark:bg-slate-800/60 text-slate-600 dark:text-slate-400">
              <th className="py-2 px-3 text-left">Bit Pos</th>
              <th className="py-2 px-3 text-indigo-600 dark:text-indigo-400">Plain Bit (m)</th>
              <th className="py-2 px-2 text-slate-400">&oplus;</th>
              <th className="py-2 px-3 text-amber-600 dark:text-amber-400">Key Bit (k)</th>
              <th className="py-2 px-2 text-slate-400">=</th>
              <th className="py-2 px-3 text-emerald-600 dark:text-emerald-400 font-bold">Cipher Bit (c)</th>
              <th className="py-2 px-3 text-right text-slate-400">Boolean Logic</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
            {trace.bit_traces.map((bit) => {
              const isFlipped = bit.bit_k === 1;
              return (
                <tr
                  key={bit.bit_index}
                  className="hover:bg-slate-50/50 dark:hover:bg-slate-800/40 transition-colors"
                >
                  <td className="py-1.5 px-3 text-left text-slate-400 font-sans">
                    Bit {bit.bit_index} (2^{7 - bit.bit_index})
                  </td>
                  <td className="py-1.5 px-3">
                    <span
                      className={`inline-block w-6 py-0.5 rounded ${
                        bit.bit_m === 1
                          ? 'bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 font-bold'
                          : 'bg-slate-100 dark:bg-slate-800 text-slate-500'
                      }`}
                    >
                      {bit.bit_m}
                    </span>
                  </td>
                  <td className="py-1.5 px-2 text-slate-400">&oplus;</td>
                  <td className="py-1.5 px-3">
                    <span
                      className={`inline-block w-6 py-0.5 rounded ${
                        bit.bit_k === 1
                          ? 'bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300 font-bold'
                          : 'bg-slate-100 dark:bg-slate-800 text-slate-500'
                      }`}
                    >
                      {bit.bit_k}
                    </span>
                  </td>
                  <td className="py-1.5 px-2 text-slate-400">=</td>
                  <td className="py-1.5 px-3">
                    <span
                      className={`inline-block w-6 py-0.5 rounded ${
                        bit.bit_c === 1
                          ? 'bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 font-bold'
                          : 'bg-slate-100 dark:bg-slate-800 text-slate-500'
                      }`}
                    >
                      {bit.bit_c}
                    </span>
                  </td>
                  <td className="py-1.5 px-3 text-right text-[11px] text-slate-500 dark:text-slate-400 font-sans">
                    {isFlipped ? (
                      <span className="text-amber-600 dark:text-amber-400">Inverted (k=1)</span>
                    ) : (
                      <span className="text-slate-400">Preserved (k=0)</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="mt-3 pt-2 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
        <div>
          Binary: <span className="font-mono text-indigo-500">{trace.byte_m_bin}</span> &oplus;{' '}
          <span className="font-mono text-amber-500">{trace.byte_k_bin}</span> ={' '}
          <span className="font-mono text-emerald-500 font-semibold">{trace.byte_c_bin}</span>
        </div>
        <div className="text-[11px]">
          <MathFormula math="c_i = m_i \oplus k_i" />
        </div>
      </div>
    </div>
  );
};
