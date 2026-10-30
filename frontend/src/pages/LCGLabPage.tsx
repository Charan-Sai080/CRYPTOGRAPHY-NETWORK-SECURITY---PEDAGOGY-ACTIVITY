import React, { useState } from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { Badge } from '../components/common/Badge';
import { ParameterForm } from '../components/labs/lcg/ParameterForm';
import { StepTraceTable } from '../components/labs/lcg/StepTraceTable';
import { HullDobellCard } from '../components/labs/lcg/HullDobellCard';
import { FloydCycleCard } from '../components/labs/lcg/FloydCycleCard';
import { ChiSquareChart } from '../components/labs/lcg/ChiSquareChart';
import { MarsagliaLatticeCard } from '../components/labs/lcg/MarsagliaLatticeCard';
import { LcgCrackerCard } from '../components/labs/lcg/LcgCrackerCard';
import { generateLcgSequence, checkHullDobell } from '../api/lcgApi';
import { parseApiError } from '../api/client';
import { LCGStepTrace, HullDobellResponse } from '../types/lcg';
import { AlertBanner } from '../components/common/AlertBanner';
import { Cpu } from 'lucide-react';

export const LCGLabPage: React.FC = () => {
  const [params, setParams] = useState<{
    m: number;
    a: number;
    c: number;
    seed: number;
    count: number;
  }>({
    m: 16,
    a: 5,
    c: 3,
    seed: 1,
    count: 20,
  });

  const [traces, setTraces] = useState<LCGStepTrace[]>([]);
  const [sequence, setSequence] = useState<number[]>([]);
  const [hullDobell, setHullDobell] = useState<HullDobellResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async (newParams: {
    m: number;
    a: number;
    c: number;
    seed: number;
    count: number;
  }) => {
    setParams(newParams);
    setIsLoading(true);
    setError(null);
    try {
      // 1. Generate sequence
      const genRes = await generateLcgSequence(newParams);
      setTraces(genRes.traces);
      setSequence(genRes.values);

      // 2. Run Hull-Dobell check
      const hdRes = await checkHullDobell({
        m: newParams.m,
        a: newParams.a,
        c: newParams.c,
      });
      setHullDobell(hdRes);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <PageHeader
        title="Lab 2: Linear Congruential Generator &amp; Marsaglia Lattice"
        subtitle="Explore modular recurrence pseudo-randomness, Hull-Dobell periodicity criteria, spectral hyperplane defects, and state recovery"
        icon={<Cpu className="w-7 h-7" />}
        badge={
          <div className="flex gap-2">
            <Badge variant="warning">Lab 2</Badge>
            <Badge variant="math">Hull-Dobell &bull; Marsaglia</Badge>
          </div>
        }
      />

      {error && (
        <AlertBanner
          type="error"
          message={error}
          onClose={() => setError(null)}
          className="mb-4"
        />
      )}

      {/* Section 1: Parameters & Presets */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <span>1. Recurrence Parameters &amp; Standard Presets</span>
        </h2>
        <ParameterForm onGenerate={handleGenerate} isLoading={isLoading} />
      </section>

      {/* Section 2: Hull-Dobell Theorem Validator */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <span>2. Hull-Dobell Full Periodicity Verification</span>
        </h2>
        <HullDobellCard analysis={hullDobell} />
      </section>

      {/* Section 3: Step Trace Table */}
      {traces.length > 0 && (
        <section className="space-y-4">
          <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
            <span>3. Step-by-Step Modular Recurrence Arithmetic Trace</span>
          </h2>
          <StepTraceTable traces={traces} m={params.m} />
        </section>
      )}

      {/* Section 4: Floyd's Cycle Detection */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <span>4. Floyd&apos;s Tortoise and Hare Cycle Finding Visualizer</span>
        </h2>
        <FloydCycleCard params={params} />
      </section>

      {/* Section 5: Chi-Square Uniformity Test */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <span>5. Chi-Square Goodness-of-Fit Uniformity Distribution</span>
        </h2>
        <ChiSquareChart params={params} />
      </section>

      {/* Section 6: Marsaglia Hyperplane Lattice 2D / 3D */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <span>6. Marsaglia Hyperplane Lattice &amp; 3D Spectral Structure</span>
        </h2>
        <MarsagliaLatticeCard params={params} />
      </section>

      {/* Section 7: Algebraic State Cracker */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <span>7. Algebraic State Recovery &amp; Predictability Exploit</span>
        </h2>
        <LcgCrackerCard currentParams={params} sampleOutputs={sequence} />
      </section>
    </div>
  );
};
