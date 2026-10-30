import axios, { AxiosError } from 'axios';
import { ErrorResponse, HealthResponse } from '../types/api';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const checkHealth = async (): Promise<HealthResponse> => {
  const response = await apiClient.get<HealthResponse>('/health');
  return response.data;
};

export function parseApiError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const axiosErr = error as AxiosError<ErrorResponse>;
    if (axiosErr.response?.data?.detail) {
      return axiosErr.response.data.detail;
    }
    if (axiosErr.message === 'Network Error') {
      return 'Cannot connect to backend server at http://localhost:8000. Is FastAPI running?';
    }
    return axiosErr.message;
  }
  return String(error);
}
