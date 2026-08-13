import React, { useState } from 'react';
import { Zap, ShieldAlert, CheckCircle2, Sparkles } from 'lucide-react';
import { predictTransaction, PredictionResult } from '../api/client';
import { ShapWaterfall } from './ShapWaterfall';

export const SinglePredictForm: React.FC = () => {
  const [amount, setAmount] = useState<number>(1250.0);
  const [time,   setTime]   = useState<number>(406.0);
  const [v14,    setV14]    = useState<number>(-4.2);
  const [v10,    setV10]    = useState<number>(-2.8);
  const [loading, setLoading] = useState<boolean>(false);
  const [result,  setResult]  = useState<PredictionResult | null>(null);

  const setPreset = (type: 'fraud' | 'legit') => {
    if (type === 'fraud') {
      setAmount(2800.5); setTime(406.0); setV14(-5.8); setV10(-3.9);
    } else {
      setAmount(45.2); setTime(12500.0); setV14(0.2); setV10(0.1);
    }
  };

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    const txData: Record<string, number> = { time, amount };
    for (let i = 1; i <= 28; i++) {
      if (i === 14) txData['v14'] = v14;
      else if (i === 10) txData['v10'] = v10;
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

  const riskColor =
    result?.risk_band === 'High'   ? 'danger'  :
    result?.risk_band === 'Medium' ? 'warning' : 'success';

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '7fr 5fr', gap: 16 }}>

      {/* ── Form ── */}
      <div className="card" style={{ padding: 24 }}>
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 22 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div className="section-icon">
              <Zap size={16} />
            </div>
            <div>
              <div style={{ fontWeight: 700, fontSize: 14, color: 'var(--text-primary)' }}>
                Single Transaction Scoring
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 1 }}>
                Evaluate real-time fraud risk via production model
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: 8 }}>
            <button className="btn-preset-legit" type="button" onClick={() => setPreset('legit')}>
              Legit Preset
            </button>
            <button className="btn-preset-fraud" type="button" onClick={() => setPreset('fraud')}>
              Fraud Preset
            </button>
          </div>
        </div>

        <hr className="divider" style={{ marginBottom: 20 }} />

        {/* Form Fields */}
        <form onSubmit={handlePredict}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
            <div>
              <label className="form-label">Amount ($)</label>
              <input
                className="form-input"
                type="number"
                step="0.01"
                value={amount}
                onChange={(e) => setAmount(parseFloat(e.target.value))}
                placeholder="e.g. 1250.00"
              />
            </div>
            <div>
              <label className="form-label">Time Elapsed (s)</label>
              <input
                className="form-input"
                type="number"
                step="1"
                value={time}
                onChange={(e) => setTime(parseFloat(e.target.value))}
                placeholder="e.g. 406"
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 22 }}>
            <div>
              <label className="form-label">
                Feature V14 <span style={{ color: '#93c5fd', fontWeight: 400, textTransform: 'none', letterSpacing: 0 }}>(Top fraud indicator)</span>
              </label>
              <input
                className="form-input"
                type="number"
                step="0.1"
                value={v14}
                onChange={(e) => setV14(parseFloat(e.target.value))}
                placeholder="e.g. -4.2"
              />
            </div>
            <div>
              <label className="form-label">
                Feature V10 <span style={{ color: '#93c5fd', fontWeight: 400, textTransform: 'none', letterSpacing: 0 }}>(2nd indicator)</span>
              </label>
              <input
                className="form-input"
                type="number"
                step="0.1"
                value={v10}
                onChange={(e) => setV10(parseFloat(e.target.value))}
                placeholder="e.g. -2.8"
              />
            </div>
          </div>

          <button className="btn-primary" type="submit" disabled={loading} style={{ width: '100%', padding: '11px 20px' }}>
            {loading ? (
              <span>Evaluating risk band…</span>
            ) : (
              <>
                <Sparkles size={14} />
                <span>Evaluate Transaction Risk</span>
              </>
            )}
          </button>
        </form>
      </div>

      {/* ── Result Panel ── */}
      <div className="card" style={{ padding: 24, display: 'flex', flexDirection: 'column' }}>
        {result ? (
          <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: 18, height: '100%' }}>
            {/* Prediction ID header */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span className="text-xs-caps">Prediction Outcome</span>
              <span className="mono" style={{ fontSize: 10, color: 'var(--text-muted)' }}>
                ID #{result.prediction_id}
              </span>
            </div>

            <hr className="divider" />

            {/* Risk band */}
            <div style={{ textAlign: 'center', padding: '12px 0' }}>
              <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
                {result.risk_band === 'High'
                  ? <ShieldAlert size={18} color="#f87171" />
                  : <CheckCircle2 size={18} color="#34d399" />
                }
                <span className={`badge badge-${riskColor === 'danger' ? 'high' : riskColor === 'warning' ? 'med' : 'low'}`}
                  style={{ fontSize: 12, padding: '4px 12px' }}>
                  {result.risk_band} Risk
                </span>
              </div>

              <div className="mono" style={{ fontSize: 34, fontWeight: 700, color: 'var(--text-primary)', marginTop: 12, lineHeight: 1 }}>
                {(result.raw_probability * 100).toFixed(2)}%
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 6 }}>
                Raw fraud probability
              </div>
            </div>

            {/* Metrics */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
              <div className="metric-block">
                <div className="text-xs-caps" style={{ marginBottom: 4 }}>Latency</div>
                <div className="mono" style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>
                  {result.inference_time_ms.toFixed(2)} ms
                </div>
              </div>
              <div className="metric-block">
                <div className="text-xs-caps" style={{ marginBottom: 4 }}>Threshold</div>
                <div className="mono" style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>
                  {result.decision_threshold}
                </div>
              </div>
            </div>

            {/* SHAP */}
            {result.top_shap_features && <ShapWaterfall features={result.top_shap_features} />}
          </div>
        ) : (
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', gap: 12, padding: 32 }}>
            <div className="section-icon muted" style={{ width: 48, height: 48, borderRadius: 12 }}>
              <Zap size={20} />
            </div>
            <div style={{ fontWeight: 600, fontSize: 13, color: 'var(--text-secondary)' }}>
              Ready for Transaction Scoring
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', maxWidth: 220, lineHeight: 1.6 }}>
              Enter parameters and submit to view fraud probability and SHAP explanations.
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
