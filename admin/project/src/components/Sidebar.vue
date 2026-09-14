<template>
    <aside :class="[
        isOpen ? 'w-64' : 'w-20',
        'flex flex-col bg-white border-r border-gray-200 transition-all duration-300 ease-in-out relative z-20 shrink-0'
    ]">
        <div class="h-16 flex items-center justify-center border-b border-gray-100 shrink-0 px-4">
            <img v-if="isOpen" src="@/assets/pasarcctv.png" alt="PasarCCTV Logo"
                class="h-8 w-auto object-contain transition-opacity duration-300" onerror="this.style.display='none'" />
            <div v-if="!isOpen"
                class="h-8 w-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-xl shadow-md">
                P
            </div>
            <span v-if="isOpen"
                class="ml-2 font-bold text-xl tracking-tight text-gray-900 hidden fallback-text">PasarCCTV</span>
        </div>

        <nav class="flex-1 overflow-y-auto py-4 scrollbar-hide">
            <ul class="space-y-1.5 px-3">

                <template v-for="(item, index) in menuItems" :key="index">
                    <li class="relative group">
                        
                        <button @click="handleMenuClick(item)" :class="[
                            'w-full flex items-center px-3 py-2.5 rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/50',
                            isActive(item.name) && !item.children
                                ? 'bg-indigo-50 text-indigo-600'
                                : 'text-gray-500 hover:bg-gray-50 hover:text-gray-900',
                            !isOpen && 'justify-center'
                        ]">
                            <span :class="[
                                'shrink-0 transition-colors duration-200',
                                (isActive(item.name) && !item.children) || openSubmenus.includes(item.name) ? 'text-indigo-600' : 'text-gray-400 group-hover:text-indigo-500'
                            ]" v-html="item.icon"></span>

                            <span v-if="isOpen"
                                :class="['ml-3 font-medium text-sm transition-opacity duration-300 truncate', (isActive(item.name) && !item.children) ? 'font-semibold' : '']">
                                {{ item.name }}
                            </span>

                            <div v-if="isActive(item.name) && isOpen && !item.children"
                                class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-indigo-600 rounded-r-md">
                            </div>

                            <svg v-if="isOpen && item.children"
                                :class="['ml-auto w-4 h-4 transition-transform duration-200', openSubmenus.includes(item.name) ? 'rotate-180 text-indigo-600' : '']"
                                fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M19 9l-7 7-7-7" />
                            </svg>

                            <div v-if="!isOpen"
                                class="absolute left-full ml-4 px-2.5 py-1.5 bg-gray-900 text-white text-xs font-medium rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 whitespace-nowrap z-50 pointer-events-none shadow-sm">
                                {{ item.name }}
                                <div class="absolute top-1/2 -translate-y-1/2 -left-1 border-[5px] border-transparent border-r-gray-900">
                                </div>
                            </div>
                        </button>

                        <div v-if="isOpen && item.children" v-show="openSubmenus.includes(item.name)"
                            class="overflow-hidden transition-all duration-300 mt-1 space-y-1">
                            <button v-for="sub in item.children" :key="sub.name"
                                @click="handleSubMenuClick(sub)"
                                :class="[
                                    'w-full flex items-center pl-10 pr-3 py-2 text-sm rounded-lg transition-colors duration-200 focus:outline-none',
                                    isActive(sub.name) ? 'text-indigo-600 bg-indigo-50 font-medium' : 'text-gray-500 hover:text-indigo-600 hover:bg-indigo-50'
                                ]">
                                {{ sub.name }}
                            </button>
                        </div>

                    </li>
                </template>

            </ul>
        </nav>
    </aside>
</template>

<style scoped>
.scrollbar-hide::-webkit-scrollbar {
    display: none;
}

.scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
}

img:focus+.fallback-text {
    display: block;
}
/* Show text if image fails to load */
</style>

<script setup>
import { path } from 'd3'
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const props = defineProps({
    isOpen: { type: Boolean, required: true }
})

const emit = defineEmits(['toggle'])

// Initialize Router
const router = useRouter()
const route = useRoute()

// State
const openSubmenus = ref(['Jasa', 'Banner Management'])
const currentActiveRoute = ref('Dashboard')

// 1. PINDAHKAN ICONS KE SINI
const iHome = `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>`
const iBriefcase = `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>`
const iBox = `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>`
const iCreditCard = `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"/></svg>`
const iImage = `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>`
const iDiamond = `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 2l8 9-8 11L4 11l8-9z" /><path stroke-linecap="round" stroke-linejoin="round" d="M12 2v20M4 11h16" /></svg>`
const iTag = `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"/></svg>`
const iMegaphone = `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
  <path stroke-linecap="round" stroke-linejoin="round" d="M3 11v2a2 2 0 002 2h2l4 3V6L7 9H5a2 2 0 00-2 2z" />
  <path stroke-linecap="round" stroke-linejoin="round" d="M11 6l8-3v18l-8-3" />
</svg>`
const iPuzzle = `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z" /></svg>`

const iMessageCircle = `<svg 
  class="w-5 h-5" 
  fill="none" 
  viewBox="0 0 24 24" 
  stroke="currentColor" 
  stroke-width="2"
>
  <path 
    stroke-linecap="round" 
    stroke-linejoin="round" 
    d="M8 10h.01M12 10h.01M16 10h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4-.8L3 20l1.2-3.2A7.683 7.683 0 013 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
  />
</svg>
`
// 2. PINDAHKAN MENU ITEMS KE SINI (Setelah icon siap)
const menuItems = [
    { name: 'Dashboard', icon: iHome, path: '/' },
    {
    name:'Pesan',
    icon: iMessageCircle,
    children:[
        {
            name:'Inbox',
            path:'/pesan'
        }
    ]
},
    {
        name: 'Jasa', icon: iBriefcase, children: [
            { name: 'Booking', path: '/jasa/booking' },
            { name: 'Check Booking', path: '/jasa/check' },
            { name: 'Paket Booking', path: '/jasa/paket' },
            { name: 'Config', path: '/jasa/config' },
            { name: 'Config List', path: '/jasa/config-list' },
            { name: 'Tim & Jadwal', path: '/jasa/technicians' },
            
        ]
    },
    { name: 'Stock', icon: iBox,children:[
        {name:'Stock List',path:'/stock'},
        {name:'Create',path:'/stock/createsData'},
    ] },
    { name: 'Addons', icon: iPuzzle, path: '/addons' },
    { name: 'Transaksi', icon: iCreditCard, children:[
        { name: 'Transaksi List', path: '/transaksi/list' },

    ] },
    {
        name: 'Banner Management', icon: iImage, children: [
            { name: 'Banner Per Route', path: '/banner/route' },
            { name: 'Main Bottom Banner', path: 'banner/main-bottom' },
            { name: 'X Banner', path: '/banner/x' },
        ]
    },
    { name: 'Brand Logo', icon: iDiamond, path: '/brands' },
    { name: 'Category', icon: iTag, path: '/category' },
    {
        name:"Marketing",icon: iMegaphone,children:[
            { name: 'Promo', path: '/promo' },
            { name: 'Kupon', path: '/promo/coupon' },
            { name: 'PortoFolio', path: '/portofolio' },
            { name: 'About', path: '/about' },
        ]
    },
    {
        name: "AI & Chatbot",
        icon: `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>`,
        children: [
            { name: "FAQ Database", path: "/chatbot/faq" },
            { name: "Chatbot Logs & Ratings", path: "/chatbot/logs" },
            { name: "AI Settings", path: "/chatbot/settings" }
        ]
    },
    {
        name: "Pengaturan",
        icon: `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>`,
        children: [
            { name: "Preferensi Kurir", path: "/settings/couriers" },
            { name: "Popup Promo Utama", path: "/settings/promo-popup" }
        ]
    }
]

// Helper
const isActive = (name) => currentActiveRoute.value === name

// Handlers
const handleMenuClick = (item) => {
    if (item.children) {
        if (!props.isOpen) emit('toggle')
        const index = openSubmenus.value.indexOf(item.name)
        if (index > -1) openSubmenus.value.splice(index, 1)
        else openSubmenus.value.push(item.name)
    } else {
        currentActiveRoute.value = item.name 
        router.push(item.path) 
    }
}

const handleSubMenuClick = (subItem) => {
    currentActiveRoute.value = subItem.name
    router.push(subItem.path)
}

// 3. WATCH BERADA DI PALING BAWAH (Sekarang aman karena menuItems sudah ada nilainya)
watch(() => route.path, (newPath) => {
    menuItems.forEach(item => {
        if (item.path === newPath) currentActiveRoute.value = item.name;
        if (item.children) {
            item.children.forEach(sub => {
                if (sub.path === newPath) {
                    currentActiveRoute.value = sub.name;
                    if (!openSubmenus.value.includes(item.name)) {
                        openSubmenus.value.push(item.name);
                    }
                }
            })
        }
    })
}, { immediate: true })

</script>