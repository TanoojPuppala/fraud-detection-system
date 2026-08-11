import React from 'react';
import { CreditCard, AlertTriangle, ShieldCheck, DollarSign } from 'lucide-react';
import { SystemStats } from '../api/client';

interface KpiCardsProps {
  stats: SystemStats | null;
}

export const KpiCards: React.FC<KpiCardsProps> = ({ stats }) => {
  const cards = [
    {
      title: 'Total Transactions Scored',
      value: stats ? stats.total_transactions.toLocaleString() : '0',
      icon: CreditCard,
      color: 'from-cyan-500/20 to-blue-600/20',
      borderColor: 'border-cyan-500/30',
      iconColor: 'text-cyan-400',
    },
    {
      title: 'Fraud Cases Flagged',
      value: stats ? stats.total_fraud_detected.toLocaleString() : '0',
      subtext: stats ? `${stats.fraud_percentage}% Fraud Rate` : '0%',
      icon: AlertTriangle,
      color: 'from-rose-500/20 to-pink-600/20',
      borderColor: 'border-rose-500/30',
      iconColor: 'text-rose-400',
    },
    {
      title: 'High-Risk Alerts',
      value: stats ? (stats.risk_distribution?.High || 0).toLocaleString() : '0',
      subtext: 'Requires Immediate Action',
      icon: ShieldCheck,
      color: 'from-amber-500/20 to-orange-600/20',
      borderColor: 'border-amber-500/30',
      iconColor: 'text-amber-400',
    },
    {
      title: 'Estimated Financial Cost Saved',
      value: stats ? `$${stats.total_estimated_cost_saved_usd.toLocaleString()}` : '$0',
      subtext: '$500 Loss per Fraud Caught',
      icon: DollarSign,
      color: 'from-emerald-500/20 to-teal-600/20',
      borderColor: 'border-emerald-500/30',
      iconColor: 'text-emerald-400',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div
            key={idx}
            className={`glass-card p-5 border ${card.borderColor} bg-gradient-to-br ${card.color} relative overflow-hidden`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{card.title}</span>
              <div className={`p-2 rounded-xl bg-slate-900/80 border border-slate-800 ${card.iconColor}`}>
                <Icon className="w-5 h-5" />
              </div>
            </div>

            <div className="mt-4">
              <h3 className="text-2xl font-extrabold text-white tracking-tight">{card.value}</h3>
              {card.subtext && <p className="text-xs text-slate-400 mt-1 font-mono">{card.subtext}</p>}
            </div>
          </div>
        );
      })}
    </div>
  );
};
