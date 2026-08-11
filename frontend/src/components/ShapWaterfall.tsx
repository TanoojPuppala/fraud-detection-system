import React from 'react';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';

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

  return (
    <div className="space-y-3">
      <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono">
        SHAP Feature Attribution Breakdown (Top Factors)
      </h4>
      <div className="space-y-2">
        {features.map((feat, idx) => {
          const isPositive = feat.shap_value > 0;
          return (
            <div key={idx} className="flex items-center justify-between p-2.5 rounded-lg bg-slate-900/60 border border-slate-800 text-xs">
              <div className="flex items-center space-x-2">
                {isPositive ? (
                  <div className="p-1 rounded bg-rose-500/20 text-rose-400">
                    <ArrowUpRight className="w-3.5 h-3.5" />
                  </div>
                ) : (
                  <div className="p-1 rounded bg-emerald-500/20 text-emerald-400">
                    <ArrowDownRight className="w-3.5 h-3.5" />
                  </div>
                )}
                <div>
                  <span className="font-bold text-slate-200">{feat.feature}</span>
                  <span className="text-slate-500 ml-2 font-mono">val: {feat.value.toFixed(4)}</span>
                </div>
              </div>

              <div className="text-right">
                <span className={`font-bold font-mono ${isPositive ? 'text-rose-400' : 'text-emerald-400'}`}>
                  {isPositive ? '+' : ''}{feat.shap_value.toFixed(4)}
                </span>
                <p className="text-[10px] text-slate-400">{feat.impact}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
