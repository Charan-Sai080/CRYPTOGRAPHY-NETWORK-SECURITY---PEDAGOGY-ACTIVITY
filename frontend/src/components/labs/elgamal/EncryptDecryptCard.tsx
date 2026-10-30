import React, { useState } from 'react';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { AlertBanner } from '../../common/AlertBanner';
import { MathFormula } from '../../common/MathFormula';
import { TextChunkingVisualizer } from './TextChunkingVisualizer';
import { encryptElGamal, decryptElGamal } from '../../../api/elgamalApi';
import { parseApiError } from '../../../api/client';
import {
  ElGamalPublicKey,
  ElGamalPrivateKey,
  ElGamalEncryptResponse,
  ElGamalDecryptResponse,
} from '../../../types/elgamal';
import { Lock, Unlock, ArrowRight, ShieldCheck } from 'lucide-react';

interface EncryptDecryptCardProps {
  publicKey: ElGamalPublicKey | null;
  privateKey: ElGamalPrivateKey | null;
}

export const EncryptDecryptCard: React.FC<EncryptDecryptCardProps> = ({
  publicKey,
  privateKey,
}) => {
  const [isIntegerMode, setIsIntegerMode] = useState<boolean>(true);
  const [intMessage, setIntMessage] = useState<number>(42);
  const [textMessage, setTextMessage] = useState<string>('CNS Lab 2026');
  const [nonceK, setNonceK] = useState<string>('');
  const [encryptResult, setEncryptResult] = useState<ElGamalEncryptResponse | null>(null);
  const [decryptResult, setDecryptResult] = useState<ElGamalDecryptResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleEncrypt = async () => {
    if (!publicKey) {
      setError('Please configure and generate Alice’s public key first.');
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const res = await encryptElGamal({
        p: Number(publicKey.p),
        g: Number(publicKey.g),
        y: Number(publicKey.y),
        message_int: isIntegerMode ? Number(intMessage) : undefined,
        message_text: !isIntegerMode ? textMessage : undefined,
        seed_k: nonceK.trim() ? Number(nonceK) : undefined,
      });
      setEncryptResult(res);
      setDecryptResult(null);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleDecrypt = async () => {
    if (!privateKey || !encryptResult) {
      setError('Ciphertext blocks and Alice’s private key are required for decryption.');
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const res = await decryptElGamal({
        p: Number(privateKey.p),
        x: Number(privateKey.x),
        c1: isIntegerMode && encryptResult.c1 !== null ? encryptResult.c1 : undefined,
        c2: isIntegerMode && encryptResult.c2 !== null ? encryptResult.c2 : undefined,
        blocks: !isIntegerMode ? encryptResult.blocks : undefined,
      });
      setDecryptResult(res);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card
      title="Asymmetric Encryption &amp; Decryption Sandbox"
      subtitle="Traced Bob encryption (c1, c2) and Alice decryption with shared secret inversion"
      icon={<Lock className="w-5 h-5 text-indigo-500" />}
      action={
        <div className="flex bg-slate-100 dark:bg-slate-800 p-1 rounded-lg">
          <button
            type="button"
            onClick={() => setIsIntegerMode(true)}
            className={`px-3 py-1 rounded text-xs font-semibold transition-all ${
              isIntegerMode
                ? 'bg-indigo-600 text-white shadow-xs'
                : 'text-slate-600 dark:text-slate-300'
            }`}
          >
            Single Integer (m &lt; p)
          </button>
          <button
            type="button"
            onClick={() => setIsIntegerMode(false)}
            className={`px-3 py-1 rounded text-xs font-semibold transition-all ${
              !isIntegerMode
                ? 'bg-indigo-600 text-white shadow-xs'
                : 'text-slate-600 dark:text-slate-300'
            }`}
          >
            Arbitrary UTF-8 Text
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

      <div className="space-y-4">
        {/* Input */}
        {isIntegerMode ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label htmlFor="int-msg" className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Plaintext Integer m (1 &le; m &lt; p):
              </label>
              <input
                id="int-msg"
                type="number"
                min={1}
                value={intMessage}
                onChange={(e) => setIntMessage(Number(e.target.value))}
                className="w-full p-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              />
            </div>
            <div>
              <label htmlFor="nonce-k" className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Ephemeral Nonce k (Optional / Auto-generated):
              </label>
              <input
                id="nonce-k"
                type="number"
                value={nonceK}
                onChange={(e) => setNonceK(e.target.value)}
                placeholder="Leave blank for random CSPRNG k"
                className="w-full p-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              />
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            <div>
              <label htmlFor="text-msg" className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Plaintext Text Message (UTF-8):
              </label>
              <textarea
                id="text-msg"
                rows={2}
                value={textMessage}
                onChange={(e) => setTextMessage(e.target.value)}
                className="w-full p-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              />
            </div>
            {encryptResult && (
              <TextChunkingVisualizer
                text={textMessage}
                blockSizeBytes={encryptResult.block_size_bytes}
                totalBlocks={encryptResult.blocks.length}
              />
            )}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-3">
          <Button
            variant="primary"
            onClick={handleEncrypt}
            isLoading={isLoading}
            disabled={!publicKey}
            icon={<ArrowRight className="w-4 h-4" />}
          >
            Encrypt with Bob&apos;s Nonce
          </Button>

          {encryptResult && (
            <Button
              variant="secondary"
              onClick={handleDecrypt}
              isLoading={isLoading}
              disabled={!privateKey}
              icon={<Unlock className="w-4 h-4" />}
            >
              Decrypt with Alice&apos;s Private Key
            </Button>
          )}
        </div>

        {/* Encryption Output */}
        {encryptResult && (
          <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-800 space-y-4">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide block">
              Ciphertext Blocks ({encryptResult.blocks.length} Block{encryptResult.blocks.length > 1 ? 's' : ''}):
            </span>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {encryptResult.blocks.map((block) => (
                <div
                  key={block.index}
                  className="p-3.5 rounded-xl bg-amber-50/50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/60 font-mono text-xs"
                >
                  <div className="flex items-center justify-between text-amber-800 dark:text-amber-300 font-semibold mb-2">
                    <span>Block #{block.index}</span>
                    <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-amber-100 dark:bg-amber-900">
                      Cipher Pair (c_1, c_2)
                    </span>
                  </div>
                  <div className="space-y-1">
                    <div>
                      <span className="text-slate-400">c_1 (g^k mod p): </span>
                      <span className="font-bold text-slate-800 dark:text-slate-200 break-all select-all">
                        {block.c1_str || String(block.c1)}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-400">c_2 (m &middot; s mod p): </span>
                      <span className="font-bold text-amber-600 dark:text-amber-400 break-all select-all">
                        {block.c2_str || String(block.c2)}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Step-by-Step KaTeX Trace */}
            {(encryptResult.single_trace || encryptResult.block_traces[0]) && (
              <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-3">
                <span className="text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wide block">
                  Encryption Mathematical Trace:
                </span>
                {(() => {
                  const tr = encryptResult.single_trace || encryptResult.block_traces[0];
                  return (
                    <div className="space-y-2 text-xs font-mono">
                      <div className="p-2.5 rounded-lg bg-white dark:bg-slate-800/80 border border-slate-100 dark:border-slate-700/60">
                        <div className="text-[11px] text-slate-500 mb-1">Ephemeral Key c1:</div>
                        <div className="text-indigo-600 dark:text-indigo-400 my-1">
                          <MathFormula math={tr.formula_c1} />
                        </div>
                      </div>
                      <div className="p-2.5 rounded-lg bg-white dark:bg-slate-800/80 border border-slate-100 dark:border-slate-700/60">
                        <div className="text-[11px] text-slate-500 mb-1">Shared Secret s:</div>
                        <div className="text-indigo-600 dark:text-indigo-400 my-1">
                          <MathFormula math={tr.formula_s} />
                        </div>
                      </div>
                      <div className="p-2.5 rounded-lg bg-white dark:bg-slate-800/80 border border-slate-100 dark:border-slate-700/60">
                        <div className="text-[11px] text-slate-500 mb-1">Masked Ciphertext c2:</div>
                        <div className="text-indigo-600 dark:text-indigo-400 my-1">
                          <MathFormula math={tr.formula_c2} />
                        </div>
                      </div>
                    </div>
                  );
                })()}
              </div>
            )}
          </div>
        )}

        {/* Decryption Output */}
        {decryptResult && (
          <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-800 space-y-3">
            <div className="p-4 bg-emerald-50/50 dark:bg-emerald-950/40 border border-emerald-300 dark:border-emerald-800 rounded-xl">
              <div className="flex items-center gap-2 text-emerald-800 dark:text-emerald-300 font-bold text-xs uppercase tracking-wide mb-1">
                <ShieldCheck className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                <span>Alice&apos;s Decryption Result:</span>
              </div>
              <div className="font-mono text-base font-bold text-emerald-950 dark:text-emerald-200 select-all">
                {isIntegerMode ? (
                  <span>Plaintext Integer: {decryptResult.recovered_int}</span>
                ) : (
                  <span>&ldquo;{decryptResult.recovered_text}&rdquo;</span>
                )}
              </div>
            </div>

            {/* Decryption KaTeX Inversion */}
            <div className="p-3 bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 text-xs font-mono text-center">
              <MathFormula
                math="s \equiv c_1^x \equiv (g^k)^x \equiv g^{kx} \pmod p \implies m \equiv c_2 \cdot s^{-1} \pmod p"
                block
              />
              <span className="text-[11px] text-slate-500 font-sans">
                Shared secret s inverted via Extended Euclidean Algorithm
              </span>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};
