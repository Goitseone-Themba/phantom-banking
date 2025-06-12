import axios from 'axios';
import type { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';
import { axiosInstance } from './axios';
import { authService } from './auth';
import { getErrorMessage } from './axios';

// Flag to prevent multiple refresh attempts
let isRefreshing = false;
// Queue of requests to retry after token refresh
let refreshSubscribers: ((token: string) => void)[] = [];

// Function to retry failed requests
const onRefreshed = (token: string) => {
  refreshSubscribers.forEach((callback) => callback(token));
  refreshSubscribers = [];
};

// Function to add request to retry queue
const addRefreshSubscriber = (callback: (token: string) => void) => {
  refreshSubscribers.push(callback);
};

// Request interceptor
axiosInstance.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    const tokens = authService.getTokens();
    if (tokens?.access && config.headers) {
      config.headers.Authorization = `Bearer ${tokens.access}`;
    }
    return config;
  },
  (error: unknown) => Promise.reject(error)
);

// Response interceptor
axiosInstance.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;
    if (!originalRequest) {
      return Promise.reject(error);
    }

    // Handle 401 Unauthorized
    if (error.response?.status === 401) {
      // If already refreshing, queue the request
      if (isRefreshing) {
        return new Promise((resolve) => {
          addRefreshSubscriber((token: string) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            resolve(axiosInstance(originalRequest));
          });
        });
      }

      isRefreshing = true;

      try {
        // Attempt to refresh token
        await authService.refreshToken();
        const tokens = authService.getTokens();
        
        if (!tokens?.access) {
          throw new Error('No access token after refresh');
        }

        // Update authorization header
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${tokens.access}`;
        }
        
        // Retry queued requests
        onRefreshed(tokens.access);
        
        // Retry original request
        return axiosInstance(originalRequest);
      } catch (refreshError) {
        // If refresh fails, logout and redirect
        await authService.logout();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    // Handle other errors
    const errorMessage = getErrorMessage(error);
    console.error('API Error:', errorMessage);
    return Promise.reject(error);
  }
); 