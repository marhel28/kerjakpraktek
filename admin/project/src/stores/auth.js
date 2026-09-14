// src/stores/auth.js
import { defineStore } from 'pinia';
import api from '@/service/api';
import router from '@/router';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('token') || null,
    refreshToken: localStorage.getItem('refresh_token') || null,
    isLoading: false,
    error: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === 'admin',
  },

  actions: {
    async login(email, password) {
      this.isLoading = true;
      this.error = null;

      try {
        const response = await api.post('auth/user/auth/login', { email, password });
        const data = response.data;

        if (data.user.role !== 'admin') {
          this.error = "Akses ditolak. Hanya Admin yang dapat masuk ke sistem ini.";
          return false;
        }

        this.token = data.access_token;
        this.refreshToken = data.refresh_token;
        this.user = data.user;

        localStorage.setItem('token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        localStorage.setItem('user', JSON.stringify(data.user));

        router.push('/');
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Login gagal';
        return false;
      } finally {
        this.isLoading = false;
      }
    },

    // 🔥 LOGOUT BARU (CALL BACKEND)
    async logout() {
      try {
        // panggil backend revoke token
        await api.post('/auth/user/auth/logout');
      } catch (err) {
        // kalau gagal, tetap lanjut logout
        console.warn('Logout API gagal:', err);
      }

      // clear state
      this.token = null;
      this.refreshToken = null;
      this.user = null;

      localStorage.clear();

      router.push('/login');
    },
  },
});