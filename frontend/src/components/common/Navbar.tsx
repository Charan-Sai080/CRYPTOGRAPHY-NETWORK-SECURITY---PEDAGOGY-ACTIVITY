import React, { useEffect, useState } from 'react';
import {
  ShieldCheck,
  Binary,
  Cpu,
  KeyRound,
  FileCheck2,
  Menu,
  X,
  Activity,
  Layers,
} from 'lucide-react';
import { ThemeToggle } from './ThemeToggle';
import { checkHealth } from '../../api/client';
import { HealthResponse } from '../../types/api';

export type TabKey = 'dashboard' | 'otp' | 'lcg' | 'elgamal' | 'dsa';

interface NavbarProps {
  activeTab: TabKey;
  onSelectTab: (tab: TabKey) => void;
}

const navItems: { key: TabKey; label: string; icon: React.ReactNode; badge?: string }[] = [
  { key: 'dashboard', label: 'Dashboard', icon: <Layers className="w-4 h-4" /> },
  { key: 'otp', label: 'One-Time Pad', icon: <Binary className="w-4 h-4" />, badge: 'Lab 1' },
  { key: 'lcg', label: 'LCG & Lattice', icon: <Cpu className="w-4 h-4" />, badge: 'Lab 2' },
  { key: 'elgamal', label: 'ElGamal', icon: <KeyRound className="w-4 h-4" />, badge: 'Lab 3' },
  { key: 'dsa', label: 'DSA & Signatures', icon: <FileCheck2 className="w-4 h-4" />, badge: 'Lab 4' },
];

export const Navbar: React.FC<NavbarProps> = ({ activeTab, onSelectTab }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isHealthLoading, setIsHealthLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    const fetchHealth = async () => {
      try {
        const data = await checkHealth();
        if (isMounted) {
          setHealth(data);
          setIsHealthLoading(false);
        }
      } catch {
        if (isMounted) {
          setHealth(null);
          setIsHealthLoading(false);
        }
      }
    };

    fetchHealth();
    const interval = setInterval(fetchHealth, 15000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <header className="sticky top-0 z-50 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand */}
          <div
            className="flex items-center gap-3 cursor-pointer select-none"
            onClick={() => onSelectTab('dashboard')}
          >
            <div className="p-2 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 text-white shadow-md shadow-indigo-500/20">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <span className="font-bold text-slate-900 dark:text-white tracking-tight text-lg">
                CNS Pedagogy
              </span>
              <span className="hidden sm:inline-block ml-2 text-xs font-semibold px-2 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800">
                Interactive Labs
              </span>
            </div>
          </div>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const isActive = activeTab === item.key;
              return (
                <button
                  key={item.key}
                  type="button"
                  onClick={() => onSelectTab(item.key)}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-300 font-semibold shadow-xs'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  {item.icon}
                  <span>{item.label}</span>
                  {item.badge && (
                    <span
                      className={`text-[10px] px-1.5 py-0.2 rounded font-mono ${
                        isActive
                          ? 'bg-indigo-200 dark:bg-indigo-800 text-indigo-800 dark:text-indigo-200'
                          : 'bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400'
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>

          {/* Actions & Health Status */}
          <div className="flex items-center gap-3">
            {/* Backend Health Badge */}
            <div
              className={`hidden sm:flex items-center gap-2 px-2.5 py-1 rounded-full text-xs font-medium border ${
                isHealthLoading
                  ? 'bg-slate-100 text-slate-600 border-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700'
                  : health?.status === 'healthy'
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/50 dark:text-emerald-300 dark:border-emerald-800'
                  : 'bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-950/50 dark:text-rose-300 dark:border-rose-800'
              }`}
              title={
                health
                  ? `FastAPI v${health.version} - Status: ${health.status}`
                  : 'Backend unreachable. Run: uvicorn backend.main:app --reload'
              }
            >
              <span
                className={`w-2 h-2 rounded-full ${
                  isHealthLoading
                    ? 'bg-slate-400 animate-pulse'
                    : health?.status === 'healthy'
                    ? 'bg-emerald-500'
                    : 'bg-rose-500'
                }`}
              />
              <span className="hidden lg:inline">
                {isHealthLoading
                  ? 'Connecting...'
                  : health?.status === 'healthy'
                  ? `API v${health.version}`
                  : 'API Offline'}
              </span>
              <Activity className="w-3.5 h-3.5 opacity-60" />
            </div>

            <ThemeToggle />

            {/* Mobile menu button */}
            <button
              type="button"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 focus:outline-none"
              aria-label="Open navigation menu"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden px-4 pt-2 pb-4 space-y-1 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 shadow-lg animate-in slide-in-from-top-2">
          {navItems.map((item) => {
            const isActive = activeTab === item.key;
            return (
              <button
                key={item.key}
                type="button"
                onClick={() => {
                  onSelectTab(item.key);
                  setMobileMenuOpen(false);
                }}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium ${
                  isActive
                    ? 'bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-300 font-semibold'
                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                }`}
              >
                <div className="flex items-center gap-3">
                  {item.icon}
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="text-xs px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-500 font-mono">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      )}
    </header>
  );
};
