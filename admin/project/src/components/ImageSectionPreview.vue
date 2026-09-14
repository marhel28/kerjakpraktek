<template>
    <Teleport to="body">
      <Transition name="panel">
        <div v-if="modelValue" class="preview-overlay" @click.self="$emit('update:modelValue', false)">
          <div class="preview-panel">
  
            <!-- ── HEAD ── -->
            <div class="preview-panel__head">
              <div class="preview-panel__head-info">
                <h3>Preview</h3>
                <p>{{ section?.identifier }}</p>
              </div>
              <div class="preview-panel__controls">
  
                <!-- URL Switcher -->
                <div class="url-switcher">
                  <button
                    v-for="preset in mergedPresets"
                    :key="preset.url"
                    class="url-switcher__btn"
                    :class="{ 'url-switcher__btn--active': activeUrl === preset.url }"
                    :title="preset.label"
                    @click="setUrl(preset.url)"
                  >
                    <span class="url-switcher__icon">{{ preset.icon }}</span>
                    <span class="url-switcher__label">{{ preset.label }}</span>
                  </button>
                  <!-- Custom URL input toggle -->
                  <button
                    class="url-switcher__btn url-switcher__btn--custom"
                    :class="{ 'url-switcher__btn--active': isCustomUrl }"
                    title="Custom URL"
                    @click="toggleCustomInput"
                  >
                    <span class="url-switcher__icon">✏️</span>
                    <span class="url-switcher__label">Custom</span>
                  </button>
                </div>
  
                <!-- Mode Switch -->
                <div v-if="!hideModePicker" class="preview-mode-switch">
                  <button
                    v-for="m in modeOptions"
                    :key="m.value"
                    class="pms__btn"
                    :class="{ 'pms__btn--active': localMode === m.value }"
                    :title="m.label"
                    @click="localMode = m.value"
                  >{{ m.icon }}</button>
                </div>
  
                <button class="icon-btn" @click="doRefresh" title="Refresh">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" :class="{ 'spin': isRefreshing }">
                    <polyline points="23 4 23 10 17 10"/>
                    <path d="M20.49 15a9 9 0 11-2.12-9.36L23 10"/>
                  </svg>
                </button>
                <button class="icon-btn" @click="$emit('update:modelValue', false)">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                  </svg>
                </button>
              </div>
            </div>
  
            <!-- Custom URL bar (shown when custom is selected) -->
            <Transition name="slide-down">
              <div v-if="showCustomInput" class="custom-url-bar">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="custom-url-bar__icon">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="2" y1="12" x2="22" y2="12"/>
                  <path d="M12 2a15.3 15.3 0 010 20M12 2a15.3 15.3 0 000 20"/>
                </svg>
                <input
                  v-model="customUrlInput"
                  type="text"
                  class="custom-url-bar__input"
                  placeholder="http://localhost:3000/your/path"
                  @keydown.enter="applyCustomUrl"
                />
                <button class="btn btn--xs btn--primary" @click="applyCustomUrl">Go</button>
              </div>
            </Transition>
  
            <!-- ── BODY ── -->
            <div class="preview-panel__body">
  
              <!-- Device Frame -->
              <div class="preview-device">
                <div class="preview-device__bar">
                  <span></span><span></span><span></span>
                  <div class="preview-device__url">
                    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <circle cx="12" cy="12" r="10"/>
                      <line x1="2" y1="12" x2="22" y2="12"/>
                      <path d="M12 2a15.3 15.3 0 010 20M12 2a15.3 15.3 0 000 20"/>
                    </svg>
                    {{ activeUrl }}
                  </div>
                </div>
                <div class="preview-device__screen">
                  <iframe
                    :key="iframeKey"
                    :src="activeUrl"
                    class="preview-device__iframe"
                    sandbox="allow-scripts allow-same-origin"
                  />
                </div>
              </div>
  
              <!-- Info Panel -->
              <div class="preview-info">
                <div v-if="!hideModePicker" class="preview-info__section">
                  <p class="preview-info__label">Mode Aktif</p>
                  <span class="badge badge--blue">{{ localMode }}</span>
                </div>
                <div class="preview-info__section">
                  <p class="preview-info__label">Banner Aktif</p>
                  <p class="preview-info__val">{{ section?.items?.length ?? 0 }} item</p>
                </div>
                <div v-if="!hideModePicker" class="preview-info__section">
                  <p class="preview-info__label">Auto Mode</p>
                  <p class="preview-info__val preview-info__val--muted">{{ getAutoMode(section?.items?.length ?? 0) }}</p>
                </div>
                <div class="preview-info__section">
                  <p class="preview-info__label">URL Preview</p>
                  <p class="preview-info__val preview-info__val--muted preview-info__val--url" :title="activeUrl">{{ activeUrl }}</p>
                </div>
                <button
                  v-if="!hideModePicker"
                  class="btn btn--sm btn--outline preview-apply-btn"
                  :disabled="isApplying"
                  @click="onApplyMode"
                >
                  <svg v-if="isApplying" class="spin" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke-opacity=".3"/>
                    <path d="M21 12a9 9 0 00-9-9"/>
                  </svg>
                  Terapkan "{{ localMode }}"
                </button>
              </div>
  
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </template>
  
  <script setup>
  import { ref, watch, computed } from 'vue'
  
  // ── Props & Emits ────────────────────────────────────────
  const props = defineProps({
    /** v-model: visible state */
    modelValue: {
      type: Boolean,
      default: false,
    },
    /** The section object being previewed */
    section: {
      type: Object,
      default: null,
    },
    /** Extra URL presets to inject (merged with defaults) */
    extraPresets: {
      type: Array,
      default: () => [],
    },
    /** Initial URL override */
    initialUrl: {
      type: String,
      default: '',
    },
    /** Whether the apply-mode button is in loading state */
    isApplying: {
      type: Boolean,
      default: false,
    },
    /** Hide the mode picker and apply button (for pages that don't use layout modes) */
    hideModePicker: {
      type: Boolean,
      default: false,
    },
  })
  
  const emit = defineEmits([
    'update:modelValue',
    /** payload: { section, mode } */
    'apply-mode',
  ])
  
  // ── Default URL Presets ──────────────────────────────────
  const DEFAULT_PRESETS = [
    { label: 'Home',     icon: '🏠', url: 'http://localhost:3000/' },
    { label: 'Category', icon: '📁', url: 'http://localhost:3000/category/security-alarm' },
    { label: 'Sub Cat',  icon: '📂', url: 'http://localhost:3000/category/kamera-cctv/kamera-cctv-series-c?category=kamera-cctv&category=kamera-cctv-series-c' },
    { label: 'Search',   icon: '🔍', url: 'http://localhost:3000/search' },
  ]
  
  const mergedPresets = computed(() => [...DEFAULT_PRESETS, ...props.extraPresets])
  
  // ── Mode Options (same as parent) ────────────────────────
  const modeOptions = [
    { value: 'auto',        label: 'Auto',        icon: '⚡' },
    { value: 'single',      label: 'Single',      icon: '▬'  },
    { value: 'double',      label: 'Double',      icon: '▬▬' },
    { value: 'mixed',       label: 'Mixed',       icon: '⬛▪' },
    { value: 'triple',      label: 'Triple',      icon: '▬▬▬' },
    { value: 'quad',        label: 'Quad',        icon: '⊞'  },
    { value: 'asymLeft',    label: 'Asym Left',   icon: '◧'  },
    { value: 'asymRight',   label: 'Asym Right',  icon: '◨'  },
    { value: 'heroStrip',   label: 'Hero Strip',  icon: '⬛▬' },
    { value: 'spotlight',   label: 'Spotlight',   icon: '⬛'  },
    { value: 'mosaic',      label: 'Mosaic',      icon: '⊟'  },
    { value: 'ribbon',      label: 'Ribbon',      icon: '↔'  },
    { value: 'featureWide', label: 'Feature Wide',icon: '▬'  },
    { value: 'cinematic',   label: 'Cinematic',   icon: '🎬' },
    { value: 'stack',       label: 'Stack',       icon: '⧉'  },
    { value: 'marquee',     label: 'Marquee',     icon: '↩'  },
    { value: 'filmStrip',   label: 'Film Strip',  icon: '🎞'  },
  ]
  
  function getAutoMode(count) {
    if (count === 1) return 'cinematic'
    if (count === 2) return 'double'
    if (count === 3) return 'mixed'
    if (count === 4) return 'quad'
    if (count === 5) return 'heroStrip'
    return 'single'
  }
  
  // ── State ────────────────────────────────────────────────
  const localMode       = ref('auto')
  const activeUrl       = ref(DEFAULT_PRESETS[0].url)
  const iframeKey       = ref(0)
  const isRefreshing    = ref(false)
  const showCustomInput = ref(false)
  const customUrlInput  = ref('')
  const isCustomUrl     = ref(false)
  
  // Sync localMode & initialUrl when section/panel opens
  watch(
    () => [props.section, props.modelValue],
    ([section, visible]) => {
      if (!visible) return
      localMode.value = section?.mode || 'auto'
      if (props.initialUrl) {
        activeUrl.value = props.initialUrl
        isCustomUrl.value = !mergedPresets.value.some(p => p.url === props.initialUrl)
      } else {
        // Auto-pick a preset that makes sense based on identifier
        const id = section?.identifier ?? ''
        if (id.startsWith('category:')) {
          const slug = id.replace('category:', '')
          // Try to build a matching URL from presets or construct one
          const catPreset = mergedPresets.value.find(p => p.url.includes('/category/'))
          activeUrl.value = catPreset
            ? `http://localhost:3000/category/${slug}`
            : DEFAULT_PRESETS[0].url
        } else {
          activeUrl.value = DEFAULT_PRESETS[0].url
        }
        isCustomUrl.value = false
      }
      iframeKey.value++
    },
  )
  
  // ── URL Controls ─────────────────────────────────────────
  const setUrl = (url) => {
    activeUrl.value   = url
    isCustomUrl.value = false
    showCustomInput.value = false
    iframeKey.value++
  }
  
  const toggleCustomInput = () => {
    showCustomInput.value = !showCustomInput.value
    if (showCustomInput.value) {
      customUrlInput.value = activeUrl.value
    }
  }
  
  const applyCustomUrl = () => {
    if (!customUrlInput.value.trim()) return
    activeUrl.value   = customUrlInput.value.trim()
    isCustomUrl.value = true
    showCustomInput.value = false
    iframeKey.value++
  }
  
  // ── Refresh ──────────────────────────────────────────────
  const doRefresh = () => {
    isRefreshing.value = true
    iframeKey.value++
    setTimeout(() => { isRefreshing.value = false }, 800)
  }
  
  // ── Apply Mode ───────────────────────────────────────────
  const onApplyMode = () => {
    emit('apply-mode', { section: props.section, mode: localMode.value })
  }
  </script>
  
  <style scoped>
  /* ══════════════════════════════════════════
     PREVIEW OVERLAY / PANEL
  ══════════════════════════════════════════ */
  .preview-overlay {
    position: fixed;
    inset: 0;
    z-index: 200;
    background: rgba(0,0,0,.5);
    backdrop-filter: blur(4px);
    display: flex;
    align-items: stretch;
    justify-content: flex-end;
  }
  
  .preview-panel {
    width: min(960px, 95vw);
    height: 100%;
    background: #f8f8f8;
    display: flex;
    flex-direction: column;
    border-left: 1px solid #e0e0e0;
    overflow: hidden;
  }
  
  /* ── Head ── */
  .preview-panel__head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    background: #fff;
    border-bottom: 1px solid #e8e8e8;
    gap: 12px;
    flex-shrink: 0;
    flex-wrap: wrap;
  }
  .preview-panel__head-info h3 {
    font-size: 14px;
    font-weight: 700;
    margin: 0 0 2px;
    font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
  }
  .preview-panel__head-info p {
    font-size: 11px;
    color: #888;
    margin: 0;
    font-family: monospace;
  }
  .preview-panel__controls {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }
  
  /* ── URL Switcher ── */
  .url-switcher {
    display: flex;
    background: #f0f0f0;
    border-radius: 7px;
    padding: 2px;
    gap: 2px;
  }
  .url-switcher__btn {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 4px 9px;
    border-radius: 5px;
    border: none;
    background: transparent;
    font-size: 11px;
    font-weight: 500;
    cursor: pointer;
    color: #777;
    transition: background 120ms, color 120ms;
    white-space: nowrap;
    font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
  }
  .url-switcher__btn:hover { background: #e0e0e0; color: #111; }
  .url-switcher__btn--active { background: #fff; color: #111; box-shadow: 0 1px 3px rgba(0,0,0,.1); }
  .url-switcher__icon { font-size: 12px; line-height: 1; }
  .url-switcher__label { font-size: 11px; }
  .url-switcher__btn--custom { border-left: 1px solid #ddd; margin-left: 2px; }
  
  /* ── Custom URL Bar ── */
  .custom-url-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    background: #fffbeb;
    border-bottom: 1px solid #fde68a;
    flex-shrink: 0;
  }
  .custom-url-bar__icon { color: #92400e; flex-shrink: 0; }
  .custom-url-bar__input {
    flex: 1;
    padding: 6px 10px;
    font-size: 12px;
    font-family: monospace;
    border: 1px solid #fcd34d;
    border-radius: 6px;
    background: #fff;
    color: #111;
    outline: none;
  }
  .custom-url-bar__input:focus { border-color: #f59e0b; box-shadow: 0 0 0 2px rgba(245,158,11,.15); }
  
  /* ── Mode Switch ── */
  .preview-mode-switch {
    display: flex;
    background: #f0f0f0;
    border-radius: 7px;
    padding: 2px;
    gap: 2px;
    flex-wrap: wrap;
    max-width: 420px;
  }
  .pms__btn {
    padding: 4px 8px;
    border-radius: 5px;
    border: none;
    background: transparent;
    font-size: 13px;
    cursor: pointer;
    color: #888;
    transition: background 120ms, color 120ms;
    line-height: 1;
  }
  .pms__btn:hover { background: #e0e0e0; color: #111; }
  .pms__btn--active { background: #fff; color: #111; box-shadow: 0 1px 3px rgba(0,0,0,.1); }
  
  /* ── Icon Button ── */
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
  
  /* ── Body ── */
  .preview-panel__body {
    display: flex;
    flex-direction: column;
    flex: 1;
    overflow: hidden;
  }
  
  /* ── Device Frame ── */
  .preview-device {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    margin: 14px 14px 0;
    background: #fff;
    border-radius: 10px;
    border: 1px solid #e0e0e0;
    box-shadow: 0 4px 24px rgba(0,0,0,.08);
  }
  .preview-device__bar {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 9px 12px;
    background: #f5f5f5;
    border-bottom: 1px solid #e8e8e8;
    border-radius: 10px 10px 0 0;
    flex-shrink: 0;
  }
  .preview-device__bar span {
    width: 10px;
    height: 10px;
    border-radius: 50%;
  }
  .preview-device__bar span:nth-child(1) { background: #fc5c5c; }
  .preview-device__bar span:nth-child(2) { background: #fdbc3d; }
  .preview-device__bar span:nth-child(3) { background: #33c748; }
  .preview-device__url {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 5px;
    margin: 0 8px;
    background: #fff;
    border: 1px solid #e8e8e8;
    border-radius: 5px;
    padding: 4px 10px;
    font-size: 11px;
    color: #888;
    font-family: monospace;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }
  .preview-device__screen {
    flex: 1;
    overflow: hidden;
    border-radius: 0 0 10px 10px;
    position: relative;
  }
  .preview-device__iframe {
    width: 100%;
    height: 100%;
    border: none;
    display: block;
  }
  
  /* ── Info Bar ── */
  .preview-info {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 10px 14px;
    background: #fff;
    border-top: 1px solid #e8e8e8;
    margin: 0 14px 14px;
    border-radius: 0 0 10px 10px;
    flex-shrink: 0;
    flex-wrap: wrap;
  }
  .preview-info__section { display: flex; flex-direction: column; gap: 3px; }
  .preview-info__label {
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    color: #aaa;
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
  }
  .preview-info__val {
    font-size: 12px;
    font-weight: 600;
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
  }
  .preview-info__val--muted { color: #888; font-weight: 400; }
  .preview-info__val--url {
    max-width: 180px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-family: monospace;
    font-size: 11px;
  }
  .preview-apply-btn { margin-left: auto; }
  
  /* ── Badges ── */
  .badge {
    display: inline-flex;
    align-items: center;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.2px;
    font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
  }
  .badge--blue { background: #eff6ff; color: #1d4ed8; }
  
  /* ── Buttons ── */
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
    font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
  }
  .btn:active { transform: scale(0.97); }
  .btn:disabled { opacity: 0.55; cursor: not-allowed; }
  .btn--primary { background: #111; color: #fff; }
  .btn--primary:hover:not(:disabled) { background: #333; }
  .btn--outline { background: transparent; color: #111; border: 1px solid #ddd; }
  .btn--outline:hover { background: #f5f5f5; }
  .btn--sm { padding: 6px 12px; font-size: 12px; }
  .btn--xs { padding: 4px 10px; font-size: 11px; border-radius: 6px; }
  
  /* ── Transitions ── */
  .panel-enter-active,
  .panel-leave-active { transition: opacity 200ms; }
  .panel-enter-active .preview-panel,
  .panel-leave-active .preview-panel { transition: transform 250ms cubic-bezier(0.4, 0, 0.2, 1); }
  .panel-enter-from,
  .panel-leave-to { opacity: 0; }
  .panel-enter-from .preview-panel,
  .panel-leave-to .preview-panel { transform: translateX(100%); }
  
  .slide-down-enter-active,
  .slide-down-leave-active { transition: max-height 200ms ease, opacity 200ms; }
  .slide-down-enter-from,
  .slide-down-leave-to { max-height: 0; opacity: 0; overflow: hidden; }
  .slide-down-enter-to,
  .slide-down-leave-from { max-height: 60px; opacity: 1; }
  
  @keyframes spin { to { transform: rotate(360deg); } }
  .spin { animation: spin 700ms linear infinite; }
  
  /* ── Responsive ── */
  @media (max-width: 640px) {
    .preview-panel { width: 100vw; }
    .preview-info { gap: 12px; }
    .url-switcher__label { display: none; }
    .preview-mode-switch { max-width: 240px; }
  }
  </style>