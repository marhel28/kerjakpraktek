import { defineStore } from 'pinia';
import api from '@/service/api';

export const useNotificationStore = defineStore('adminNotifications', {
  state: () => ({
    notifications: [],
    unreadCount: 0,
    isLoading: false,
    error: null,
    pollingInterval: null
  }),

  actions: {
    async fetchNotifications() {
      try {
        const response = await api.get('/recap/notifications');
        const prevCount = this.unreadCount;
        this.notifications = response.data || [];
        this.unreadCount = this.notifications.filter(n => n.read_at === null).length;
        
        // Return true if there are new notifications compared to previous fetch
        return this.unreadCount > prevCount;
      } catch (err) {
        console.error('Gagal mengambil notifikasi admin:', err);
        this.error = err.response?.data?.detail || 'Gagal mengambil notifikasi';
        return false;
      }
    },

    async markAsRead(id) {
      try {
        await api.patch(`/recap/notifications/${id}/read`);
        const index = this.notifications.findIndex(n => n.id === id);
        if (index !== -1) {
          this.notifications[index].read_at = new Date().toISOString();
        }
        this.unreadCount = this.notifications.filter(n => n.read_at === null).length;
      } catch (err) {
        console.error('Gagal menandai notifikasi dibaca:', err);
      }
    },

    async markAllAsRead() {
      try {
        await api.post('/recap/notifications/read-all');
        this.notifications.forEach(n => {
          if (n.read_at === null) {
            n.read_at = new Date().toISOString();
          }
        });
        this.unreadCount = 0;
      } catch (err) {
        console.error('Gagal menandai semua notifikasi dibaca:', err);
      }
    },

    startPolling(intervalMs = 15000) {
      if (this.pollingInterval) return;
      this.fetchNotifications();
      this.pollingInterval = setInterval(() => {
        this.fetchNotifications();
      }, intervalMs);
    },

    stopPolling() {
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval);
        this.pollingInterval = null;
      }
    }
  }
});
