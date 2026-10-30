import React from 'react';
import { Layers } from 'lucide-react';

interface TextChunkingVisualizerProps {
  text: string;
  blockSizeBytes: number;
  totalBlocks: number;
}

export const TextChunkingVisualizer: React.FC<TextChunkingVisualizerProps> = ({
  text,
  blockSizeBytes,
  totalBlocks,
}) => {
  if (!text || blockSizeBytes <= 0) return null;

  const encoder = new TextEncoder();
  const rawBytes = encoder.encode(text);

  // Divide into chunks
  const chunks: { index: number; sliceText: string; hex: string; intVal: bigint }[] = [];
  for (let i = 0; i < rawBytes.length; i += blockSizeBytes) {
    const slice = rawBytes.subarray(i, i + blockSizeBytes);
    let intVal = 0n;
    for (const b of slice) {
      intVal = (intVal << 8n) | BigInt(b);
    }
    const hex = Array.from(slice)
      .map((b) => b.toString(16).padStart(2, '0'))
      .join('');
    const sliceText = new TextDecoder().decode(slice);
    chunks.push({
      index: i / blockSizeBytes,
      sliceText,
      hex,
      intVal,
    });
  }

  return (
    <div className="p-3 bg-slate-50 dark:bg-slate-900/60 rounded-xl border border-slate-200 dark:border-slate-800 space-y-3">
      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center gap-1.5 font-semibold text-slate-700 dark:text-slate-300">
          <Layers className="w-4 h-4 text-indigo-500" />
          <span>UTF-8 Message Chunking Pipeline</span>
        </div>
        <span className="text-slate-500 font-mono">
          Chunk Size: {blockSizeBytes} bytes &bull; {totalBlocks} Blocks
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
        {chunks.map((chk) => (
          <div
            key={chk.index}
            className="p-2.5 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 font-mono text-xs"
          >
            <div className="flex items-center justify-between text-[10px] text-slate-400 mb-1">
              <span>Block #{chk.index}</span>
              <span>0x{chk.hex}</span>
            </div>
            <div className="font-bold text-indigo-600 dark:text-indigo-400 truncate">
              &ldquo;{chk.sliceText}&rdquo;
            </div>
            <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 truncate">
              Big-Endian Integer: <span className="font-semibold text-slate-700 dark:text-slate-200">{chk.intVal.toString()}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
