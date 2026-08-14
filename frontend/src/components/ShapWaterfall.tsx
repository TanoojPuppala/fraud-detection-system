import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface FeatureImpact {
  feature: string;
  value: number;
  shap_value: number;
  impact: string;
}

interface ShapWaterfallProps {
  features: FeatureImpact[];
}

export const ShapWaterfall: React.FC<ShapWaterfallProps> = ({ features }) => {
  if (!features || features.length === 0) return null;

  const maxAbs = Math.max(...features.map((f) => Math.abs(f.shap_value)));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      <div className="text-xs-caps">SHAP Feature Attribution</div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {features.map((feat, idx) => {
          const isPositive = feat.shap_value > 0;
          const pct = Math.abs(feat.shap_value) / maxAbs;

          return (
            <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  {isPositive
                    ? <TrendingUp size={12} color="#dc2626" />
                    : <TrendingDown size={12} color="#16a34a" />
                  }
                  <span className="mono" style={{ fontSize: 11, color: 'var(--text-secondary)', fontWeight: 600 }}>
                    {feat.feature}
                  </span>
                  <span className="mono" style={{ fontSize: 10, color: 'var(--text-muted)' }}>
                    = {feat.value.toFixed(3)}
                  </span>
                </div>
                <span
                  className="mono"
                  style={{ fontSize: 11, fontWeight: 600, color: isPositive ? '#dc2626' : '#16a34a' }}
                >
                  {isPositive ? '+' : ''}{feat.shap_value.toFixed(4)}
                </span>
              </div>

              {/* Progress bar */}
              <div className="progress-bar-track">
                <div
                  className="progress-bar-fill"
                  style={{
                    width: `${pct * 100}%`,
                    background: isPositive
                      ? 'linear-gradient(90deg, #ef4444, #dc2626)'
                      : 'linear-gradient(90deg, #22c55e, #16a34a)',
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
