import React, { useEffect, useState } from 'react';
import { BarChart3, ShieldCheck, Award, Zap } from 'lucide-react';
import { fetchModelInfo } from '../api/client';

export const ModelComparisonView: React.FC = () => {
  const [info, setInfo] = useState<any | null>(null);

  useEffect(() => {
    fetchModelInfo()
      .then(setInfo)
      .catch((err) => console.error(err));
  }, []);

  const models = [
    { name: 'XGBoost (SMOTE)', prauc: '0.8186', cost: '$10,595.00', recall: '77.89%', precision: '79.57%', fp: '19', fn: '21', status: 'PR-AUC Winner' },
    { name: 'PyTorch DNN (SMOTE)', prauc: '0.7172', cost: '$9,770.00', recall: '80.00%', precision: '58.46%', fp: '54', fn: '19', status: 'PRODUCTION CHAMPION', champion: true },
    { name: 'Logistic Regression (SMOTE)', prauc: '0.6750', cost: '$13,410.00', recall: '87.37%', precision: '5.30%', fp: '1,482', fn: '12', status: 'Evaluated' },
    { name: 'Logistic Regression (Baseline)', prauc: '0.6719', cost: '$12,945.00', recall: '87.37%', precision: '5.64%', fp: '1,389', fn: '12', status: 'Evaluated' },
    { name: 'Logistic Regression (Undersample)', prauc: '0.5896', cost: '$13,815.00', recall: '87.37%', precision: '5.04%', fp: '1,563', fn: '12', status: 'Evaluated' },
    { name: 'PyTorch Autoencoder', prauc: '0.2013', cost: '$23,730.00', recall: '52.63%', precision: '16.89%', fp: '246', fn: '45', status: 'Unsupervised' },
  ];

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="glass-card p-6 border border-emerald-500/30 bg-gradient-to-r from-emerald-500/10 via-slate-900 to-indigo-500/10">
        <div className="flex items-center space-x-4">
          <div className="p-3 rounded-2xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">
            <Award className="w-8 h-8" />
          </div>
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400 font-mono">Production Deployment Winner</span>
            <h3 className="text-xl font-extrabold text-white">PyTorch DNN (SMOTE)</h3>
            <p className="text-xs text-slate-300 mt-1 max-w-3xl">
              Selected via cost-aware financial evaluation (${info?.metadata?.metrics?.['Total Business Cost ($)'] || '9,770.00'} total cost vs $10,595 for XGBoost). Minimizes catastrophic false negatives ($500 per uncaught fraud).
            </p>
          </div>
        </div>
      </div>

      {/* Model Benchmark Matrix */}
      <div className="glass-card p-6 space-y-4">
        <div className="flex items-center space-x-3">
          <BarChart3 className="w-5 h-5 text-cyan-400" />
          <h3 className="text-lg font-bold text-white">All 6 Models Benchmark Matrix</h3>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-900 text-slate-400 border-b border-slate-800 uppercase font-semibold">
              <tr>
                <th className="px-4 py-3">Model Variant</th>
                <th className="px-4 py-3">PR-AUC</th>
                <th className="px-4 py-3">Recall</th>
                <th className="px-4 py-3">Precision</th>
                <th className="px-4 py-3">False Pos</th>
                <th className="px-4 py-3">False Neg</th>
                <th className="px-4 py-3">Business Cost ($)</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {models.map((m, idx) => (
                <tr key={idx} className={m.champion ? 'bg-emerald-500/10 font-bold' : 'hover:bg-slate-900/40'}>
                  <td className="px-4 py-3 text-white">{m.name}</td>
                  <td className="px-4 py-3 text-cyan-400">{m.prauc}</td>
                  <td className="px-4 py-3 text-emerald-400">{m.recall}</td>
                  <td className="px-4 py-3 text-indigo-400">{m.precision}</td>
                  <td className="px-4 py-3 text-slate-300">{m.fp}</td>
                  <td className="px-4 py-3 text-rose-400">{m.fn}</td>
                  <td className="px-4 py-3 text-amber-400 font-extrabold">{m.cost}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] uppercase ${
                        m.champion
                          ? 'bg-emerald-500/30 text-emerald-300 border border-emerald-500/50'
                          : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {m.status}
                    </span>
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
