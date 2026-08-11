import React, { useEffect, useState } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { KpiCards } from './components/KpiCards';
import { SinglePredictForm } from './components/SinglePredictForm';
import { BatchPredict } from './components/BatchPredict';
import { TransactionHistoryTable } from './components/TransactionHistoryTable';
import { ModelComparisonView } from './components/ModelComparisonView';
import { SimulatorControlView } from './components/SimulatorControlView';
import { fetchSystemStats, SystemStats } from './api/client';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [stats, setStats] = useState<SystemStats | null>(null);

  const loadStats = async () => {
    try {
      const data = await fetchSystemStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to load system stats', err);
    }
  };

  useEffect(() => {
    loadStats();
    const interval = setInterval(loadStats, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 font-sans">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <div className="flex flex-1">
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

        <main className="flex-1 p-8 space-y-8 max-w-7xl">
          {activeTab === 'dashboard' && (
            <>
              <KpiCards stats={stats} />
              <SinglePredictForm />
              <TransactionHistoryTable />
            </>
          )}

          {activeTab === 'predict' && <SinglePredictForm />}
          {activeTab === 'batch' && <BatchPredict />}
          {activeTab === 'history' && <TransactionHistoryTable />}
          {activeTab === 'analytics' && <ModelComparisonView />}
          {activeTab === 'simulator' && <SimulatorControlView />}
        </main>
      </div>
    </div>
  );
};

export default App;
