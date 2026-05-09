// src/service/api.js
import axios from 'axios';

// ============================
// MAIN API (pakai interceptor)
// ============================
const api = axios.create({
  // baseURL : 'http://127.0.0.1:8000',
  baseURL: 'https://cctv-api.desa-sidomukti.com',
  headers: {
    'Content-Type': 'application/json',
  },
});

// ============================
// REFRESH CLIENT (NO interceptor)
// ============================
const refreshClient = axios.create({
  baseURL: 'https://cctv-api.desa-sidomukti.com',
});

// ============================
// STATE
// ============================
let isRefreshing = false;
let failedQueue = [];
let isLoggingOut = false;

// ============================
// HELPER LOGOUT
// ============================
const logout = () => {
  if (isLoggingOut) return;
  isLoggingOut = true;

  localStorage.removeItem('token');
  localStorage.removeItem('refresh_token');

  window.location.href = '/login';
};

// ============================
// PROCESS QUEUE
// ============================
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

// ============================
// REQUEST INTERCEPTOR
// ============================
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // 🔥 PENTING: Jangan set Content-Type manual untuk FormData
    // Biarkan browser yang menentukan boundary otomatis
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// ============================
// RESPONSE INTERCEPTOR
// ============================
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // ❌ kalau tidak ada response → reject
    if (!error.response) {
      return Promise.reject(error);
    }

    // ❌ bukan 401 → reject biasa
    if (error.response.status !== 401) {
      return Promise.reject(error);
    }

    // ❌ kalau request refresh itu sendiri gagal → logout
    if (originalRequest.url.includes('/auth/user/auth/refresh')) {
      logout();
      return Promise.reject(error);
    }

    // ❌ sudah retry tapi masih gagal → logout
    if (originalRequest._retry) {
      logout();
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    const refreshToken = localStorage.getItem('refresh_token');

    // ❌ tidak ada refresh token → logout
    if (!refreshToken) {
      logout();
      return Promise.reject(error);
    }

    // ============================
    // 🔥 kalau sedang refresh → queue
    // ============================
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({
          resolve: (token) => {
            originalRequest.headers.Authorization = 'Bearer ' + token;
            resolve(api(originalRequest));
          },
          reject: (err) => reject(err),
        });
      });
    }

    isRefreshing = true;

    try {
      // ============================
      // 🔥 REFRESH TOKEN (NO interceptor)
      // ============================
      const res = await refreshClient.post('/auth/user/auth/refresh', {
        refresh_token: refreshToken,
      });

      const newToken = res.data.access_token;

      // simpan access token baru
      localStorage.setItem('token', newToken);

      // kalau backend kirim refresh baru (optional)
      if (res.data.refresh_token) {
        localStorage.setItem('refresh_token', res.data.refresh_token);
      }

      // proses queue
      processQueue(null, newToken);

      // retry request lama
      originalRequest.headers.Authorization = `Bearer ${newToken}`;
      return api(originalRequest);

    } catch (err) {
      processQueue(err, null);

      // ❌ refresh gagal → logout
      logout();

      return Promise.reject(err);
    } finally {
      isRefreshing = false;
    }
  }
);

export default api;