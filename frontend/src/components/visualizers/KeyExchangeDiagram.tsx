import React from 'react';
import { UserCheck, ShieldAlert, ArrowRight, Lock, Key } from 'lucide-react';
import { MathFormula } from '../common/MathFormula';

export const KeyExchangeDiagram: React.FC = () => {
  return (
    <div className="p-4 bg-slate-50 dark:bg-slate-900/60 rounded-xl border border-slate-200 dark:border-slate-800">
      <div className="text-xs uppercase tracking-wider font-semibold text-slate-500 dark:text-slate-400 mb-4">
        Asymmetric Key Flow &bull; Diffie-Hellman / ElGamal Architecture
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 items-stretch">
        {/* Alice (Receiver) */}
        <div className="p-4 rounded-xl bg-white dark:bg-slate-800 border border-indigo-200 dark:border-indigo-900/50 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 text-indigo-600 dark:text-indigo-400 font-bold text-sm mb-3">
              <UserCheck className="w-4 h-4" />
              <span>Alice (Receiver)</span>
            </div>
            <div className="space-y-2 text-xs">
              <div className="p-2 rounded bg-indigo-50/50 dark:bg-indigo-950/40 border border-indigo-100 dark:border-indigo-900/40">
                <span className="font-semibold block text-slate-700 dark:text-slate-300">1. Domain &amp; Keygen:</span>
                <div className="mt-1 font-mono text-[11px]">
                  <MathFormula math="x \in_R [2, p - 2]" />
                  <br />
                  <MathFormula math="y \equiv g^x \pmod p" />
                </div>
              </div>
              <div className="p-2 rounded bg-indigo-50/50 dark:bg-indigo-950/40 border border-indigo-100 dark:border-indigo-900/40">
                <span className="font-semibold block text-slate-700 dark:text-slate-300">4. Decryption:</span>
                <div className="mt-1 font-mono text-[11px]">
                  <MathFormula math="s \equiv c_1^x \equiv (g^k)^x \pmod p" />
                  <br />
                  <MathFormula math="m \equiv c_2 \cdot s^{-1} \pmod p" />
                </div>
              </div>
            </div>
          </div>
          <div className="mt-3 text-[11px] text-indigo-600 dark:text-indigo-400 font-medium flex items-center gap-1">
            <Key className="w-3.5 h-3.5" /> Holds Secret x
          </div>
        </div>

        {/* Public Insecure Channel & Eve */}
        <div className="p-4 rounded-xl bg-rose-50/50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900/50 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-rose-600 dark:text-rose-400 font-bold text-sm mb-3">
              <div className="flex items-center gap-2">
                <ShieldAlert className="w-4 h-4" />
                <span>Insecure Public Network</span>
              </div>
              <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-rose-100 dark:bg-rose-900 text-rose-800 dark:text-rose-200">
                Eavesdropper Eve
              </span>
            </div>
            <div className="space-y-2 text-xs">
              <div className="p-2 rounded bg-white dark:bg-slate-800 border border-rose-200 dark:border-rose-900/40 font-mono text-[11px] text-center">
                <span className="text-slate-500 block text-[10px]">Public Parameters:</span>
                <span className="font-bold text-slate-800 dark:text-slate-200">(p, g, y)</span>
              </div>
              <div className="flex items-center justify-center text-slate-400">
                <ArrowRight className="w-4 h-4" />
              </div>
              <div className="p-2 rounded bg-white dark:bg-slate-800 border border-rose-200 dark:border-rose-900/40 font-mono text-[11px] text-center">
                <span className="text-slate-500 block text-[10px]">Transmitted Ciphertext:</span>
                <span className="font-bold text-amber-600 dark:text-amber-400">(c_1 = g^k, c_2 = m &middot; y^k)</span>
              </div>
            </div>
          </div>
          <div className="mt-3 text-[11px] text-rose-600 dark:text-rose-400 font-mono bg-rose-100/50 dark:bg-rose-950/60 p-2 rounded text-center">
            Security Hardness: Discrete Log <MathFormula math="\log_g y" /> or <MathFormula math="\log_g c_1" /> is intractable!
          </div>
        </div>

        {/* Bob (Sender) */}
        <div className="p-4 rounded-xl bg-white dark:bg-slate-800 border border-amber-200 dark:border-amber-900/50 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 text-amber-600 dark:text-amber-400 font-bold text-sm mb-3">
              <Lock className="w-4 h-4" />
              <span>Bob (Sender)</span>
            </div>
            <div className="space-y-2 text-xs">
              <div className="p-2 rounded bg-amber-50/50 dark:bg-amber-950/40 border border-amber-100 dark:border-amber-900/40">
                <span className="font-semibold block text-slate-700 dark:text-slate-300">2. Ephemeral Nonce:</span>
                <div className="mt-1 font-mono text-[11px]">
                  <MathFormula math="k \in_R [2, p - 2]" />
                </div>
              </div>
              <div className="p-2 rounded bg-amber-50/50 dark:bg-amber-950/40 border border-amber-100 dark:border-amber-900/40">
                <span className="font-semibold block text-slate-700 dark:text-slate-300">3. Encapsulation:</span>
                <div className="mt-1 font-mono text-[11px]">
                  <MathFormula math="c_1 \equiv g^k \pmod p" />
                  <br />
                  <MathFormula math="s \equiv y^k \pmod p" />
                  <br />
                  <MathFormula math="c_2 \equiv (m \cdot s) \pmod p" />
                </div>
              </div>
            </div>
          </div>
          <div className="mt-3 text-[11px] text-amber-600 dark:text-amber-400 font-medium flex items-center gap-1">
            <Lock className="w-3.5 h-3.5" /> Generates (c_1, c_2)
          </div>
        </div>
      </div>
    </div>
  );
};
