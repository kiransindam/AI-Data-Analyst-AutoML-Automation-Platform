// frontend/src/services/api.ts
import axios, { AxiosInstance, AxiosResponse } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: { 'Content-Type': 'application/json' },
    });

    // Request interceptor for auth token
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Try refresh token
          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
            try {
              const { data } = await axios.post(`${API_BASE_URL}/auth/refresh`, {
                refresh_token: refreshToken,
              });
              localStorage.setItem('access_token', data.access_token);
              error.config.headers.Authorization = `Bearer ${data.access_token}`;
              return this.client(error.config);
            } catch {
              localStorage.clear();
              window.location.href = '/login';
            }
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth
  async login(email: string, password: string) {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    return this.client.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  }

  async register(data: { email: string; username: string; password: string }) {
    return this.client.post('/auth/register', data);
  }

  // Upload
  async uploadFile(file: File, description?: string) {
    const formData = new FormData();
    formData.append('file', file);
    if (description) formData.append('description', description);
    return this.client.post('/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  }

  async getDatasetPreview(datasetId: string) {
    return this.client.get(`/upload/${datasetId}/preview`);
  }

  async listDatasets() {
    return this.client.get('/upload/');
  }

  // Analysis
  async startAnalysis(data: { dataset_id: string; project_name?: string; config?: any }) {
    return this.client.post('/analysis/start', data);
  }

  async getAnalysisStatus(projectId: string) {
    return this.client.get(`/analysis/${projectId}/status`);
  }

  async getEDAReport(projectId: string) {
    return this.client.get(`/analysis/${projectId}/eda`);
  }

  async getInsights(projectId: string) {
    return this.client.get(`/analysis/${projectId}/insights`);
  }

  // ML
  async trainModel(data: {
    project_id: string;
    target_column: string;
    problem_type?: string;
    algorithms?: string[];
    tune_hyperparams?: boolean;
  }) {
    return this.client.post('/ml/train', data);
  }

  async getModels(projectId: string) {
    return this.client.get(`/ml/${projectId}/models`);
  }

  async compareModels(projectId: string) {
    return this.client.get(`/ml/${projectId}/comparison`);
  }

  // Predictions
  async predict(data: { model_id: string; input_data: Record<string, any> }) {
    return this.client.post('/predict/', data);
  }

  // Reports
  async generateReport(projectId: string, format: string) {
    return this.client.post(`/reports/generate`, { project_id: projectId, format });
  }

  async downloadReport(reportId: string) {
    return this.client.get(`/reports/${reportId}/download`, { responseType: 'blob' });
  }
}

export const api = new ApiService();
