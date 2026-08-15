import React, { useEffect, useState } from 'react';
import { BarChart3, Award, Trophy, CheckCircle2, ShieldCheck, Target, Zap } from 'lucide-react';
import { fetchModelInfo } from '../api/client';

const models = [
  { name: 'XGBoost (SMOTE)',                   accuracy: '99.93%', rocauc: '0.9693', prauc: '0.8186', cost: '$10,595', recall: '77.89%', precision: '79.57%', fp: '19',    fn: '21', champion: false },
  { name: 'PyTorch DNN (SMOTE)',               accuracy: '99.87%', rocauc: '0.9514', prauc: '0.7172', cost: '$9,770',  recall: '80.00%', precision: '58.46%', fp: '54',    fn: '19', champion: true  },
  { name: 'Logistic Regression (Baseline)',    accuracy: '97.53%', rocauc: '0.9657', prauc: '0.6719', cost: '$12,945', recall: '87.37%', precision: '5.64%',  fp: '1,389', fn: '12', champion: false },
  { name: 'Logistic Regression (SMOTE)',       accuracy: '97.37%', rocauc: '0.9626', prauc: '0.6750', cost: '$13,410', recall: '87.37%', precision: '5.30%',  fp: '1,482', fn: '12', champion: false },
  { name: 'Logistic Regression (Undersample)', accuracy: '97.22%', rocauc: '0.9571', prauc: '0.5896', cost: '$13,815', recall: '87.37%', precision: '5.04%',  fp: '1,563', fn: '12', champion: false },
  { name: 'PyTorch Autoencoder',               accuracy: '99.49%', rocauc: '0.9277', prauc: '0.2013', cost: '$23,730', recall: '52.63%', precision: '16.89%', fp: '246',   fn: '45', champion: false },
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
        border: '1px solid #a7f3d0',
        background: 'linear-gradient(135deg, #ecfdf5 0%, #ffffff 100%)',
      }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 16 }}>
          <div className="section-icon success" style={{ width: 44, height: 44, borderRadius: 12 }}>
            <Trophy size={20} />
          </div>
          <div style={{ flex: 1 }}>
            <div className="text-xs-caps" style={{ color: '#059669', marginBottom: 4 }}>
              Production Deployment Champion
            </div>
            <div style={{ fontWeight: 700, fontSize: 16, color: 'var(--text-primary)', marginBottom: 6 }}>
              PyTorch DNN (SMOTE)
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.6, maxWidth: 640 }}>
              Selected via cost-aware financial evaluation — achieving <strong style={{ color: '#047857', fontFamily: 'JetBrains Mono, monospace' }}>99.87% Accuracy</strong>,{' '}
              <strong style={{ color: '#047857', fontFamily: 'JetBrains Mono, monospace' }}>0.9514 ROC-AUC</strong>, and total business cost{' '}
              <strong style={{ color: '#047857', fontFamily: 'JetBrains Mono, monospace' }}>
                ${info?.metadata?.metrics?.['Total Business Cost ($)'] || '9,770'}
              </strong>{' '}
              (saving $825 vs XGBoost by minimizing catastrophic false negatives).
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '6px 16px', flexShrink: 0, minWidth: 260, background: 'rgba(255,255,255,0.8)', padding: '10px 14px', borderRadius: 8, border: '1px solid #d1fae5' }}>
            {[
              { label: 'Accuracy',  value: '99.87%', color: '#059669' },
              { label: 'ROC-AUC',   value: '0.9514', color: '#2563eb' },
              { label: 'PR-AUC',    value: '0.7172', color: '#7c3aed' },
              { label: 'Recall',    value: '80.00%', color: '#16a34a' },
              { label: 'Precision', value: '58.46%', color: 'var(--text-secondary)' },
              { label: 'Total Cost',value: '$9,770', color: '#b45309' },
            ].map((m, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
                <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{m.label}:</span>
                <span className="mono" style={{ fontSize: 11, fontWeight: 700, color: m.color }}>{m.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Benchmark Summary Stat Highlights */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
        <div className="card" style={{ padding: '12px 16px', display: 'flex', alignItems: 'center', gap: 12 }}>
          <div className="section-icon success" style={{ width: 36, height: 36, borderRadius: 8 }}>
            <CheckCircle2 size={16} />
          </div>
          <div>
            <div className="text-xs-caps" style={{ fontSize: 9 }}>Peak Accuracy</div>
            <div className="mono" style={{ fontSize: 16, fontWeight: 700, color: '#059669' }}>99.93%</div>
            <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>XGBoost (SMOTE)</div>
          </div>
        </div>

        <div className="card" style={{ padding: '12px 16px', display: 'flex', alignItems: 'center', gap: 12 }}>
          <div className="section-icon accent" style={{ width: 36, height: 36, borderRadius: 8, background: '#eff6ff', color: '#2563eb' }}>
            <ShieldCheck size={16} />
          </div>
          <div>
            <div className="text-xs-caps" style={{ fontSize: 9 }}>Top ROC-AUC</div>
            <div className="mono" style={{ fontSize: 16, fontWeight: 700, color: '#2563eb' }}>0.9693 (96.9%)</div>
            <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>Exceeds 90% Benchmark</div>
          </div>
        </div>

        <div className="card" style={{ padding: '12px 16px', display: 'flex', alignItems: 'center', gap: 12 }}>
          <div className="section-icon warning" style={{ width: 36, height: 36, borderRadius: 8 }}>
            <Target size={16} />
          </div>
          <div>
            <div className="text-xs-caps" style={{ fontSize: 9 }}>Peak Recall</div>
            <div className="mono" style={{ fontSize: 16, fontWeight: 700, color: '#16a34a' }}>87.37%</div>
            <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>83 of 95 Frauds Caught</div>
          </div>
        </div>

        <div className="card" style={{ padding: '12px 16px', display: 'flex', alignItems: 'center', gap: 12 }}>
          <div className="section-icon" style={{ width: 36, height: 36, borderRadius: 8, background: '#fef3c7', color: '#b45309' }}>
            <Zap size={16} />
          </div>
          <div>
            <div className="text-xs-caps" style={{ fontSize: 9 }}>Lowest Business Cost</div>
            <div className="mono" style={{ fontSize: 16, fontWeight: 700, color: '#b45309' }}>$9,770</div>
            <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>PyTorch DNN (SMOTE)</div>
          </div>
        </div>
      </div>

      {/* Benchmark Table */}
      <div className="card fade-in" style={{ padding: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 18 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <BarChart3 size={16} color="var(--accent)" />
            <span style={{ fontWeight: 700, fontSize: 14, color: 'var(--text-primary)' }}>
              6-Model Benchmark Matrix (Overall Accuracy & ROC-AUC Evaluated)
            </span>
          </div>
          <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
            Evaluated on 56,746 held-out test transactions
          </span>
        </div>

        <hr className="divider" style={{ marginBottom: 0 }} />

        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Model Variant</th>
                <th>Overall Accuracy</th>
                <th>ROC-AUC</th>
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
                    background: m.champion ? '#f0fdf4' : undefined,
                    fontWeight: m.champion ? 600 : 400,
                  }}
                >
                  <td style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-primary)' }}>
                    {m.champion && <Award size={12} color="#059669" />}
                    {m.name}
                  </td>
                  <td className="mono" style={{ color: '#059669', fontWeight: 700 }}>{m.accuracy}</td>
                  <td className="mono" style={{ color: '#2563eb', fontWeight: 700 }}>{m.rocauc}</td>
                  <td className="mono" style={{ color: '#7c3aed', fontWeight: 600 }}>{m.prauc}</td>
                  <td className="mono" style={{ color: '#16a34a', fontWeight: 600 }}>{m.recall}</td>
                  <td className="mono" style={{ color: 'var(--text-secondary)' }}>{m.precision}</td>
                  <td className="mono" style={{ color: 'var(--text-secondary)' }}>{m.fp}</td>
                  <td className="mono" style={{ color: '#dc2626', fontWeight: 600 }}>{m.fn}</td>
                  <td className="mono" style={{ color: '#b45309', fontWeight: 700 }}>{m.cost}</td>
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

