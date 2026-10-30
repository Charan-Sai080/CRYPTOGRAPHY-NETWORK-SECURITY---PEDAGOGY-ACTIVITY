import React, { useState } from 'react';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { AlertBanner } from '../../common/AlertBanner';
import { verifyDsaSignature } from '../../../api/dsaApi';
import { parseApiError } from '../../../api/client';
import { DSAPublicKey, DSAVerifyResponse } from '../../../types/dsa';
import { FileCheck, CheckCircle2, XCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { MathFormula } from '../../common/MathFormula';

interface VerificationProofCardProps {
  publicKey: DSAPublicKey | null;
  initialMessage?: string;
  initialR?: string;
  initialS?: string;
}

export const VerificationProofCard: React.FC<VerificationProofCardProps> = ({
  publicKey,
  initialMessage = "Transfer $5,000 to Bob's Account - Authorization ID #8841",
  initialR = '',
  initialS = '',
}) => {
  const [message, setMessage] = useState<string>(initialMessage);
  const [rVal, setRVal] = useState<string>(initialR);
  const [sVal, setSVal] = useState<string>(initialS);
  const [verifyResult, setVerifyResult] = useState<DSAVerifyResponse | null>(null);
  const [showProof, setShowProof] = useState<boolean>(true);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Sync if initial props change
  React.useEffect(() => {
    if (initialR) setRVal(initialR);
    if (initialS) setSVal(initialS);
    if (initialMessage) setMessage(initialMessage);
  }, [initialR, initialS, initialMessage]);

  const handleVerify = async () => {
    if (!publicKey) {
      setError('Public key is required to verify digital signature.');
      return;
    }
    if (!rVal.trim() || !sVal.trim()) {
      setError('Both signature components (r, s) are required.');
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const res = await verifyDsaSignature({
        message,
        r: Number(rVal.trim()),
        s: Number(sVal.trim()),
        p: Number(publicKey.p),
        q: Number(publicKey.q),
        g: Number(publicKey.g),
        y: Number(publicKey.y),
      });
      setVerifyResult(res);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card
      title="Signature Verification Engine &amp; Algebraic Proof"
      subtitle="Verify unforgeability via intermediate variables w, u1, u2, v and check v == r"
      icon={<FileCheck className="w-5 h-5 text-indigo-500" />}
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
        {/* Verification Inputs */}
        <div className="space-y-3 font-mono text-xs">
          <div>
            <label htmlFor="ver-doc" className="font-sans font-semibold text-slate-700 dark:text-slate-300 block mb-1">
              Document Message to Verify:
            </label>
            <textarea
              id="ver-doc"
              rows={2}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              className="w-full p-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label htmlFor="ver-r" className="font-sans font-semibold text-slate-700 dark:text-slate-300 block mb-1">
                Signature Component r:
              </label>
              <input
                id="ver-r"
                type="number"
                value={rVal}
                onChange={(e) => setRVal(e.target.value)}
                className="w-full p-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              />
            </div>
            <div>
              <label htmlFor="ver-s" className="font-sans font-semibold text-slate-700 dark:text-slate-300 block mb-1">
                Signature Component s:
              </label>
              <input
                id="ver-s"
                type="number"
                value={sVal}
                onChange={(e) => setSVal(e.target.value)}
                className="w-full p-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              />
            </div>
          </div>
        </div>

        <div>
          <Button
            variant="primary"
            onClick={handleVerify}
            isLoading={isLoading}
            disabled={!publicKey}
            icon={<FileCheck className="w-4 h-4" />}
          >
            Verify Digital Signature
          </Button>
        </div>

        {/* Verification Result */}
        {verifyResult && (
          <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-800 space-y-4 font-mono text-xs">
            {/* Verdict Card */}
            <div
              className={`p-4 rounded-xl border flex items-center justify-between ${
                verifyResult.is_valid
                  ? 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-300 dark:border-emerald-800 text-emerald-900 dark:text-emerald-200'
                  : 'bg-rose-50 dark:bg-rose-950/40 border-rose-300 dark:border-rose-800 text-rose-900 dark:text-rose-200'
              }`}
            >
              <div className="flex items-center gap-3">
                {verifyResult.is_valid ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                ) : (
                  <XCircle className="w-5 h-5 text-rose-600 dark:text-rose-400" />
                )}
                <div>
                  <h4 className="font-sans font-bold text-sm">
                    {verifyResult.is_valid ? 'VALID SIGNATURE CONFIRMED' : 'INVALID SIGNATURE DETECTED'}
                  </h4>
                  <p className="font-sans text-[11px] opacity-80">
                    {verifyResult.reason}
                  </p>
                </div>
              </div>
              <span className="font-bold text-sm">
                v: {verifyResult.v !== null ? verifyResult.v : 'N/A'} {verifyResult.is_valid ? '==' : '!='} r: {verifyResult.r}
              </span>
            </div>

            {/* Intermediate Calculation Pipeline */}
            {verifyResult.trace && (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                  <span className="text-slate-400 block text-[10px]">w &equiv; s^-1 mod q:</span>
                  <span className="font-bold text-slate-800 dark:text-slate-200 break-all">
                    {verifyResult.trace.w}
                  </span>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                  <span className="text-slate-400 block text-[10px]">u1 &equiv; (z &middot; w) mod q:</span>
                  <span className="font-bold text-slate-800 dark:text-slate-200 break-all">
                    {verifyResult.trace.u1}
                  </span>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                  <span className="text-slate-400 block text-[10px]">u2 &equiv; (r &middot; w) mod q:</span>
                  <span className="font-bold text-slate-800 dark:text-slate-200 break-all">
                    {verifyResult.trace.u2}
                  </span>
                </div>
                <div className="p-2.5 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-200 dark:border-indigo-900">
                  <span className="text-indigo-600 dark:text-indigo-400 block text-[10px]">v = (g^u1 &middot; y^u2 mod p) mod q:</span>
                  <span className="font-bold text-indigo-700 dark:text-indigo-300 break-all">
                    {verifyResult.trace.v}
                  </span>
                </div>
              </div>
            )}

            {/* LaTeX Soundness Proof Accordion */}
            <div className="rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden bg-slate-50 dark:bg-slate-900">
              <button
                type="button"
                onClick={() => setShowProof(!showProof)}
                className="w-full px-4 py-2.5 flex items-center justify-between text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-850"
              >
                <span>Mathematical Soundness Proof of DSA:</span>
                {showProof ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>

              {showProof && (
                <div className="p-4 pt-1 border-t border-slate-200 dark:border-slate-800 text-xs">
                  <div className="text-center my-2">
                    <MathFormula
                      math="v \equiv g^{u_1} y^{u_2} \equiv g^{z w} g^{x r w} \equiv g^{(z + x r) w} \equiv g^{(z + x r) s^{-1}} \equiv g^k \equiv r \pmod q"
                      block
                    />
                  </div>
                  <p className="font-sans text-[11px] text-slate-500 mt-2">
                    Because <MathFormula math="s \equiv k^{-1}(z + x r) \pmod q" />, multiplying by <MathFormula math="s^{-1}" /> recovers the exponent <MathFormula math="k" />, proving that only a party in possession of private key <MathFormula math="x" /> could generate matching signature components.
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};
