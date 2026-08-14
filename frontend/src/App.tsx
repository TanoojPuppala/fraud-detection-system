import React, { useEffect, useState } from 'react';
import { Navbar }                  from './components/Navbar';
import { Sidebar }                 from './components/Sidebar';
import { KpiCards }                from './components/KpiCards';
import { SinglePredictForm }       from './components/SinglePredictForm';
import { BatchPredict }            from './components/BatchPredict';
import { TransactionHistoryTable } from './components/TransactionHistoryTable';
import { ModelComparisonView }     from './components/ModelComparisonView';
import { SimulatorControlView }    from './components/SimulatorControlView';
import { fetchSystemStats, SystemStats } from './api/client';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [stats, setStats] = useState<SystemStats | null>(null);

  const loadStats = async () => {
    try { setStats(await fetchSystemStats()); }
    catch (err) { console.error('Failed to load system stats', err); }
  };

  useEffect(() => {
    loadStats();
    const interval = setInterval(loadStats, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--bg-app)', color: 'var(--text-primary)' }}>
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <div style={{ display: 'flex', flex: 1 }}>
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

        <main style={{ flex: 1, padding: '28px 32px', display: 'flex', flexDirection: 'column', gap: 20, minWidth: 0 }}>

          {activeTab === 'dashboard' && (
            <>
              {/* Page Title */}
              <div>
                <h2 style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)', margin: 0, lineHeight: 1.3 }}>
                  Dashboard Overview
                </h2>
                <p style={{ fontSize: 12, color: 'var(--text-muted)', margin: '4px 0 0' }}>
                  Real-time fraud detection metrics and transaction scoring
                </p>
              </div>

              <KpiCards stats={stats} />
              <SinglePredictForm />
              <TransactionHistoryTable />
            </>
          )}

          {activeTab === 'batch' && (
            <>
              <div>
                <h2 style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>Batch CSV Scoring</h2>
                <p style={{ fontSize: 12, color: 'var(--text-muted)', margin: '4px 0 0' }}>High-throughput scoring for transaction datasets</p>
              </div>
              <BatchPredict />
            </>
          )}

          {activeTab === 'analytics' && (
            <>
              <div>
                <h2 style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>Model Benchmark & SHAP</h2>
                <p style={{ fontSize: 12, color: 'var(--text-muted)', margin: '4px 0 0' }}>Comparative analysis across all evaluated model variants</p>
              </div>
              <ModelComparisonView />
            </>
          )}

          {activeTab === 'simulator' && (
            <>
              <div>
                <h2 style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>Real-Time Simulator</h2>
                <p style={{ fontSize: 12, color: 'var(--text-muted)', margin: '4px 0 0' }}>Synthetic live transaction stream to simulate production traffic</p>
              </div>
              <SimulatorControlView />
            </>
          )}

        </main>
      </div>
    </div>
  );
};

export default App;
