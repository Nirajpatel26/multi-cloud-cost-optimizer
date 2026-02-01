// API service for backend communication
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Health Check
export const checkHealth = async () => {
  const response = await apiClient.get('/health');
  return response.data;
};

// Cost APIs
export const getCosts = async (filters = {}) => {
  const response = await apiClient.get('/aws/costs', { params: filters });
  return response.data;
};

export const getCostsSummary = async (filters = {}) => {
  const response = await apiClient.get('/aws/costs/summary', { params: filters });
  return response.data;
};

// Resource APIs
export const scanResources = async (data) => {
  const response = await apiClient.post('/aws/resources/scan', data);
  return response.data;
};

export const getResources = async (filters = {}) => {
  const response = await apiClient.get('/aws/resources', { params: filters });
  return response.data;
};

// Recommendation APIs
export const getRecommendations = async (filters = {}) => {
  const response = await apiClient.get('/aws/recommendations', { params: filters });
  return response.data;
};

export const getIdleInstances = async (filters = {}) => {
  const response = await apiClient.get('/aws/recommendations/idle-instances', { params: filters });
  return response.data;
};

export const getUnattachedVolumes = async (filters = {}) => {
  const response = await apiClient.get('/aws/recommendations/unattached-volumes', { params: filters });
  return response.data;
};

// Analytics APIs
export const getSavings = async () => {
  const response = await apiClient.get('/aws/savings');
  return response.data;
};

export const runAnalysis = async (data) => {
  const response = await apiClient.post('/aws/analyze', data);
  return response.data;
};

export default apiClient;
