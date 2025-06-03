import axios from 'axios';
import authService from './auth';

// Add a request interceptor
axios.interceptors.request.use(
  (config) => {
    const user = authService.getCurrentUser();
    if (user?.tokens.access) {
      config.headers.Authorization = `Bearer ${user.tokens.access}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor
axios.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // If the error status is 401 and there is no originalRequest._retry flag,
    // it means the token has expired and we need to refresh it
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const response = await authService.refreshToken();
        if (response?.access) {
          axios.defaults.headers.common['Authorization'] = `Bearer ${response.access}`;
          return axios(originalRequest);
        }
      } catch (error) {
        authService.logout();
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);