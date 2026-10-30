import React, { useEffect, useRef } from 'react';
import { LatticePoint2D } from '../../types/lcg';

interface LatticePlot2DProps {
  points: LatticePoint2D[];
  theoreticalBound?: number;
  width?: number;
  height?: number;
}

export const LatticePlot2D: React.FC<LatticePlot2DProps> = ({
  points,
  theoreticalBound,
  width = 450,
  height = 360,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Support High-DPI screens
    const dpr = window.devicePixelRatio || 1;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.scale(dpr, dpr);

    // Dark/Light detection
    const isDark = document.documentElement.classList.contains('dark');
    const bgColor = isDark ? '#090d16' : '#f8fafc';
    const gridColor = isDark ? '#1e293b' : '#e2e8f0';
    const axisColor = isDark ? '#475569' : '#94a3b8';
    const pointColor = isDark ? '#818cf8' : '#4f46e5';

    // Background
    ctx.fillStyle = bgColor;
    ctx.fillRect(0, 0, width, height);

    const pad = 40;
    const plotW = width - pad * 2;
    const plotH = height - pad * 2;

    // Draw Grid
    ctx.strokeStyle = gridColor;
    ctx.lineWidth = 1;
    ctx.beginPath();
    const gridDivs = 4;
    for (let i = 0; i <= gridDivs; i++) {
      const gx = pad + (plotW * i) / gridDivs;
      const gy = pad + (plotH * i) / gridDivs;
      // vertical
      ctx.moveTo(gx, pad);
      ctx.lineTo(gx, pad + plotH);
      // horizontal
      ctx.moveTo(pad, gy);
      ctx.lineTo(pad + plotW, gy);
    }
    ctx.stroke();

    // Draw Axes
    ctx.strokeStyle = axisColor;
    ctx.lineWidth = 1.5;
    ctx.strokeRect(pad, pad, plotW, plotH);

    // Axes Labels
    ctx.fillStyle = axisColor;
    ctx.font = '10px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('0.0', pad, pad + plotH + 15);
    ctx.fillText('0.5', pad + plotW / 2, pad + plotH + 15);
    ctx.fillText('1.0', pad + plotW, pad + plotH + 15);
    ctx.fillText('X(n)', pad + plotW / 2, pad + plotH + 28);

    ctx.textAlign = 'right';
    ctx.fillText('0.0', pad - 8, pad + plotH + 3);
    ctx.fillText('0.5', pad - 8, pad + plotH / 2 + 3);
    ctx.fillText('1.0', pad - 8, pad + 3);

    // Plot Points (cap to 5000 for smooth 60fps)
    const pointsToPlot = points.slice(0, 5000);
    ctx.fillStyle = pointColor;

    for (let i = 0; i < pointsToPlot.length; i++) {
      const p = pointsToPlot[i];
      const px = pad + p.x * plotW;
      const py = pad + (1 - p.y) * plotH; // Invert Y for Cartesian

      ctx.beginPath();
      ctx.arc(px, py, 1.8, 0, Math.PI * 2);
      ctx.fill();
    }
  }, [points, width, height]);

  return (
    <div className="flex flex-col items-center">
      <div className="relative border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-inner">
        <canvas
          ref={canvasRef}
          style={{ width: `${width}px`, height: `${height}px` }}
          className="block"
        />
        {theoreticalBound !== undefined && (
          <div className="absolute top-2 right-2 bg-slate-900/80 dark:bg-slate-950/80 backdrop-blur-xs text-[11px] font-mono text-indigo-300 px-2 py-1 rounded border border-indigo-500/30">
            Marsaglia Bound: &le; {Math.round(theoreticalBound)} lines
          </div>
        )}
      </div>
      <div className="mt-2 text-xs text-slate-500 dark:text-slate-400 font-mono text-center">
        Normalized pairs (X_n / m, X_{'{n+1}'} / m) &bull; Displaying {Math.min(points.length, 5000).toLocaleString()} points
      </div>
    </div>
  );
};
