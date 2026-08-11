import React, { useState } from 'react';
import { UploadCloud, FileText, CheckCircle, AlertTriangle } from 'lucide-react';
import { predictBatchCSV } from '../api/client';

export const BatchPredict: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState<any | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
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
    <div className="glass-card p-6 space-y-6">
      <div className="flex items-center space-x-3">
        <div className="p-2.5 rounded-xl bg-gradient-to-tr from-cyan-500/20 to-indigo-500/20 border border-cyan-500/30 text-cyan-400">
          <UploadCloud className="w-6 h-6" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-white">Batch Transaction CSV Scoring</h3>
          <p className="text-xs text-slate-400">Upload a CSV file containing transactions (Time, V1..V28, Amount) for high-throughput batch scoring</p>
        </div>
      </div>

      {/* File Dropzone */}
      <div className="border-2 border-dashed border-slate-800 hover:border-cyan-500/50 rounded-2xl p-8 text-center transition-all bg-slate-900/40">
        <input
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          className="hidden"
          id="csv-upload-input"
        />
        <label htmlFor="csv-upload-input" className="cursor-pointer flex flex-col items-center space-y-3">
          <FileText className="w-10 h-10 text-cyan-400" />
          <div>
            <span className="text-sm font-semibold text-slate-200">
              {file ? file.name : 'Click to select CSV file or drag and drop'}
            </span>
            <p className="text-xs text-slate-500 mt-1">Supports standard Kaggle creditcard.csv formatted files</p>
          </div>
        </label>

        {file && (
          <button
            onClick={handleUpload}
            disabled={loading}
            className="mt-5 px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-bold text-sm shadow-lg shadow-cyan-500/25 transition-all"
          >
            {loading ? 'Processing Batch...' : 'Process Batch Predictions'}
          </button>
        )}
      </div>

      {/* Summary Matrix */}
      {summary && (
        <div className="space-y-4 pt-4 border-t border-slate-800">
          <h4 className="text-sm font-bold text-white uppercase tracking-wider font-mono">Batch Processing Results</h4>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
              <span className="text-xs text-slate-400 font-mono">Total Processed</span>
              <p className="text-xl font-extrabold text-white mt-1">{summary.total_processed}</p>
            </div>
            <div className="p-4 rounded-xl bg-slate-900 border border-rose-500/30">
              <span className="text-xs text-rose-400 font-mono">Fraud Flagged</span>
              <p className="text-xl font-extrabold text-rose-400 mt-1">{summary.fraud_detected_count}</p>
            </div>
            <div className="p-4 rounded-xl bg-slate-900 border border-amber-500/30">
              <span className="text-xs text-amber-400 font-mono">High Risk</span>
              <p className="text-xl font-extrabold text-amber-400 mt-1">{summary.high_risk_count}</p>
            </div>
            <div className="p-4 rounded-xl bg-slate-900 border border-emerald-500/30">
              <span className="text-xs text-emerald-400 font-mono">Low Risk</span>
              <p className="text-xl font-extrabold text-emerald-400 mt-1">{summary.low_risk_count}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
