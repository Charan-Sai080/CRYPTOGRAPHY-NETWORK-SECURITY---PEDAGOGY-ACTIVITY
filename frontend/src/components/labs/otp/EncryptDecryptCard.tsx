import React, { useState } from 'react';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { AlertBanner } from '../../common/AlertBanner';
import { ByteVisualizer } from './ByteVisualizer';
import { encryptOtp, decryptOtp } from '../../../api/otpApi';
import { parseApiError } from '../../../api/client';
import { OTPEncryptResponse, OTPDecryptResponse } from '../../../types/otp';
import { Lock, Unlock, ArrowRight, ShieldCheck, Copy, Check } from 'lucide-react';
import { MathFormula } from '../../common/MathFormula';

interface EncryptDecryptCardProps {
  initialKey?: string;
}

export const EncryptDecryptCard: React.FC<EncryptDecryptCardProps> = ({
  initialKey = '',
}) => {
  const [mode, setMode] = useState<'encrypt' | 'decrypt'>('encrypt');
  const [plaintext, setPlaintext] = useState<string>('Cryptography is fun!');
  const [keyInput, setKeyInput] = useState<string>(initialKey);
  const [ciphertextInput, setCiphertextInput] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [encryptResult, setEncryptResult] = useState<OTPEncryptResponse | null>(null);
  const [decryptResult, setDecryptResult] = useState<OTPDecryptResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<boolean>(false);

  // Sync initialKey if updated externally
  React.useEffect(() => {
    if (initialKey) {
      setKeyInput(initialKey);
    }
  }, [initialKey]);

  const plainLen = new TextEncoder().encode(plaintext).length;
  // Key hex length in bytes is length / 2
  const keyBytesLen = keyInput.trim().length / 2;
  const isKeyShort = mode === 'encrypt' && keyInput.length > 0 && keyBytesLen < plainLen;

  const handleEncrypt = async () => {
    if (!keyInput.trim()) {
      setError('Please provide or generate a hexadecimal key first.');
      return;
    }
    if (isKeyShort) {
      setError(
        `Key length (${keyBytesLen} bytes) is shorter than plaintext (${plainLen} bytes). Perfect Secrecy requires |K| >= |M|.`
      );
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const res = await encryptOtp({
        plaintext,
        key: keyInput.trim(),
        key_format: 'hex',
      });
      setEncryptResult(res);
      setCiphertextInput(res.ciphertext_hex);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleDecrypt = async () => {
    if (!ciphertextInput.trim() || !keyInput.trim()) {
      setError('Both ciphertext (hex) and key (hex) are required.');
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const res = await decryptOtp({
        ciphertext: ciphertextInput.trim(),
        key: keyInput.trim(),
        ciphertext_format: 'hex',
        key_format: 'hex',
      });
      setDecryptResult(res);
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
      title="Traced XOR Sandbox & Bitwise Cryptanalysis"
      subtitle="Examine byte-by-byte and bit-by-bit XOR truth table operations"
      icon={<Lock className="w-5 h-5" />}
      action={
        <div className="flex bg-slate-100 dark:bg-slate-800 p-1 rounded-lg">
          <button
            type="button"
            onClick={() => {
              setMode('encrypt');
              setError(null);
            }}
            className={`px-3 py-1 rounded text-xs font-semibold transition-all ${
              mode === 'encrypt'
                ? 'bg-indigo-600 text-white shadow-xs'
                : 'text-slate-600 dark:text-slate-300'
            }`}
          >
            Encrypt (M &oplus; K)
          </button>
          <button
            type="button"
            onClick={() => {
              setMode('decrypt');
              setError(null);
            }}
            className={`px-3 py-1 rounded text-xs font-semibold transition-all ${
              mode === 'decrypt'
                ? 'bg-indigo-600 text-white shadow-xs'
                : 'text-slate-600 dark:text-slate-300'
            }`}
          >
            Decrypt (C &oplus; K)
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

      {isKeyShort && (
        <AlertBanner
          type="warning"
          title="Shannon Vulnerability Warning"
          message={`Your key length (${keyBytesLen} bytes) is less than the message length (${plainLen} bytes). In One-Time Pad, reusing or truncating a key destroys information-theoretic secrecy!`}
          className="mb-4"
        />
      )}

      <div className="space-y-4">
        {mode === 'encrypt' ? (
          <div>
            <div className="flex justify-between items-center text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
              <label htmlFor="plain-input">Plaintext Message (UTF-8):</label>
              <span className="font-mono text-slate-500">{plainLen} bytes</span>
            </div>
            <textarea
              id="plain-input"
              rows={2}
              value={plaintext}
              onChange={(e) => setPlaintext(e.target.value)}
              className="w-full p-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              placeholder="Enter plaintext message..."
            />
          </div>
        ) : (
          <div>
            <div className="flex justify-between items-center text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
              <label htmlFor="cipher-input">Ciphertext Stream (Hexadecimal):</label>
              <span className="font-mono text-slate-500">
                {ciphertextInput.length / 2} bytes
              </span>
            </div>
            <textarea
              id="cipher-input"
              rows={2}
              value={ciphertextInput}
              onChange={(e) => setCiphertextInput(e.target.value)}
              className="w-full p-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              placeholder="Enter hex ciphertext..."
            />
          </div>
        )}

        {/* Key Input */}
        <div>
          <div className="flex justify-between items-center text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
            <label htmlFor="key-input">Hex Key (K):</label>
            <span className="font-mono text-slate-500">{keyBytesLen} bytes</span>
          </div>
          <input
            id="key-input"
            type="text"
            value={keyInput}
            onChange={(e) => setKeyInput(e.target.value)}
            className="w-full p-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            placeholder="Hex key e.g. a1b2c3d4..."
          />
        </div>

        {/* Action Button */}
        <div>
          {mode === 'encrypt' ? (
            <Button
              variant="primary"
              onClick={handleEncrypt}
              isLoading={isLoading}
              icon={<ArrowRight className="w-4 h-4" />}
            >
              Encrypt with XOR
            </Button>
          ) : (
            <Button
              variant="primary"
              onClick={handleDecrypt}
              isLoading={isLoading}
              icon={<Unlock className="w-4 h-4" />}
            >
              Decrypt with XOR
            </Button>
          )}
        </div>

        {/* Encrypt Result */}
        {mode === 'encrypt' && encryptResult && (
          <div className="mt-6 pt-4 border-t border-slate-200 dark:border-slate-800 space-y-4">
            <div className="p-3 bg-amber-50/50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/50 rounded-lg">
              <div className="flex items-center justify-between text-xs text-amber-800 dark:text-amber-300 mb-1 font-semibold">
                <span>Resulting Ciphertext (Hex):</span>
                <button
                  type="button"
                  onClick={() => copyText(encryptResult.ciphertext_hex)}
                  className="flex items-center gap-1 hover:underline text-xs"
                >
                  {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>Copy</span>
                </button>
              </div>
              <div className="font-mono text-xs break-all text-amber-950 dark:text-amber-200 select-all">
                {encryptResult.ciphertext_hex}
              </div>
            </div>

            {/* Entropy comparison */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700">
                <span className="text-slate-500 block mb-1">Plaintext Entropy:</span>
                <span className="font-mono font-bold text-slate-900 dark:text-slate-100 text-sm">
                  {encryptResult.entropy_plaintext.toFixed(2)} bits/byte
                </span>
                <div className="text-[11px] text-slate-400 mt-1">
                  Structured language redundancy
                </div>
              </div>
              <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700">
                <span className="text-slate-500 block mb-1">Ciphertext Entropy:</span>
                <span className="font-mono font-bold text-emerald-600 dark:text-emerald-400 text-sm">
                  {encryptResult.entropy_ciphertext.toFixed(2)} bits/byte
                </span>
                <div className="text-[11px] text-emerald-500/80 mt-1">
                  Uniform distribution (Perfect Secrecy)
                </div>
              </div>
            </div>

            {/* Perfect Secrecy note */}
            <div className="text-xs text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-slate-900 p-3 rounded-lg border border-slate-200 dark:border-slate-800 flex items-start gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold text-slate-800 dark:text-slate-200">
                  Shannon&apos;s Theorem of Perfect Secrecy:{' '}
                </span>
                <MathFormula math="H(M | C) = H(M)" />. Given ciphertext C, an eavesdropper
                learns zero additional information about message M.
              </div>
            </div>

            {/* Aligned Byte Grid */}
            <ByteVisualizer traces={encryptResult.byte_traces} />
          </div>
        )}

        {/* Decrypt Result */}
        {mode === 'decrypt' && decryptResult && (
          <div className="mt-6 pt-4 border-t border-slate-200 dark:border-slate-800 space-y-4">
            <div className="p-3 bg-emerald-50/50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-900/50 rounded-lg">
              <span className="text-xs text-emerald-800 dark:text-emerald-300 font-semibold block mb-1">
                Recovered Plaintext (UTF-8):
              </span>
              <div className="font-mono text-sm font-bold text-emerald-950 dark:text-emerald-200 select-all">
                &ldquo;{decryptResult.recovered_ascii}&rdquo;
              </div>
            </div>

            <ByteVisualizer traces={decryptResult.byte_traces} />
          </div>
        )}
      </div>
    </Card>
  );
};
