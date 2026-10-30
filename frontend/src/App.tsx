import React, { useEffect, useState } from 'react';
import { ThemeProvider } from './context/ThemeContext';
import { AppLayout } from './components/layout/AppLayout';
import { TabKey } from './components/common/Navbar';
import { DashboardPage } from './pages/DashboardPage';
import { OTPLabPage } from './pages/OTPLabPage';
import { LCGLabPage } from './pages/LCGLabPage';
import { ElGamalLabPage } from './pages/ElGamalLabPage';
import { DSALabPage } from './pages/DSALabPage';

const validTabs: TabKey[] = ['dashboard', 'otp', 'lcg', 'elgamal', 'dsa'];

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabKey>(() => {
    if (typeof window !== 'undefined' && window.location.hash) {
      const hash = window.location.hash.replace('#', '') as TabKey;
      if (validTabs.includes(hash)) {
        return hash;
      }
    }
    return 'dashboard';
  });

  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.replace('#', '') as TabKey;
      if (validTabs.includes(hash)) {
        setActiveTab(hash);
      }
    };
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const handleSelectTab = (tab: TabKey) => {
    setActiveTab(tab);
    window.location.hash = tab === 'dashboard' ? '' : tab;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <ThemeProvider>
      <AppLayout activeTab={activeTab} onSelectTab={handleSelectTab}>
        {activeTab === 'dashboard' && <DashboardPage onSelectTab={handleSelectTab} />}
        {activeTab === 'otp' && <OTPLabPage />}
        {activeTab === 'lcg' && <LCGLabPage />}
        {activeTab === 'elgamal' && <ElGamalLabPage />}
        {activeTab === 'dsa' && <DSALabPage />}
      </AppLayout>
    </ThemeProvider>
  );
};

export default App;
