import React, { useEffect, useState } from 'react';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { AlertBanner } from '../../common/AlertBanner';
import { generateDsaDomain, generateDsaKeyPair, getDsaPresets } from '../../../api/dsaApi';
import { parseApiError } from '../../../api/client';
import { DSAPreset, DSAPublicKey, DSAPrivateKey } from '../../../types/dsa';
import { ShieldCheck, KeyRound, Eye, EyeOff, Sparkles, Copy, Check } from 'lucide-react';
import { MathFormula } from '../../common/MathFormula';

interface DomainKeygenCardProps {
  onKeysGenerated: (publicKey: DSAPublicKey, privateKey: DSAPrivateKey) => void;
}

export const DomainKeygenCard: React.FC<DomainKeygenCardProps> = ({
  onKeysGenerated,
}) => {
  const [presets, setPresets] = useState<DSAPreset[]>([]);
  const [selectedPreset, setSelectedPreset] = useState<string>('Educational Small (16-bit)');
  const [pVal, setPVal] = useState<string>('467');
  const [qVal, setQVal] = useState<string>('233');
  const [gVal, setGVal] = useState<string>('4');
  const [showPrivateKey, setShowPrivateKey] = useState<boolean>(false);
  const [publicKey, setPublicKey] = useState<DSAPublicKey | null>(null);
  const [privateKey, setPrivateKey] = useState<DSAPrivateKey | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  useEffect(() => {
    const fetchPresets = async () => {
      try {
        const list = await getDsaPresets();
        setPresets(list);
      } catch {
        // Fallback presets if offline
        setPresets([
          {
            name: 'Educational Small (16-bit)',
            p: 467,
            q: 233,
            g: 4,
            p_str: '467',
            q_str: '233',
            g_str: '4',
            p_bits: 9,
            q_bits: 8,
          },
          {
            name: 'Educational Medium (24-bit)',
            p: 8388617,
            q: 4194308,
            g: 2,
            p_str: '8388617',
            q_str: '4194308',
            g_str: '2',
            p_bits: 23,
            q_bits: 22,
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
      setPVal(found.p_str || String(found.p));
      setQVal(found.q_str || String(found.q));
      setGVal(found.g_str || String(found.g));
    }
  };

  const handleGenerateDomain = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await generateDsaDomain({ p_bits: 16, q_bits: 12 });
      setPVal(res.p_str || String(res.p));
      setQVal(res.q_str || String(res.q));
      setGVal(res.g_str || String(res.g));
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
      const res = await generateDsaKeyPair({
        p: Number(pVal),
        q: Number(qVal),
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
      title="DSA Domain Parameters &amp; Key Pair Setup"
      subtitle="FIPS 186-4 group parameters (p, q, g) and signing key pair (x, y = g^x mod p)"
      icon={<ShieldCheck className="w-5 h-5 text-indigo-500" />}
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
          <label htmlFor="dsa-preset" className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
            Standard Domain Presets:
          </label>
          <div className="flex gap-2">
            <select
              id="dsa-preset"
              value={selectedPreset}
              onChange={(e) => handleSelectPreset(e.target.value)}
              className="flex-1 p-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 text-xs font-medium focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            >
              {presets.map((preset) => (
                <option key={preset.name} value={preset.name}>
                  {preset.name} (p: {preset.p_bits}-bit, q: {preset.q_bits}-bit)
                </option>
              ))}
            </select>
            <Button
              variant="outline"
              size="sm"
              onClick={handleGenerateDomain}
              isLoading={isLoading}
              icon={<Sparkles className="w-3.5 h-3.5" />}
            >
              Search New (p, q, g)
            </Button>
          </div>
        </div>

        {/* Domain Parameters Display */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 font-mono text-xs">
          <div>
            <label htmlFor="dsa-p" className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Prime Modulus (p):
            </label>
            <input
              id="dsa-p"
              type="text"
              value={pVal}
              onChange={(e) => setPVal(e.target.value)}
              className="w-full p-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            />
          </div>

          <div>
            <label htmlFor="dsa-q" className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Prime Subgroup Divisor (q | p - 1):
            </label>
            <input
              id="dsa-q"
              type="text"
              value={qVal}
              onChange={(e) => setQVal(e.target.value)}
              className="w-full p-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            />
          </div>

          <div>
            <label htmlFor="dsa-g" className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
              {"Subgroup Generator (g = h^{(p-1)/q} mod p):"}
            </label>
            <input
              id="dsa-g"
              type="text"
              value={gVal}
              onChange={(e) => setGVal(e.target.value)}
              className="w-full p-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            />
          </div>
        </div>

        {/* Generate Key Pair */}
        <div>
          <Button
            variant="primary"
            onClick={handleGenerateKeys}
            isLoading={isLoading}
            icon={<KeyRound className="w-4 h-4" />}
          >
            Generate DSA Key Pair (x, y)
          </Button>
        </div>

        {/* Generated Keys */}
        {publicKey && privateKey && (
          <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-800 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
            {/* Public Key */}
            <div className="p-3.5 rounded-xl bg-indigo-50/50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-900">
              <div className="flex items-center justify-between text-indigo-700 dark:text-indigo-300 font-semibold mb-2">
                <span>Public Verification Key (y):</span>
                <button
                  type="button"
                  onClick={() => copyText(publicKey.y_str || String(publicKey.y), 'pub')}
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
                Included in digital certificates to verify signatures
              </div>
            </div>

            {/* Private Key */}
            <div className="p-3.5 rounded-xl bg-amber-50/50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900">
              <div className="flex items-center justify-between text-amber-700 dark:text-amber-300 font-semibold mb-2">
                <span>Private Signing Key (x):</span>
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
                    onClick={() => copyText(privateKey.x_str || String(privateKey.x), 'priv')}
                    className="flex items-center gap-1 hover:underline text-[11px]"
                  >
                    {copiedKey === 'priv' ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                    <span>Copy x</span>
                  </button>
                </div>
              </div>
              <div className="text-[11px] text-slate-500">
                x &isin; [1, q - 1]:{' '}
                <span className="font-bold text-amber-600 dark:text-amber-400 break-all select-all">
                  {showPrivateKey
                    ? privateKey.x_str || String(privateKey.x)
                    : '••••••••••••••••••••••••••••••••'}
                </span>
              </div>
              <div className="mt-2 text-[10px] text-amber-600 dark:text-amber-400 font-sans">
                Never disclose: creates unforgeable signatures
              </div>
            </div>
          </div>
        )}

        <div className="text-center text-xs text-slate-400 font-mono pt-1">
          <MathFormula math="q \mid (p - 1) \quad \text{and} \quad g^q \equiv 1 \pmod p" />
        </div>
      </div>
    </Card>
  );
};
