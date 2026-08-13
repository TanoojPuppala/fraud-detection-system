import React, { useEffect, useState } from 'react';
import { History, CheckCircle, AlertOctagon, Filter } from 'lucide-react';
import { fetchTransactionHistory } from '../api/client';

export const TransactionHistoryTable: React.FC = () => {
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [filter,  setFilter]  = useState<string>('All');

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

  useEffect(() => { loadHistory(); }, [filter]);

  return (
    <div className="card" style={{ padding: 24 }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 18 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div className="section-icon">
            <History size={16} />
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: 14, color: 'var(--text-primary)' }}>Transaction Audit Log</div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 1 }}>Real-time persistent audit trail</div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Filter size={13} color="var(--text-muted)" />
          <select
            className="form-select"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="All">All Risk Bands</option>
            <option value="High">High Risk</option>
            <option value="Medium">Medium Risk</option>
            <option value="Low">Low Risk</option>
          </select>
        </div>
      </div>

      <hr className="divider" style={{ marginBottom: 0 }} />

      {/* Table */}
      <div style={{ overflowX: 'auto' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Pred ID</th>
              <th>Amount</th>
              <th>Raw Prob</th>
              <th>Risk Band</th>
              <th>Outcome</th>
              <th>Latency</th>
              <th>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={7} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '32px 0' }}>
                  Loading audit log…
                </td>
              </tr>
            ) : history.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '32px 0' }}>
                  No scored transactions found.
                </td>
              </tr>
            ) : (
              history.map((row) => (
                <tr key={row.prediction_id}>
                  <td style={{ color: 'var(--text-muted)', fontWeight: 500 }}>#{row.prediction_id}</td>
                  <td style={{ fontWeight: 600 }}>${row.amount.toFixed(2)}</td>
                  <td style={{ color: '#93c5fd', fontWeight: 600 }}>{(row.raw_probability * 100).toFixed(2)}%</td>
                  <td>
                    <span className={`badge ${
                      row.risk_band === 'High' ? 'badge-high' :
                      row.risk_band === 'Medium' ? 'badge-med' : 'badge-low'
                    }`}>
                      {row.risk_band}
                    </span>
                  </td>
                  <td>
                    {row.is_fraud ? (
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5, color: '#f87171', fontWeight: 600 }}>
                        <AlertOctagon size={12} /> FRAUD
                      </span>
                    ) : (
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5, color: '#34d399', fontWeight: 600 }}>
                        <CheckCircle size={12} /> LEGIT
                      </span>
                    )}
                  </td>
                  <td style={{ color: 'var(--text-secondary)' }}>{row.inference_time_ms.toFixed(2)} ms</td>
                  <td style={{ color: 'var(--text-muted)' }}>{new Date(row.created_at).toLocaleTimeString()}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
