import React, { useState } from 'react';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { AlertBanner } from '../../common/AlertBanner';
import { MathFormula } from '../../common/MathFormula';
import { analyzeTwoTimePad } from '../../../api/otpApi';
import { parseApiError } from '../../../api/client';
import { TwoTimePadAnalyzeResponse } from '../../../types/otp';
import { ShieldAlert, Zap, Copy, Check } from 'lucide-react';

interface TwoTimePadSandboxProps {
  onXorCalculated?: (c1XorC2Hex: string) => void;
}

export const TwoTimePadSandbox: React.FC<TwoTimePadSandboxProps> = ({
  onXorCalculated,
}) => {
  const [msg1, setMsg1] = useState<string>('Attack at dawn tomorrow!');
  const [msg2, setMsg2] = useState<string>('Retreat to southern base');
  const [simulatedKey, setSimulatedKey] = useState<string>(
    '7a4f91c3d2e5b8a04411ee66299100ffaa33bbcc445566778899001122334455'
  );
  const [c1Hex, setC1Hex] = useState<string>('');
  const [c2Hex, setC2Hex] = useState<string>('');
  const [analysis, setAnalysis] = useState<TwoTimePadAnalyzeResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<boolean>(false);

  // Helper to XOR two byte arrays in browser for instant preview
  const runSimulatedEncryption = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const b1 = new TextEncoder().encode(msg1);
      const b2 = new TextEncoder().encode(msg2);
      const keyBytes = new Uint8Array(
        simulatedKey.match(/.{1,2}/g)?.map((byte) => parseInt(byte, 16)) || []
      );

      // Pad key if needed
      const maxLen = Math.max(b1.length, b2.length);
      const padKey = new Uint8Array(maxLen);
      for (let i = 0; i < maxLen; i++) {
        padKey[i] = keyBytes[i % keyBytes.length];
      }

      // Compute C1 and C2
      const c1 = new Uint8Array(b1.length);
      for (let i = 0; i < b1.length; i++) c1[i] = b1[i] ^ padKey[i];

      const c2 = new Uint8Array(b2.length);
      for (let i = 0; i < b2.length; i++) c2[i] = b2[i] ^ padKey[i];

      const c1H = Array.from(c1)
        .map((b) => b.toString(16).padStart(2, '0'))
        .join('');
      const c2H = Array.from(c2)
        .map((b) => b.toString(16).padStart(2, '0'))
        .join('');

      setC1Hex(c1H);
      setC2Hex(c2H);

      // Call backend to analyze key cancellation
      const res = await analyzeTwoTimePad({
        c1: c1H,
        c2: c2H,
        input_format: 'hex',
        p1_known: msg1,
      });
      setAnalysis(res);
      if (onXorCalculated) {
        onXorCalculated(res.xor_diff_hex);
      }
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  const copyText = (txt: string) => {
    navigator.clipboard.writeText(txt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Card
      title="Two-Time Pad (Key Reuse) Vulnerability Sandbox"
      subtitle="Witness the catastrophic algebraic cancellation when a key is reused across two ciphertexts"
      icon={<ShieldAlert className="w-5 h-5 text-rose-500" />}
      className="border-rose-200 dark:border-rose-900/60"
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
        {/* Messages Input Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="msg1" className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Message 1 (Alice &rarr; Bob):
            </label>
            <input
              id="msg1"
              type="text"
              value={msg1}
              onChange={(e) => setMsg1(e.target.value)}
              className="w-full p-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-rose-500 focus:outline-none"
            />
          </div>

          <div>
            <label htmlFor="msg2" className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Message 2 (Alice &rarr; Charlie):
            </label>
            <input
              id="msg2"
              type="text"
              value={msg2}
              onChange={(e) => setMsg2(e.target.value)}
              className="w-full p-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-rose-500 focus:outline-none"
            />
          </div>
        </div>

        {/* Reused Key */}
        <div>
          <label htmlFor="reused-key" className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
            Reused Ephemeral Key K (Hex):
          </label>
          <input
            id="reused-key"
            type="text"
            value={simulatedKey}
            onChange={(e) => setSimulatedKey(e.target.value)}
            className="w-full p-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-rose-500 focus:outline-none"
          />
        </div>

        <div>
          <Button
            variant="danger"
            onClick={runSimulatedEncryption}
            isLoading={isLoading}
            icon={<Zap className="w-4 h-4" />}
          >
            Simulate Key Reuse &amp; Compute C1 &oplus; C2
          </Button>
        </div>

        {/* Results */}
        {analysis && (
          <div className="mt-6 pt-4 border-t border-slate-200 dark:border-slate-800 space-y-4">
            {/* KaTeX Proof */}
            <div className="p-4 bg-rose-50/60 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/60 rounded-xl">
              <span className="text-xs font-bold text-rose-800 dark:text-rose-300 uppercase tracking-wide block mb-2">
                Algebraic Key Cancellation Proof:
              </span>
              <div className="text-sm font-mono text-center">
                <MathFormula
                  math="C_1 \oplus C_2 = (P_1 \oplus K) \oplus (P_2 \oplus K) = P_1 \oplus P_2 \oplus (K \oplus K) = P_1 \oplus P_2"
                  block
                />
              </div>
              <div className="mt-3 space-y-1 text-xs text-rose-900 dark:text-rose-200 font-mono">
                {analysis.proof_steps.map((step, idx) => (
                  <div key={idx}>{step}</div>
                ))}
              </div>
            </div>

            {/* Ciphertexts & XOR hex stream */}
            <div className="space-y-2 text-xs font-mono">
              <div className="p-2.5 rounded bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
                <span className="text-slate-500 block text-[10px]">C_1 = P_1 &oplus; K:</span>
                <span className="text-amber-600 dark:text-amber-400 break-all">{c1Hex}</span>
              </div>
              <div className="p-2.5 rounded bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
                <span className="text-slate-500 block text-[10px]">C_2 = P_2 &oplus; K:</span>
                <span className="text-amber-600 dark:text-amber-400 break-all">{c2Hex}</span>
              </div>
              <div className="p-3 rounded bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-200 dark:border-indigo-800">
                <div className="flex items-center justify-between text-indigo-700 dark:text-indigo-300 font-semibold mb-1">
                  <span>C_1 &oplus; C_2 = P_1 &oplus; P_2 (Pure Plaintext XOR Stream, Entropy: {analysis.shannon_entropy_diff.toFixed(2)} bits/byte):</span>
                  <button
                    type="button"
                    onClick={() => copyText(analysis.xor_diff_hex)}
                    className="flex items-center gap-1 hover:underline text-xs"
                  >
                    {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>Copy XOR Hex</span>
                  </button>
                </div>
                <div className="text-indigo-950 dark:text-indigo-200 font-bold break-all select-all">
                  {analysis.xor_diff_hex}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};
