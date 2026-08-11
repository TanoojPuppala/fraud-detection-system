import React, { useEffect, useState } from 'react';
import { History, CheckCircle, AlertOctagon, Filter } from 'lucide-react';
import { fetchTransactionHistory } from '../api/client';

export const TransactionHistoryTable: React.FC = () => {
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [filter, setFilter] = useState<string>('All');

  const loadHistory = async () => {
    setLoading(true);
    try {
      const data = await fetchTransactionHistory(50, 0, filter === 'All' ? undefined : filter);
      setHistory(data.items || []);
    } catch (err) {
      console.error('Failed to load history', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, [filter]);

  return (
    <div className="glass-card p-6 space-y-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-xl bg-indigo-500/20 border border-indigo-500/30 text-indigo-400">
            <History className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Transaction Audit Log</h3>
            <p className="text-xs text-slate-400">Real-time persistent audit trail of scored transactions</p>
          </div>
        </div>

        {/* Filter Dropdown */}
        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-slate-500" />
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-lg text-xs font-mono px-3 py-1.5 text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="All">All Risk Bands</option>
            <option value="High">High Risk</option>
            <option value="Medium">Medium Risk</option>
            <option value="Low">Low Risk</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs font-mono">
          <thead className="bg-slate-900/80 text-slate-400 border-b border-slate-800 uppercase font-semibold">
            <tr>
              <th className="px-4 py-3">Pred ID</th>
              <th className="px-4 py-3">Amount</th>
              <th className="px-4 py-3">Raw Prob</th>
              <th className="px-4 py-3">Risk Band</th>
              <th className="px-4 py-3">Outcome</th>
              <th className="px-4 py-3">Latency</th>
              <th className="px-4 py-3">Timestamp</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {loading ? (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-slate-500">Loading audit log...</td>
              </tr>
            ) : history.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-slate-500">No scored transactions found.</td>
              </tr>
            ) : (
              history.map((row) => (
                <tr key={row.prediction_id} className="hover:bg-slate-900/50 transition-colors">
                  <td className="px-4 py-3 text-slate-300 font-bold">#{row.prediction_id}</td>
                  <td className="px-4 py-3 font-bold text-white">${row.amount.toFixed(2)}</td>
                  <td className="px-4 py-3 text-cyan-400 font-bold">{(row.raw_probability * 100).toFixed(2)}%</td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-0.5 rounded font-bold text-[10px] ${
                        row.risk_band === 'High'
                          ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                          : row.risk_band === 'Medium'
                          ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                          : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      }`}
                    >
                      {row.risk_band}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {row.is_fraud ? (
                      <span className="flex items-center gap-1 text-rose-400 font-bold">
                        <AlertOctagon className="w-3.5 h-3.5" /> FRAUD
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-emerald-400 font-bold">
                        <CheckCircle className="w-3.5 h-3.5" /> LEGIT
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-slate-400">{row.inference_time_ms.toFixed(2)} ms</td>
                  <td className="px-4 py-3 text-slate-500">{new Date(row.created_at).toLocaleTimeString()}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
