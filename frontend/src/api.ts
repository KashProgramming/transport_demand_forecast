import axios from 'axios';
import type {
  AppConfig,
  BaseAnalysisRequest,
  DataInfo,
  EDAData,
  ForecastData,
  ForecastRequest,
  LoadSummary,
  ModelComparisonData,
  SpatialData,
  SpatialRequest,
} from './types';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const healthCheck = async (): Promise<{ status: string }> => {
  const response = await api.get('/health');
  return response.data;
};

export const getOptions = async (): Promise<AppConfig> => {
  const response = await api.get('/api/options');
  return response.data;
};

export const loadData = async (request: BaseAnalysisRequest): Promise<LoadSummary> => {
  const response = await api.post('/api/load', request);
  return response.data;
};

export const getEDA = async (request: BaseAnalysisRequest): Promise<EDAData> => {
  const response = await api.post('/api/eda', request);
  return response.data;
};

export const getForecasting = async (request: ForecastRequest): Promise<ForecastData> => {
  const response = await api.post('/api/forecasting', request);
  return response.data;
};

export const getModelComparison = async (request: BaseAnalysisRequest): Promise<ModelComparisonData> => {
  const response = await api.post('/api/model-comparison', request);
  return response.data;
};

export const getSpatial = async (request: SpatialRequest): Promise<SpatialData> => {
  const response = await api.post('/api/spatial', request);
  return response.data;
};

export const getDataInfo = async (request: BaseAnalysisRequest): Promise<DataInfo> => {
  const response = await api.post('/api/data-info', request);
  return response.data;
};
