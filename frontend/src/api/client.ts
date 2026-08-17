import axios from 'axios';

// Dynamic API Base URL: Uses relative URL in production or window.location.origin
const getApiBaseUrl = () => {
  if (typeof window !== 'undefined') {
    const origin = window.location.origin;
    if (origin.includes(':5173')) {
      return 'http://localhost:8000/api/v1';
    }
    return `${origin}/api/v1`;
  }
  return '/api/v1';
};

export const apiClient = axios.create({
  baseURL: getApiBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000,
});

export interface SystemStats {
  total_transactions: number;
  total_fraud_detected: number;
  fraud_percentage: number;
  total_estimated_cost_saved_usd: number;
  risk_distribution: {
    Low: number;
    Medium: number;
    High: number;
  };
  model_performance: Record<string, any>;
}

export interface PredictionResult {
  prediction_id: number;
  transaction_id: number;
  raw_probability: number;
  is_fraud: boolean;
  risk_band: 'Low' | 'Medium' | 'High';
  decision_threshold: number;
  model_version: string;
  inference_time_ms: number;
  top_shap_features?: Array<{
    feature: string;
    value: number;
    shap_value: number;
    impact: string;
  }>;
  created_at: string;
}

export interface BatchPredictionItem {
  prediction_id: number;
  transaction_id: number;
  amount: number;
  time: number;
  raw_probability: number;
  is_fraud: boolean;
  risk_band: 'Low' | 'Medium' | 'High';
  decision_threshold: number;
  model_version: string;
  inference_time_ms: number;
  created_at: string;
}

export interface BatchPredictionSummaryResponse {
  total_processed: number;
  fraud_detected_count: number;
  high_risk_count: number;
  medium_risk_count: number;
  low_risk_count: number;
  total_amount_processed_usd: number;
  total_fraud_amount_usd: number;
  batch_inference_time_ms: number;
  predictions: BatchPredictionItem[];
}

export interface SimulatorStatus {
  is_running: boolean;
  interval_seconds: number;
  total_simulated_transactions: number;
  fraud_alerts_generated: number;
}

export const fetchSystemStats = async (): Promise<SystemStats> => {
  const response = await apiClient.get('/statistics');
  return response.data;
};

export const fetchTransactionHistory = async (limit = 50, offset = 0, risk_band?: string) => {
  const response = await apiClient.get('/history', {
    params: { limit, offset, risk_band },
  });
  return response.data;
};

export const predictTransaction = async (txData: Record<string, number>): Promise<PredictionResult> => {
  const response = await apiClient.post('/predict', txData);
  return response.data;
};

export const predictBatchCSV = async (file: File): Promise<BatchPredictionSummaryResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await apiClient.post('/batch_predict', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const fetchModelInfo = async () => {
  const response = await apiClient.get('/model-info');
  return response.data;
};

export const fetchFraudAlerts = async (status = 'New') => {
  const response = await apiClient.get('/alerts', { params: { status_filter: status } });
  return response.data;
};

export const submitFeedback = async (prediction_id: number, actual_label: number, notes?: string) => {
  const response = await apiClient.post('/feedback', {
    prediction_id,
    actual_label,
    analyst_notes: notes,
  });
  return response.data;
};

export const controlSimulator = async (action: 'start' | 'stop', interval = 2.0): Promise<SimulatorStatus> => {
  const endpoint = action === 'start' ? '/simulator/start' : '/simulator/stop';
  const response = await apiClient.post(endpoint, { action, interval_seconds: interval });
  return response.data;
};

export const fetchSimulatorStatus = async (): Promise<SimulatorStatus> => {
  const response = await apiClient.get('/simulator/status');
  return response.data;
};
