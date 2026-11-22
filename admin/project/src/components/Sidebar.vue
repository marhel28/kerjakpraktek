<template>
    <aside id="admin-sidebar" :class="[
        // Responsive width & layout
        isCollapsed ? 'lg:w-[76px]' : 'lg:w-64',
        'fixed inset-y-0 left-0 z-50 w-72 lg:static lg:z-20',
        isMobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
        'flex flex-col bg-white border-r border-gray-200 transition-all duration-300 ease-in-out shrink-0 select-none shadow-xl lg:shadow-none'
    ]">
        <!-- ── Header ─────────────────────────────────────────────── -->
        <div class="h-16 flex items-center border-b border-gray-100 shrink-0 px-3.5 transition-all duration-300"
            :class="isCollapsed ? 'lg:justify-center' : 'justify-between'">

            <!-- Logo & Brand -->
            <div class="flex items-center min-w-0" :class="isCollapsed && 'lg:hidden'">
                <img src="@/assets/pasarcctv.png" alt="PasarCCTV Logo"
                    class="h-8 w-auto object-contain transition-opacity duration-300"
                    onerror="this.style.display='none'" />
                <span class="ml-2.5 font-bold text-lg tracking-tight text-gray-900 truncate fallback-text">
                    PasarCCTV
                </span>
            </div>

            <!-- Monogram badge when collapsed on desktop -->
            <button v-if="isCollapsed" @click="$emit('toggle-collapse')"
                class="hidden lg:flex h-9 w-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-indigo-500 items-center justify-center text-white font-bold text-base shadow-sm hover:scale-105 active:scale-95 transition-all"
                title="Perluas sidebar">
                P
            </button>

            <!-- Toggle & Close Actions -->
            <div class="flex items-center space-x-1" :class="isCollapsed && 'lg:hidden'">
                <!-- Desktop Collapse Button -->
                <button @click="$emit('toggle-collapse')"
                    class="hidden lg:flex p-1.5 rounded-lg text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition-colors active:scale-95"
                    title="Ciutkan sidebar">
                    <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round"
                            d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
                    </svg>
                </button>

                <!-- Mobile Close Button -->
                <button @click="$emit('close-mobile')"
                    class="lg:hidden p-1.5 rounded-lg text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition-colors active:scale-95"
                    title="Tutup menu">
                    <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
        </div>

        <!-- ── Navigation List ────────────────────────────────────── -->
        <nav class="flex-1 overflow-y-auto py-3 px-2.5 space-y-1 scrollbar-hide" aria-label="Navigasi utama">
            <template v-for="(item, index) in menuItems" :key="index">
                <!-- Group with Popover handler for collapsed mode -->
                <div class="relative"
                    @mouseenter="handleMouseEnter(item.name)"
                    @mouseleave="handleMouseLeave">

                    <!-- Main Menu Button -->
                    <button @click="handleMenuClick(item)" :aria-current="isItemActive(item) ? 'page' : undefined" :aria-expanded="item.children ? (isCollapsed ? hoveredItem === item.name : openSubmenus.includes(item.name)) : undefined" :class="[
                        'w-full flex items-center rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/40 relative',
                        isCollapsed ? 'lg:justify-center lg:px-0 lg:py-2.5 px-3 py-2.5' : 'px-3 py-2.5',
                        isItemActive(item)
                            ? 'bg-indigo-50 text-indigo-600 font-semibold shadow-xs'
                            : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    ]">
                        <!-- Left Active Indicator Bar (Expanded only) -->
                        <div v-if="isItemActive(item) && !isCollapsed"
                            class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-indigo-600 rounded-r-md">
                        </div>

                        <!-- Menu Icon -->
                        <span :class="[
                            'shrink-0 transition-colors duration-200',
                            isItemActive(item) ? 'text-indigo-600' : 'text-gray-400 group-hover:text-indigo-500'
                        ]" v-html="item.icon"></span>

                        <!-- Label (Expanded only) -->
                        <span v-if="!isCollapsed"
                            class="ml-3 text-sm font-medium transition-opacity duration-200 truncate">
                            {{ item.name }}
                        </span>

                        <!-- Accordion Chevron (Expanded only) -->
                        <svg v-if="!isCollapsed && item.children"
                            :class="[
                                'ml-auto w-4 h-4 transition-transform duration-200',
                                openSubmenus.includes(item.name) ? 'rotate-180 text-indigo-600' : 'text-gray-400'
                            ]"
                            fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
                        </svg>

                        <!-- Active Dot for Collapsed Mode -->
                        <div v-if="isCollapsed && isItemActive(item)"
                            class="hidden lg:block absolute right-1.5 top-1.5 w-2 h-2 rounded-full bg-indigo-600 ring-2 ring-white">
                        </div>
                    </button>

                    <!-- ── Collapsed Hover Tooltip (Single items without children) ── -->
                    <div v-if="isCollapsed && !item.children && hoveredItem === item.name"
                        class="hidden lg:flex items-center absolute left-full top-1/2 -translate-y-1/2 ml-3 z-50 pointer-events-none">
                        <div class="px-2.5 py-1.5 bg-gray-900 text-white text-xs font-medium rounded-lg shadow-lg whitespace-nowrap">
                            {{ item.name }}
                        </div>
                        <div class="w-1.5 h-1.5 bg-gray-900 rotate-45 -left-1 absolute top-1/2 -translate-y-1/2"></div>
                    </div>

                    <!-- ── Collapsed Floating Flyout Card (Items with children) ── -->
                    <div v-if="isCollapsed && item.children && hoveredItem === item.name"
                        class="hidden lg:block absolute left-full top-0 ml-3 z-50 min-w-[210px] bg-white rounded-2xl shadow-xl border border-gray-100 py-2.5 px-2 animate-in fade-in zoom-in-95 duration-150"
                        @mouseenter="handleMouseEnter(item.name)"
                        @mouseleave="handleMouseLeave">

                        <!-- Header Title in Flyout -->
                        <div class="px-3 py-1.5 mb-1 border-b border-gray-100 flex items-center justify-between">
                            <span class="text-xs font-bold text-gray-800 tracking-wide">{{ item.name }}</span>
                            <span class="text-[10px] px-1.5 py-0.5 rounded-full bg-indigo-50 text-indigo-600 font-semibold">
                                {{ item.children.length }}
                            </span>
                        </div>

                        <!-- Child links in Flyout -->
                        <div class="space-y-0.5">
                            <button v-for="sub in item.children" :key="sub.name"
                                @click="handleSubMenuClick(sub)"
                                :aria-current="isActive(sub.name) ? 'page' : undefined"
                                :class="[
                                    'w-full flex items-center px-3 py-2 text-xs rounded-xl transition-colors duration-150 text-left',
                                    isActive(sub.name)
                                        ? 'bg-indigo-50 text-indigo-600 font-semibold'
                                        : 'text-gray-600 hover:bg-gray-50 hover:text-indigo-600'
                                ]">
                                <span class="w-1.5 h-1.5 rounded-full mr-2.5 transition-colors"
                                    :class="isActive(sub.name) ? 'bg-indigo-600' : 'bg-gray-300'"></span>
                                <span class="truncate">{{ sub.name }}</span>
                            </button>
                        </div>
                    </div>

                    <!-- ── Expanded Accordion Submenu ────────────────────── -->
                    <div v-if="!isCollapsed && item.children && openSubmenus.includes(item.name)"
                        class="overflow-hidden transition-all duration-300 mt-1 pl-6 pr-1 space-y-1">
                        <button v-for="sub in item.children" :key="sub.name"
                            @click="handleSubMenuClick(sub)"
                            :class="[
                                'w-full flex items-center px-3 py-2 text-xs rounded-xl transition-colors duration-150 text-left',
                                isActive(sub.name)
                                    ? 'bg-indigo-50 text-indigo-600 font-semibold'
                                    : 'text-gray-500 hover:text-indigo-600 hover:bg-gray-50'
                            ]">
                            <span class="w-1.5 h-1.5 rounded-full mr-2.5 transition-colors"
                                :class="isActive(sub.name) ? 'bg-indigo-600' : 'bg-gray-300'"></span>
                            <span class="truncate">{{ sub.name }}</span>
                        </button>
                    </div>

                </div>
            </template>
        </nav>

        <!-- ── Footer Controls ───────────────────────────────────── -->
        <div class="p-3 border-t border-gray-100 shrink-0">
            <!-- Expanded Footer Toggle -->
            <button v-if="!isCollapsed" @click="$emit('toggle-collapse')"
                class="hidden lg:flex w-full items-center justify-between px-3 py-2 rounded-xl text-xs font-medium text-gray-500 hover:text-gray-800 hover:bg-gray-50 transition-colors">
                <span class="flex items-center gap-2">
                    <svg class="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
                    </svg>
                    <span>Ciutkan Sidebar</span>
                </span>
                <kbd class="px-1.5 py-0.5 text-[10px] font-mono bg-gray-100 text-gray-500 rounded border border-gray-200">Alt + S</kbd>
            </button>

            <!-- Collapsed Footer Toggle Button -->
            <button v-if="isCollapsed" @click="$emit('toggle-collapse')"
                class="hidden lg:flex mx-auto p-2 rounded-xl text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors"
                title="Perluas sidebar (Alt + S)">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
                </svg>
            </button>
        </div>
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
</style>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const props = defineProps({
    isCollapsed: { type: Boolean, default: false },
    isMobileOpen: { type: Boolean, default: false }
})

const emit = defineEmits(['toggle-collapse', 'close-mobile'])

const router = useRouter()
const route = useRoute()

const openSubmenus = ref(['Jasa', 'Banner Management'])
const currentActiveRoute = ref('Dashboard')
const hoveredItem = ref(null)
let flyoutTimeout = null

// Icons
const iHome = `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>`
const iBriefcase = `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>`
const iBox = `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>`
const iCreditCard = `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"/></svg>`
const iImage = `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>`
const iDiamond = `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 2l8 9-8 11L4 11l8-9z" /><path stroke-linecap="round" stroke-linejoin="round" d="M12 2v20M4 11h16" /></svg>`
const iTag = `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"/></svg>`
const iMegaphone = `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3 11v2a2 2 0 002 2h2l4 3V6L7 9H5a2 2 0 00-2 2z" /><path stroke-linecap="round" stroke-linejoin="round" d="M11 6l8-3v18l-8-3" /></svg>`
const iPuzzle = `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z" /></svg>`
const iMessageCircle = `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4-.8L3 20l1.2-3.2A7.683 7.683 0 013 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg>`
const iBot = `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>`
const iGear = `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>`

const menuItems = [
    { name: 'Dashboard', icon: iHome, path: '/' },
    {
        name: 'Pesan',
        icon: iMessageCircle,
        children: [
            { name: 'Inbox', path: '/pesan' }
        ]
    },
    {
        name: 'Jasa',
        icon: iBriefcase,
        children: [
            { name: 'Booking', path: '/jasa/booking' },
            { name: 'Check Booking', path: '/jasa/check' },
            { name: 'Paket Booking', path: '/jasa/paket' },
            { name: 'Config', path: '/jasa/config' },
            { name: 'Config List', path: '/jasa/config-list' },
            { name: 'Tim & Jadwal', path: '/jasa/technicians' },
        ]
    },
    {
        name: 'Stock',
        icon: iBox,
        children: [
            { name: 'Stock List', path: '/stock' },
            { name: 'Create', path: '/stock/createsData' },
        ]
    },
    { name: 'Addons', icon: iPuzzle, path: '/addons' },
    {
        name: 'Transaksi',
        icon: iCreditCard,
        children: [
            { name: 'Transaksi List', path: '/transaksi/list' },
        ]
    },
    {
        name: 'Banner Management',
        icon: iImage,
        children: [
            { name: 'Banner Per Route', path: '/banner/route' },
            { name: 'Main Bottom Banner', path: '/banner/main-bottom' },
            { name: 'X Banner', path: '/banner/x' },
        ]
    },
    { name: 'Brand Logo', icon: iDiamond, path: '/brands' },
    { name: 'Category', icon: iTag, path: '/category' },
    {
        name: 'Marketing',
        icon: iMegaphone,
        children: [
            { name: 'Promo', path: '/promo' },
            { name: 'Kupon', path: '/promo/coupon' },
            { name: 'PortoFolio', path: '/portofolio' },
            { name: 'About', path: '/about' },
        ]
    },
    {
        name: 'AI & Chatbot',
        icon: iBot,
        children: [
            { name: 'FAQ Database', path: '/chatbot/faq' },
            { name: 'Chatbot Logs & Ratings', path: '/chatbot/logs' },
            { name: 'AI Settings', path: '/chatbot/settings' }
        ]
    },
    {
        name: 'Pengaturan',
        icon: iGear,
        children: [
            { name: 'Preferensi Kurir', path: '/settings/couriers' },
            { name: 'Popup Promo Utama', path: '/settings/promo-popup' },
            { name: 'Link Preview', path: '/settings/preview' }
        ]
    }
]

// Helpers
const isActive = (name) => currentActiveRoute.value === name

const isItemActive = (item) => {
    if (!item.children) return isActive(item.name)
    return item.children.some(sub => isActive(sub.name))
}

const handleMouseEnter = (name) => {
    if (!props.isCollapsed) return
    clearTimeout(flyoutTimeout)
    hoveredItem.value = name
}

const handleMouseLeave = () => {
    if (!props.isCollapsed) return
    flyoutTimeout = setTimeout(() => {
        hoveredItem.value = null
    }, 150)
}

const handleMenuClick = (item) => {
    if (item.children) {
        if (props.isCollapsed) {
            hoveredItem.value = hoveredItem.value === item.name ? null : item.name
            return
        }
        const index = openSubmenus.value.indexOf(item.name)
        if (index > -1) {
            openSubmenus.value.splice(index, 1)
        } else {
            openSubmenus.value.push(item.name)
        }
    } else {
        currentActiveRoute.value = item.name
        hoveredItem.value = null
        emit('close-mobile')
        router.push(item.path)
    }
}

const handleSubMenuClick = (subItem) => {
    currentActiveRoute.value = subItem.name
    hoveredItem.value = null
    emit('close-mobile')
    router.push(subItem.path)
}

// Keyboard shortcut (Alt + S) to toggle collapse
const handleKeydown = (e) => {
    if (e.altKey && (e.key === 's' || e.key === 'S')) {
        e.preventDefault()
        emit('toggle-collapse')
    }
}

watch(() => route.path, (newPath) => {
    menuItems.forEach(item => {
        if (item.path === newPath) currentActiveRoute.value = item.name
        if (item.children) {
            item.children.forEach(sub => {
                if (sub.path === newPath) {
                    currentActiveRoute.value = sub.name
                    if (!openSubmenus.value.includes(item.name)) {
                        openSubmenus.value.push(item.name)
                    }
                }
            })
        }
    })
}, { immediate: true })

onMounted(() => {
    window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown)
    clearTimeout(flyoutTimeout)
})
</script>
