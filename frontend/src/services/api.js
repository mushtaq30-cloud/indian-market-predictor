import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  timeout: 60000, // 60 seconds for first request
});

export const getDashboard = async () => {
  const response = await api.get('/dashboard');
  return response.data;
};

export const getGoldAnalysis = async () => {
  const response = await api.get('/gold/analysis');
  return response.data;
};

export const getSilverAnalysis = async () => {
  const response = await api.get('/silver/analysis');
  return response.data;
};

export const getStockAnalysis = async (symbol) => {
  const response = await api.get(`/stock/${symbol}/analysis`);
  return response.data;
};

export const chatbotQuery = async (question) => {
  const response = await api.post('/chatbot', { question });
  return response.data;
};

export const getMarketOverview = async () => {
  const response = await api.get('/market/overview');
  return response.data;
};

export default api;
