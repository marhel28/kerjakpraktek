/**
 * services/stock.js
 * Padjajaran CCTV — Centralized API Service
 */

// Sesuaikan path import di bawah ini dengan lokasi file api.js kamu
// Misalnya jika dalam satu folder: import api from './api';
import api from '@/service/api'; 

// ── Stock API ────────────────────────────────────────────────────
export const stockApi = {
  /** GET /stok/public/list — daftar produk dengan filter */
  list(params = {}) {
    // Axios menggunakan config { params } untuk query URL
    return api.get('/stok/admin/stocks', { params });
  },

  /** GET /stok/public/detail/:uuid */
  detail(uuid) {
    return api.get(`/stok/public/detail/${uuid}`);
  },

  /** POST /stok/admin/create — multipart/form-data */
  create(formData) {
    return api.post('/stok/admin/create', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  /** PATCH /stok/admin/:uuid — update stock */
  update(uuid, formData) {
    return api.patch(`/stok/admin/update/${uuid}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  /** DELETE /stok/admin/:uuid */
  remove(uuid) {
    return api.delete(`/stok/admin/delete/${uuid}`);
  },

  /** GET /stok/public/popular */
  popular() {
    return api.get('/stok/public/popular');
  },

  /** GET /stok/public/trending-searches */
  trendingSearches() {
    return api.get('/stok/public/trending-searches');
  },
};

// ── Brand API ────────────────────────────────────────────────────
export const brandApi = {
  /** GET /brands/ */
  list() {
    return api.get('/brands/');
  },
};

// ── Category API ─────────────────────────────────────────────────
export const categoryApi = {
  /** GET /category/ */
  list() {
    return api.get('/category/');
  },

  /** GET /category/:slug/subcategories */
  subcategories(slug) {
    return api.get(`/category/${slug}/subcategories`);
  },
};

// ── Coupon API ───────────────────────────────────────────────────
export const couponApi = {
  /** GET /stok/admin/coupon */
  list(params = {}) {
    return api.get('/stok/admin/coupon', { params });
  },

  /** GET /stok/admin/coupon/:code */
  detail(code) {
    return api.get(`/stok/admin/coupon/${code}`);
  },

  /** POST /stok/admin/coupon */
  create(body) {
    return api.post('/stok/admin/coupon', body);
  },

  /** PATCH /stok/admin/coupon/:code */
  update(code, body) {
    return api.patch(`/stok/admin/coupon/${code}`, body);
  },

  /** DELETE /stok/admin/coupon/:code */
  remove(code) {
    return api.delete(`/stok/admin/coupon/${code}`);
  },

  /** POST /stok/public/coupon/validate */
  validate(body) {
    return api.post('/stok/public/coupon/validate', body);
  },
};