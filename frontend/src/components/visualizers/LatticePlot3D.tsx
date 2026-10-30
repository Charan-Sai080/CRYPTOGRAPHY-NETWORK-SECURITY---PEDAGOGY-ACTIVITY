import React, { useEffect, useRef, useState } from 'react';
import { LatticePoint3D } from '../../types/lcg';
import { RotateCcw } from 'lucide-react';

interface LatticePlot3DProps {
  points: LatticePoint3D[];
  theoreticalBound?: number;
  width?: number;
  height?: number;
}

export const LatticePlot3D: React.FC<LatticePlot3DProps> = ({
  points,
  theoreticalBound,
  width = 450,
  height = 360,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [rotX, setRotX] = useState<number>(0.5); // pitch
  const [rotY, setRotY] = useState<number>(0.6); // yaw
  const isDraggingRef = useRef<boolean>(false);
  const lastMouseRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });

  const resetRotation = () => {
    setRotX(0.5);
    setRotY(0.6);
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.scale(dpr, dpr);

    const isDark = document.documentElement.classList.contains('dark');
    const bgColor = isDark ? '#090d16' : '#f8fafc';
    const cubeColor = isDark ? '#334155' : '#cbd5e1';
    const pointColor = isDark ? '#a78bfa' : '#6d28d9';

    ctx.fillStyle = bgColor;
    ctx.fillRect(0, 0, width, height);

    // Center of projection
    const cx = width / 2;
    const cy = height / 2;
    const scale = Math.min(width, height) * 0.45;

    // 3D rotation projection helper
    const project = (x: number, y: number, z: number): [number, number, number] => {
      // Center coordinates around [-0.5, 0.5]
      const nx = x - 0.5;
      const ny = y - 0.5;
      const nz = z - 0.5;

      // Rotate around Y axis (yaw)
      const cosY = Math.cos(rotY);
      const sinY = Math.sin(rotY);
      const x1 = nx * cosY + nz * sinY;
      const y1 = ny;
      const z1 = -nx * sinY + nz * cosY;

      // Rotate around X axis (pitch)
      const cosX = Math.cos(rotX);
      const sinX = Math.sin(rotX);
      const x2 = x1;
      const y2 = y1 * cosX - z1 * sinX;
      const z2 = y1 * sinX + z1 * cosX;

      // Screen coords
      const px = cx + x2 * scale;
      const py = cy - y2 * scale; // Invert Y
      return [px, py, z2];
    };

    // Draw 3D Bounding Cube Edges
    const corners = [
      [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
      [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1],
    ];
    const edges = [
      [0, 1], [1, 2], [2, 3], [3, 0], // bottom face
      [4, 5], [5, 6], [6, 7], [7, 4], // top face
      [0, 4], [1, 5], [2, 6], [3, 7], // vertical pillars
    ];

    ctx.strokeStyle = cubeColor;
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    for (const [s, e] of edges) {
      const [sx, sy] = project(corners[s][0], corners[s][1], corners[s][2]);
      const [ex, ey] = project(corners[e][0], corners[e][1], corners[e][2]);
      ctx.moveTo(sx, sy);
      ctx.lineTo(ex, ey);
    }
    ctx.stroke();
    ctx.setLineDash([]);

    // Draw points (sorted by depth z2 for realistic painter's rendering)
    const pointsToPlot = points.slice(0, 3000);
    const projectedPoints = pointsToPlot.map((p) => {
      const [px, py, pz] = project(p.x, p.y, p.z);
      return { px, py, pz };
    });

    projectedPoints.sort((a, b) => a.pz - b.pz);

    ctx.fillStyle = pointColor;
    for (let i = 0; i < projectedPoints.length; i++) {
      const pt = projectedPoints[i];
      // Size depends slightly on depth
      const r = Math.max(0.8, 1.6 + pt.pz * 0.8);
      ctx.beginPath();
      ctx.arc(pt.px, pt.py, r, 0, Math.PI * 2);
      ctx.fill();
    }
  }, [points, rotX, rotY, width, height]);

  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    isDraggingRef.current = true;
    lastMouseRef.current = { x: e.clientX, y: e.clientY };
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDraggingRef.current) return;
    const dx = e.clientX - lastMouseRef.current.x;
    const dy = e.clientY - lastMouseRef.current.y;
    lastMouseRef.current = { x: e.clientX, y: e.clientY };

    setRotY((prev) => prev + dx * 0.01);
    setRotX((prev) => Math.max(-Math.PI / 2, Math.min(Math.PI / 2, prev + dy * 0.01)));
  };

  const handleMouseUp = () => {
    isDraggingRef.current = false;
  };

  return (
    <div className="flex flex-col items-center select-none">
      <div className="relative border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-inner cursor-grab active:cursor-grabbing">
        <canvas
          ref={canvasRef}
          style={{ width: `${width}px`, height: `${height}px` }}
          className="block"
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
        />
        {theoreticalBound !== undefined && (
          <div className="absolute top-2 right-2 bg-slate-900/80 dark:bg-slate-950/80 backdrop-blur-xs text-[11px] font-mono text-violet-300 px-2 py-1 rounded border border-violet-500/30">
            3D Marsaglia Bound: &le; {Math.round(theoreticalBound)} planes
          </div>
        )}
        <button
          type="button"
          onClick={resetRotation}
          className="absolute bottom-2 right-2 p-1.5 rounded-lg bg-slate-800/70 hover:bg-slate-800 text-slate-300 transition-colors border border-slate-700 text-xs flex items-center gap-1"
          title="Reset 3D camera orientation"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset</span>
        </button>
      </div>
      <div className="mt-2 text-xs text-slate-500 dark:text-slate-400 font-mono text-center">
        Click and drag to rotate the 3D unit cube &bull; {Math.min(points.length, 3000).toLocaleString()} triples (X_n, X_{'{n+1}'}, X_{'{n+2}'})
      </div>
    </div>
  );
};
