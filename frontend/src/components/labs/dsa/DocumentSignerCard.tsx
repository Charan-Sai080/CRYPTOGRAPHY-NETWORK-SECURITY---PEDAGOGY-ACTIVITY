import React, { useState } from 'react';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { AlertBanner } from '../../common/AlertBanner';
import { signDsaMessage } from '../../../api/dsaApi';
import { parseApiError } from '../../../api/client';
import { DSAPrivateKey, DSASignResponse } from '../../../types/dsa';
import { PenTool, ArrowRight } from 'lucide-react';
import { MathFormula } from '../../common/MathFormula';

interface DocumentSignerCardProps {
  privateKey: DSAPrivateKey | null;
  onSignatureGenerated?: (message: string, r: string, s: string) => void;
}

export const DocumentSignerCard: React.FC<DocumentSignerCardProps> = ({
  privateKey,
  onSignatureGenerated,
}) => {
  const [message, setMessage] = useState<string>(
    "Transfer $5,000 to Bob's Account - Authorization ID #8841"
  );
  const [nonceK, setNonceK] = useState<string>('');
  const [signResult, setSignResult] = useState<DSASignResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleSign = async () => {
    if (!privateKey) {
      setError('Please generate DSA key pair in the setup card first.');
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const res = await signDsaMessage({
        message,
        p: Number(privateKey.p),
        q: Number(privateKey.q),
        g: Number(privateKey.g),
        x: Number(privateKey.x),
        seed_k: nonceK.trim() ? Number(nonceK.trim()) : undefined,
      });
      setSignResult(res);
      if (onSignatureGenerated) {
        onSignatureGenerated(res.trace.message, res.r_str, res.s_str);
      }
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card
      title="FIPS 186-4 Digital Signature Engine"
      subtitle="Sign arbitrary messages using SHA-256 hash truncation and ephemeral random secret k"
      icon={<PenTool className="w-5 h-5 text-indigo-500" />}
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
        {/* Document Text */}
        <div>
          <label htmlFor="doc-text" className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
            Document / Transaction Payload:
          </label>
          <textarea
            id="doc-text"
            rows={2}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            className="w-full p-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
          />
        </div>

        {/* Nonce k input */}
        <div>
          <label htmlFor="dsa-k" className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
            Ephemeral Nonce k &isin; [1, q - 1] (Leave blank for CSPRNG random):
          </label>
          <input
            id="dsa-k"
            type="number"
            value={nonceK}
            onChange={(e) => setNonceK(e.target.value)}
            placeholder="Auto-generated cryptographic random nonce"
            className="w-full p-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
          />
        </div>

        {/* Action Button */}
        <div>
          <Button
            variant="primary"
            onClick={handleSign}
            isLoading={isLoading}
            disabled={!privateKey}
            icon={<ArrowRight className="w-4 h-4" />}
          >
            Compute Digital Signature (r, s)
          </Button>
        </div>

        {/* Signing Trace Result */}
        {signResult && (
          <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-800 space-y-4 font-mono text-xs">
            {/* Signature Output */}
            <div className="p-4 rounded-xl bg-indigo-50/50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-900">
              <div className="flex items-center justify-between text-indigo-700 dark:text-indigo-300 font-semibold mb-2">
                <span className="font-sans">Generated DSA Signature Pair (r, s):</span>
                {signResult.trace.resample_count > 0 && (
                  <span className="text-[10px] px-2 py-0.5 rounded bg-amber-100 text-amber-800 font-bold">
                    FIPS 186-4 Resampled {signResult.trace.resample_count}x (r=0 or s=0)
                  </span>
                )}
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="p-2.5 rounded bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                  <span className="text-slate-400 block text-[10px]">r = (g^k mod p) mod q:</span>
                  <span className="font-bold text-indigo-600 dark:text-indigo-400 break-all select-all">
                    {signResult.r_str}
                  </span>
                </div>
                <div className="p-2.5 rounded bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                  <span className="text-slate-400 block text-[10px]">s = k^-1 (z + x &middot; r) mod q:</span>
                  <span className="font-bold text-indigo-600 dark:text-indigo-400 break-all select-all">
                    {signResult.s_str}
                  </span>
                </div>
              </div>
            </div>

            {/* Arithmetic Steps from Single Trace Object */}
            <div className="space-y-2">
              <span className="font-sans font-semibold text-slate-500 uppercase tracking-wide block">
                FIPS 186-4 Cryptographic Signing Pipeline Steps:
              </span>

              {/* Step 1: SHA-256 Digest */}
              <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                <div className="flex items-center justify-between font-sans text-slate-500 text-[11px] mb-1">
                  <span className="font-semibold text-slate-700 dark:text-slate-300">
                    Step 1: SHA-256 Hash Digest &amp; Truncation (z)
                  </span>
                  <span>z = {signResult.hash_int}</span>
                </div>
                <div className="text-indigo-600 dark:text-indigo-400 font-mono my-1 break-all">
                  SHA-256 Hex: {signResult.hash_hex}
                </div>
              </div>

              {/* Step 2: Nonce & Inversion */}
              <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                <div className="flex items-center justify-between font-sans text-slate-500 text-[11px] mb-1">
                  <span className="font-semibold text-slate-700 dark:text-slate-300">
                    Step 2: Ephemeral Secret k &amp; Modular Inverse (k^-1 mod q)
                  </span>
                  <span>k = {signResult.trace.k}, k^-1 mod q = {signResult.trace.k_inv}</span>
                </div>
                <div className="text-indigo-600 dark:text-indigo-400 font-mono my-1">
                  <MathFormula math={`k \\cdot k^{-1} \\equiv ${signResult.trace.k} \\cdot ${signResult.trace.k_inv} \\equiv 1 \\pmod{${signResult.trace.q}}`} />
                </div>
              </div>

              {/* Step 3: r formula */}
              <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                <div className="flex items-center justify-between font-sans text-slate-500 text-[11px] mb-1">
                  <span className="font-semibold text-slate-700 dark:text-slate-300">
                    Step 3: Component r Calculation
                  </span>
                  <span>r = {signResult.r}</span>
                </div>
                <div className="text-indigo-600 dark:text-indigo-400 font-mono my-1">
                  <MathFormula math={signResult.trace.formula_r} />
                </div>
              </div>

              {/* Step 4: s formula */}
              <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                <div className="flex items-center justify-between font-sans text-slate-500 text-[11px] mb-1">
                  <span className="font-semibold text-slate-700 dark:text-slate-300">
                    Step 4: Component s Calculation
                  </span>
                  <span>s = {signResult.s}</span>
                </div>
                <div className="text-indigo-600 dark:text-indigo-400 font-mono my-1">
                  <MathFormula math={signResult.trace.formula_s} />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};
