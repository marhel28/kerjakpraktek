// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/login.vue'),
      meta: { guestOnly: true } // Rute khusus untuk user yang belum login
    },
    {
      path: '/',
      component: () => import('@/layouts/publicLayout.vue'), 
      meta: { requiresAdmin: true }, 
      children: [
        {
          path: '', 
          name: 'dashboard',
          component: () => import('@/views/dashboard.vue') // Ganti dengan view dashboard kamu
        },
        {
          path: 'banner/x', // Harus sama dengan path di Sidebar ({ name: 'X Banner', path: '/banner/x' })
          name: 'x-banner',
          component: () => import('@/views/xbanner.vue') // ⚠️ Sesuaikan dengan lokasi kamu menyimpan file xbanner.vue
        },
        {
          path:'brands',
          name:'brands',
          component: () => import('@/views/brand.vue')
        },
        {
          path:'category',
          name:'category',
          component: () => import('@/views/category.vue')
        },
        {
          path:'banner/route',
          name:'brand',
          component: () => import('@/views/banner-perroute.vue')
        },
        {
          path:'jasa/booking',
          name:'jasa-booking',
          component: () => import('@/views/jasa/booking.vue')
        },
        {
          path:'/jasa/check',
          name:'jasa-check',
          component: () => import('@/views/jasa/check-stats.vue')
        },
        {
          path:'/jasa/paket',
          name:'jasa-paket',
          component: ()=>import('@/views/jasa/paket-booking.vue')
        },
        {
          path:'/jasa/config',
          name:'jasa-configurasi',
          component: () => import('@/views/jasa/configurasi.vue')
        },
        {
          path:'/transaksi/list',
          name:'transaksi-list',
          component: () => import('@/views/transaksi/index.vue')
        },
        {
          path:'/transaksi/:uuid',
          name:'transaksi-id',
          component: () => import('@/views/transaksi/transaksi-id.vue')
        },{
          path:'/stock',
          name:'stock-list',
          component: () => import('@/views/stock/stock-list.vue')
        },
        {
          path:'/stock/createsData',
          name:'stock-creates',
          component: () => import('@/views/stock/createStock.vue')
        },
        {
          path: '/stock/:uuid/edit',
          name:'stock-create',
          component: () => import('@/views/stock/edit.vue')
        },{
          path:'/banner/main-bottom',
          name:'botom-banner',
          component:()=> import('@/views/main-bottom.vue')
        },
        {
          path:'/promo',
          name:'promo-utama',
          component: ()=> import('@/views/promo/mainPromo.vue')
        },
        {
          path:'/promo/detail',
          name:'promo-detail',
          component: ()=> import('@/views/promo/detail.vue')
        },
        {
          path: '/pesan',
          component: () => import('@/views/pesan/index.vue'),
          children: [
            {
              path: ':id',
              name: 'pesan-detail',
              component: () => import('@/views/pesan/id.vue'),
              props: true
            }
          ]
        }
      ]
      
    },
    {
      // Catch-all route: Jika URL tidak ditemukan, arahkan kembali ke root (dashboard)
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ],
});

// Middleware / Route Guard
router.beforeEach((to, from) => {
  const authStore = useAuthStore();

  if (to.meta.requiresAdmin && (!authStore.isAuthenticated || !authStore.isAdmin)) {
    return { name: 'login' };
  }

  if (to.meta.guestOnly && authStore.isAuthenticated && authStore.isAdmin) {
    return { name: 'dashboard' };
  }

  return true; // lanjut
});

export default router;