import React, { useState } from 'react';
import {
  Zap,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Sparkles,
  RotateCcw,
  Sliders,
  ChevronDown,
  ChevronUp,
  ThumbsUp,
  ThumbsDown,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { predictTransaction, submitFeedback, PredictionResult } from '../api/client';
import { ShapWaterfall } from './ShapWaterfall';

interface SinglePredictFormProps {
  onScored?: () => void;
}

export const SinglePredictForm: React.FC<SinglePredictFormProps> = ({ onScored }) => {
  // Primary Form State (using strings for rock-solid input typing & deletion without NaN bugs)
  const [amount, setAmount] = useState<string>('1250.00');
  const [time, setTime] = useState<string>('406');
  const [v14, setV14] = useState<string>('-4.20');
  const [v10, setV10] = useState<string>('-2.80');
  const [v12, setV12] = useState<string>('-3.10');
  const [v4, setV4] = useState<string>('2.50');
  const [v17, setV17] = useState<string>('-2.10');
  const [v11, setV11] = useState<string>('1.80');

  // Advanced PCA 28 Features State
  const [allFeatures, setAllFeatures] = useState<Record<string, string>>(() => {
    const initial: Record<string, string> = {};
    for (let i = 1; i <= 28; i++) {
      initial[`v${i}`] = '0.00';
    }
    initial['v14'] = '-4.20';
    initial['v10'] = '-2.80';
    initial['v12'] = '-3.10';
    initial['v4'] = '2.50';
    initial['v17'] = '-2.10';
    initial['v11'] = '1.80';
    return initial;
  });

  const [showAdvanced, setShowAdvanced] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [feedbackSuccess, setFeedbackSuccess] = useState<string | null>(null);
  const [feedbackLoading, setFeedbackLoading] = useState<boolean>(false);

  // Safe float parsing helper to guarantee NO NaN or null values
  const safeFloat = (val: string | number | undefined, defaultVal = 0.0): number => {
    if (val === undefined || val === null || val === '') return defaultVal;
    const parsed = parseFloat(String(val).trim());
    return isNaN(parsed) ? defaultVal : parsed;
  };

  // Presets
  const setPreset = (type: 'legit' | 'fraud' | 'suspicious' | 'random') => {
    setErrorMsg(null);
    setFeedbackSuccess(null);

    if (type === 'legit') {
      setAmount('45.20');
      setTime('12500');
      setV14('0.25');
      setV10('0.15');
      setV12('0.18');
      setV4('-0.30');
      setV17('0.05');
      setV11('-0.20');

      const updated = { ...allFeatures };
      for (let i = 1; i <= 28; i++) {
        updated[`v${i}`] = (0.05 * (i % 2 === 0 ? 1 : -1)).toFixed(2);
      }
      updated['v14'] = '0.25';
      updated['v10'] = '0.15';
      updated['v12'] = '0.18';
      updated['v4'] = '-0.30';
      updated['v17'] = '0.05';
      updated['v11'] = '-0.20';
      setAllFeatures(updated);
    } else if (type === 'fraud') {
      setAmount('2800.50');
      setTime('406');
      setV14('-5.80');
      setV10('-3.90');
      setV12('-4.60');
      setV4('3.80');
      setV17('-4.10');
      setV11('3.20');

      const updated = { ...allFeatures };
      for (let i = 1; i <= 28; i++) {
        updated[`v${i}`] = (0.25 * (i % 3 === 0 ? -1 : 1)).toFixed(2);
      }
      updated['v14'] = '-5.80';
      updated['v10'] = '-3.90';
      updated['v12'] = '-4.60';
      updated['v4'] = '3.80';
      updated['v17'] = '-4.10';
      updated['v11'] = '3.20';
      setAllFeatures(updated);
    } else if (type === 'suspicious') {
      setAmount('1450.00');
      setTime('850');
      setV14('-2.50');
      setV10('-1.80');
      setV12('-1.90');
      setV4('1.80');
      setV17('-1.50');
      setV11('1.20');

      const updated = { ...allFeatures };
      for (let i = 1; i <= 28; i++) {
        updated[`v${i}`] = (0.1 * (i % 2 === 0 ? 1 : -1)).toFixed(2);
      }
      updated['v14'] = '-2.50';
      updated['v10'] = '-1.80';
      updated['v12'] = '-1.90';
      updated['v4'] = '1.80';
      updated['v17'] = '-1.50';
      updated['v11'] = '1.20';
      setAllFeatures(updated);
    } else if (type === 'random') {
      const isFraudSim = Math.random() > 0.5;
      const randAmt = isFraudSim ? (Math.random() * 3000 + 500).toFixed(2) : (Math.random() * 150 + 5).toFixed(2);
      const randTime = Math.floor(Math.random() * 86400).toString();
      const randV14 = (isFraudSim ? -Math.random() * 5 - 2 : Math.random() * 1.5 - 0.5).toFixed(2);
      const randV10 = (isFraudSim ? -Math.random() * 4 - 1.5 : Math.random() * 1.2 - 0.4).toFixed(2);
      const randV12 = (isFraudSim ? -Math.random() * 4 - 1.5 : Math.random() * 1.0 - 0.3).toFixed(2);
      const randV4 = (isFraudSim ? Math.random() * 4 + 1.0 : -Math.random() * 1.0).toFixed(2);
      const randV17 = (isFraudSim ? -Math.random() * 3.5 - 1.0 : Math.random() * 0.8).toFixed(2);
      const randV11 = (isFraudSim ? Math.random() * 3.0 + 1.0 : -Math.random() * 0.8).toFixed(2);

      setAmount(randAmt);
      setTime(randTime);
      setV14(randV14);
      setV10(randV10);
      setV12(randV12);
      setV4(randV4);
      setV17(randV17);
      setV11(randV11);

      const updated = { ...allFeatures };
      for (let i = 1; i <= 28; i++) {
        const noise = (Math.random() * 0.4 - 0.2).toFixed(2);
        updated[`v${i}`] = noise;
      }
      updated['v14'] = randV14;
      updated['v10'] = randV10;
      updated['v12'] = randV12;
      updated['v4'] = randV4;
      updated['v17'] = randV17;
      updated['v11'] = randV11;
      setAllFeatures(updated);
    }
  };

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg(null);
    setFeedbackSuccess(null);

    // Build payload with guaranteed numerical validation
    const parsedAmount = Math.max(0, safeFloat(amount, 100.0));
    const parsedTime = Math.max(0, safeFloat(time, 0.0));

    const txData: Record<string, number> = {
      time: parsedTime,
      amount: parsedAmount,
    };

    for (let i = 1; i <= 28; i++) {
      if (i === 14) txData['v14'] = safeFloat(v14, -4.2);
      else if (i === 10) txData['v10'] = safeFloat(v10, -2.8);
      else if (i === 12) txData['v12'] = safeFloat(v12, -3.1);
      else if (i === 4) txData['v4'] = safeFloat(v4, 2.5);
      else if (i === 17) txData['v17'] = safeFloat(v17, -2.1);
      else if (i === 11) txData['v11'] = safeFloat(v11, 1.8);
      else {
        txData[`v${i}`] = safeFloat(allFeatures[`v${i}`], 0.0);
      }
    }

    try {
      const res = await predictTransaction(txData);
      setResult(res);
      if (onScored) {
        onScored();
      }
    } catch (err: any) {
      console.error('Prediction failed', err);
      const detail =
        err?.response?.data?.detail ||
        err?.message ||
        'Failed to evaluate transaction. Please ensure the backend server is running.';
      setErrorMsg(typeof detail === 'string' ? detail : JSON.stringify(detail));
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (actualLabel: number) => {
    if (!result) return;
    setFeedbackLoading(true);
    try {
      await submitFeedback(
        result.prediction_id,
        actualLabel,
        actualLabel === 1 ? 'Analyst confirmed fraudulent pattern.' : 'Analyst confirmed legitimate transaction.'
      );
      setFeedbackSuccess(
        actualLabel === 1 ? 'Logged: Confirmed Fraud (Class 1)' : 'Logged: False Alarm / Legit (Class 0)'
      );
      if (onScored) onScored();
    } catch (err: any) {
      console.error('Feedback submission failed', err);
      setErrorMsg('Failed to submit analyst feedback.');
    } finally {
      setFeedbackLoading(false);
    }
  };

  const isHighRisk = result?.risk_band === 'High';
  const isMedRisk = result?.risk_band === 'Medium';
  const riskColor = isHighRisk ? 'danger' : isMedRisk ? 'warning' : 'success';

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.2fr) minmax(0, 1fr)', gap: 20 }}>
      {/* ── Form Card ── */}
      <div className="card" style={{ padding: 24, display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 18, flexWrap: 'wrap', gap: 10 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div className="section-icon" style={{ background: 'var(--accent-subtle)', color: 'var(--accent)', padding: 8, borderRadius: 8 }}>
              <Zap size={18} />
            </div>
            <div>
              <div style={{ fontWeight: 700, fontSize: 15, color: 'var(--text-primary)' }}>
                Single Transaction Scoring
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
                Real-time risk scoring via production Deep Neural Network & SHAP
              </div>
            </div>
          </div>

          {/* Preset Buttons */}
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            <button
              className="btn-preset-legit"
              type="button"
              onClick={() => setPreset('legit')}
              style={{ fontSize: 11, padding: '5px 10px', borderRadius: 6, fontWeight: 600, cursor: 'pointer' }}
            >
              🟢 Legit Preset
            </button>
            <button
              className="btn-preset-fraud"
              type="button"
              onClick={() => setPreset('fraud')}
              style={{ fontSize: 11, padding: '5px 10px', borderRadius: 6, fontWeight: 600, cursor: 'pointer' }}
            >
              🚨 Fraud Preset
            </button>
            <button
              type="button"
              onClick={() => setPreset('random')}
              style={{
                fontSize: 11,
                padding: '5px 10px',
                borderRadius: 6,
                background: 'var(--bg-card-alt)',
                border: '1px solid var(--border-subtle)',
                color: 'var(--text-primary)',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              🎲 Randomize
            </button>
          </div>
        </div>

        <hr className="divider" style={{ marginBottom: 18 }} />

        {/* Error Alert Box */}
        {errorMsg && (
          <div style={{
            background: 'var(--danger-subtle)',
            border: '1px solid var(--danger-border)',
            borderRadius: 8,
            padding: '12px 14px',
            marginBottom: 16,
            display: 'flex',
            alignItems: 'flex-start',
            gap: 10,
            color: 'var(--danger)'
          }}>
            <AlertCircle size={18} style={{ flexShrink: 0, marginTop: 2 }} />
            <div style={{ fontSize: 12, lineHeight: 1.5 }}>
              <strong>Evaluation Error:</strong> {errorMsg}
            </div>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handlePredict} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {/* Row 1: Amount & Time */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
            <div>
              <label className="form-label" style={{ fontWeight: 600, fontSize: 12, marginBottom: 6, display: 'block' }}>
                Transaction Amount ($)
              </label>
              <input
                className="form-input"
                type="number"
                step="any"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="e.g. 1250.00"
                required
              />
              <span style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4, display: 'block' }}>
                Monetary value in USD
              </span>
            </div>

            <div>
              <label className="form-label" style={{ fontWeight: 600, fontSize: 12, marginBottom: 6, display: 'block' }}>
                Time Elapsed (s)
              </label>
              <input
                className="form-input"
                type="number"
                step="any"
                value={time}
                onChange={(e) => setTime(e.target.value)}
                placeholder="e.g. 406"
                required
              />
              <span style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4, display: 'block' }}>
                Seconds since reference baseline
              </span>
            </div>
          </div>

          {/* Row 2: Top Fraud Indicator PCA Features */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
            <div>
              <label className="form-label" style={{ fontWeight: 600, fontSize: 12, marginBottom: 6, display: 'block' }}>
                Feature V14 <span style={{ color: 'var(--accent)', fontWeight: 500 }}>(#1 Fraud Risk Driver)</span>
              </label>
              <input
                className="form-input"
                type="number"
                step="any"
                value={v14}
                onChange={(e) => {
                  setV14(e.target.value);
                  setAllFeatures(prev => ({ ...prev, v14: e.target.value }));
                }}
                placeholder="e.g. -4.20"
                required
              />
              <span style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4, display: 'block' }}>
                Negative values indicate severe anomaly
              </span>
            </div>

            <div>
              <label className="form-label" style={{ fontWeight: 600, fontSize: 12, marginBottom: 6, display: 'block' }}>
                Feature V10 <span style={{ color: 'var(--accent)', fontWeight: 500 }}>(#2 Fraud Indicator)</span>
              </label>
              <input
                className="form-input"
                type="number"
                step="any"
                value={v10}
                onChange={(e) => {
                  setV10(e.target.value);
                  setAllFeatures(prev => ({ ...prev, v10: e.target.value }));
                }}
                placeholder="e.g. -2.80"
                required
              />
              <span style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4, display: 'block' }}>
                Account velocity & device metric
              </span>
            </div>
          </div>

          {/* Row 3: Secondary Features */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: 10 }}>
            <div>
              <label className="form-label" style={{ fontSize: 11, marginBottom: 4, display: 'block' }}>V12 (Merchant)</label>
              <input
                className="form-input"
                type="number"
                step="any"
                value={v12}
                onChange={(e) => {
                  setV12(e.target.value);
                  setAllFeatures(prev => ({ ...prev, v12: e.target.value }));
                }}
                style={{ fontSize: 11, padding: '6px 8px' }}
              />
            </div>
            <div>
              <label className="form-label" style={{ fontSize: 11, marginBottom: 4, display: 'block' }}>V4 (Velocity)</label>
              <input
                className="form-input"
                type="number"
                step="any"
                value={v4}
                onChange={(e) => {
                  setV4(e.target.value);
                  setAllFeatures(prev => ({ ...prev, v4: e.target.value }));
                }}
                style={{ fontSize: 11, padding: '6px 8px' }}
              />
            </div>
            <div>
              <label className="form-label" style={{ fontSize: 11, marginBottom: 4, display: 'block' }}>V17 (Pattern)</label>
              <input
                className="form-input"
                type="number"
                step="any"
                value={v17}
                onChange={(e) => {
                  setV17(e.target.value);
                  setAllFeatures(prev => ({ ...prev, v17: e.target.value }));
                }}
                style={{ fontSize: 11, padding: '6px 8px' }}
              />
            </div>
            <div>
              <label className="form-label" style={{ fontSize: 11, marginBottom: 4, display: 'block' }}>V11 (Geo)</label>
              <input
                className="form-input"
                type="number"
                step="any"
                value={v11}
                onChange={(e) => {
                  setV11(e.target.value);
                  setAllFeatures(prev => ({ ...prev, v11: e.target.value }));
                }}
                style={{ fontSize: 11, padding: '6px 8px' }}
              />
            </div>
          </div>

          {/* Collapsible Advanced PCA Features (V1..V28) */}
          <div>
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
                fontSize: 12,
                color: 'var(--accent)',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                padding: '4px 0',
                fontWeight: 600
              }}
            >
              <Sliders size={13} />
              <span>{showAdvanced ? 'Hide All 28 PCA Features' : 'Configure All 28 PCA Features (V1 to V28)'}</span>
              {showAdvanced ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>

            {showAdvanced && (
              <div style={{
                marginTop: 10,
                padding: 14,
                background: 'var(--bg-card-alt)',
                borderRadius: 8,
                border: '1px solid var(--border-muted)',
                maxHeight: 220,
                overflowY: 'auto'
              }}>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 8 }}>
                  {Array.from({ length: 28 }, (_, idx) => {
                    const featKey = `v${idx + 1}`;
                    return (
                      <div key={featKey}>
                        <label style={{ fontSize: 10, fontWeight: 600, color: 'var(--text-muted)', display: 'block' }}>
                          {featKey.toUpperCase()}
                        </label>
                        <input
                          className="form-input"
                          type="number"
                          step="any"
                          value={allFeatures[featKey] || '0.00'}
                          onChange={(e) => setAllFeatures(prev => ({ ...prev, [featKey]: e.target.value }))}
                          style={{ fontSize: 11, padding: '4px 6px' }}
                        />
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* Submit Button */}
          <button
            className="btn-primary"
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '12px 20px',
              fontSize: 14,
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 8,
              marginTop: 4,
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            {loading ? (
              <span>Scoring & Computing SHAP Attribution…</span>
            ) : (
              <>
                <Sparkles size={16} />
                <span>Evaluate Transaction Risk</span>
              </>
            )}
          </button>
        </form>
      </div>

      {/* ── Result Panel ── */}
      <div className="card" style={{ padding: 24, display: 'flex', flexDirection: 'column', minHeight: 480 }}>
        {result ? (
          <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: 16, height: '100%' }}>
            {/* Prediction Header */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span className="text-xs-caps" style={{ letterSpacing: 0.5, fontWeight: 700 }}>
                  Model Decision
                </span>
                <span className="mono" style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                  Tx #{result.transaction_id}
                </span>
              </div>
              <span className="mono" style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                Pred #{result.prediction_id}
              </span>
            </div>

            <hr className="divider" />

            {/* Risk Gauge Header */}
            <div style={{
              textAlign: 'center',
              padding: '16px 12px',
              background: isHighRisk ? 'var(--danger-subtle)' : isMedRisk ? 'var(--warning-subtle)' : 'var(--success-subtle)',
              border: `1px solid ${isHighRisk ? 'var(--danger-border)' : isMedRisk ? 'var(--warning-border)' : 'var(--success-border)'}`,
              borderRadius: 12
            }}>
              <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                {isHighRisk ? (
                  <ShieldAlert size={22} color="var(--danger)" />
                ) : isMedRisk ? (
                  <AlertTriangle size={22} color="var(--warning)" />
                ) : (
                  <ShieldCheck size={22} color="var(--success)" />
                )}

                <span style={{
                  fontSize: 13,
                  fontWeight: 800,
                  textTransform: 'uppercase',
                  letterSpacing: 0.8,
                  color: isHighRisk ? 'var(--danger)' : isMedRisk ? 'var(--warning)' : 'var(--success)'
                }}>
                  {result.risk_band} Risk {isHighRisk ? '— BLOCKED' : isMedRisk ? '— REVIEW REQUIRED' : '— APPROVED'}
                </span>
              </div>

              {/* Large Fraud Probability Percentage */}
              <div className="mono" style={{
                fontSize: 38,
                fontWeight: 800,
                color: isHighRisk ? 'var(--danger)' : isMedRisk ? 'var(--warning)' : 'var(--success)',
                lineHeight: 1
              }}>
                {(result.raw_probability * 100).toFixed(2)}%
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-secondary)', marginTop: 6, fontWeight: 500 }}>
                Raw Fraud Probability (Threshold: {(result.decision_threshold * 100).toFixed(1)}%)
              </div>

              {/* Animated Progress Bar */}
              <div style={{
                width: '100%',
                height: 8,
                background: 'rgba(0,0,0,0.08)',
                borderRadius: 999,
                marginTop: 12,
                overflow: 'hidden'
              }}>
                <div style={{
                  width: `${Math.min(100, Math.max(2, result.raw_probability * 100))}%`,
                  height: '100%',
                  background: isHighRisk
                    ? 'linear-gradient(90deg, #f87171, #dc2626)'
                    : isMedRisk
                    ? 'linear-gradient(90deg, #fbbf24, #d97706)'
                    : 'linear-gradient(90deg, #4ade80, #16a34a)',
                  transition: 'width 0.6s cubic-bezier(0.4, 0, 0.2, 1)'
                }} />
              </div>
            </div>

            {/* Performance Metrics Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10 }}>
              <div className="metric-block" style={{ padding: '8px 12px', background: 'var(--bg-card-alt)', borderRadius: 8 }}>
                <div className="text-xs-caps" style={{ fontSize: 9, color: 'var(--text-muted)' }}>Latency</div>
                <div className="mono" style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)', marginTop: 2 }}>
                  {result.inference_time_ms.toFixed(1)} ms
                </div>
              </div>

              <div className="metric-block" style={{ padding: '8px 12px', background: 'var(--bg-card-alt)', borderRadius: 8 }}>
                <div className="text-xs-caps" style={{ fontSize: 9, color: 'var(--text-muted)' }}>Decision</div>
                <div className="mono" style={{
                  fontSize: 12,
                  fontWeight: 700,
                  color: result.is_fraud ? 'var(--danger)' : 'var(--success)',
                  marginTop: 2
                }}>
                  {result.is_fraud ? 'FLAGGED FRAUD' : 'CLEARED LEGIT'}
                </div>
              </div>

              <div className="metric-block" style={{ padding: '8px 12px', background: 'var(--bg-card-alt)', borderRadius: 8 }}>
                <div className="text-xs-caps" style={{ fontSize: 9, color: 'var(--text-muted)' }}>Model Architecture</div>
                <div className="mono" style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-secondary)', marginTop: 2, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {result.model_version}
                </div>
              </div>
            </div>

            {/* SHAP Feature Waterfall */}
            {result.top_shap_features && result.top_shap_features.length > 0 && (
              <div style={{ borderTop: '1px solid var(--border-muted)', paddingTop: 12 }}>
                <ShapWaterfall features={result.top_shap_features} />
              </div>
            )}

            {/* Analyst Feedback Loop Actions */}
            <div style={{ borderTop: '1px solid var(--border-muted)', paddingTop: 12, marginTop: 'auto' }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-secondary)', marginBottom: 8 }}>
                Analyst Ground Truth Feedback:
              </div>

              {feedbackSuccess ? (
                <div style={{
                  background: 'var(--success-subtle)',
                  border: '1px solid var(--success-border)',
                  color: 'var(--success)',
                  padding: '8px 12px',
                  borderRadius: 6,
                  fontSize: 12,
                  fontWeight: 600,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6
                }}>
                  <CheckCircle2 size={14} />
                  <span>{feedbackSuccess}</span>
                </div>
              ) : (
                <div style={{ display: 'flex', gap: 8 }}>
                  <button
                    type="button"
                    disabled={feedbackLoading}
                    onClick={() => handleFeedback(0)}
                    style={{
                      flex: 1,
                      padding: '8px 10px',
                      background: 'var(--bg-card-alt)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 6,
                      fontSize: 11,
                      fontWeight: 600,
                      color: 'var(--text-primary)',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: 6
                    }}
                  >
                    <ThumbsUp size={13} color="var(--success)" />
                    <span>Verify Legit (Class 0)</span>
                  </button>

                  <button
                    type="button"
                    disabled={feedbackLoading}
                    onClick={() => handleFeedback(1)}
                    style={{
                      flex: 1,
                      padding: '8px 10px',
                      background: 'var(--danger-subtle)',
                      border: '1px solid var(--danger-border)',
                      borderRadius: 6,
                      fontSize: 11,
                      fontWeight: 600,
                      color: 'var(--danger)',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: 6
                    }}
                  >
                    <ThumbsDown size={13} color="var(--danger)" />
                    <span>Confirm Fraud (Class 1)</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        ) : (
          /* Empty / Initial State */
          <div style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            textAlign: 'center',
            gap: 14,
            padding: 32
          }}>
            <div style={{
              width: 56,
              height: 56,
              borderRadius: 16,
              background: 'var(--accent-subtle)',
              color: 'var(--accent)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Zap size={26} />
            </div>
            <div>
              <div style={{ fontWeight: 700, fontSize: 15, color: 'var(--text-primary)' }}>
                Awaiting Transaction Input
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', maxWidth: 260, lineHeight: 1.6, marginTop: 4 }}>
                Enter transaction parameters on the left or choose a preset to evaluate real-time fraud probability and SHAP attribution.
              </div>
            </div>

            <div style={{ display: 'flex', gap: 8, marginTop: 6 }}>
              <button
                type="button"
                className="btn-preset-legit"
                onClick={() => setPreset('legit')}
                style={{ fontSize: 11, padding: '6px 12px', borderRadius: 6, fontWeight: 600 }}
              >
                Test Legit Preset
              </button>
              <button
                type="button"
                className="btn-preset-fraud"
                onClick={() => setPreset('fraud')}
                style={{ fontSize: 11, padding: '6px 12px', borderRadius: 6, fontWeight: 600 }}
              >
                Test Fraud Preset
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
