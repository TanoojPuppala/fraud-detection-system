import React, { useState } from 'react';
import { Zap, AlertTriangle, CheckCircle2, ShieldAlert, Sparkles } from 'lucide-react';
import { predictTransaction, PredictionResult } from '../api/client';
import { ShapWaterfall } from './ShapWaterfall';

export const SinglePredictForm: React.FC = () => {
  const [amount, setAmount] = useState<number>(1250.0);
  const [time, setTime] = useState<number>(406.0);
  const [v14, setV14] = useState<number>(-4.2);
  const [v10, setV10] = useState<number>(-2.8);
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<PredictionResult | null>(null);

  // Preset scenarios
  const setPreset = (type: 'fraud' | 'legit') => {
    if (type === 'fraud') {
      setAmount(2800.5);
      setTime(406.0);
      setV14(-5.8);
      setV10(-3.9);
    } else {
      setAmount(45.2);
      setTime(12500.0);
      setV14(0.2);
      setV10(0.1);
    }
  };

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    const txData: Record<string, number> = { time, amount };
    for (let i = 1; i <= 28; i++) {
      if (i === 14) txData[`v14`] = v14;
      else if (i === 10) txData[`v10`] = v10;
      else txData[`v${i}`] = 0.05 * (i % 2 === 0 ? 1 : -1);
    }

    try {
      const res = await predictTransaction(txData);
      setResult(res);
    } catch (err) {
      console.error('Prediction failed', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
      {/* Form Container */}
      <div className="lg:col-span-7 glass-card p-6 space-y-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-xl bg-cyan-500/20 border border-cyan-500/30 text-cyan-400">
              <Zap className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Single Transaction Real-Time Scoring</h3>
              <p className="text-xs text-slate-400">Submit parameters to evaluate production model decision risk band</p>
            </div>
          </div>

          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setPreset('legit')}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/20"
            >
              Legit Preset
            </button>
            <button
              type="button"
              onClick={() => setPreset('fraud')}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-rose-500/10 border border-rose-500/30 text-rose-400 hover:bg-rose-500/20"
            >
              Fraud Preset
            </button>
          </div>
        </div>

        <form onSubmit={handlePredict} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Amount ($)</label>
              <input
                type="number"
                step="0.01"
                value={amount}
                onChange={(e) => setAmount(parseFloat(e.target.value))}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500 font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Time Elapsed (s)</label>
              <input
                type="number"
                step="1"
                value={time}
                onChange={(e) => setTime(parseFloat(e.target.value))}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500 font-mono"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">
                Feature V14 <span className="text-cyan-400 text-[10px]">(Top Fraud Import)</span>
              </label>
              <input
                type="number"
                step="0.1"
                value={v14}
                onChange={(e) => setV14(parseFloat(e.target.value))}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500 font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">
                Feature V10 <span className="text-cyan-400 text-[10px]">(2nd Import)</span>
              </label>
              <input
                type="number"
                step="0.1"
                value={v10}
                onChange={(e) => setV10(parseFloat(e.target.value))}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500 font-mono"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-bold text-sm shadow-lg shadow-cyan-500/25 flex items-center justify-center space-x-2 transition-all"
          >
            {loading ? (
              <span>Evaluating Risk Band...</span>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Evaluate Transaction Risk</span>
              </>
            )}
          </button>
        </form>
      </div>

      {/* Result Container */}
      <div className="lg:col-span-5 glass-card p-6 flex flex-col justify-between">
        {result ? (
          <div className="space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono">Prediction Outcome</span>
              <span className="text-xs text-slate-500 font-mono">ID #{result.prediction_id}</span>
            </div>

            {/* Risk Gauge Header */}
            <div className="text-center py-3">
              <div
                className={`inline-flex items-center space-x-2 px-4 py-2 rounded-full font-extrabold text-sm border ${
                  result.risk_band === 'High'
                    ? 'bg-rose-500/20 border-rose-500/40 text-rose-400 shadow-lg shadow-rose-500/20'
                    : result.risk_band === 'Medium'
                    ? 'bg-amber-500/20 border-amber-500/40 text-amber-400'
                    : 'bg-emerald-500/20 border-emerald-500/40 text-emerald-400'
                }`}
              >
                {result.risk_band === 'High' ? (
                  <ShieldAlert className="w-5 h-5" />
                ) : (
                  <CheckCircle2 className="w-5 h-5" />
                )}
                <span>RISK BAND: {result.risk_band.toUpperCase()}</span>
              </div>

              <div className="mt-3">
                <span className="text-3xl font-extrabold text-white font-mono">
                  {(result.raw_probability * 100).toFixed(2)}%
                </span>
                <p className="text-xs text-slate-400 mt-1">Raw Model Fraud Probability</p>
              </div>
            </div>

            {/* Metrics Breakdown */}
            <div className="grid grid-cols-2 gap-3 p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-xs font-mono">
              <div>
                <span className="text-slate-500">Inference Latency:</span>
                <p className="text-slate-200 font-semibold">{result.inference_time_ms.toFixed(2)} ms</p>
              </div>
              <div>
                <span className="text-slate-500">Decision Threshold:</span>
                <p className="text-slate-200 font-semibold">{result.decision_threshold}</p>
              </div>
            </div>

            {/* SHAP Waterfall */}
            {result.top_shap_features && <ShapWaterfall features={result.top_shap_features} />}
          </div>
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-center p-8 space-y-3">
            <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 text-slate-600">
              <Zap className="w-8 h-8" />
            </div>
            <h4 className="text-sm font-semibold text-slate-300">Ready for Transaction Scoring</h4>
            <p className="text-xs text-slate-500">Enter transaction parameters and submit to view instant fraud probability and SHAP explanations.</p>
          </div>
        )}
      </div>
    </div>
  );
};
