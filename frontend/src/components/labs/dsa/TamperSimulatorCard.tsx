import React, { useState } from 'react';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { AlertBanner } from '../../common/AlertBanner';
import { TamperIndicator } from '../../visualizers/TamperIndicator';
import { detectTampering } from '../../../api/dsaApi';
import { parseApiError } from '../../../api/client';
import { DSAPublicKey, DSAPrivateKey, DSATamperResponse } from '../../../types/dsa';
import { ShieldAlert, Zap, RefreshCw } from 'lucide-react';

interface TamperSimulatorCardProps {
  publicKey: DSAPublicKey | null;
  privateKey?: DSAPrivateKey | null;
  originalMessage: string;
  signatureR: string;
  signatureS: string;
}

export const TamperSimulatorCard: React.FC<TamperSimulatorCardProps> = ({
  publicKey,
  privateKey,
  originalMessage,
}) => {
  const [tamperedText, setTamperedText] = useState<string>(originalMessage);
  const [tamperResult, setTamperResult] = useState<DSATamperResponse | null>(null);
  const [bitIndex, setBitIndex] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  React.useEffect(() => {
    setTamperedText(originalMessage);
  }, [originalMessage]);

  const flipBitInDocument = () => {
    if (!tamperedText || tamperedText.length === 0) return;
    const charIndex = Math.floor(tamperedText.length / 2);
    const charCode = tamperedText.charCodeAt(charIndex);
    const flippedChar = String.fromCharCode(charCode ^ 1);
    const mutated =
      tamperedText.substring(0, charIndex) +
      flippedChar +
      tamperedText.substring(charIndex + 1);
    setTamperedText(mutated);
    setBitIndex((charIndex * 8) + 1);
  };

  const handleTestTampering = async (target: 'message' | 'r' | 's' = 'message') => {
    if (!publicKey) {
      setError('Please generate DSA public key first.');
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const res = await detectTampering({
        message: target === 'message' ? tamperedText : originalMessage,
        p: Number(publicKey.p),
        q: Number(publicKey.q),
        g: Number(publicKey.g),
        x: Number(privateKey?.x ?? 105),
        y: Number(publicKey.y),
        tamper_target: target,
        bit_index: bitIndex,
      });
      setTamperResult(res);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  const resetMessage = () => {
    setTamperedText(originalMessage);
    setTamperResult(null);
    setBitIndex(0);
  };

  return (
    <Card
      title="Real-Time Document &amp; Signature Tampering Simulator"
      subtitle="Experience how single-bit alterations trigger SHA-256 avalanche and invalidate DSA verification"
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
        {/* Document Editor */}
        <div>
          <div className="flex justify-between items-center text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
            <label htmlFor="tampered-text">Target Document (Edit or click Flip 1-Bit):</label>
            {tamperedText !== originalMessage && (
              <span className="text-[10px] px-2 py-0.5 rounded bg-rose-100 text-rose-800 font-mono font-bold">
                1+ Bits Mutated!
              </span>
            )}
          </div>
          <textarea
            id="tampered-text"
            rows={2}
            value={tamperedText}
            onChange={(e) => setTamperedText(e.target.value)}
            className="w-full p-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-rose-500 focus:outline-none"
          />
        </div>

        {/* Mutation Controls */}
        <div className="flex flex-wrap items-center gap-2">
          <Button
            variant="danger"
            size="sm"
            onClick={flipBitInDocument}
            icon={<Zap className="w-3.5 h-3.5" />}
          >
            Flip 1 Bit in Document
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={() => handleTestTampering('message')}
            isLoading={isLoading}
          >
            Check Tampered Document
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={() => handleTestTampering('r')}
            isLoading={isLoading}
          >
            Mutate Signature (r)
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={() => handleTestTampering('s')}
            isLoading={isLoading}
          >
            Mutate Signature (s)
          </Button>

          <Button
            variant="ghost"
            size="sm"
            onClick={resetMessage}
            icon={<RefreshCw className="w-3.5 h-3.5" />}
          >
            Restore Original
          </Button>
        </div>

        {/* Live Discrepancy Indicator */}
        {tamperResult && (
          <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-800">
            <TamperIndicator result={tamperResult} />
          </div>
        )}
      </div>
    </Card>
  );
};
