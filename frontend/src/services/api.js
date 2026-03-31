// API service for backend communication
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Every call appends ?data_mode=mock or ?data_mode=real
const withMode = (params = {}, mode = 'mock') => ({ ...params, data_mode: mode });

// Health Check
export const checkHealth = async () => {
  const response = await apiClient.get('/health');
  return response.data;
};

// ── AWS Cost APIs ──────────────────────────────────────────────────────────
export const getCosts = async (filters = {}, mode = 'mock') => {
  const response = await apiClient.get('/aws/costs', { params: withMode(filters, mode) });
  return response.data;
};

export const getCostsSummary = async (filters = {}, mode = 'mock') => {
  const response = await apiClient.get('/aws/costs/summary', { params: withMode(filters, mode) });
  return response.data;
};

// ── AWS Resource APIs ──────────────────────────────────────────────────────
export const scanResources = async (data, mode = 'mock') => {
  const response = await apiClient.post(`/aws/resources/scan?data_mode=${mode}`, data);
  return response.data;
};

export const getResources = async (filters = {}, mode = 'mock') => {
  const response = await apiClient.get('/aws/resources', { params: withMode(filters, mode) });
  return response.data;
};

// ── AWS Recommendation APIs ────────────────────────────────────────────────
export const getRecommendations = async (filters = {}, mode = 'mock') => {
  const response = await apiClient.get('/aws/recommendations', { params: withMode(filters, mode) });
  return response.data;
};

export const getIdleInstances = async (filters = {}, mode = 'mock') => {
  const response = await apiClient.get('/aws/recommendations/idle-instances', { params: withMode(filters, mode) });
  return response.data;
};

export const getUnattachedVolumes = async (filters = {}, mode = 'mock') => {
  const response = await apiClient.get('/aws/recommendations/unattached-volumes', { params: withMode(filters, mode) });
  return response.data;
};

// ── AWS Analytics APIs ─────────────────────────────────────────────────────
export const getSavings = async (mode = 'mock') => {
  const response = await apiClient.get('/aws/savings', { params: withMode({}, mode) });
  return response.data;
};

export const runAnalysis = async (data, mode = 'mock') => {
  const response = await apiClient.post(`/aws/analyze?data_mode=${mode}`, data);
  return response.data;
};

// ── Azure Cost APIs ────────────────────────────────────────────────────────
export const getAzureCostsSummary = async (filters = {}, mode = 'mock') => {
  const response = await apiClient.get('/azure/costs/summary', { params: withMode(filters, mode) });
  return response.data;
};

export const getAzureSavings = async (mode = 'mock') => {
  const response = await apiClient.get('/azure/savings', { params: withMode({}, mode) });
  return response.data;
};

export const getAzureIdleVMs = async (mode = 'mock') => {
  const response = await apiClient.get('/azure/recommendations/idle-vms', { params: withMode({}, mode) });
  return response.data;
};

export const getAzureUnattachedDisks = async (mode = 'mock') => {
  const response = await apiClient.get('/azure/recommendations/unattached-disks', { params: withMode({}, mode) });
  return response.data;
};

export default apiClient;
