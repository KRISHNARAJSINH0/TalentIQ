/**
 * Axios Instance – Pre-configured HTTP client with JWT interceptors.
 *
 * Automatically attaches the access token to every request.
 * On 401 responses, attempts a silent token refresh.
 * If refresh also fails, clears tokens and redirects to /login.
 */

import axios from 'axios';

const getApiBaseUrl = () => {
  const hostname = window.location.hostname;
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8000/api';
  }
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  // Default fallback to local Django server for development/testing when no production API env var is defined
  return 'http://localhost:8000/api';
};

const API_BASE_URL = getApiBaseUrl();

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ── Request interceptor: attach access token ──
axiosInstance.interceptors.request.use(
  (config) => {
    const tokens = JSON.parse(localStorage.getItem('tokens') || 'null');
    if (tokens?.access) {
      config.headers.Authorization = `Bearer ${tokens.access}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ── Response interceptor: handle 401 + token refresh ──
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Only attempt refresh on 401, and not on auth endpoints themselves
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url.includes('/auth/login') &&
      !originalRequest.url.includes('/auth/register') &&
      !originalRequest.url.includes('/auth/token/refresh')
    ) {
      if (isRefreshing) {
        // Queue requests while refreshing
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return axiosInstance(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const tokens = JSON.parse(localStorage.getItem('tokens') || 'null');
        if (!tokens?.refresh) throw new Error('No refresh token');

        const { data } = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
          refresh: tokens.refresh,
        });

        const newTokens = {
          access: data.access,
          refresh: data.refresh || tokens.refresh,
        };
        localStorage.setItem('tokens', JSON.stringify(newTokens));

        processQueue(null, newTokens.access);

        originalRequest.headers.Authorization = `Bearer ${newTokens.access}`;
        return axiosInstance(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        localStorage.removeItem('tokens');
        localStorage.removeItem('user');

        const isPublicPath = /^\/portfolio\/[^/]+$/.test(window.location.pathname) || window.location.pathname.startsWith('/u/');
        if (!isPublicPath) {
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
        delete originalRequest.headers.Authorization;
        return axiosInstance(originalRequest);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default axiosInstance;
