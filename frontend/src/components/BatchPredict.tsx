import React, { useState } from 'react';
import { UploadCloud, FileText } from 'lucide-react';
import { predictBatchCSV } from '../api/client';

export const BatchPredict: React.FC = () => {
  const [file,    setFile]    = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState<any | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const res = await predictBatchCSV(file);
      setSummary(res);
    } catch (err) {
      console.error('Batch predict failed', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card" style={{ padding: 24 }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 22 }}>
        <div className="section-icon">
          <UploadCloud size={16} />
        </div>
        <div>
          <div style={{ fontWeight: 700, fontSize: 14, color: 'var(--text-primary)' }}>Batch CSV Scoring</div>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 1 }}>
            Upload CSV (Time, V1..V28, Amount) for high-throughput batch scoring
          </div>
        </div>
      </div>

      <hr className="divider" style={{ marginBottom: 20 }} />

      {/* Dropzone */}
      <label
        htmlFor="csv-upload-input"
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 14,
          padding: '40px 24px',
          border: '1.5px dashed var(--border-subtle)',
          borderRadius: 12,
          cursor: 'pointer',
          background: 'var(--bg-app)',
          transition: 'border-color 0.2s, background 0.2s',
          textAlign: 'center',
        }}
        onMouseEnter={(e) => {
          (e.currentTarget as HTMLLabelElement).style.borderColor = 'var(--accent-border)';
          (e.currentTarget as HTMLLabelElement).style.background = 'var(--accent-subtle)';
        }}
        onMouseLeave={(e) => {
          (e.currentTarget as HTMLLabelElement).style.borderColor = 'var(--border-subtle)';
          (e.currentTarget as HTMLLabelElement).style.background = 'var(--bg-app)';
        }}
      >
        <input
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          style={{ display: 'none' }}
          id="csv-upload-input"
        />
        <div className="section-icon" style={{ width: 48, height: 48, borderRadius: 12 }}>
          <FileText size={20} />
        </div>
        <div>
          <div style={{ fontWeight: 600, fontSize: 13, color: 'var(--text-primary)' }}>
            {file ? file.name : 'Click to select CSV file'}
          </div>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>
            Supports Kaggle creditcard.csv format
          </div>
        </div>

        {file && (
          <button
            type="button"
            onClick={(e) => { e.preventDefault(); handleUpload(); }}
            disabled={loading}
            className="btn-primary"
            style={{ marginTop: 4 }}
          >
            {loading ? 'Processing…' : 'Run Batch Predictions'}
          </button>
        )}
      </label>

      {/* Results */}
      {summary && (
        <div className="fade-in" style={{ marginTop: 24 }}>
          <hr className="divider" style={{ marginBottom: 18 }} />
          <div className="text-xs-caps" style={{ marginBottom: 14 }}>Batch Results</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
            {[
              { label: 'Total Processed', value: summary.total_processed,       color: 'var(--text-primary)', border: 'var(--border-muted)',  bg: 'var(--bg-app)' },
              { label: 'Fraud Flagged',   value: summary.fraud_detected_count,  color: '#dc2626',             border: 'var(--danger-border)',  bg: 'var(--danger-subtle)' },
              { label: 'High Risk',       value: summary.high_risk_count,       color: '#d97706',             border: 'var(--warning-border)', bg: 'var(--warning-subtle)' },
              { label: 'Low Risk',        value: summary.low_risk_count,        color: '#16a34a',             border: 'var(--success-border)', bg: 'var(--success-subtle)' },
            ].map((item, i) => (
              <div
                key={i}
                className="metric-block"
                style={{ borderColor: item.border, background: item.bg }}
              >
                <div className="text-xs-caps" style={{ marginBottom: 8 }}>{item.label}</div>
                <div className="mono" style={{ fontSize: 22, fontWeight: 700, color: item.color }}>{item.value}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
