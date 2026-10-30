import React from 'react';
import { TabKey } from '../components/common/Navbar';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { MathFormula } from '../components/common/MathFormula';
import {
  Binary,
  Cpu,
  KeyRound,
  FileCheck2,
  ArrowRight,
  ShieldCheck,
  ShieldAlert,
  Sparkles,
  BookOpen,
  Award,
  Zap,
} from 'lucide-react';

interface DashboardPageProps {
  onSelectTab: (tab: TabKey) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onSelectTab }) => {
  const pillars: {
    key: TabKey;
    labNumber: string;
    title: string;
    subtitle: string;
    icon: React.ReactNode;
    difficulty: 'Introductory' | 'Intermediate' | 'Advanced';
    badgeVariant: 'default' | 'success' | 'warning' | 'danger' | 'info';
    mathFormula: string;
    objectives: string[];
  }[] = [
    {
      key: 'otp',
      labNumber: 'Lab 1',
      title: 'One-Time Pad & Cryptanalysis',
      subtitle: 'Information-Theoretic Perfect Secrecy vs. Key-Reuse Vulnerability',
      icon: <Binary className="w-6 h-6 text-indigo-500" />,
      difficulty: 'Introductory',
      badgeVariant: 'info',
      mathFormula: 'H(M | C) = H(M) \\iff C_1 \\oplus C_2 = P_1 \\oplus P_2',
      objectives: [
        'CSPRNG key generation & Shannon entropy calculation (H(X) in bits/byte)',
        'Bit-by-bit truth table visualization of XOR diffusion',
        'Two-Time Pad algebraic key cancellation demonstration',
        'Interactive & automated dictionary-based crib-dragging attack',
      ],
    },
    {
      key: 'lcg',
      labNumber: 'Lab 2',
      title: 'LCG & Marsaglia Lattice',
      subtitle: 'Pseudorandom Number Generators, Spectral Defects & State Recovery',
      icon: <Cpu className="w-6 h-6 text-amber-500" />,
      difficulty: 'Intermediate',
      badgeVariant: 'warning',
      mathFormula: 'X_{n+1} \\equiv (a X_n + c) \\bmod m \\quad \\& \\quad k \\le (d! \\cdot m)^{1/d}',
      objectives: [
        'Hull-Dobell Theorem full-period verification across 3 conditions',
        'Floyd’s tortoise-and-hare empirical cycle detection in O(1) space',
        'Chi-Square goodness-of-fit uniformity testing with p-value verdicts',
        '2D and 3D Marsaglia hyperplane lattice scatter plots (PNAS 1968)',
        'Algebraic LCG state cracking from consecutive outputs',
      ],
    },
    {
      key: 'elgamal',
      labNumber: 'Lab 3',
      title: 'ElGamal Public-Key Cryptosystem',
      subtitle: 'Discrete Logarithms, Diffie-Hellman Key Agreement & Homomorphism',
      icon: <KeyRound className="w-6 h-6 text-emerald-500" />,
      difficulty: 'Advanced',
      badgeVariant: 'success',
      mathFormula: 'y \\equiv g^x \\pmod p \\quad \\& \\quad E(m_1) \\cdot E(m_2) = E(m_1 m_2)',
      objectives: [
        'Safe prime generation (p = 2q + 1) and primitive root generator search',
        'Alice, Bob & Eve key exchange architecture with Discrete Log hardness',
        'Traced integer & chunked UTF-8 string encryption & decryption',
        'Multiplicative homomorphism enabling privacy-preserving computation',
        'Ephemeral nonce reuse exploit recovering plaintext without private key',
      ],
    },
    {
      key: 'dsa',
      labNumber: 'Lab 4',
      title: 'DSA & Sony PS3 Exploit',
      subtitle: 'FIPS 186-4 Digital Signatures, Bit Tampering & Key Extraction',
      icon: <FileCheck2 className="w-6 h-6 text-rose-500" />,
      difficulty: 'Advanced',
      badgeVariant: 'danger',
      mathFormula: 's \\equiv k^{-1}(z + x r) \\bmod q \\iff k = (z_1 - z_2)(s_1 - s_2)^{-1}',
      objectives: [
        'FIPS 186-4 domain parameters (p, q, g) and asymmetric key pair generation',
        'Document signing with SHA-256 truncation and r=0, s=0 resampling trace',
        'Signature verification engine with full step-by-step LaTeX algebraic proof',
        'Real-time single-bit document tampering and signature mutation simulator',
        'Sony PlayStation 3 nonce reuse exploit extracting master private key x',
      ],
    },
  ];

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-indigo-900 via-slate-900 to-slate-950 text-white p-8 sm:p-12 border border-indigo-900/50 shadow-2xl">
        <div className="absolute top-0 right-0 -mt-12 -mr-12 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 -mb-12 -ml-12 w-96 h-96 bg-violet-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 backdrop-blur-xs">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Interactive Pedagogy Learning Environment</span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight leading-tight">
            Cryptography &amp; Network Security Platform
          </h1>

          <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
            Welcome to the interactive digital laboratories for modern cryptography. Explore Claude Shannon&apos;s information-theoretic security, pseudorandom generator lattices, public-key discrete logarithm hardness, and historic digital signature vulnerabilities through live calculation traces and real-time cryptanalytic exploits.
          </p>

          <div className="pt-2 flex flex-wrap items-center gap-4">
            <Button
              variant="primary"
              size="lg"
              onClick={() => onSelectTab('otp')}
              icon={<ArrowRight className="w-4 h-4" />}
            >
              Start Lab 1: One-Time Pad
            </Button>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium bg-slate-800/80 hover:bg-slate-700/80 text-slate-200 border border-slate-700 transition-colors"
            >
              <BookOpen className="w-4 h-4" />
              <span>Interactive API Docs</span>
            </a>
          </div>
        </div>
      </div>

      {/* 4 Pillars Interactive Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-slate-100 tracking-tight">
              Four Pedagogical Pillars
            </h2>
            <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
              Interactive sandboxes combining rigorous mathematics with dynamic visualizers
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {pillars.map((pillar) => (
            <Card
              key={pillar.key}
              title={
                <span className="flex items-center gap-2">
                  <span>{pillar.title}</span>
                </span>
              }
              subtitle={pillar.subtitle}
              icon={pillar.icon}
              action={
                <Badge variant={pillar.badgeVariant} size="sm">
                  {pillar.difficulty}
                </Badge>
              }
              footer={
                <div className="flex items-center justify-between">
                  <span className="font-mono text-[11px] text-slate-400">
                    {pillar.labNumber}
                  </span>
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => onSelectTab(pillar.key)}
                    icon={<ArrowRight className="w-3.5 h-3.5" />}
                  >
                    Launch Lab
                  </Button>
                </div>
              }
              className="flex flex-col justify-between hover:border-indigo-300 dark:hover:border-indigo-800 hover:shadow-md transition-all duration-200"
            >
              <div className="space-y-4">
                {/* Core Math Equation */}
                <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/70 border border-slate-200 dark:border-slate-700 text-center text-xs font-mono text-indigo-600 dark:text-indigo-400">
                  <MathFormula math={pillar.mathFormula} />
                </div>

                {/* Key Objectives */}
                <div className="space-y-2">
                  <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide block">
                    Key Laboratory Objectives:
                  </span>
                  <ul className="space-y-1.5 text-xs text-slate-600 dark:text-slate-300">
                    {pillar.objectives.map((obj, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-indigo-500 dark:text-indigo-400 mt-0.5">&bull;</span>
                        <span>{obj}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Theoretical Course Syllabus Overview */}
      <Card
        title="Theoretical Foundations &amp; Theorems Explored"
        subtitle="Core mathematical theorems and FIPS cryptographic standards implemented across the laboratories"
        icon={<Award className="w-5 h-5 text-indigo-500" />}
      >
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-1.5">
            <div className="font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-emerald-500" />
              <span>Shannon&apos;s Perfect Secrecy (1949)</span>
            </div>
            <p className="text-slate-600 dark:text-slate-400 text-[11px]">
              Proves that true perfect secrecy requires <MathFormula math="H(K) \ge H(M)" /> and key length <MathFormula math="|K| \ge |M|" />. Explores the Two-Time Pad vulnerability when a key is reused.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-1.5">
            <div className="font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-1.5">
              <Cpu className="w-4 h-4 text-amber-500" />
              <span>Hull-Dobell Theorem (1962)</span>
            </div>
            <p className="text-slate-600 dark:text-slate-400 text-[11px]">
              Establishes the three strict modular arithmetic conditions necessary and sufficient for an LCG to achieve full period <MathFormula math="m" /> without early cyclic degeneration.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-1.5">
            <div className="font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-1.5">
              <Zap className="w-4 h-4 text-rose-500" />
              <span>Marsaglia Hyperplane Bounds (1968)</span>
            </div>
            <p className="text-slate-600 dark:text-slate-400 text-[11px]">
              Demonstrates that LCG d-tuples fall into at most <MathFormula math="(d! \cdot m)^{1/d}" /> parallel hyperplanes, breaking Monte Carlo simulations and key generation.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-1.5">
            <div className="font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-1.5">
              <KeyRound className="w-4 h-4 text-indigo-500" />
              <span>Discrete Logarithm &amp; Homomorphism</span>
            </div>
            <p className="text-slate-600 dark:text-slate-400 text-[11px]">
              Computational Diffie-Hellman hardness in cyclic safe-prime groups, and component-wise multiplicative homomorphic properties of ElGamal ciphertexts.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-1.5">
            <div className="font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-1.5">
              <FileCheck2 className="w-4 h-4 text-rose-500" />
              <span>FIPS 186-4 Digital Signatures</span>
            </div>
            <p className="text-slate-600 dark:text-slate-400 text-[11px]">
              U.S. Federal Information Processing Standard for digital signatures with hash truncation, resampling loops, and zero-knowledge soundness verification.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-1.5">
            <div className="font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-1.5">
              <ShieldAlert className="w-4 h-4 text-rose-500" />
              <span>Sony PS3 Nonce Reuse Exploit (2010)</span>
            </div>
            <p className="text-slate-600 dark:text-slate-400 text-[11px]">
              The real-world PlayStation 3 vulnerability showing how repeating ephemeral nonce <MathFormula math="k" /> across two signatures permits algebraic extraction of root private keys.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
};
