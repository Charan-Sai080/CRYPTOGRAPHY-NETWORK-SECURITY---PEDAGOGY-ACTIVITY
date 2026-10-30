import React, { useEffect, useState } from 'react';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { getLcgPresets } from '../../../api/lcgApi';
import { LCGPreset } from '../../../types/lcg';
import { Sliders, RefreshCw } from 'lucide-react';

interface ParameterFormProps {
  onGenerate: (params: { m: number; a: number; c: number; seed: number; count: number }) => void;
  isLoading?: boolean;
}

export const ParameterForm: React.FC<ParameterFormProps> = ({
  onGenerate,
  isLoading = false,
}) => {
  const [presets, setPresets] = useState<LCGPreset[]>([]);
  const [selectedPreset, setSelectedPreset] = useState<string>('Educational Small (m=16)');
  const [m, setM] = useState<number>(16);
  const [a, setA] = useState<number>(5);
  const [c, setC] = useState<number>(3);
  const [seed, setSeed] = useState<number>(1);
  const [count, setCount] = useState<number>(20);

  useEffect(() => {
    const fetchPresets = async () => {
      try {
        const list = await getLcgPresets();
        setPresets(list);
      } catch {
        // Fallback default presets if backend loading
        setPresets([
          {
            name: 'Educational Small (m=16)',
            description: 'Small modulus for transparent step tracing',
            m: 16,
            a: 5,
            c: 3,
            default_seed: 1,
            is_full_period: true,
          },
          {
            name: 'ANSI C / ISO C rand()',
            description: 'Standard C library rand() generator',
            m: 2147483648,
            a: 1103515245,
            c: 12345,
            default_seed: 12345,
            is_full_period: true,
          },
          {
            name: 'MINSTD (Park-Miller)',
            description: 'Minimal standard generator (c=0)',
            m: 2147483647,
            a: 16807,
            c: 0,
            default_seed: 1,
            is_full_period: false,
          },
          {
            name: 'Borland C/C++',
            description: 'Borland rand() generator',
            m: 2147483648,
            a: 22695477,
            c: 1,
            default_seed: 1,
            is_full_period: true,
          },
        ]);
      }
    };
    fetchPresets();
  }, []);

  const handlePresetChange = (name: string) => {
    setSelectedPreset(name);
    const found = presets.find((p) => p.name === name);
    if (found) {
      setM(found.m);
      setA(found.a);
      setC(found.c);
      setSeed(found.default_seed);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onGenerate({ m, a, c, seed, count });
  };

  return (
    <Card
      title="LCG Parameter Configuration &amp; Presets"
      subtitle="Configure recurrence equation X_{n+1} ≡ (a · X_n + c) mod m"
      icon={<Sliders className="w-5 h-5" />}
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Preset Selector */}
        <div>
          <label htmlFor="lcg-preset" className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
            Standard Historical Presets:
          </label>
          <select
            id="lcg-preset"
            value={selectedPreset}
            onChange={(e) => handlePresetChange(e.target.value)}
            className="w-full p-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 text-xs font-medium focus:ring-2 focus:ring-indigo-500 focus:outline-none"
          >
            {presets.map((preset) => (
              <option key={preset.name} value={preset.name}>
                {preset.name} &bull; m={preset.m.toLocaleString()}
              </option>
            ))}
          </select>
          {presets.find((p) => p.name === selectedPreset)?.description && (
            <p className="text-[11px] text-slate-500 mt-1 italic">
              {presets.find((p) => p.name === selectedPreset)?.description} &bull;{' '}
              {presets.find((p) => p.name === selectedPreset)?.is_full_period
                ? 'Full period guaranteed'
                : 'Defective/Partial period'}
            </p>
          )}
        </div>

        {/* Parameter Inputs Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
          <div>
            <label htmlFor="param-m" className="block text-[11px] font-mono font-semibold text-slate-600 dark:text-slate-400 mb-1">
              Modulus (m):
            </label>
            <input
              id="param-m"
              type="number"
              min={2}
              value={m}
              onChange={(e) => setM(Number(e.target.value))}
              className="w-full p-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            />
          </div>

          <div>
            <label htmlFor="param-a" className="block text-[11px] font-mono font-semibold text-slate-600 dark:text-slate-400 mb-1">
              Multiplier (a):
            </label>
            <input
              id="param-a"
              type="number"
              min={1}
              value={a}
              onChange={(e) => setA(Number(e.target.value))}
              className="w-full p-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            />
          </div>

          <div>
            <label htmlFor="param-c" className="block text-[11px] font-mono font-semibold text-slate-600 dark:text-slate-400 mb-1">
              Increment (c):
            </label>
            <input
              id="param-c"
              type="number"
              min={0}
              value={c}
              onChange={(e) => setC(Number(e.target.value))}
              className="w-full p-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            />
          </div>

          <div>
            <label htmlFor="param-seed" className="block text-[11px] font-mono font-semibold text-slate-600 dark:text-slate-400 mb-1">
              Seed (X_0):
            </label>
            <input
              id="param-seed"
              type="number"
              min={0}
              value={seed}
              onChange={(e) => setSeed(Number(e.target.value))}
              className="w-full p-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            />
          </div>

          <div>
            <label htmlFor="param-count" className="block text-[11px] font-mono font-semibold text-slate-600 dark:text-slate-400 mb-1">
              Count (N):
            </label>
            <input
              id="param-count"
              type="number"
              min={1}
              max={1000}
              value={count}
              onChange={(e) => setCount(Number(e.target.value))}
              className="w-full p-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            />
          </div>
        </div>

        <div className="pt-2 flex items-center justify-between">
          <Button
            type="submit"
            variant="primary"
            isLoading={isLoading}
            icon={<RefreshCw className="w-4 h-4" />}
          >
            Generate &amp; Analyze Sequence
          </Button>
          <span className="text-xs font-mono text-slate-400">
            Equation: X_{'{n+1}'} = ({a} &middot; X_n + {c}) mod {m}
          </span>
        </div>
      </form>
    </Card>
  );
};
