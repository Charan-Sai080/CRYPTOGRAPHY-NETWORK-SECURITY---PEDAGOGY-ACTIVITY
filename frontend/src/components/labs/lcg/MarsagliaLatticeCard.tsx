import React, { useEffect, useState } from 'react';
import { Card } from '../../common/Card';
import { LatticePlot2D } from '../../visualizers/LatticePlot2D';
import { LatticePlot3D } from '../../visualizers/LatticePlot3D';
import { getMarsagliaLattice } from '../../../api/lcgApi';
import { parseApiError } from '../../../api/client';
import { MarsagliaLatticeResponse } from '../../../types/lcg';
import { AlertBanner } from '../../common/AlertBanner';
import { Grid, Eye } from 'lucide-react';
import { MathFormula } from '../../common/MathFormula';

interface MarsagliaLatticeCardProps {
  params: { m: number; a: number; c: number; seed: number };
}

export const MarsagliaLatticeCard: React.FC<MarsagliaLatticeCardProps> = ({ params }) => {
  const [activeDimension, setActiveDimension] = useState<'2D' | '3D'>('2D');
  const [latticeData, setLatticeData] = useState<MarsagliaLatticeResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    const fetchLattice = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const dim = activeDimension === '2D' ? 2 : 3;
        const res = await getMarsagliaLattice({
          m: params.m,
          a: params.a,
          c: params.c,
          seed: params.seed,
          count: 500,
          dimension: dim,
        });
        if (isMounted) {
          setLatticeData(res);
        }
      } catch (err) {
        if (isMounted) {
          setError(parseApiError(err));
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };
    fetchLattice();
    return () => {
      isMounted = false;
    };
  }, [params.m, params.a, params.c, params.seed, activeDimension]);

  return (
    <Card
      title="Marsaglia Hyperplane Lattice &amp; Spectral Structure"
      subtitle="&ldquo;Random Numbers Fall Mainly in the Planes&rdquo; (Marsaglia, PNAS 1968)"
      icon={<Grid className="w-5 h-5 text-indigo-500" />}
      action={
        <div className="flex bg-slate-100 dark:bg-slate-800 p-1 rounded-lg">
          <button
            type="button"
            onClick={() => setActiveDimension('2D')}
            className={`px-3 py-1 rounded text-xs font-semibold transition-all ${
              activeDimension === '2D'
                ? 'bg-indigo-600 text-white shadow-xs'
                : 'text-slate-600 dark:text-slate-300'
            }`}
          >
            2D Lattice (X_n, X_{'{n+1}'})
          </button>
          <button
            type="button"
            onClick={() => setActiveDimension('3D')}
            className={`px-3 py-1 rounded text-xs font-semibold transition-all ${
              activeDimension === '3D'
                ? 'bg-indigo-600 text-white shadow-xs'
                : 'text-slate-600 dark:text-slate-300'
            }`}
          >
            3D Hyperplanes (X_n, X_{'{n+1}'}, X_{'{n+2}'})
          </button>
        </div>
      }
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
        {/* Marsaglia Theoretical Explanation */}
        <div className="p-3.5 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700 text-xs">
          <div className="flex items-center gap-2 font-semibold text-slate-800 dark:text-slate-200 mb-1">
            <Eye className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
            <span>Marsaglia&apos;s Theorem on Hyperplane Bounds:</span>
          </div>
          <p className="text-slate-600 dark:text-slate-400 leading-relaxed mb-2">
            In any dimension <MathFormula math="d" />, all consecutive <MathFormula math="d" />-tuples
            produced by an LCG fall into at most a small family of parallel hyperplanes:
          </p>
          <div className="font-mono text-center my-1 text-slate-800 dark:text-slate-200">
            <MathFormula
              math="k \le \lfloor (d! \cdot m)^{1/d} \rfloor \implies \begin{cases} d=2: k \le \sqrt{2m} \text{ lines} \\ d=3: k \le \sqrt[3]{6m} \text{ planes} \end{cases}"
              block
            />
          </div>
          {latticeData && (
            <p className="text-[11px] text-indigo-600 dark:text-indigo-400 font-mono mt-2">
              Theoretical Max Hyperplanes: {latticeData.theoretical_max_hyperplanes} &bull; {latticeData.explanation}
            </p>
          )}
        </div>

        {/* Visualizer Plot Container */}
        {isLoading ? (
          <div className="h-80 flex items-center justify-center font-mono text-xs text-slate-400 animate-pulse">
            Generating {activeDimension} lattice scatter plot...
          </div>
        ) : latticeData ? (
          <div className="flex justify-center pt-2">
            {activeDimension === '2D' ? (
              <LatticePlot2D
                points={latticeData.points_2d}
                theoreticalBound={latticeData.theoretical_max_hyperplanes}
              />
            ) : (
              <LatticePlot3D
                points={latticeData.points_3d}
                theoreticalBound={latticeData.theoretical_max_hyperplanes}
              />
            )}
          </div>
        ) : (
          <div className="p-6 text-center text-xs text-slate-500 font-mono">
            No lattice data loaded.
          </div>
        )}
      </div>
    </Card>
  );
};
