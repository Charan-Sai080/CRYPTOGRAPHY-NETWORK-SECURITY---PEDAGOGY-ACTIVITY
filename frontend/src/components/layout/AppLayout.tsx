import React from 'react';
import { Navbar, TabKey } from '../common/Navbar';
import { Footer } from '../common/Footer';

interface AppLayoutProps {
  children: React.ReactNode;
  activeTab: TabKey;
  onSelectTab: (tab: TabKey) => void;
}

export const AppLayout: React.FC<AppLayoutProps> = ({
  children,
  activeTab,
  onSelectTab,
}) => {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100 transition-colors duration-200">
      <Navbar activeTab={activeTab} onSelectTab={onSelectTab} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      <Footer />
    </div>
  );
};
