import React, { useMemo, useState } from 'react';
import { Card } from '../../common/Card';
import { Sliders, Search } from 'lucide-react';

interface CribDragSliderProps {
  c1XorC2Hex: string;
}

export const CribDragSlider: React.FC<CribDragSliderProps> = ({ c1XorC2Hex }) => {
  const [crib, setCrib] = useState<string>(' the ');
  const [offset, setOffset] = useState<number>(0);

  // Convert hex stream to byte array
  const xorBytes = useMemo(() => {
    if (!c1XorC2Hex) return [];
    const bytes: number[] = [];
    for (let i = 0; i < c1XorC2Hex.length; i += 2) {
      bytes.push(parseInt(c1XorC2Hex.substr(i, 2), 16));
    }
    return bytes;
  }, [c1XorC2Hex]);

  const cribBytes = useMemo(() => {
    return Array.from(new TextEncoder().encode(crib));
  }, [crib]);

  const maxOffset = Math.max(0, xorBytes.length - cribBytes.length);

  // Drag crib at current offset
  const candidateChars = useMemo(() => {
    if (xorBytes.length === 0 || cribBytes.length === 0 || offset > maxOffset) return [];
    const res: { char: string; code: number; isPrintable: boolean }[] = [];
    for (let i = 0; i < cribBytes.length; i++) {
      const xorVal = xorBytes[offset + i] ^ cribBytes[i];
      const isPrintable = xorVal >= 32 && xorVal <= 126;
      const char = isPrintable ? String.fromCharCode(xorVal) : '·';
      res.push({ char, code: xorVal, isPrintable });
    }
    return res;
  }, [xorBytes, cribBytes, offset, maxOffset]);

  const validCount = candidateChars.filter((c) => c.isPrintable).length;
  const englishLikelihood =
    candidateChars.length > 0 ? Math.round((validCount / candidateChars.length) * 100) : 0;

  return (
    <Card
      title="Interactive Crib-Dragging Slider"
      subtitle="Slide guessed crib phrases across C1 ⊕ C2 to uncover plaintext fragments"
      icon={<Sliders className="w-5 h-5 text-indigo-500" />}
    >
      <div className="space-y-4">
        {/* Crib Input */}
        <div>
          <label htmlFor="crib-phrase" className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
            Guessed Crib Phrase (e.g. &ldquo; the &rdquo;, &ldquo;Attack&rdquo;, &ldquo;Retreat&rdquo;):
          </label>
          <div className="relative">
            <input
              id="crib-phrase"
              type="text"
              value={crib}
              onChange={(e) => {
                setCrib(e.target.value);
                setOffset(0);
              }}
              className="w-full p-2.5 pl-9 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              placeholder="Enter crib..."
            />
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          </div>
        </div>

        {xorBytes.length > 0 ? (
          <div>
            {/* Offset Slider */}
            <div className="flex justify-between items-center text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
              <span>Position Offset:</span>
              <span className="font-mono text-indigo-600 dark:text-indigo-400 font-bold">
                Offset {offset} / {maxOffset}
              </span>
            </div>
            <input
              type="range"
              min={0}
              max={maxOffset}
              value={offset}
              onChange={(e) => setOffset(Number(e.target.value))}
              disabled={maxOffset <= 0}
              className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-600"
            />

            {/* Visual alignment stream */}
            <div className="mt-4 p-4 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-500 uppercase tracking-wide">
                  Recovered Plaintext Slice:
                </span>
                <span
                  className={`px-2 py-0.5 rounded text-[11px] font-mono font-bold ${
                    englishLikelihood >= 80
                      ? 'bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300'
                      : 'bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300'
                  }`}
                >
                  {englishLikelihood}% Printable ASCII
                </span>
              </div>

              {/* Character blocks */}
              <div className="flex gap-1.5 flex-wrap">
                {candidateChars.map((item, idx) => (
                  <div
                    key={idx}
                    className={`flex flex-col items-center justify-center w-8 h-10 rounded border font-mono text-xs ${
                      item.isPrintable
                        ? 'bg-emerald-50 dark:bg-emerald-950/60 border-emerald-300 dark:border-emerald-700 text-emerald-800 dark:text-emerald-200 font-bold'
                        : 'bg-rose-50 dark:bg-rose-950/60 border-rose-300 dark:border-rose-700 text-rose-600 dark:text-rose-300'
                    }`}
                  >
                    <span className="text-sm">{item.char === ' ' ? '␣' : item.char}</span>
                    <span className="text-[9px] opacity-70">0x{item.code.toString(16)}</span>
                  </div>
                ))}
              </div>

              <div className="text-[11px] text-slate-500 font-mono">
                Recovered String: &ldquo;
                <span className="font-bold text-slate-900 dark:text-slate-100">
                  {candidateChars.map((c) => c.char).join('')}
                </span>
                &rdquo;
              </div>
            </div>
          </div>
        ) : (
          <div className="p-4 text-center text-xs text-slate-500 font-mono bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800">
            Please simulate key reuse above to generate the C1 ⊕ C2 stream.
          </div>
        )}
      </div>
    </Card>
  );
};
