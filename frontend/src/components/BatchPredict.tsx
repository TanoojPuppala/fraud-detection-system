import React, { useState } from 'react';
import {
  UploadCloud,
  FileText,
  AlertOctagon,
  CheckCircle,
  AlertTriangle,
  Download,
  Search,
  Filter,
  Sparkles,
  RefreshCw,
  Clock,
  DollarSign,
  ChevronLeft,
  ChevronRight,
  ShieldAlert,
  ShieldCheck
} from 'lucide-react';
import { predictBatchCSV, BatchPredictionSummaryResponse, BatchPredictionItem } from '../api/client';

export const BatchPredict: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [summary, setSummary] = useState<BatchPredictionSummaryResponse | null>(null);

  // Table filtering & pagination state
  const [riskFilter, setRiskFilter] = useState<string>('All');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [currentPage, setCurrentPage] = useState<number>(1);
  const pageSize = 15;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setErrorMsg(null);
    }
  };

  const handleUpload = async (fileToUpload?: File) => {
    const targetFile = fileToUpload || file;
    if (!targetFile) return;
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await predictBatchCSV(targetFile);
      setSummary(res);
      setCurrentPage(1);
    } catch (err: any) {
      console.error('Batch predict failed', err);
      const detail =
        err?.response?.data?.detail ||
        err?.message ||
        'Batch CSV processing failed. Ensure the CSV contains "Amount", "Time", and PCA features (V1..V28).';
      setErrorMsg(typeof detail === 'string' ? detail : JSON.stringify(detail));
    } finally {
      setLoading(false);
    }
  };

  // Generate a test sample CSV in memory and run immediately
  const handleTestSampleBatch = () => {
    const headers = ['Time', ...Array.from({ length: 28 }, (_, i) => `V${i + 1}`), 'Amount'];
    const rows: string[] = [headers.join(',')];

    // Generate 30 realistic mixed transactions
    for (let i = 1; i <= 30; i++) {
      const isFraud = i % 5 === 0; // 6 fraud cases, 24 legit
      const time = (i * 360).toFixed(1);
      const amount = isFraud ? (Math.random() * 2500 + 450).toFixed(2) : (Math.random() * 120 + 8.5).toFixed(2);

      const vVals: string[] = [];
      for (let v = 1; v <= 28; v++) {
        if (isFraud) {
          if (v === 14) vVals.push((-Math.random() * 4 - 3).toFixed(3));
          else if (v === 10) vVals.push((-Math.random() * 3 - 2).toFixed(3));
          else if (v === 12) vVals.push((-Math.random() * 3 - 2).toFixed(3));
          else if (v === 4) vVals.push((Math.random() * 3 + 1.5).toFixed(3));
          else if (v === 17) vVals.push((-Math.random() * 3 - 1.5).toFixed(3));
          else if (v === 11) vVals.push((Math.random() * 2.5 + 1).toFixed(3));
          else vVals.push((Math.random() * 1.5 - 0.75).toFixed(3));
        } else {
          vVals.push((Math.random() * 0.4 - 0.2).toFixed(3));
        }
      }

      rows.push([time, ...vVals, amount].join(','));
    }

    const csvContent = rows.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const sampleFile = new File([blob], 'sample_creditcard_batch_30.csv', { type: 'text/csv' });
    setFile(sampleFile);
    handleUpload(sampleFile);
  };

  // Download Sample Template
  const handleDownloadTemplate = () => {
    const headers = ['Time', ...Array.from({ length: 28 }, (_, i) => `V${i + 1}`), 'Amount'];
    const sampleRow = ['406.0', ...Array.from({ length: 28 }, () => '0.05'), '1250.00'];
    const csvContent = [headers.join(','), sampleRow.join(',')].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'fraud_detection_batch_template.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  // Export Scored Results to CSV
  const handleExportResults = () => {
    if (!summary || !summary.predictions || summary.predictions.length === 0) return;

    const headers = ['Prediction_ID', 'Transaction_ID', 'Amount_USD', 'Fraud_Probability', 'Risk_Band', 'Outcome', 'Inference_Latency_MS', 'Timestamp'];
    const rows = summary.predictions.map((p) => [
      p.prediction_id,
      p.transaction_id,
      p.amount.toFixed(2),
      (p.raw_probability * 100).toFixed(4) + '%',
      p.risk_band,
      p.is_fraud ? 'FRAUD' : 'LEGIT',
      p.inference_time_ms.toFixed(2),
      p.created_at
    ]);

    const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `scored_batch_results_${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Filtered Predictions for Table
  const allPredictions: BatchPredictionItem[] = summary?.predictions || [];
  const filteredPredictions = allPredictions.filter((p) => {
    // Risk Filter
    if (riskFilter === 'FraudOnly' && !p.is_fraud) return false;
    if (riskFilter === 'High' && p.risk_band !== 'High') return false;
    if (riskFilter === 'Medium' && p.risk_band !== 'Medium') return false;
    if (riskFilter === 'Low' && p.risk_band !== 'Low') return false;

    // Search Query (ID or Amount)
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      const idMatch = p.transaction_id.toString().includes(q) || p.prediction_id.toString().includes(q);
      const amtMatch = p.amount.toString().includes(q);
      if (!idMatch && !amtMatch) return false;
    }

    return true;
  });

  // Pagination calculation
  const totalPages = Math.max(1, Math.ceil(filteredPredictions.length / pageSize));
  const displayedPredictions = filteredPredictions.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* ── Top Upload & Control Card ── */}
      <div className="card" style={{ padding: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20, flexWrap: 'wrap', gap: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div className="section-icon" style={{ background: 'var(--accent-subtle)', color: 'var(--accent)', padding: 8, borderRadius: 8 }}>
              <UploadCloud size={18} />
            </div>
            <div>
              <div style={{ fontWeight: 700, fontSize: 15, color: 'var(--text-primary)' }}>
                Batch CSV Transaction Scoring
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
                High-throughput vectorized inference across transaction datasets via PyTorch Deep Learning
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <button
              type="button"
              onClick={handleTestSampleBatch}
              disabled={loading}
              style={{
                fontSize: 12,
                padding: '6px 12px',
                borderRadius: 6,
                background: 'var(--accent-subtle)',
                color: 'var(--accent)',
                border: '1px solid var(--accent-border)',
                fontWeight: 600,
                cursor: loading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 6
              }}
            >
              <Sparkles size={14} />
              <span>⚡ Generate & Test Sample Batch (30 Txns)</span>
            </button>

            <button
              type="button"
              onClick={handleDownloadTemplate}
              style={{
                fontSize: 12,
                padding: '6px 12px',
                borderRadius: 6,
                background: 'var(--bg-card-alt)',
                color: 'var(--text-primary)',
                border: '1px solid var(--border-subtle)',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 6
              }}
            >
              <Download size={14} />
              <span>Download CSV Template</span>
            </button>
          </div>
        </div>

        <hr className="divider" style={{ marginBottom: 20 }} />

        {/* Error Box */}
        {errorMsg && (
          <div style={{
            background: 'var(--danger-subtle)',
            border: '1px solid var(--danger-border)',
            borderRadius: 8,
            padding: '12px 14px',
            marginBottom: 16,
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            color: 'var(--danger)',
            fontSize: 13
          }}>
            <AlertOctagon size={16} />
            <span><strong>Batch Scoring Error:</strong> {errorMsg}</span>
          </div>
        )}

        {/* Dropzone Container */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: 16, alignItems: 'center' }}>
          <label
            htmlFor="csv-upload-input"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 16,
              padding: '24px 20px',
              border: '1.5px dashed var(--border-subtle)',
              borderRadius: 10,
              cursor: 'pointer',
              background: file ? 'var(--accent-subtle)' : 'var(--bg-app)',
              borderColor: file ? 'var(--accent-border)' : 'var(--border-subtle)',
              transition: 'border-color 0.2s, background 0.2s'
            }}
          >
            <input
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              style={{ display: 'none' }}
              id="csv-upload-input"
            />
            <div style={{
              width: 44,
              height: 44,
              borderRadius: 10,
              background: 'var(--bg-surface)',
              border: '1px solid var(--border-muted)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--accent)'
            }}>
              <FileText size={22} />
            </div>
            <div>
              <div style={{ fontWeight: 600, fontSize: 13, color: 'var(--text-primary)' }}>
                {file ? file.name : 'Click to select CSV file or drag & drop'}
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                {file ? `${(file.size / 1024).toFixed(1)} KB · Ready to evaluate` : 'Supports standard Credit Card datasets (Time, Amount, V1..V28)'}
              </div>
            </div>
          </label>

          <button
            type="button"
            onClick={() => handleUpload()}
            disabled={!file || loading}
            className="btn-primary"
            style={{
              height: '100%',
              padding: '0 24px',
              minHeight: 52,
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              fontSize: 14,
              fontWeight: 700,
              cursor: (!file || loading) ? 'not-allowed' : 'pointer'
            }}
          >
            {loading ? (
              <>
                <RefreshCw size={16} className="animate-spin" />
                <span>Processing Batch…</span>
              </>
            ) : (
              <>
                <Sparkles size={16} />
                <span>Run Batch Scoring</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* ── Summary & Results Section ── */}
      {summary && (
        <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* Summary KPI Cards Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 12 }}>
            <div className="card" style={{ padding: '16px', background: 'var(--bg-card)' }}>
              <div className="text-xs-caps" style={{ fontSize: 9, marginBottom: 6, color: 'var(--text-muted)' }}>Total Evaluated</div>
              <div className="mono" style={{ fontSize: 24, fontWeight: 800, color: 'var(--text-primary)' }}>
                {summary.total_processed}
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>
                ${summary.total_amount_processed_usd.toLocaleString('en-US', { minimumFractionDigits: 2 })} vol
              </div>
            </div>

            <div className="card" style={{ padding: '16px', background: 'var(--danger-subtle)', borderColor: 'var(--danger-border)' }}>
              <div className="text-xs-caps" style={{ fontSize: 9, marginBottom: 6, color: 'var(--danger)' }}>Fraud Flagged</div>
              <div className="mono" style={{ fontSize: 24, fontWeight: 800, color: 'var(--danger)' }}>
                {summary.fraud_detected_count}
              </div>
              <div style={{ fontSize: 11, color: 'var(--danger)', fontWeight: 600, marginTop: 4 }}>
                {((summary.fraud_detected_count / (summary.total_processed || 1)) * 100).toFixed(1)}% fraud rate
              </div>
            </div>

            <div className="card" style={{ padding: '16px', background: 'var(--danger-subtle)', borderColor: 'var(--danger-border)' }}>
              <div className="text-xs-caps" style={{ fontSize: 9, marginBottom: 6, color: 'var(--danger)' }}>High Risk Alerts</div>
              <div className="mono" style={{ fontSize: 24, fontWeight: 800, color: 'var(--danger)' }}>
                {summary.high_risk_count}
              </div>
              <div style={{ fontSize: 11, color: 'var(--danger)', marginTop: 4 }}>
                ${summary.total_fraud_amount_usd.toLocaleString('en-US', { minimumFractionDigits: 2 })} intercepted
              </div>
            </div>

            <div className="card" style={{ padding: '16px', background: 'var(--warning-subtle)', borderColor: 'var(--warning-border)' }}>
              <div className="text-xs-caps" style={{ fontSize: 9, marginBottom: 6, color: 'var(--warning)' }}>Medium Risk</div>
              <div className="mono" style={{ fontSize: 24, fontWeight: 800, color: 'var(--warning)' }}>
                {summary.medium_risk_count}
              </div>
              <div style={{ fontSize: 11, color: 'var(--warning)', marginTop: 4 }}>
                Manual review queue
              </div>
            </div>

            <div className="card" style={{ padding: '16px', background: 'var(--success-subtle)', borderColor: 'var(--success-border)' }}>
              <div className="text-xs-caps" style={{ fontSize: 9, marginBottom: 6, color: 'var(--success)' }}>Low Risk (Cleared)</div>
              <div className="mono" style={{ fontSize: 24, fontWeight: 800, color: 'var(--success)' }}>
                {summary.low_risk_count}
              </div>
              <div style={{ fontSize: 11, color: 'var(--success)', marginTop: 4 }}>
                {summary.batch_inference_time_ms.toFixed(1)} ms total time
              </div>
            </div>
          </div>

          {/* ── Scored Batch Results Table Card (Rendered Directly Below) ── */}
          <div className="card" style={{ padding: 24 }}>
            {/* Table Header & Action Controls */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 18, flexWrap: 'wrap', gap: 12 }}>
              <div>
                <div style={{ fontWeight: 700, fontSize: 15, color: 'var(--text-primary)' }}>
                  Scored Batch Records ({filteredPredictions.length} Transactions)
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                  Individual risk bands and inference probabilities for all submitted records
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
                {/* Search Box */}
                <div style={{ position: 'relative' }}>
                  <Search size={13} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                  <input
                    type="text"
                    placeholder="Search Tx ID or Amount..."
                    value={searchQuery}
                    onChange={(e) => {
                      setSearchQuery(e.target.value);
                      setCurrentPage(1);
                    }}
                    style={{
                      padding: '6px 12px 6px 28px',
                      fontSize: 12,
                      borderRadius: 6,
                      border: '1px solid var(--border-subtle)',
                      background: 'var(--bg-input)',
                      color: 'var(--text-primary)',
                      outline: 'none',
                      fontFamily: 'JetBrains Mono, monospace'
                    }}
                  />
                </div>

                {/* Risk Filter Select */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <Filter size={13} color="var(--text-muted)" />
                  <select
                    className="form-select"
                    value={riskFilter}
                    onChange={(e) => {
                      setRiskFilter(e.target.value);
                      setCurrentPage(1);
                    }}
                    style={{ fontSize: 11, padding: '5px 28px 5px 10px' }}
                  >
                    <option value="All">All Risk Bands ({allPredictions.length})</option>
                    <option value="FraudOnly">🚨 Fraud Flagged Only ({summary.fraud_detected_count})</option>
                    <option value="High">🔴 High Risk ({summary.high_risk_count})</option>
                    <option value="Medium">🟡 Medium Risk ({summary.medium_risk_count})</option>
                    <option value="Low">🟢 Low Risk ({summary.low_risk_count})</option>
                  </select>
                </div>

                {/* Export Scored CSV Button */}
                <button
                  type="button"
                  onClick={handleExportResults}
                  style={{
                    fontSize: 11,
                    padding: '6px 12px',
                    borderRadius: 6,
                    background: 'var(--accent)',
                    color: '#ffffff',
                    border: 'none',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 6
                  }}
                >
                  <Download size={13} />
                  <span>Export Scored CSV</span>
                </button>
              </div>
            </div>

            <hr className="divider" style={{ marginBottom: 0 }} />

            {/* Scored Data Table */}
            <div style={{ overflowX: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Pred ID</th>
                    <th>Tx ID</th>
                    <th>Amount ($)</th>
                    <th>Fraud Probability</th>
                    <th>Risk Band</th>
                    <th>Model Decision</th>
                    <th>Latency</th>
                    <th>Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {displayedPredictions.length === 0 ? (
                    <tr>
                      <td colSpan={9} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '36px 0' }}>
                        No transactions matched the selected filter.
                      </td>
                    </tr>
                  ) : (
                    displayedPredictions.map((row, index) => {
                      const isHigh = row.risk_band === 'High';
                      const isMed = row.risk_band === 'Medium';
                      const rowIndex = (currentPage - 1) * pageSize + index + 1;

                      return (
                        <tr key={row.prediction_id} style={{ background: row.is_fraud ? 'rgba(254, 242, 242, 0.5)' : undefined }}>
                          <td style={{ color: 'var(--text-muted)', fontSize: 11 }}>{rowIndex}</td>
                          <td className="mono" style={{ fontSize: 11, color: 'var(--text-muted)' }}>#{row.prediction_id}</td>
                          <td className="mono" style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-primary)' }}>#{row.transaction_id}</td>
                          <td className="mono" style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-primary)' }}>
                            ${row.amount.toFixed(2)}
                          </td>
                          <td>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                              <span className="mono" style={{
                                fontSize: 12,
                                fontWeight: 700,
                                color: isHigh ? 'var(--danger)' : isMed ? 'var(--warning)' : 'var(--success)'
                              }}>
                                {(row.raw_probability * 100).toFixed(2)}%
                              </span>
                              <div style={{ width: 45, height: 5, background: 'rgba(0,0,0,0.06)', borderRadius: 99, overflow: 'hidden' }}>
                                <div style={{
                                  width: `${Math.min(100, Math.max(4, row.raw_probability * 100))}%`,
                                  height: '100%',
                                  background: isHigh ? '#dc2626' : isMed ? '#d97706' : '#16a34a'
                                }} />
                              </div>
                            </div>
                          </td>
                          <td>
                            <span className={`badge ${isHigh ? 'badge-high' : isMed ? 'badge-med' : 'badge-low'}`}>
                              {row.risk_band}
                            </span>
                          </td>
                          <td>
                            {row.is_fraud ? (
                              <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5, color: '#dc2626', fontWeight: 700, fontSize: 11 }}>
                                <ShieldAlert size={13} /> FRAUD FLAGGED
                              </span>
                            ) : (
                              <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5, color: '#16a34a', fontWeight: 600, fontSize: 11 }}>
                                <ShieldCheck size={13} /> APPROVED
                              </span>
                            )}
                          </td>
                          <td className="mono" style={{ fontSize: 11, color: 'var(--text-secondary)' }}>
                            {row.inference_time_ms.toFixed(2)} ms
                          </td>
                          <td style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                            {new Date(row.created_at).toLocaleTimeString()}
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 16, paddingTop: 12, borderTop: '1px solid var(--border-muted)' }}>
                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                  Showing {(currentPage - 1) * pageSize + 1} to {Math.min(currentPage * pageSize, filteredPredictions.length)} of {filteredPredictions.length} records
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <button
                    type="button"
                    disabled={currentPage === 1}
                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                    style={{
                      padding: '4px 8px',
                      fontSize: 11,
                      borderRadius: 4,
                      border: '1px solid var(--border-subtle)',
                      background: 'var(--bg-surface)',
                      cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 4
                    }}
                  >
                    <ChevronLeft size={13} />
                    <span>Previous</span>
                  </button>

                  <span className="mono" style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-primary)', padding: '0 4px' }}>
                    Page {currentPage} of {totalPages}
                  </span>

                  <button
                    type="button"
                    disabled={currentPage === totalPages}
                    onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                    style={{
                      padding: '4px 8px',
                      fontSize: 11,
                      borderRadius: 4,
                      border: '1px solid var(--border-subtle)',
                      background: 'var(--bg-surface)',
                      cursor: currentPage === totalPages ? 'not-allowed' : 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 4
                    }}
                  >
                    <span>Next</span>
                    <ChevronRight size={13} />
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
