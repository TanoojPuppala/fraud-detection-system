import React, { useEffect, useState } from 'react';
import { Radio, Play, Square, Activity } from 'lucide-react';
import { controlSimulator, fetchSimulatorStatus, SimulatorStatus } from '../api/client';

export const SimulatorControlView: React.FC = () => {
  const [status,  setStatus]  = useState<SimulatorStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const loadStatus = async () => {
    try { setStatus(await fetchSimulatorStatus()); }
    catch (err) { console.error(err); }
  };

  useEffect(() => {
    loadStatus();
    const timer = setInterval(loadStatus, 2000);
    return () => clearInterval(timer);
  }, []);

  const handleToggle = async () => {
    if (!status) return;
    setLoading(true);
    try {
      const action = status.is_running ? 'stop' : 'start';
      setStatus(await controlSimulator(action, 1.5));
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const isRunning = status?.is_running ?? false;

  return (
    <div className="card" style={{ padding: 24 }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 22 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div className={`section-icon ${isRunning ? 'danger' : 'muted'}`}>
            <Radio size={16} style={{ animation: isRunning ? 'pulse 1.5s ease-in-out infinite' : 'none' }} />
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: 14, color: 'var(--text-primary)' }}>Live Transaction Simulator</div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 1 }}>
              Streams synthetic scoring requests to simulate production traffic
            </div>
          </div>
        </div>

        <button
          onClick={handleToggle}
          disabled={loading}
          className={isRunning ? 'btn-danger' : 'btn-success'}
        >
          {isRunning
            ? <><Square size={13} /> Stop Simulator</>
            : <><Play  size={13} /> Start Stream</>
          }
        </button>
      </div>

      <hr className="divider" style={{ marginBottom: 20 }} />

      {/* Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14 }}>
        <div className="metric-block">
          <div className="text-xs-caps" style={{ marginBottom: 10 }}>Stream Status</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            {isRunning ? (
              <>
                <span className="pulse-dot" />
                <span className="mono" style={{ fontSize: 14, fontWeight: 700, color: '#16a34a' }}>STREAMING</span>
              </>
            ) : (
              <>
                <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--text-faint)', display: 'inline-block' }} />
                <span className="mono" style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-secondary)' }}>IDLE</span>
              </>
            )}
          </div>
        </div>

        <div className="metric-block">
          <div className="text-xs-caps" style={{ marginBottom: 10 }}>Simulated Transactions</div>
          <div className="mono" style={{ fontSize: 22, fontWeight: 700, color: 'var(--accent)' }}>
            {status?.total_simulated_transactions || 0}
          </div>
        </div>

        <div className="metric-block" style={{ borderColor: 'var(--danger-border)', background: 'var(--danger-subtle)' }}>
          <div className="text-xs-caps" style={{ marginBottom: 10, color: '#dc2626' }}>Fraud Alerts Raised</div>
          <div className="mono" style={{ fontSize: 22, fontWeight: 700, color: '#dc2626' }}>
            {status?.fraud_alerts_generated || 0}
          </div>
        </div>
      </div>

      {isRunning && (
        <div className="fade-in" style={{ marginTop: 16, display: 'flex', alignItems: 'center', gap: 8, fontSize: 11, color: 'var(--text-muted)' }}>
          <Activity size={12} color="#16a34a" />
          <span>Simulator actively generating and scoring transactions — auto-refreshes every 2 seconds.</span>
        </div>
      )}
    </div>
  );
};
