import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getAssets = async () => {
  const response = await api.get('/api/assets');
  return response.data;
};

export const createAsset = async (assetData) => {
  const response = await api.post('/api/assets', assetData);
  return response.data;
};

export const updateAsset = async (id, updateData) => {
  const response = await api.put(`/api/assets/${id}`, updateData);
  return response.data;
};

export const deleteAsset = async (id) => {
  const response = await api.delete(`/api/assets/${id}`);
  return response.data;
};
