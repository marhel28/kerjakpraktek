<template>
    <div class="admin-wrap">
  
      <!-- ── HEADER ── -->
      <div class="admin-header">
        <div class="admin-header__left">
          <h1 class="admin-header__title">Image Sections</h1>
          <p class="admin-header__sub">Kelola banner berdasarkan halaman atau route</p>
        </div>
        <button class="btn btn--primary" @click="openSectionModal()">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M12 4v16m8-8H4"/>
          </svg>
          Tambah Section
        </button>
      </div>
  
      <!-- ── LOADING ── -->
      <div v-if="isLoading" class="skeleton-list">
        <div v-for="i in 2" :key="i" class="skeleton-card">
          <div class="skeleton-card__header">
            <div class="skel skel--title"></div>
            <div class="skel skel--badge"></div>
          </div>
          <div class="skeleton-card__body">
            <div v-for="j in 3" :key="j" class="skel skel--img"></div>
          </div>
        </div>
      </div>
  
      <!-- ── EMPTY ── -->
      <div v-else-if="sections.length === 0" class="empty-state">
        <div class="empty-state__icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <rect x="3" y="3" width="18" height="18" rx="2"/>
            <path d="M3 9h18M9 21V9"/>
          </svg>
        </div>
        <h3 class="empty-state__title">Belum ada section</h3>
        <p class="empty-state__desc">Buat section baru untuk mulai mengelola banner per halaman.</p>
        <button class="btn btn--primary btn--sm" @click="openSectionModal()">Buat Section Pertama</button>
      </div>
  
      <!-- ── SECTIONS LIST ── -->
      <div v-else class="section-list">
        <div v-for="section in sections" :key="section.uuid" class="section-card">
  
          <!-- Section Header -->
          <div class="section-card__head">
            <div class="section-card__meta">
              <div class="section-card__title-row">
                <h2 class="section-card__title">{{ section.title }}</h2>
                <span class="badge" :class="section.is_active ? 'badge--green' : 'badge--gray'">
                  {{ section.is_active ? 'Active' : 'Inactive' }}
                </span>
                <span class="badge badge--mode">{{ section.mode || 'auto' }}</span>
              </div>
              <div class="section-card__id">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/>
                  <path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/>
                </svg>
                <code>{{ section.identifier }}</code>
              </div>
            </div>
            <div class="section-card__actions">
              <button class="icon-btn" @click="openPreview(section)" title="Preview">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
              </button>
              <button class="icon-btn" @click="openSectionModal(section)" title="Edit">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
                  <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
              </button>
              <button class="icon-btn icon-btn--danger" @click="confirmDelete('section', section.uuid)" title="Hapus">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6"/>
                  <path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/>
                  <path d="M10 11v6M14 11v6"/>
                  <path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2"/>
                </svg>
              </button>
            </div>
          </div>
  
          <!-- Banner Items Grid -->
          <div class="section-card__body">
            <div class="banner-grid">
              <div v-for="item in section.items" :key="item.uuid" class="banner-item">
                <div class="banner-item__order">#{{ item.order }}</div>
                <button
                  class="banner-item__delete"
                  @click="confirmDelete('item', item.uuid)"
                  title="Hapus banner"
                >
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                  </svg>
                </button>
                <div class="banner-item__img">
                  <img :src="item.image_url" :alt="item.alt_text || 'Banner'" loading="lazy" />
                </div>
                <div class="banner-item__info">
                  <a :href="item.target_url" target="_blank" class="banner-item__url" :title="item.target_url">
                    {{ item.target_url }}
                  </a>
                  <span v-if="item.alt_text" class="banner-item__alt">{{ item.alt_text }}</span>
                </div>
              </div>
  
              <!-- Upload Slot -->
              <button
                v-if="section.items.length < 5"
                class="banner-add"
                @click="openBannerModal(section.identifier, section.items.length + 1)"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M12 4v16m8-8H4"/>
                </svg>
                <span>Upload Banner</span>
                <small>{{ 5 - section.items.length }} slot tersisa</small>
              </button>
            </div>
          </div>
  
        </div>
      </div>
  
      <!-- ════════════════════════════════
           MODAL: CREATE / EDIT SECTION
      ════════════════════════════════ -->
      <Teleport to="body">
        <Transition name="modal-fade">
          <div v-if="showSectionModal" class="modal-overlay" @click.self="closeModals">
            <div class="modal modal--md">
  
              <div class="modal__head">
                <h3>{{ sectionForm.uuid ? 'Edit Section' : 'Buat Section Baru' }}</h3>
                <button class="modal__close" @click="closeModals">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                  </svg>
                </button>
              </div>
  
              <div class="modal__body">
  
                <!-- Preset Rute Utama Amazon / E-Commerce Style -->
                <div v-if="!sectionForm.uuid" class="field-group">
                  <label class="field-label field-label--sm">Preset Rekomendasi Rute</label>
                  <div class="preset-chips">
                    <button
                      v-for="p in ROUTE_PRESETS"
                      :key="p.identifier"
                      type="button"
                      class="chip-btn"
                      :class="{ 'chip-btn--active': sectionForm.identifier === p.identifier }"
                      @click="applyPreset(p)"
                    >
                      <span class="chip-btn__tag">{{ p.tag }}</span>
                      <span class="chip-btn__id">{{ p.identifier }}</span>
                    </button>
                  </div>
                </div>

                <!-- Auto-fill dari kategori -->
                <div v-if="!sectionForm.uuid" class="field-group field-group--accent">
                  <label class="field-label field-label--sm">Atau Quick fill dari Kategori</label>
                  <select class="field-select" @change="autoFillFromCategory">
                    <option value="">-- Pilih Kategori --</option>
                    <template v-for="cat in categoriesList" :key="cat.id">
                      <option :value="cat.slug" :data-name="cat.name">📁 {{ cat.name }}</option>
                      <option v-for="sub in cat.subcategories" :key="sub.slug" :value="sub.slug" :data-name="sub.name">
                        &nbsp;&nbsp;↳ {{ sub.name }}
                      </option>
                    </template>
                  </select>
                </div>
  
                <div class="field-group">
                  <label class="field-label">Identifier <span class="field-req">*</span></label>
                  <input
                    v-model="sectionForm.identifier"
                    type="text"
                    class="field-input field-input--mono"
                    placeholder="category:kamera-cctv"
                    :disabled="!!sectionForm.uuid"
                    required
                  />
                  <span class="field-hint">Digunakan sebagai key unik pada API dan frontend</span>
                </div>
  
                <div class="field-group">
                  <label class="field-label">Judul Section <span class="field-req">*</span></label>
                  <input
                    v-model="sectionForm.title"
                    type="text"
                    class="field-input"
                    placeholder="Banner Kamera Utama"
                    required
                  />
                </div>
  
                <!-- Mode Picker -->
                <div class="field-group">
                  <label class="field-label">Layout Mode</label>
                  <div class="mode-grid">
                    <button
                      v-for="m in MODE_OPTIONS"
                      :key="m.value"
                      type="button"
                      class="mode-option"
                      :class="{ 'mode-option--active': sectionForm.mode === m.value }"
                      @click="sectionForm.mode = m.value"
                    >
                      <span class="mode-option__icon">{{ m.icon }}</span>
                      <span class="mode-option__label">{{ m.label }}</span>
                      <span class="mode-option__slots">{{ m.slots }}</span>
                    </button>
                  </div>
                </div>
  
                <div class="field-group">
                  <div class="toggle-row">
                    <div>
                      <p class="toggle-row__label">Status Aktif</p>
                      <p class="toggle-row__desc">Tampilkan section ini ke publik</p>
                    </div>
                    <button
                      type="button"
                      class="toggle"
                      :class="{ 'toggle--on': sectionForm.is_active }"
                      @click="sectionForm.is_active = !sectionForm.is_active"
                    >
                      <span class="toggle__knob"></span>
                    </button>
                  </div>
                </div>
  
              </div>
  
              <div class="modal__foot">
                <button class="btn btn--ghost" @click="closeModals">Batal</button>
                <button class="btn btn--primary" :disabled="isSubmitting" @click="saveSection">
                  <svg v-if="isSubmitting" class="spin" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke-opacity=".3"/>
                    <path d="M21 12a9 9 0 00-9-9"/>
                  </svg>
                  {{ isSubmitting ? 'Menyimpan...' : 'Simpan' }}
                </button>
              </div>
  
            </div>
          </div>
        </Transition>
      </Teleport>
  
      <!-- ════════════════════════════════
           MODAL: UPLOAD BANNER
      ════════════════════════════════ -->
      <Teleport to="body">
        <Transition name="modal-fade">
          <div v-if="showBannerModal" class="modal-overlay" @click.self="closeModals">
            <div class="modal modal--md">
  
              <div class="modal__head">
                <h3>Upload Banner</h3>
                <button class="modal__close" @click="closeModals">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                  </svg>
                </button>
              </div>
  
              <div class="modal__body">
  
                <div class="target-badge">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/>
                    <path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/>
                  </svg>
                  <code>{{ bannerForm.targetIdentifier }}</code>
                </div>
  
                <!-- Drop Zone -->
                <div
                  class="dropzone"
                  :class="{ 'dropzone--filled': imagePreview, 'dropzone--drag': isDragging }"
                  @click="triggerFileInput"
                  @dragover.prevent="isDragging = true"
                  @dragleave="isDragging = false"
                  @drop.prevent="handleDrop"
                >
                  <template v-if="imagePreview">
                    <img :src="imagePreview" class="dropzone__preview" />
                    <div class="dropzone__overlay">Ganti Gambar</div>
                  </template>
                  <template v-else>
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="dropzone__icon">
                      <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
                      <polyline points="17 8 12 3 7 8"/>
                      <line x1="12" y1="3" x2="12" y2="15"/>
                    </svg>
                    <p class="dropzone__label">Klik atau drag gambar ke sini</p>
                    <p class="dropzone__hint">JPG, PNG, WEBP — maks. 2MB</p>
                  </template>
                  <input type="file" ref="fileInput" class="dropzone__input" accept="image/*" @change="handleFileChange" />
                </div>
  
                <div class="field-group">
                  <label class="field-label">Tipe Tujuan (Destination) <span class="field-req">*</span></label>
                  <div class="dest-type-selector">
                    <button
                      v-for="dest in DESTINATION_TYPES"
                      :key="dest.type"
                      type="button"
                      class="dest-type-btn"
                      :class="{ 'dest-type-btn--active': destinationType === dest.type }"
                      @click="setDestinationType(dest.type)"
                    >
                      <span class="dest-type-icon">{{ dest.icon }}</span>
                      <span class="dest-type-name">{{ dest.label }}</span>
                    </button>
                  </div>
                </div>

                <!-- Destination Specific Inputs -->
                <div v-if="destinationType === 'category'" class="field-group">
                  <label class="field-label">Pilih Kategori / Subkategori</label>
                  <select v-model="destCategorySlug" class="field-select" @change="buildTargetUrl">
                    <option value="">-- Pilih Kategori --</option>
                    <template v-for="cat in categoriesList" :key="cat.uuid">
                      <option :value="cat.slug">{{ cat.name }} (/category/{{ cat.slug }})</option>
                      <option
                        v-for="sub in (cat.subcategories || [])"
                        :key="sub.uuid"
                        :value="sub.slug"
                      >
                        &nbsp;&nbsp;↳ {{ sub.name }} (/category/{{ sub.slug }})
                      </option>
                    </template>
                  </select>
                </div>

                <div v-else-if="destinationType === 'brand'" class="field-group">
                  <label class="field-label">Pilih Brand</label>
                  <select v-model="destBrandSlug" class="field-select" @change="buildTargetUrl">
                    <option value="">-- Pilih Brand --</option>
                    <option v-for="b in brandsList" :key="b.uuid || b.id" :value="b.name.toLowerCase()">
                      {{ b.name }} (/brands/{{ b.name.toLowerCase() }})
                    </option>
                  </select>
                </div>

                <div v-else-if="destinationType === 'search'" class="field-group">
                  <label class="field-label">Kata Kunci Pencarian</label>
                  <input
                    v-model="destSearchQuery"
                    type="text"
                    class="field-input"
                    placeholder="Contoh: ColorVu atau Paket 4 Kamera"
                    @input="buildTargetUrl"
                  />
                </div>

                <div v-else-if="destinationType === 'product'" class="field-group">
                  <label class="field-label">Cari & Pilih Produk</label>
                  <input
                    v-model="destProductSearch"
                    type="text"
                    class="field-input mb-1"
                    placeholder="Ketik nama produk..."
                    @input="onProductSearch"
                  />
                  <select v-if="productOptions.length" v-model="destProductSlug" class="field-select" @change="buildTargetUrl">
                    <option value="">-- Pilih Produk Terkait --</option>
                    <option v-for="p in productOptions" :key="p.uuid" :value="p.slug">
                      {{ p.title }} (/product/{{ p.slug }})
                    </option>
                  </select>
                </div>

                <div class="field-group">
                  <label class="field-label">Target URL (Hasil Rakitan) <span class="field-req">*</span></label>
                  <div class="target-url-preview">
                    <input
                      v-model="bannerForm.target_url"
                      type="text"
                      class="field-input font-mono text-xs"
                      :placeholder="destinationType === 'external' ? 'https://example.com/promo' : '/category/kamera-cctv'"
                      required
                    />
                  </div>
                  <p class="field-hint text-xs text-gray-400 mt-1">
                    {{ destinationType === 'external' ? 'Mengarahkan ke situs luar (wajib https://)' : 'Rute internal marketplace, otomatis tervalidasi & bebas layout shift.' }}
                  </p>
                </div>
  
                <div class="field-row">
                  <div class="field-group field-group--grow">
                    <label class="field-label">Alt Text <span class="field-opt">(Opsional)</span></label>
                    <input v-model="bannerForm.alt_text" type="text" class="field-input" placeholder="Promo diskon 50%" />
                  </div>
                  <div class="field-group field-group--fixed">
                    <label class="field-label">Urutan</label>
                    <input v-model.number="bannerForm.order" type="number" min="1" max="5" class="field-input field-input--center" />
                  </div>
                </div>
  
              </div>
  
              <div class="modal__foot">
                <button class="btn btn--ghost" @click="closeModals">Batal</button>
                <button class="btn btn--primary" :disabled="isSubmitting" @click="saveBanner">
                  <svg v-if="isSubmitting" class="spin" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke-opacity=".3"/>
                    <path d="M21 12a9 9 0 00-9-9"/>
                  </svg>
                  {{ isSubmitting ? 'Mengunggah...' : 'Upload Banner' }}
                </button>
              </div>
  
            </div>
          </div>
        </Transition>
      </Teleport>
  
      <!-- ════════════════════════════════
           MODAL: DELETE CONFIRM
      ════════════════════════════════ -->
      <Teleport to="body">
        <Transition name="modal-fade">
          <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
            <div class="modal modal--sm modal--danger">
              <div class="modal__head">
                <h3>{{ deleteType === 'section' ? 'Hapus Section?' : 'Hapus Banner?' }}</h3>
                <button class="modal__close" @click="showDeleteModal = false">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                  </svg>
                </button>
              </div>
              <div class="modal__body">
                <p class="delete-desc">
                  {{ deleteType === 'section'
                    ? 'Semua banner dalam section ini akan ikut terhapus. Aksi ini tidak dapat dibatalkan.'
                    : 'Banner ini akan dihapus secara permanen dari sistem dan CDN.' }}
                </p>
              </div>
              <div class="modal__foot">
                <button class="btn btn--ghost" @click="showDeleteModal = false">Batal</button>
                <button class="btn btn--danger" :disabled="isSubmitting" @click="executeDelete">
                  <svg v-if="isSubmitting" class="spin" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke-opacity=".3"/>
                    <path d="M21 12a9 9 0 00-9-9"/>
                  </svg>
                  {{ isSubmitting ? 'Menghapus...' : 'Ya, Hapus' }}
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>
  
      <!-- ════════════════════════════════
           PREVIEW PANEL (component)
      ════════════════════════════════ -->
      <ImageSectionPreview
        v-model="showPreview"
        :section="previewSection"
        :is-applying="isSubmitting"
        :extra-presets="customPresets"
        @apply-mode="onApplyMode"
      />
  
    </div>
  </template>
  
  <script setup>
  import { ref, reactive, onMounted } from 'vue'
  import { useToastStore } from '@/stores/toast'
  import api from '@/service/api'
  import ImageSectionPreview from '@/components/ImageSectionPreview.vue'
  
  const toastStore = useToastStore()
  
  const API_BASE    = '/image-sections'
  const CATEGORY_API = '/category'
  
  // ── Mode options ──────────────────────────────────────
  const MODE_OPTIONS = [
    { value: 'auto',        label: 'Auto',        icon: '⚡', slots: 'dynamic' },
    { value: 'single',      label: 'Single',      icon: '▬',  slots: '1–5 items' },
    { value: 'double',      label: 'Double',      icon: '▬▬', slots: '2 items' },
    { value: 'mixed',       label: 'Mixed',       icon: '⬛▪', slots: '3 items' },
    { value: 'triple',      label: 'Triple',      icon: '▬▬▬', slots: '3 items' },
    { value: 'quad',        label: 'Quad',        icon: '⊞',  slots: '4 items' },
    { value: 'asymLeft',    label: 'Asym Left',   icon: '◧',  slots: '3 items' },
    { value: 'asymRight',   label: 'Asym Right',  icon: '◨',  slots: '3 items' },
    { value: 'heroStrip',   label: 'Hero Strip',  icon: '⬛▬', slots: '4 items' },
    { value: 'spotlight',   label: 'Spotlight',   icon: '⬛',  slots: '1 item' },
    { value: 'mosaic',      label: 'Mosaic',      icon: '⊟',  slots: '5 items' },
    { value: 'ribbon',      label: 'Ribbon',      icon: '↔',  slots: '2–5 items' },
    { value: 'featureWide', label: 'Feature Wide',icon: '▬',  slots: '1 item' },
    { value: 'cinematic',   label: 'Cinematic',   icon: '🎬', slots: '1 item' },
    { value: 'stack',       label: 'Stack',       icon: '⧉',  slots: '2–5 items' },
    { value: 'marquee',     label: 'Marquee',     icon: '↩',  slots: '2–5 items' },
    { value: 'filmStrip',   label: 'Film Strip',  icon: '🎞',  slots: '2–5 items' },
  ]
  
  // ── Extra presets to inject into preview (optional per-page customization) ──
  // Add/remove presets here or pass them from parent if this page is itself a component
  const customPresets = [
    // Example: { label: 'Promo', icon: '🎉', url: 'http://localhost:3000/promo' },
  ]
  
  // ── State ─────────────────────────────────────────────
  const sections       = ref([])
  const categoriesList = ref([])
  const brandsList     = ref([])
  const productOptions = ref([])
  const isLoading      = ref(true)
  const isSubmitting   = ref(false)
  
  const showSectionModal = ref(false)
  const showBannerModal  = ref(false)
  const showDeleteModal  = ref(false)
  const showPreview      = ref(false)
  
  const deleteType   = ref('section')
  const itemToDelete = ref(null)
  
  // ── Destination System State ──────────────────────────
  const DESTINATION_TYPES = [
    { type: 'category',  label: 'Kategori',  icon: '📁' },
    { type: 'brand',     label: 'Brand',     icon: '🏷️' },
    { type: 'product',   label: 'Produk',    icon: '📦' },
    { type: 'promo',     label: 'Promo',     icon: '🎉' },
    { type: 'search',    label: 'Cari/Filter', icon: '🔍' },
    { type: 'custom',    label: 'Internal',  icon: '🔗' },
    { type: 'external',  label: 'External',  icon: '🌐' }
  ]
  const destinationType  = ref('category')
  const destCategorySlug = ref('')
  const destBrandSlug    = ref('')
  const destProductSlug  = ref('')
  const destProductSearch= ref('')
  const destSearchQuery  = ref('')

  let searchTimeout = null
  const onProductSearch = () => {
    if (searchTimeout) clearTimeout(searchTimeout)
    searchTimeout = setTimeout(async () => {
      const q = destProductSearch.value.trim()
      if (!q) return
      try {
        const res = await api.get(`/stock/public?q=${encodeURIComponent(q)}&limit=10`)
        productOptions.value = res.data?.data || res.data?.items || []
      } catch (e) {
        console.error('Failed to search stock', e)
      }
    }, 300)
  }

  const setDestinationType = (type) => {
    destinationType.value = type
    buildTargetUrl()
  }

  const buildTargetUrl = () => {
    if (destinationType.value === 'category' && destCategorySlug.value) {
      bannerForm.target_url = `/category/${destCategorySlug.value}`
    } else if (destinationType.value === 'brand' && destBrandSlug.value) {
      bannerForm.target_url = `/brands/${destBrandSlug.value}`
    } else if (destinationType.value === 'product' && destProductSlug.value) {
      bannerForm.target_url = `/product/${destProductSlug.value}`
    } else if (destinationType.value === 'promo') {
      bannerForm.target_url = `/promo`
    } else if (destinationType.value === 'search' && destSearchQuery.value.trim()) {
      bannerForm.target_url = `/search?q=${encodeURIComponent(destSearchQuery.value.trim())}`
    } else if (destinationType.value === 'custom') {
      if (!bannerForm.target_url || !bannerForm.target_url.startsWith('/')) {
        bannerForm.target_url = '/'
      }
    } else if (destinationType.value === 'external') {
      if (!bannerForm.target_url || !bannerForm.target_url.startsWith('http')) {
        bannerForm.target_url = 'https://'
      }
    }
  }
  
  const sectionForm = reactive({
    uuid: null,
    identifier: '',
    title: '',
    mode: 'auto',
    is_active: true,
  })
  
  const bannerForm = reactive({
    targetIdentifier: '',
    target_url: '',
    alt_text: '',
    order: 1,
  })
  
  const fileInput    = ref(null)
  const selectedFile = ref(null)
  const imagePreview = ref(null)
  const isDragging   = ref(false)
  
  // Preview
  const previewSection = ref(null)
  
  // ── Fetch ─────────────────────────────────────────────
  const fetchSections = async () => {
    isLoading.value = true
    try {
      const res = await api.get(API_BASE)
      sections.value = res.data.data || []
    } catch (e) {
      console.error(e)
    } finally {
      isLoading.value = false
    }
  }
  
  const fetchCategories = async () => {
    try {
      const res = await api.get(`${CATEGORY_API}/`)
      categoriesList.value = res.data?.data || res.data || []
    } catch (e) {
      console.error(e)
    }
  }

  const fetchBrands = async () => {
    try {
      const res = await api.get('/brandlogo/public')
      brandsList.value = res.data?.data || res.data || []
    } catch (e) {
      console.error(e)
    }
  }
  
  // ── Modal controllers ─────────────────────────────────
  const openSectionModal = (section = null) => {
    if (section) {
      sectionForm.uuid       = section.uuid
      sectionForm.identifier = section.identifier
      sectionForm.title      = section.title
      sectionForm.mode       = section.mode || 'auto'
      sectionForm.is_active  = section.is_active
    } else {
      sectionForm.uuid       = null
      sectionForm.identifier = ''
      sectionForm.title      = ''
      sectionForm.mode       = 'auto'
      sectionForm.is_active  = true
    }
    showSectionModal.value = true
  }
  
  const openBannerModal = (identifier, defaultOrder) => {
    bannerForm.targetIdentifier = identifier
    bannerForm.target_url       = ''
    bannerForm.alt_text         = ''
    bannerForm.order            = Math.min(defaultOrder, 5)
    selectedFile.value          = null
    imagePreview.value          = null
    showBannerModal.value       = true
  }
  
  const closeModals = () => {
    if (isSubmitting.value) return
    showSectionModal.value = false
    showBannerModal.value  = false
  }
  
  // ── Auto fill ─────────────────────────────────────────
  const ROUTE_PRESETS = [
    { identifier: 'home:promo-strip', title: 'Banner Promo Eksklusif Strip (Pre-Footer)', mode: 'single', tag: 'Pre-Footer' },
    { identifier: 'home:hero-carousel', title: 'Hero Carousel Utama Homepage', mode: 'auto', tag: 'Hero Utama' },
    { identifier: 'promo:ramadan-sale', title: 'Banner Promo Eksklusif / Event', mode: 'single', tag: 'Promo Event' },
    { identifier: 'category:kamera-cctv', title: 'Banner Kategori Kamera CCTV', mode: 'single', tag: 'Katalog Kamera' },
  ]

  const applyPreset = (preset) => {
    sectionForm.identifier = preset.identifier
    sectionForm.title      = preset.title
    sectionForm.mode       = preset.mode || 'single'
  }

  const autoFillFromCategory = (e) => {
    const slug = e.target.value
    if (!slug) return
    const name = e.target.options[e.target.selectedIndex].dataset.name
    sectionForm.identifier = `category:${slug}`
    sectionForm.title      = `Banner ${name}`
    e.target.value = ''
  }
  
  // ── File handling ─────────────────────────────────────
  const triggerFileInput = () => fileInput.value?.click()
  
  const processFile = (file) => {
    if (!file) return
    if (file.size > 2 * 1024 * 1024) { toastStore.warning('Ukuran gambar maksimal 2MB'); return }
    if (!file.type.startsWith('image/')) { toastStore.warning('Format file harus berupa gambar'); return }
    selectedFile.value = file
    const reader = new FileReader()
    reader.onload = (e) => { imagePreview.value = e.target.result }
    reader.readAsDataURL(file)
  }
  
  const handleFileChange = (e) => processFile(e.target.files[0])
  const handleDrop = (e) => {
    isDragging.value = false
    processFile(e.dataTransfer?.files[0])
  }
  
  // ── Save Section ──────────────────────────────────────
  const saveSection = async () => {
    if (!sectionForm.identifier || !sectionForm.title) {
      toastStore.warning('Identifier dan Judul wajib diisi.')
      return
    }
    isSubmitting.value = true
    try {
      const payload = {
        identifier: sectionForm.identifier,
        title:      sectionForm.title,
        mode:       sectionForm.mode,
        is_active:  sectionForm.is_active,
      }
      if (sectionForm.uuid) {
        await api.put(`${API_BASE}/${sectionForm.uuid}`, payload)
      } else {
        await api.post(API_BASE, payload)
      }
      await fetchSections()
      closeModals()
      toastStore.success('Section berhasil disimpan.')
    } catch (e) {
      toastStore.error(e.response?.data?.detail || 'Gagal menyimpan section.')
    } finally {
      isSubmitting.value = false
    }
  }
  
  // ── Save Banner ───────────────────────────────────────
  const saveBanner = async () => {
    if (!selectedFile.value)           { toastStore.warning('Pilih gambar terlebih dahulu.'); return }
    if (!bannerForm.target_url.trim()) { toastStore.warning('Target URL wajib diisi.'); return }
  
    isSubmitting.value = true
    const fd = new FormData()
    fd.append('file', selectedFile.value)
    fd.append('target_url', bannerForm.target_url.trim())
    if (bannerForm.alt_text) fd.append('alt_text', bannerForm.alt_text)
    fd.append('order', String(bannerForm.order))
  
    try {
      const res = await fetch(
        `http://localhost:8000/image-sections/${encodeURIComponent(bannerForm.targetIdentifier)}/upload-banner`,
        { method: 'POST', body: fd },
      )
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Upload gagal')
      await fetchSections()
      closeModals()
      toastStore.success('Banner berhasil diupload.')
    } catch (e) {
      toastStore.error(e.message)
    } finally {
      isSubmitting.value = false
    }
  }
  
  // ── Delete ────────────────────────────────────────────
  const confirmDelete = (type, id) => {
    deleteType.value      = type
    itemToDelete.value    = id
    showDeleteModal.value = true
  }
  
  const executeDelete = async () => {
    if (!itemToDelete.value) return
    isSubmitting.value = true
    try {
      if (deleteType.value === 'section') {
        await api.delete(`${API_BASE}/${itemToDelete.value}`)
      } else {
        await api.delete(`${API_BASE}/items/${itemToDelete.value}`)
      }
      await fetchSections()
      showDeleteModal.value = false
      toastStore.success('Data berhasil dihapus.')
    } catch (e) {
      toastStore.error(e.response?.data?.detail || 'Gagal menghapus.')
    } finally {
      isSubmitting.value = false
      itemToDelete.value = null
    }
  }
  
  // ── Preview ───────────────────────────────────────────
  const openPreview = (section) => {
    previewSection.value = section
    showPreview.value    = true
  }
  
  /**
   * Called when user clicks "Terapkan mode" inside the preview component.
   * @param {{ section: Object, mode: string }} payload
   */
  const onApplyMode = async ({ section, mode }) => {
    isSubmitting.value = true
    try {
      await api.put(`${API_BASE}/${section.uuid}`, { mode })
      await fetchSections()
      // Keep preview section reference fresh
      previewSection.value = sections.value.find(s => s.uuid === section.uuid) ?? null
      toastStore.success('Mode layout berhasil diperbarui.')
    } catch (e) {
      toastStore.error(e.response?.data?.detail || 'Gagal mengupdate mode.')
    } finally {
      isSubmitting.value = false
    }
  }
  
  // ── Init ──────────────────────────────────────────────
  onMounted(() => {
    fetchSections()
    fetchCategories()
    fetchBrands()
  })
  </script>
  
  <style scoped>
  /* ══════════════════════════════════════════
     BASE
  ══════════════════════════════════════════ */
  .admin-wrap {
    max-width: 1080px;
    margin: 0 auto;
    padding: 32px 24px 80px;
    font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif;
    color: #111;
    -webkit-font-smoothing: antialiased;
  }
  
  /* ══════════════════════════════════════════
     HEADER
  ══════════════════════════════════════════ */
  .admin-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 28px;
  }
  .admin-header__title {
    font-size: 20px;
    font-weight: 700;
    letter-spacing: -0.3px;
    margin: 0;
  }
  .admin-header__sub { font-size: 13px; color: #888; margin: 3px 0 0; }
  
  /* ══════════════════════════════════════════
     BUTTONS
  ══════════════════════════════════════════ */
  .btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 600;
    border-radius: 8px;
    border: none;
    cursor: pointer;
    transition: background 150ms, opacity 150ms, transform 100ms;
    white-space: nowrap;
  }
  .btn:active { transform: scale(0.97); }
  .btn:disabled { opacity: 0.55; cursor: not-allowed; }
  .btn--primary { background: #111; color: #fff; }
  .btn--primary:hover:not(:disabled) { background: #333; }
  .btn--ghost { background: transparent; color: #555; border: 1px solid #e0e0e0; }
  .btn--ghost:hover { background: #f5f5f5; }
  .btn--danger { background: #dc2626; color: #fff; }
  .btn--danger:hover:not(:disabled) { background: #b91c1c; }
  .btn--sm { padding: 6px 12px; font-size: 12px; }
  
  .icon-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 30px;
    height: 30px;
    border-radius: 6px;
    border: none;
    background: transparent;
    color: #888;
    cursor: pointer;
    transition: background 120ms, color 120ms;
    padding: 0;
  }
  .icon-btn:hover { background: #f0f0f0; color: #111; }
  .icon-btn--danger:hover { background: #fef2f2; color: #dc2626; }
  
  /* ══════════════════════════════════════════
     BADGES
  ══════════════════════════════════════════ */
  .badge {
    display: inline-flex;
    align-items: center;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.2px;
    text-transform: uppercase;
  }
  .badge--green { background: #dcfce7; color: #15803d; }
  .badge--gray  { background: #f1f1f1; color: #777; }
  .badge--mode  { background: #eff6ff; color: #1d4ed8; font-family: monospace; text-transform: none; }
  
  /* ══════════════════════════════════════════
     SKELETON
  ══════════════════════════════════════════ */
  .skeleton-list { display: flex; flex-direction: column; gap: 16px; }
  .skeleton-card {
    background: #fff;
    border: 1px solid #e8e8e8;
    border-radius: 10px;
    overflow: hidden;
  }
  .skeleton-card__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid #f0f0f0;
    background: #fafafa;
  }
  .skeleton-card__body {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    padding: 16px 20px;
  }
  .skel {
    background: #f0f0f0;
    border-radius: 6px;
    animation: shimmer 1.4s ease-in-out infinite;
  }
  @keyframes shimmer { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
  .skel--title { height: 16px; width: 160px; }
  .skel--badge { height: 22px; width: 60px; }
  .skel--img   { aspect-ratio: 16/9; }
  
  /* ══════════════════════════════════════════
     EMPTY STATE
  ══════════════════════════════════════════ */
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 64px 24px;
    border: 1px dashed #d0d0d0;
    border-radius: 10px;
    text-align: center;
  }
  .empty-state__icon {
    width: 48px;
    height: 48px;
    background: #f5f5f5;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 16px;
    color: #aaa;
  }
  .empty-state__title { font-size: 15px; font-weight: 600; margin: 0 0 6px; }
  .empty-state__desc  { font-size: 13px; color: #888; margin: 0 0 20px; max-width: 320px; }
  
  /* ══════════════════════════════════════════
     SECTION CARD
  ══════════════════════════════════════════ */
  .section-list { display: flex; flex-direction: column; gap: 16px; }
  .section-card {
    background: #fff;
    border: 1px solid #e8e8e8;
    border-radius: 10px;
    overflow: hidden;
  }
  .section-card__head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 18px;
    background: #fafafa;
    border-bottom: 1px solid #f0f0f0;
    gap: 12px;
  }
  .section-card__title-row {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }
  .section-card__title {
    font-size: 14px;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.1px;
  }
  .section-card__id {
    display: flex;
    align-items: center;
    gap: 5px;
    margin-top: 4px;
    color: #999;
  }
  .section-card__id code {
    font-size: 11px;
    background: #f0f0f0;
    padding: 2px 6px;
    border-radius: 4px;
    color: #555;
    font-family: 'SF Mono', Menlo, monospace;
  }
  .section-card__actions {
    display: flex;
    align-items: center;
    gap: 4px;
    flex-shrink: 0;
  }
  .section-card__body { padding: 16px 18px; }
  
  /* ══════════════════════════════════════════
     BANNER GRID
  ══════════════════════════════════════════ */
  .banner-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 12px;
  }
  .banner-item {
    position: relative;
    border: 1px solid #e8e8e8;
    border-radius: 8px;
    overflow: hidden;
    background: #fff;
  }
  .banner-item__order {
    position: absolute;
    top: 6px;
    left: 6px;
    z-index: 2;
    background: rgba(0,0,0,.6);
    color: #fff;
    font-size: 10px;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 4px;
    backdrop-filter: blur(4px);
  }
  .banner-item__delete {
    position: absolute;
    top: 6px;
    right: 6px;
    z-index: 2;
    width: 22px;
    height: 22px;
    border-radius: 4px;
    background: rgba(255,255,255,.9);
    border: none;
    color: #dc2626;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 150ms;
  }
  .banner-item:hover .banner-item__delete { opacity: 1; }
  .banner-item__img {
    aspect-ratio: 16/9;
    overflow: hidden;
    background: #f5f5f5;
  }
  .banner-item__img img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    transition: transform 300ms;
  }
  .banner-item:hover .banner-item__img img { transform: scale(1.04); }
  .banner-item__info {
    padding: 8px 10px;
    border-top: 1px solid #f0f0f0;
  }
  .banner-item__url {
    display: block;
    font-size: 11px;
    color: #1d4ed8;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    text-decoration: none;
  }
  .banner-item__url:hover { text-decoration: underline; }
  .banner-item__alt {
    display: block;
    font-size: 10px;
    color: #aaa;
    margin-top: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .banner-add {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
    aspect-ratio: 16/9;
    border: 1px dashed #d0d0d0;
    border-radius: 8px;
    background: #fafafa;
    cursor: pointer;
    color: #aaa;
    font-size: 12px;
    font-weight: 500;
    transition: border-color 150ms, color 150ms, background 150ms;
    padding: 0;
  }
  .banner-add:hover { border-color: #111; color: #111; background: #f5f5f5; }
  .banner-add small { font-size: 10px; color: #bbb; }
  
  /* ══════════════════════════════════════════
     MODAL
  ══════════════════════════════════════════ */
  .modal-overlay {
    position: fixed;
    inset: 0;
    z-index: 100;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 16px;
    background: rgba(0,0,0,.4);
    backdrop-filter: blur(3px);
  }
  .modal {
    position: relative;
    background: #fff;
    border-radius: 12px;
    width: 100%;
    border: 1px solid #e8e8e8;
    display: flex;
    flex-direction: column;
    max-height: 90vh;
    overflow: hidden;
  }
  .modal--sm { max-width: 380px; }
  .modal--md { max-width: 520px; }
  .modal__head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 20px;
    border-bottom: 1px solid #f0f0f0;
  }
  .modal__head h3 { font-size: 15px; font-weight: 700; margin: 0; }
  .modal__close {
    width: 28px;
    height: 28px;
    border-radius: 6px;
    border: none;
    background: transparent;
    color: #888;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 120ms;
  }
  .modal__close:hover { background: #f0f0f0; color: #111; }
  .modal__body {
    padding: 20px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  .modal__foot {
    padding: 14px 20px;
    border-top: 1px solid #f0f0f0;
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    background: #fafafa;
  }
  
  /* ══════════════════════════════════════════
     FORM FIELDS
  ══════════════════════════════════════════ */
  .field-group { display: flex; flex-direction: column; gap: 6px; }
  .field-group--grow { flex: 1; }
  .field-group--fixed { width: 80px; }
  .field-group--accent {
    background: #f8f9ff;
    border: 1px solid #e0e7ff;
    border-radius: 8px;
    padding: 12px;
  }
  .preset-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 4px;
  }
  .chip-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 10px;
    border-radius: 6px;
    border: 1px solid #e2e8f0;
    background: #ffffff;
    cursor: pointer;
    font-size: 11px;
    transition: all 150ms ease;
  }
  .chip-btn:hover {
    border-color: #03AC0E;
    background: #F0FBF2;
  }
  .chip-btn--active {
    border-color: #03AC0E;
    background: #E8F8EA;
    box-shadow: 0 0 0 1px #03AC0E;
  }
  .chip-btn__tag {
    font-weight: 700;
    color: #03AC0E;
    background: #E8F8EA;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 10px;
  }
  .chip-btn__id {
    font-family: 'SF Mono', Menlo, monospace;
    color: #334155;
    font-size: 11px;
  }
  .field-label { font-size: 12px; font-weight: 600; color: #555; }
  .field-label--sm { font-size: 11px; text-transform: uppercase; letter-spacing: 0.4px; color: #6366f1; }
  .field-req { color: #dc2626; margin-left: 2px; }
  .field-opt { font-weight: 400; color: #aaa; }
  .field-hint { font-size: 11px; color: #aaa; }
  .field-input {
    padding: 9px 12px;
    font-size: 13px;
    border: 1px solid #e0e0e0;
    border-radius: 7px;
    background: #fafafa;
    color: #111;
    outline: none;
    transition: border-color 150ms, background 150ms, box-shadow 150ms;
    width: 100%;
    box-sizing: border-box;
  }
  .field-input:focus { border-color: #111; background: #fff; box-shadow: 0 0 0 3px rgba(0,0,0,.06); }
  .field-input:disabled { opacity: 0.5; cursor: not-allowed; }
  .field-input--mono { font-family: 'SF Mono', Menlo, monospace; font-size: 12px; }
  .field-input--center { text-align: center; }
  
  /* ── Destination Type Selector ── */
  .dest-type-selector {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
    gap: 6px;
    margin-bottom: 4px;
  }
  .dest-type-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    padding: 8px 6px;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    background: #ffffff;
    cursor: pointer;
    transition: all 150ms ease;
  }
  .dest-type-btn:hover {
    border-color: #03AC0E;
    background: #F0FBF2;
  }
  .dest-type-btn--active {
    border-color: #03AC0E;
    background: #E8F8EA;
    box-shadow: 0 0 0 1px #03AC0E;
  }
  .dest-type-icon { font-size: 14px; }
  .dest-type-name { font-size: 11px; font-weight: 700; color: #1e293b; }
  .target-url-preview {
    background: #f8fafc;
    border-radius: 6px;
  }

  .field-select {
    padding: 8px 12px;
    font-size: 13px;
    border: 1px solid #e0e0e0;
    border-radius: 7px;
    background: #fff;
    color: #111;
    outline: none;
    cursor: pointer;
    transition: border-color 150ms;
    width: 100%;
  }
  .field-select:focus { border-color: #111; }
  .field-row { display: flex; gap: 12px; align-items: flex-start; }
  
  /* ══════════════════════════════════════════
     MODE GRID
  ══════════════════════════════════════════ */
  .mode-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(90px, 1fr));
    gap: 6px;
  }
  .mode-option {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 3px;
    padding: 10px 6px;
    border: 1px solid #e8e8e8;
    border-radius: 8px;
    background: #fafafa;
    cursor: pointer;
    transition: border-color 150ms, background 150ms;
    text-align: center;
  }
  .mode-option:hover { border-color: #aaa; background: #f5f5f5; }
  .mode-option--active { border-color: #111; background: #111; color: #fff; }
  .mode-option__icon  { font-size: 16px; line-height: 1; }
  .mode-option__label { font-size: 11px; font-weight: 600; }
  .mode-option__slots { font-size: 10px; color: #aaa; }
  
  /* ══════════════════════════════════════════
     TOGGLE
  ══════════════════════════════════════════ */
  .toggle-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 14px;
    background: #fafafa;
    border: 1px solid #f0f0f0;
    border-radius: 8px;
  }
  .toggle-row__label { font-size: 13px; font-weight: 600; margin: 0 0 2px; }
  .toggle-row__desc  { font-size: 11px; color: #888; margin: 0; }
  .toggle {
    position: relative;
    width: 42px;
    height: 24px;
    border-radius: 12px;
    background: #ddd;
    border: none;
    cursor: pointer;
    transition: background 200ms;
    flex-shrink: 0;
    padding: 0;
  }
  .toggle--on { background: #111; }
  .toggle__knob {
    position: absolute;
    top: 2px;
    left: 2px;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #fff;
    transition: transform 200ms;
    box-shadow: 0 1px 3px rgba(0,0,0,.2);
  }
  .toggle--on .toggle__knob { transform: translateX(18px); }
  
  /* ══════════════════════════════════════════
     DROP ZONE
  ══════════════════════════════════════════ */
  .dropzone {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    aspect-ratio: 16/9;
    border: 1px dashed #d0d0d0;
    border-radius: 8px;
    background: #fafafa;
    cursor: pointer;
    overflow: hidden;
    transition: border-color 150ms, background 150ms;
  }
  .dropzone:hover, .dropzone--drag { border-color: #111; background: #f5f5f5; }
  .dropzone--filled { border-style: solid; border-color: #e0e0e0; }
  .dropzone__icon  { color: #aaa; }
  .dropzone__label { font-size: 13px; font-weight: 500; color: #555; }
  .dropzone__hint  { font-size: 11px; color: #aaa; }
  .dropzone__input { display: none; }
  .dropzone__preview {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  .dropzone__overlay {
    position: absolute;
    inset: 0;
    background: rgba(0,0,0,.5);
    color: #fff;
    font-size: 13px;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 150ms;
  }
  .dropzone:hover .dropzone__overlay { opacity: 1; }
  
  /* ══════════════════════════════════════════
     TARGET BADGE
  ══════════════════════════════════════════ */
  .target-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 10px;
    background: #f5f5f5;
    border-radius: 6px;
    color: #555;
  }
  .target-badge code {
    font-size: 12px;
    font-family: monospace;
    color: #111;
    font-weight: 600;
  }
  
  /* ══════════════════════════════════════════
     DELETE MODAL
  ══════════════════════════════════════════ */
  .delete-desc { font-size: 13px; color: #555; line-height: 1.6; margin: 0; }
  
  /* ══════════════════════════════════════════
     MODAL TRANSITION (modal-fade)
  ══════════════════════════════════════════ */
  .modal-fade-enter-active, .modal-fade-leave-active {
    transition: opacity 0.25s ease;
  }
  .modal-fade-enter-active .modal, .modal-fade-leave-active .modal {
    transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.25s ease;
  }
  .modal-fade-enter-from, .modal-fade-leave-to {
    opacity: 0;
  }
  .modal-fade-enter-from .modal {
    transform: scale(0.95) translateY(12px);
    opacity: 0;
  }
  .modal-fade-leave-to .modal {
    transform: scale(0.95) translateY(10px);
    opacity: 0;
  }
  
  /* ══════════════════════════════════════════
     SPIN
  ══════════════════════════════════════════ */
  @keyframes spin { to { transform: rotate(360deg); } }
  .spin { animation: spin 700ms linear infinite; }
  
  /* ══════════════════════════════════════════
     RESPONSIVE
  ══════════════════════════════════════════ */
  @media (max-width: 640px) {
    .admin-wrap { padding: 20px 16px 60px; }
    .banner-grid { grid-template-columns: 1fr 1fr; }
    .mode-grid { grid-template-columns: repeat(3, 1fr); }
  }
  </style>