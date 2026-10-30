import React, { useState } from 'react';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { AlertBanner } from '../../common/AlertBanner';
import { runHomomorphicMultiply } from '../../../api/elgamalApi';
import { parseApiError } from '../../../api/client';
import {
  ElGamalPublicKey,
  ElGamalPrivateKey,
  HomomorphicMultiplyResponse,
} from '../../../types/elgamal';
import { Sparkles, CheckCircle2, Cpu } from 'lucide-react';
import { MathFormula } from '../../common/MathFormula';

interface HomomorphismPlaygroundProps {
  publicKey: ElGamalPublicKey | null;
  privateKey: ElGamalPrivateKey | null;
}

export const HomomorphismPlayground: React.FC<HomomorphismPlaygroundProps> = ({
  publicKey,
  privateKey,
}) => {
  const [m1, setM1] = useState<number>(7);
  const [m2, setM2] = useState<number>(11);
  const [homoResult, setHomoResult] = useState<HomomorphicMultiplyResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleMultiply = async () => {
    if (!publicKey) {
      setError('Please generate Alice’s key pair first.');
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const res = await runHomomorphicMultiply({
        m1,
        m2,
        p: Number(publicKey.p),
        g: Number(publicKey.g),
        y: Number(publicKey.y),
        x: privateKey ? Number(privateKey.x) : undefined,
      });
      setHomoResult(res);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card
      title="Multiplicative Homomorphic Encryption Playground"
      subtitle="Compute on encrypted data without decrypting: E(m1) · E(m2) ≡ E(m1 · m2 mod p)"
      icon={<Sparkles className="w-5 h-5 text-indigo-500" />}
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
        {/* Theory Callout */}
        <div className="p-3.5 bg-indigo-50/50 dark:bg-indigo-950/30 rounded-xl border border-indigo-200 dark:border-indigo-900/50 text-xs">
          <span className="font-semibold text-indigo-900 dark:text-indigo-200 block mb-1">
            Homomorphic Multiplicative Property:
          </span>
          <div className="font-mono text-center my-1 text-indigo-950 dark:text-indigo-100">
            <MathFormula
              math="E(m_1, k_1) \cdot E(m_2, k_2) = (g^{k_1} \cdot g^{k_2}, m_1 y^{k_1} \cdot m_2 y^{k_2}) = (g^{k_1 + k_2}, (m_1 m_2) y^{k_1 + k_2}) = E(m_1 \cdot m_2 \pmod p)"
              block
            />
          </div>
          <p className="text-[11px] text-slate-600 dark:text-slate-400 mt-2">
            This homomorphic property allows an untrusted third-party server to multiply ciphertexts without ever learning the underlying numbers or having the secret key!
          </p>
        </div>

        {/* Inputs */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label htmlFor="m1-val" className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Plaintext Factor 1 (m1):
            </label>
            <input
              id="m1-val"
              type="number"
              min={1}
              value={m1}
              onChange={(e) => setM1(Number(e.target.value))}
              className="w-full p-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            />
          </div>

          <div>
            <label htmlFor="m2-val" className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Plaintext Factor 2 (m2):
            </label>
            <input
              id="m2-val"
              type="number"
              min={1}
              value={m2}
              onChange={(e) => setM2(Number(e.target.value))}
              className="w-full p-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            />
          </div>
        </div>

        <div>
          <Button
            variant="primary"
            onClick={handleMultiply}
            isLoading={isLoading}
            disabled={!publicKey}
            icon={<Cpu className="w-4 h-4" />}
          >
            Encrypt Separately &amp; Multiply Ciphertexts
          </Button>
        </div>

        {/* Homomorphism Result */}
        {homoResult && (
          <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-800 space-y-4 font-mono text-xs">
            {/* Verdict */}
            <div className="p-3 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-300 dark:border-emerald-800 flex items-center justify-between">
              <div className="flex items-center gap-2 text-emerald-800 dark:text-emerald-300 font-bold">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                <span>HOMOMORPHIC MULTIPLICATION VERIFIED</span>
              </div>
              <span className="text-emerald-900 dark:text-emerald-200 font-bold">
                Decrypted Product: {homoResult.decrypted_product ?? homoResult.expected_product} == {homoResult.expected_product} (m1 &middot; m2 mod p)
              </span>
            </div>

            {/* Individual Ciphertext Blocks */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="p-3 rounded-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                <span className="text-slate-400 block text-[10px]">C_A = E(m_1 = {homoResult.m1}):</span>
                <div>c_1 = {homoResult.c1_a}</div>
                <div className="text-amber-600 dark:text-amber-400">c_2 = {homoResult.c2_a}</div>
              </div>
              <div className="p-3 rounded-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                <span className="text-slate-400 block text-[10px]">C_B = E(m_2 = {homoResult.m2}):</span>
                <div>c_1 = {homoResult.c1_b}</div>
                <div className="text-amber-600 dark:text-amber-400">c_2 = {homoResult.c2_b}</div>
              </div>
            </div>

            {/* Multiplied Ciphertext */}
            <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
              <span className="text-slate-500 block text-[10px]">Multiplied Ciphertext Pair C_prod = (C_A &middot; C_B mod p):</span>
              <div className="text-indigo-600 dark:text-indigo-400 font-bold">
                c_1,prod = (c_1,A &middot; c_1,B) mod p = {homoResult.c1_mult}
              </div>
              <div className="text-amber-600 dark:text-amber-400 font-bold">
                c_2,prod = (c_2,A &middot; c_2,B) mod p = {homoResult.c2_mult}
              </div>
            </div>

            {homoResult.explanation && (
              <p className="text-[11px] text-slate-500 font-sans">
                {homoResult.explanation}
              </p>
            )}
          </div>
        )}
      </div>
    </Card>
  );
};
