import React, { useState } from 'react';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { ShannonEntropyGauge } from '../../visualizers/ShannonEntropyGauge';
import { generateOtpKey } from '../../../api/otpApi';
import { parseApiError } from '../../../api/client';
import { OTPKeyGenerateResponse } from '../../../types/otp';
import { AlertBanner } from '../../common/AlertBanner';
import { KeyRound, Sparkles, Copy, Check } from 'lucide-react';

interface KeyGenCardProps {
  onKeyGenerated?: (keyHex: string, length: number) => void;
}

export const KeyGenCard: React.FC<KeyGenCardProps> = ({ onKeyGenerated }) => {
  const [length, setLength] = useState<number>(16);
  const [encoding, setEncoding] = useState<'hex' | 'base64' | 'raw'>('hex');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [keyResult, setKeyResult] = useState<OTPKeyGenerateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<boolean>(false);

  const handleGenerate = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await generateOtpKey({ length, format: encoding });
      setKeyResult(res);
      if (onKeyGenerated) {
        onKeyGenerated(res.key_hex, res.length);
      }
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Card
      title="CSPRNG One-Time Pad Key Generator"
      subtitle="Generates cryptographically secure random byte sequences using OS entropy"
      icon={<KeyRound className="w-5 h-5" />}
      className="h-full"
    >
      {error && (
        <AlertBanner
          type="error"
          message={error}
          onClose={() => setError(null)}
          className="mb-4"
        />
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-center">
        <div className="lg:col-span-2 space-y-4">
          {/* Length Slider & Input */}
          <div>
            <div className="flex justify-between items-center text-sm font-medium mb-1.5">
              <label htmlFor="key-length" className="text-slate-700 dark:text-slate-300">
                Key Length (bytes):
              </label>
              <span className="font-mono font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950 px-2 py-0.5 rounded text-xs">
                {length} bytes ({length * 8} bits)
              </span>
            </div>
            <input
              id="key-length"
              type="range"
              min={1}
              max={128}
              value={length}
              onChange={(e) => setLength(Number(e.target.value))}
              className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-600"
            />
            <div className="flex justify-between text-[10px] text-slate-400 mt-1 font-mono">
              <span>1 byte</span>
              <span>16 bytes</span>
              <span>32 bytes</span>
              <span>64 bytes</span>
              <span>128 bytes</span>
            </div>
          </div>

          {/* Encoding Format Selector */}
          <div>
            <span className="text-xs font-medium text-slate-700 dark:text-slate-300 block mb-1.5">
              Representation Encoding:
            </span>
            <div className="flex gap-2">
              {(['hex', 'base64', 'raw'] as const).map((fmt) => (
                <button
                  key={fmt}
                  type="button"
                  onClick={() => setEncoding(fmt)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-all ${
                    encoding === fmt
                      ? 'bg-indigo-600 text-white shadow-xs'
                      : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
                  }`}
                >
                  {fmt.toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          {/* Generate Button */}
          <div className="pt-2">
            <Button
              variant="primary"
              onClick={handleGenerate}
              isLoading={isLoading}
              icon={<Sparkles className="w-4 h-4" />}
            >
              Generate CSPRNG Key
            </Button>
          </div>

          {/* Output Display */}
          {keyResult && (
            <div className="mt-4 p-3 rounded-lg bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700">
              <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
                <span className="font-semibold uppercase tracking-wider">
                  Generated {encoding.toUpperCase()} Stream:
                </span>
                <button
                  type="button"
                  onClick={() =>
                    copyToClipboard(
                      encoding === 'base64'
                        ? keyResult.key_base64
                        : keyResult.key_hex
                    )
                  }
                  className="flex items-center gap-1 text-indigo-600 dark:text-indigo-400 hover:underline"
                >
                  {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copied ? 'Copied!' : 'Copy'}</span>
                </button>
              </div>
              <div className="font-mono text-xs break-all text-slate-900 dark:text-slate-100 select-all max-h-24 overflow-y-auto">
                {encoding === 'base64'
                  ? keyResult.key_base64
                  : keyResult.key_hex}
              </div>
            </div>
          )}
        </div>

        {/* Shannon Entropy Visualizer */}
        <div className="flex justify-center">
          <ShannonEntropyGauge
            entropy={keyResult?.entropy ?? 8.0}
            maxEntropy={8.0}
            label="Key Shannon Entropy"
            interpretation={
              keyResult
                ? `CSPRNG key Shannon entropy: ${keyResult.entropy.toFixed(3)} bits/byte`
                : 'CSPRNG keys achieve maximal Shannon entropy (~8.0 bits/byte)'
            }
          />
        </div>
      </div>
    </Card>
  );
};
