import React, { useEffect, useState } from 'react';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { AlertBanner } from '../../common/AlertBanner';
import {
  generateElGamalDomain,
  generateElGamalKeyPair,
  getElGamalPresets,
} from '../../../api/elgamalApi';
import { parseApiError } from '../../../api/client';
import {
  ElGamalPreset,
  ElGamalPublicKey,
  ElGamalPrivateKey,
} from '../../../types/elgamal';
import { KeyRound, Shield, Eye, EyeOff, Sparkles, Copy, Check } from 'lucide-react';
import { MathFormula } from '../../common/MathFormula';

interface DomainKeygenCardProps {
  onKeysGenerated: (publicKey: ElGamalPublicKey, privateKey: ElGamalPrivateKey) => void;
}

export const DomainKeygenCard: React.FC<DomainKeygenCardProps> = ({
  onKeysGenerated,
}) => {
  const [presets, setPresets] = useState<ElGamalPreset[]>([]);
  const [selectedPreset, setSelectedPreset] = useState<string>('Educational Small (16-bit)');
  const [bits, setBits] = useState<number>(16);
  const [pVal, setPVal] = useState<string>('65537');
  const [gVal, setGVal] = useState<string>('3');
  const [showPrivateKey, setShowPrivateKey] = useState<boolean>(false);
  const [publicKey, setPublicKey] = useState<ElGamalPublicKey | null>(null);
  const [privateKey, setPrivateKey] = useState<ElGamalPrivateKey | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  useEffect(() => {
    const fetchPresets = async () => {
      try {
        const list = await getElGamalPresets();
        setPresets(list);
      } catch {
        // Fallback presets if offline
        setPresets([
          {
            name: 'Educational Small (16-bit)',
            description: 'Safe prime p=65537 for mental arithmetic and small-step KaTeX traces',
            p: 65537,
            g: 3,
            p_bits: 16,
            is_safe_prime: false,
          },
          {
            name: 'Educational Safe Prime (24-bit)',
            description: 'Safe prime p=2q+1 for modular subgroup demonstrations',
            p: 16777259,
            g: 2,
            p_bits: 24,
            is_safe_prime: true,
          },
          {
            name: 'RFC 2409 1024-bit MODP Group',
            description: 'Standard Oakley Group 2 (1024-bit prime, g=2)',
            p: '179769313486231590772930519078902473361797697894230657273430081157732675805500963132708477322407536021120113879871393357658789768814416622492847430639474124377767893424865485276302219601246094119453082952085005768838150682342462881473913110540827237163350510684586298239947245938479716304835356329624224137216',
            g: 2,
            p_bits: 1024,
            is_safe_prime: true,
          },
        ]);
      }
    };
    fetchPresets();
  }, []);

  const handleSelectPreset = (name: string) => {
    setSelectedPreset(name);
    const found = presets.find((p) => p.name === name);
    if (found) {
      setPVal(String(found.p));
      setGVal(String(found.g));
      setBits(found.p_bits);
    }
  };

  const handleGenerateDomain = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await generateElGamalDomain({ bits });
      setPVal(String(res.p));
      setGVal(String(res.g));
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateKeys = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await generateElGamalKeyPair({
        p: Number(pVal),
        g: Number(gVal),
      });
      setPublicKey(res.public_key);
      setPrivateKey(res.private_key);
      onKeysGenerated(res.public_key, res.private_key);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  const copyText = (txt: string, id: string) => {
    navigator.clipboard.writeText(txt);
    setCopiedKey(id);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  return (
    <Card
      title="Domain Parameters &amp; Asymmetric Key Pair Setup"
      subtitle="Configure cyclic group (Z_p*, ·) and generate Alice's key pair (x, y = g^x mod p)"
      icon={<Shield className="w-5 h-5 text-indigo-500" />}
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
        {/* Preset Selector */}
        <div>
          <label htmlFor="elg-preset" className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
            Standard Domain Presets:
          </label>
          <select
            id="elg-preset"
            value={selectedPreset}
            onChange={(e) => handleSelectPreset(e.target.value)}
            className="w-full p-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 text-xs font-medium focus:ring-2 focus:ring-indigo-500 focus:outline-none"
          >
            {presets.map((preset) => (
              <option key={preset.name} value={preset.name}>
                {preset.name} ({preset.p_bits}-bit)
              </option>
            ))}
          </select>
          {presets.find((p) => p.name === selectedPreset)?.description && (
            <p className="text-[11px] text-slate-500 mt-1 italic">
              {presets.find((p) => p.name === selectedPreset)?.description}
            </p>
          )}
        </div>

        {/* Dynamic Safe Prime Generator */}
        <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <div>
              <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 block">
                Generate Custom Safe Prime (p = 2q + 1):
              </span>
              <span className="text-[11px] text-slate-500">
                Bit length: {bits} bits (Educational small safe primes)
              </span>
            </div>
            <div className="flex items-center gap-2 w-full sm:w-auto">
              <input
                type="range"
                min={12}
                max={28}
                value={bits}
                onChange={(e) => setBits(Number(e.target.value))}
                className="w-28 h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-600"
              />
              <Button
                variant="outline"
                size="sm"
                onClick={handleGenerateDomain}
                isLoading={isLoading}
                icon={<Sparkles className="w-3.5 h-3.5" />}
              >
                Find Safe Prime
              </Button>
            </div>
          </div>
        </div>

        {/* Modulus and Generator inputs */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 font-mono text-xs">
          <div>
            <label htmlFor="p-val" className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Prime Modulus (p):
            </label>
            <textarea
              id="p-val"
              rows={2}
              value={pVal}
              onChange={(e) => setPVal(e.target.value)}
              className="w-full p-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            />
          </div>

          <div>
            <label htmlFor="g-val" className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Generator (g &isin; Z_p*):
            </label>
            <input
              id="g-val"
              type="text"
              value={gVal}
              onChange={(e) => setGVal(e.target.value)}
              className="w-full p-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            />
          </div>
        </div>

        {/* Generate Key Pair Button */}
        <div>
          <Button
            variant="primary"
            onClick={handleGenerateKeys}
            isLoading={isLoading}
            icon={<KeyRound className="w-4 h-4" />}
          >
            Generate Alice&apos;s Key Pair (x, y)
          </Button>
        </div>

        {/* Generated Keys Display */}
        {publicKey && privateKey && (
          <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-800 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
            {/* Public Key */}
            <div className="p-3.5 rounded-xl bg-indigo-50/50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-900">
              <div className="flex items-center justify-between text-indigo-700 dark:text-indigo-300 font-semibold mb-2">
                <span>Alice&apos;s Public Key (p, g, y):</span>
                <button
                  type="button"
                  onClick={() => copyText(String(publicKey.y_str || publicKey.y), 'pub')}
                  className="flex items-center gap-1 hover:underline text-[11px]"
                >
                  {copiedKey === 'pub' ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                  <span>Copy y</span>
                </button>
              </div>
              <div className="space-y-1">
                <div className="text-[11px] text-slate-500">
                  y &equiv; g^x mod p:{' '}
                  <span className="font-bold text-indigo-600 dark:text-indigo-400 break-all select-all">
                    {publicKey.y_str || String(publicKey.y)}
                  </span>
                </div>
              </div>
              <div className="mt-2 text-[10px] text-indigo-500 font-sans">
                Shared freely across untrusted networks
              </div>
            </div>

            {/* Private Key */}
            <div className="p-3.5 rounded-xl bg-amber-50/50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900">
              <div className="flex items-center justify-between text-amber-700 dark:text-amber-300 font-semibold mb-2">
                <span>Alice&apos;s Private Key (x):</span>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setShowPrivateKey(!showPrivateKey)}
                    className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                    title={showPrivateKey ? 'Hide secret key' : 'Show secret key'}
                  >
                    {showPrivateKey ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                  </button>
                  <button
                    type="button"
                    onClick={() => copyText(String(privateKey.x_str || privateKey.x), 'priv')}
                    className="flex items-center gap-1 hover:underline text-[11px]"
                  >
                    {copiedKey === 'priv' ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                    <span>Copy x</span>
                  </button>
                </div>
              </div>
              <div className="text-[11px] text-slate-500">
                x &isin; [2, p - 2]:{' '}
                <span className="font-bold text-amber-600 dark:text-amber-400 break-all select-all">
                  {showPrivateKey
                    ? privateKey.x_str || String(privateKey.x)
                    : '••••••••••••••••••••••••••••••••'}
                </span>
              </div>
              <div className="mt-2 text-[10px] text-amber-600 dark:text-amber-400 font-sans">
                Must remain strictly confidential
              </div>
            </div>
          </div>
        )}

        <div className="text-center text-xs text-slate-400 font-mono pt-1">
          <MathFormula math="y \equiv g^x \pmod p \iff x = \log_g y \pmod p" />
        </div>
      </div>
    </Card>
  );
};
