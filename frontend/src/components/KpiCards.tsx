import React from 'react';
import { CreditCard, AlertTriangle, ShieldOff, TrendingUp } from 'lucide-react';
import { SystemStats } from '../api/client';

interface KpiCardsProps {
  stats: SystemStats | null;
}

const cards = (stats: SystemStats | null) => [
  {
    title: 'Transactions Scored',
    value: stats ? stats.total_transactions.toLocaleString() : '—',
    icon: CreditCard,
    iconClass: 'muted',
    trend: null,
  },
  {
    title: 'Fraud Flagged',
    value: stats ? stats.total_fraud_detected.toLocaleString() : '—',
    sub: stats ? `${stats.fraud_percentage}% fraud rate` : null,
    icon: AlertTriangle,
    iconClass: 'danger',
    trend: 'danger',
  },
  {
    title: 'High-Risk Alerts',
    value: stats ? (stats.risk_distribution?.High || 0).toLocaleString() : '—',
    sub: 'Requires action',
    icon: ShieldOff,
    iconClass: 'warning',
    trend: 'warning',
  },
  {
    title: 'Cost Savings Est.',
    value: stats ? `$${stats.total_estimated_cost_saved_usd.toLocaleString()}` : '—',
    sub: '$500 per fraud caught',
    icon: TrendingUp,
    iconClass: 'success',
    trend: 'success',
  },
];

const trendColors: Record<string, string> = {
  danger:  '#dc2626',
  warning: '#d97706',
  success: '#16a34a',
};

export const KpiCards: React.FC<KpiCardsProps> = ({ stats }) => {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 16 }}>
      {cards(stats).map((card, idx) => {
        const Icon = card.icon;
        const valueColor = card.trend ? trendColors[card.trend] : 'var(--text-primary)';
        return (
          <div
            key={idx}
            className="card card-hover fade-in"
            style={{ padding: '18px 20px', animationDelay: `${idx * 50}ms` }}
          >
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 14 }}>
              <span className="text-xs-caps">{card.title}</span>
              <div className={`section-icon ${card.iconClass}`} style={{ width: 32, height: 32, borderRadius: 8 }}>
                <Icon size={14} />
              </div>
            </div>

            <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 26, fontWeight: 700, color: valueColor, lineHeight: 1 }}>
              {card.value}
            </div>

            {card.sub && (
              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 6, fontFamily: 'JetBrains Mono, monospace' }}>
                {card.sub}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};
