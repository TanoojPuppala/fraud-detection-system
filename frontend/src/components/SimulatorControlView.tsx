import React, { useEffect, useState } from 'react';
import { Radio, Play, Square, AlertTriangle, Activity } from 'lucide-react';
import { controlSimulator, fetchSimulatorStatus, SimulatorStatus } from '../api/client';

export const SimulatorControlView: React.FC = () => {
  const [status, setStatus] = useState<SimulatorStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const loadStatus = async () => {
    try {
      const res = await fetchSimulatorStatus();
      setStatus(res);
    } catch (err) {
      console.error(err);
    }
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
      const updated = await controlSimulator(action, 1.5);
      setStatus(updated);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-card p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-gradient-to-tr from-rose-500/20 to-amber-500/20 border border-rose-500/30 text-rose-400">
            <Radio className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Real-Time Transaction Stream Simulator</h3>
            <p className="text-xs text-slate-400">Streams synthetic live transaction scoring requests to simulate real-world production traffic</p>
          </div>
        </div>

        <button
          onClick={handleToggle}
          disabled={loading}
          className={`px-5 py-2.5 rounded-xl font-bold text-sm flex items-center space-x-2 transition-all shadow-lg ${
            status?.is_running
              ? 'bg-rose-500 hover:bg-rose-600 text-white shadow-rose-500/25'
              : 'bg-emerald-500 hover:bg-emerald-600 text-white shadow-emerald-500/25'
          }`}
        >
          {status?.is_running ? (
            <>
              <Square className="w-4 h-4" />
              <span>Stop Simulator</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              <span>Start Live Stream</span>
            </>
          )}
        </button>
      </div>

      {/* Simulator Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
          <span className="text-xs text-slate-400 font-mono">Stream Status</span>
          <div className="flex items-center space-x-2 mt-1">
            <span className={`inline-block w-2.5 h-2.5 rounded-full ${status?.is_running ? 'bg-emerald-400 animate-ping' : 'bg-slate-600'}`} />
            <span className="text-lg font-bold text-white uppercase">{status?.is_running ? 'Streaming' : 'Idle'}</span>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
          <span className="text-xs text-slate-400 font-mono">Simulated Transactions</span>
          <p className="text-2xl font-extrabold text-cyan-400 mt-1 font-mono">{status?.total_simulated_transactions || 0}</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-rose-500/30">
          <span className="text-xs text-rose-400 font-mono">Real-Time Alerts Raised</span>
          <p className="text-2xl font-extrabold text-rose-400 mt-1 font-mono">{status?.fraud_alerts_generated || 0}</p>
        </div>
      </div>
    </div>
  );
};
