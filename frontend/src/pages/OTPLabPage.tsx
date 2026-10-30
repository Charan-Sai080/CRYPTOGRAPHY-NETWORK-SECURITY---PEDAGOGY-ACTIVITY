import React, { useState } from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { Badge } from '../components/common/Badge';
import { KeyGenCard } from '../components/labs/otp/KeyGenCard';
import { EncryptDecryptCard } from '../components/labs/otp/EncryptDecryptCard';
import { TwoTimePadSandbox } from '../components/labs/otp/TwoTimePadSandbox';
import { CribDragSlider } from '../components/labs/otp/CribDragSlider';
import { DictionaryAttackView } from '../components/labs/otp/DictionaryAttackView';
import { Binary } from 'lucide-react';

export const OTPLabPage: React.FC = () => {
  const [activeKeyHex, setActiveKeyHex] = useState<string>('');
  const [c1XorC2Stream, setC1XorC2Stream] = useState<string>('');

  return (
    <div className="space-y-8">
      <PageHeader
        title="Lab 1: One-Time Pad &amp; Two-Time Pad Cryptanalysis"
        subtitle="Explore Claude Shannon's Perfect Secrecy, bitwise XOR diffusion, and algebraic vulnerabilities when keys are reused"
        icon={<Binary className="w-7 h-7" />}
        badge={
          <div className="flex gap-2">
            <Badge variant="info">Lab 1</Badge>
            <Badge variant="math">Shannon Secrecy</Badge>
          </div>
        }
      />

      {/* Section 1: Keygen & Shannon Entropy */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <span>1. CSPRNG Key Generation &amp; Shannon Entropy Meter</span>
        </h2>
        <KeyGenCard onKeyGenerated={(keyHex) => setActiveKeyHex(keyHex)} />
      </section>

      {/* Section 2: Traced XOR Encryption & Truth Table */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <span>2. Traced XOR Encryption &amp; Bit Truth Table</span>
        </h2>
        <EncryptDecryptCard initialKey={activeKeyHex} />
      </section>

      {/* Section 3: Two-Time Pad Vulnerability Sandbox */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <span>3. Two-Time Pad (Key Reuse) Algebraic Cancellation Sandbox</span>
        </h2>
        <TwoTimePadSandbox
          onXorCalculated={(c1XorC2) => setC1XorC2Stream(c1XorC2)}
        />
      </section>

      {/* Section 4: Interactive & Automated Crib Dragging */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <span>4. Crib-Dragging Plaintext Recovery Playground</span>
        </h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
          <CribDragSlider c1XorC2Hex={c1XorC2Stream} />
          <DictionaryAttackView c1XorC2Hex={c1XorC2Stream} />
        </div>
      </section>
    </div>
  );
};
