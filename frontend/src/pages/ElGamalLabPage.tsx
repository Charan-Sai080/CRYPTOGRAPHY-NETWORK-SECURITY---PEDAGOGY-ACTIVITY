import React, { useState } from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { Badge } from '../components/common/Badge';
import { KeyExchangeDiagram } from '../components/visualizers/KeyExchangeDiagram';
import { DomainKeygenCard } from '../components/labs/elgamal/DomainKeygenCard';
import { EncryptDecryptCard } from '../components/labs/elgamal/EncryptDecryptCard';
import { HomomorphismPlayground } from '../components/labs/elgamal/HomomorphismPlayground';
import { NonceReuseExploitCard } from '../components/labs/elgamal/NonceReuseExploitCard';
import { ElGamalPublicKey, ElGamalPrivateKey } from '../types/elgamal';
import { KeyRound } from 'lucide-react';

export const ElGamalLabPage: React.FC = () => {
  const [publicKey, setPublicKey] = useState<ElGamalPublicKey | null>({
    p: 65537,
    g: 3,
    y: 27902,
    p_str: '65537',
    g_str: '3',
    y_str: '27902',
  });

  const [privateKey, setPrivateKey] = useState<ElGamalPrivateKey | null>({
    p: 65537,
    g: 3,
    x: 4321,
    p_str: '65537',
    g_str: '3',
    x_str: '4321',
  });

  return (
    <div className="space-y-8">
      <PageHeader
        title="Lab 3: ElGamal Public-Key Cryptosystem &amp; Homomorphism"
        subtitle="Explore asymmetric cryptography, Diffie-Hellman key agreement, discrete logarithm hardness, and multiplicative homomorphism"
        icon={<KeyRound className="w-7 h-7" />}
        badge={
          <div className="flex gap-2">
            <Badge variant="success">Lab 3</Badge>
            <Badge variant="math">Discrete Log &bull; Homomorphism</Badge>
          </div>
        }
      />

      {/* Section 1: Alice, Bob & Eve Architecture Diagram */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <span>1. Asymmetric Cryptosystem Architecture &amp; Discrete Logarithm Hardness</span>
        </h2>
        <KeyExchangeDiagram />
      </section>

      {/* Section 2: Domain Parameters & Key Pair Generator */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <span>2. Domain Parameters (p, g) &amp; Key Pair Setup</span>
        </h2>
        <DomainKeygenCard
          onKeysGenerated={(pub, priv) => {
            setPublicKey(pub);
            setPrivateKey(priv);
          }}
        />
      </section>

      {/* Section 3: Traced Encryption & Chunking Decryption */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <span>3. Traced Encryption &amp; UTF-8 Chunked Decryption</span>
        </h2>
        <EncryptDecryptCard publicKey={publicKey} privateKey={privateKey} />
      </section>

      {/* Section 4: Multiplicative Homomorphism Playground */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <span>4. Multiplicative Homomorphic Encryption Playground</span>
        </h2>
        <HomomorphismPlayground publicKey={publicKey} privateKey={privateKey} />
      </section>

      {/* Section 5: Ephemeral Nonce Reuse Exploit Sandbox */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <span>5. Ephemeral Nonce Reuse Vulnerability Sandbox</span>
        </h2>
        <NonceReuseExploitCard modulusP={publicKey?.p ?? 65537} />
      </section>
    </div>
  );
};
