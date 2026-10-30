import React, { useState } from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { Badge } from '../components/common/Badge';
import { DomainKeygenCard } from '../components/labs/dsa/DomainKeygenCard';
import { DocumentSignerCard } from '../components/labs/dsa/DocumentSignerCard';
import { VerificationProofCard } from '../components/labs/dsa/VerificationProofCard';
import { TamperSimulatorCard } from '../components/labs/dsa/TamperSimulatorCard';
import { SonyPs3ExploitCard } from '../components/labs/dsa/SonyPs3ExploitCard';
import { DSAPublicKey, DSAPrivateKey } from '../types/dsa';
import { FileCheck2 } from 'lucide-react';

export const DSALabPage: React.FC = () => {
  const [publicKey, setPublicKey] = useState<DSAPublicKey | null>({
    p: 467,
    q: 233,
    g: 4,
    y: 91,
    p_str: '467',
    q_str: '233',
    g_str: '4',
    y_str: '91',
  });

  const [privateKey, setPrivateKey] = useState<DSAPrivateKey | null>({
    p: 467,
    q: 233,
    g: 4,
    x: 105,
    p_str: '467',
    q_str: '233',
    g_str: '4',
    x_str: '105',
  });

  const [currentMessage, setCurrentMessage] = useState<string>(
    "Transfer $5,000 to Bob's Account - Authorization ID #8841"
  );
  const [signatureR, setSignatureR] = useState<string>('125');
  const [signatureS, setSignatureS] = useState<string>('84');

  return (
    <div className="space-y-8">
      <PageHeader
        title="Lab 4: Digital Signature Algorithm &amp; Sony PS3 Exploit"
        subtitle="Explore FIPS 186-4 digital signatures, SHA-256 hash truncation, single-bit tampering detection, and the historic Sony PlayStation 3 nonce reuse attack"
        icon={<FileCheck2 className="w-7 h-7" />}
        badge={
          <div className="flex gap-2">
            <Badge variant="danger">Lab 4</Badge>
            <Badge variant="math">FIPS 186-4 &bull; Nonce Reuse</Badge>
          </div>
        }
      />

      {/* Section 1: Domain Parameters & Key Pair Generator */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <span>1. FIPS 186-4 Domain Parameters &amp; Key Pair Setup</span>
        </h2>
        <DomainKeygenCard
          onKeysGenerated={(pub, priv) => {
            setPublicKey(pub);
            setPrivateKey(priv);
          }}
        />
      </section>

      {/* Section 2: Document Signing Interface */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <span>2. Cryptographic Document Signing Pipeline</span>
        </h2>
        <DocumentSignerCard
          privateKey={privateKey}
          onSignatureGenerated={(msg, r, s) => {
            setCurrentMessage(msg);
            setSignatureR(r);
            setSignatureS(s);
          }}
        />
      </section>

      {/* Section 3: Signature Verification Engine */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <span>3. Signature Verification &amp; Algebraic Proof Engine</span>
        </h2>
        <VerificationProofCard
          publicKey={publicKey}
          initialMessage={currentMessage}
          initialR={signatureR}
          initialS={signatureS}
        />
      </section>

      {/* Section 4: Document & Signature Tampering Simulator */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <span>4. Real-Time Document &amp; Signature Bit-Tamper Simulator</span>
        </h2>
        <TamperSimulatorCard
          publicKey={publicKey}
          privateKey={privateKey}
          originalMessage={currentMessage}
          signatureR={signatureR}
          signatureS={signatureS}
        />
      </section>

      {/* Section 5: Sony PS3 Nonce Reuse Exploit Sandbox */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <span>5. Sony PlayStation 3 Private Key Extraction Sandbox</span>
        </h2>
        <SonyPs3ExploitCard publicKey={publicKey} />
      </section>
    </div>
  );
};
