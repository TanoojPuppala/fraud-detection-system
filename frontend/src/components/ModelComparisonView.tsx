import React, { useEffect, useState } from 'react';
import { BarChart3, Award, Trophy } from 'lucide-react';
import { fetchModelInfo } from '../api/client';

const models = [
  { name: 'XGBoost (SMOTE)',                     prauc: '0.8186', cost: '$10,595', recall: '77.89%', precision: '79.57%', fp: '19',    fn: '21', champion: false },
  { name: 'PyTorch DNN (SMOTE)',                 prauc: '0.7172', cost: '$9,770',  recall: '80.00%', precision: '58.46%', fp: '54',    fn: '19', champion: true  },
  { name: 'Logistic Regression (SMOTE)',         prauc: '0.6750', cost: '$13,410', recall: '87.37%', precision: '5.30%',  fp: '1,482', fn: '12', champion: false },
  { name: 'Logistic Regression (Baseline)',      prauc: '0.6719', cost: '$12,945', recall: '87.37%', precision: '5.64%',  fp: '1,389', fn: '12', champion: false },
  { name: 'Logistic Regression (Undersample)',   prauc: '0.5896', cost: '$13,815', recall: '87.37%', precision: '5.04%',  fp: '1,563', fn: '12', champion: false },
  { name: 'PyTorch Autoencoder',                 prauc: '0.2013', cost: '$23,730', recall: '52.63%', precision: '16.89%', fp: '246',   fn: '45', champion: false },
];

export const ModelComparisonView: React.FC = () => {
  const [info, setInfo] = useState<any | null>(null);

  useEffect(() => {
    fetchModelInfo().then(setInfo).catch(console.error);
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>

      {/* Champion Banner */}
      <div className="card fade-in" style={{
        padding: 20,
        border: '1px solid var(--success-border)',
        background: 'linear-gradient(135deg, rgba(16,185,129,0.07) 0%, var(--bg-card) 100%)',
      }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 16 }}>
          <div className="section-icon success" style={{ width: 44, height: 44, borderRadius: 12 }}>
            <Trophy size={20} />
          </div>
          <div style={{ flex: 1 }}>
            <div className="text-xs-caps" style={{ color: '#34d399', marginBottom: 4 }}>
              Production Deployment Champion
            </div>
            <div style={{ fontWeight: 700, fontSize: 16, color: 'var(--text-primary)', marginBottom: 6 }}>
              PyTorch DNN (SMOTE)
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.6, maxWidth: 640 }}>
              Selected via cost-aware financial evaluation — total cost{' '}
              <strong style={{ color: '#34d399', fontFamily: 'JetBrains Mono, monospace' }}>
                ${info?.metadata?.metrics?.['Total Business Cost ($)'] || '9,770'}
              </strong>{' '}
              vs $10,595 for XGBoost. Minimizes catastrophic false negatives ($500/fraud caught).
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, flexShrink: 0, minWidth: 130 }}>
            {[
              { label: 'PR-AUC',    value: '0.7172' },
              { label: 'Recall',    value: '80.00%' },
              { label: 'Precision', value: '58.46%' },
            ].map((m, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', gap: 12 }}>
                <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{m.label}</span>
                <span className="mono" style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-primary)' }}>{m.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Benchmark Table */}
      <div className="card fade-in" style={{ padding: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 18 }}>
          <BarChart3 size={16} color="#93c5fd" />
          <span style={{ fontWeight: 700, fontSize: 14, color: 'var(--text-primary)' }}>
            6-Model Benchmark Matrix
          </span>
        </div>

        <hr className="divider" style={{ marginBottom: 0 }} />

        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Model Variant</th>
                <th>PR-AUC</th>
                <th>Recall</th>
                <th>Precision</th>
                <th>False Pos</th>
                <th>False Neg</th>
                <th>Business Cost</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {models.map((m, idx) => (
                <tr
                  key={idx}
                  style={{
                    background: m.champion ? 'rgba(16,185,129,0.05)' : undefined,
                    fontWeight: m.champion ? 600 : 400,
                  }}
                >
                  <td style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-primary)' }}>
                    {m.champion && <Award size={12} color="#34d399" />}
                    {m.name}
                  </td>
                  <td style={{ color: '#93c5fd' }}>{m.prauc}</td>
                  <td style={{ color: '#34d399' }}>{m.recall}</td>
                  <td style={{ color: 'var(--text-secondary)' }}>{m.precision}</td>
                  <td style={{ color: 'var(--text-secondary)' }}>{m.fp}</td>
                  <td style={{ color: '#f87171' }}>{m.fn}</td>
                  <td className="mono" style={{ color: '#fbbf24', fontWeight: 700 }}>{m.cost}</td>
                  <td>
                    {m.champion ? (
                      <span className="badge badge-champion">Champion</span>
                    ) : (
                      <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>Evaluated</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
