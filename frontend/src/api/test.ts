import axios from 'axios';

export const testApiConnection = async () => {
  try {
    const response = await axios.get('/api/health/');
    return response.data;
  } catch (error) {
    console.error('API connection test failed:', error);
    throw error;
  }
};