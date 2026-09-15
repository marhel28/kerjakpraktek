<script setup>
/**
 * pages/admin/abouts/index.vue
 * Admin panel – About Us page manager
 */

import { ref, computed, reactive, watch, onMounted } from "vue";
import api from "@/service/api";
import ImageSectionPreview from "@/components/ImageSectionPreview.vue";
import { usePreviewStore } from "@/stores/previewStore";

const previewStore = usePreviewStore();

// ── Remote state ─────────────────────────────────────────────────
const pageData  = ref(null);
const isLoading = ref(true);

// ── Preview panel state ──────────────────────────────────────────
const showPreview = ref(false);

// ── Tab state ────────────────────────────────────────────────────
const activeTab = ref("hero");

// ── Toast ────────────────────────────────────────────────────────
const toast = ref(null);
function showToast(message, type = "success") {
  toast.value = { message, type };
  setTimeout(() => { toast.value = null; }, 3500);
}

// ── Form state ───────────────────────────────────────────────────
const form = reactive({
  hero_badge_text:    "",
  hero_heading:       "",
  hero_subheading:    "",
  cta_heading:        "",
  cta_body:           "",
  cta_primary_text:   "",
  cta_secondary_text: "",
  cta_secondary_url:  "",
  stats:  [],
  values: [],
});

function populateForm(d) {
  if (!d) return;
  form.hero_badge_text    = d.hero_badge_text    ?? "";
  form.hero_heading       = d.hero_heading       ?? "";
  form.hero_subheading    = d.hero_subheading    ?? "";
  form.cta_heading        = d.cta_heading        ?? "";
  form.cta_body           = d.cta_body           ?? "";
  form.cta_primary_text   = d.cta_primary_text   ?? "";
  form.cta_secondary_text = d.cta_secondary_text ?? "";
  form.cta_secondary_url  = d.cta_secondary_url  ?? "";
  form.stats  = d.stats?.map(s => ({ ...s }))  ?? [];
  form.values = d.values?.map(v => ({ ...v })) ?? [];
}

watch(pageData, populateForm);

// ── Fetch page ────────────────────────────────────────────────────
async function fetchPage() {
  isLoading.value = true;
  try {
    const res = await api.get("/abouts");
    pageData.value = res.data;
  } catch (e) {
    if (e?.response?.status !== 404) {
      showToast(e?.response?.data?.detail ?? "Gagal memuat data.", "error");
    }
    pageData.value = null;
  } finally {
    isLoading.value = false;
  }
}

// ── Gallery ───────────────────────────────────────────────────────
const gallery          = computed(() => pageData.value?.gallery ?? []);
const galleryUploading = ref(false);
const galleryFileInput = ref(null);
const galleryAlt       = ref("");

async function uploadGallery() {
  const file = galleryFileInput.value?.files?.[0];
  if (!file || !galleryAlt.value.trim()) {
    showToast("Pilih file dan isi caption dulu.", "error");
    return;
  }
  galleryUploading.value = true;
  try {
    const fd = new FormData();
    fd.append("file", file);
    fd.append("alt",  galleryAlt.value.trim());
    await api.post("/abouts/gallery", fd, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    galleryAlt.value = "";
    if (galleryFileInput.value) galleryFileInput.value.value = "";
    await fetchPage();
    showToast("Gambar berhasil diupload.");
  } catch (e) {
    showToast(e?.response?.data?.detail ?? "Upload gagal.", "error");
  } finally {
    galleryUploading.value = false;
  }
}

async function deleteGallery(id) {
  if (!confirm("Hapus gambar ini?")) return;
  try {
    await api.delete(`/abouts/gallery/${id}`);
    await fetchPage();
    showToast("Gambar dihapus.");
  } catch (e) {
    showToast(e?.response?.data?.detail ?? "Gagal hapus gambar.", "error");
  }
}

// ── Stats helpers ─────────────────────────────────────────────────
function addStat() {
  form.stats.push({ value: "", label: "", order: form.stats.length });
}
function removeStat(i) {
  form.stats.splice(i, 1);
  form.stats.forEach((s, idx) => { s.order = idx; });
}

// ── Values helpers ────────────────────────────────────────────────
const ICONS = [
  "lucide:shield-alert", "lucide:zap",          "lucide:badge-check",
  "lucide:smartphone",   "lucide:shield-check",  "lucide:eye",
  "lucide:lock",         "lucide:camera",
];
function addValue() {
  form.values.push({ icon: ICONS[0], title: "", desc: "", order: form.values.length });
}
function removeValue(i) {
  form.values.splice(i, 1);
  form.values.forEach((v, idx) => { v.order = idx; });
}

// ── Save ──────────────────────────────────────────────────────────
const isSaving = ref(false);

async function save() {
    if (form.stats.length === 0) {
    showToast("Minimal 1 stat harus diisi.", "error");
    activeTab.value = "stats"; // otomatis pindah tab ke stats
    return;
  }
  isSaving.value = true;
  try {
    const payload = {
      hero_badge_text:    form.hero_badge_text,
      hero_heading:       form.hero_heading,
      hero_subheading:    form.hero_subheading    || null,
      cta_heading:        form.cta_heading,
      cta_body:           form.cta_body           || null,
      cta_primary_text:   form.cta_primary_text,
      cta_secondary_text: form.cta_secondary_text,
      cta_secondary_url:  form.cta_secondary_url,
      stats:  form.stats.map((s, i)  => ({ value: s.value, label: s.label, order: i })),
      values: form.values.map((v, i) => ({ icon: v.icon, title: v.title, desc: v.desc, order: i })),
    };

    if (pageData.value?.id) {
      await api.patch("/abouts", payload);
    } else {
      await api.post("/abouts", payload);
    }

    await fetchPage();
    showToast("Perubahan berhasil disimpan!");
  } catch (e) {
    const msg = e?.response?.data?.detail;
    showToast(
      Array.isArray(msg) ? msg.map(m => m.msg).join(", ") : (msg ?? "Gagal menyimpan."),
      "error"
    );
  } finally {
    isSaving.value = false;
  }
}

// ── Icon path map ─────────────────────────────────────────────────
const iconPaths = {
  "lucide:shield-alert": "M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10zM12 8v4M12 16h.01",
  "lucide:zap":          "M13 2L3 14h9l-1 8 10-12h-9l1-8z",
  "lucide:badge-check":  "M3.85 8.62a4 4 0 0 1 4.78-4.77 4 4 0 0 1 6.74 0 4 4 0 0 1 4.78 4.78 4 4 0 0 1 0 6.74 4 4 0 0 1-4.77 4.78 4 4 0 0 1-6.75 0 4 4 0 0 1-4.78-4.77 4 4 0 0 1 0-6.76zM9 12l2 2 4-4",
  "lucide:smartphone":   "M17 2H7a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2zM12 18h.01",
  "lucide:shield-check": "M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10zM9 12l2 2 4-4",
  "lucide:eye":          "M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8zM12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6z",
  "lucide:lock":         "M19 11H5a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7a2 2 0 0 0-2-2zM7 11V7a5 5 0 0 1 10 0v4",
  "lucide:camera":       "M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2zM12 17a4 4 0 1 0 0-8 4 4 0 0 0 0 8z",
};
function getIconPath(name) {
  return iconPaths[name] ?? iconPaths["lucide:shield-check"];
}

// ── Tabs ──────────────────────────────────────────────────────────
const tabs = [
  { id: "hero",    label: "Hero",    icon: "⬡" },
  { id: "stats",   label: "Stats",   icon: "◈" },
  { id: "values",  label: "Values",  icon: "◆" },
  { id: "gallery", label: "Gallery", icon: "◉" },
  { id: "cta",     label: "CTA",     icon: "▶" },
];

// ── Init ──────────────────────────────────────────────────────────
onMounted(fetchPage);
</script>

<template>
  <div class="h-full max-w-7xl mx-auto flex flex-col font-sans text-gray-800">

    <!-- ══ HEADER ════════════════════════════════════════════════ -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-gray-900">Manajemen About Us</h1>
        <p class="mt-1 text-sm text-gray-500">Kelola konten halaman About Us — hero, stats, values, gallery, dan CTA.</p>
      </div>
      <div class="flex items-center gap-2 shrink-0">
        <button
          @click="showPreview = true"
          class="inline-flex items-center justify-center px-4 py-2.5 bg-white text-gray-700 text-sm font-semibold rounded-xl shadow-sm border border-gray-200 hover:bg-gray-50 active:scale-95 transition-all focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
        >
          <svg class="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
            <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
          </svg>
          Preview
        </button>
        <button
          @click="save"
          :disabled="isSaving"
          class="inline-flex items-center justify-center px-4 py-2.5 bg-indigo-600 text-white text-sm font-semibold rounded-xl shadow-sm hover:bg-indigo-700 active:scale-95 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-60 disabled:cursor-not-allowed"
        >
          <svg v-if="isSaving" class="animate-spin w-4 h-4 mr-1.5 text-white" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
          </svg>
          <svg v-else class="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z"/>
            <polyline points="17 21 17 13 7 13 7 21"/>
            <polyline points="7 3 7 8 15 8"/>
          </svg>
          {{ isSaving ? "Menyimpan…" : pageData?.id ? "Simpan Perubahan" : "Buat Halaman" }}
        </button>
      </div>
    </div>

    <!-- ══ STATUS BADGE ══════════════════════════════════════════ -->
    <div v-if="pageData?.id || (!isLoading && !pageData)" class="mb-5">
      <div v-if="pageData?.id" class="inline-flex items-center gap-2 px-3 py-1.5 bg-emerald-50 border border-emerald-200 rounded-xl">
        <span class="w-2 h-2 rounded-full bg-emerald-500 shadow-sm shadow-emerald-300"></span>
        <span class="text-xs font-semibold text-emerald-700">Live · ID {{ pageData.id.slice(0, 8) }}…</span>
      </div>
      <div v-else class="inline-flex items-center gap-2 px-3 py-1.5 bg-amber-50 border border-amber-200 rounded-xl">
        <span class="w-2 h-2 rounded-full bg-amber-500"></span>
        <span class="text-xs font-semibold text-amber-700">Belum ada halaman — buat baru</span>
      </div>
    </div>

    <!-- ══ LOADING ════════════════════════════════════════════════ -->
    <div v-if="isLoading" class="flex flex-col items-center justify-center py-20 bg-white border border-gray-200 rounded-2xl shadow-sm">
      <svg class="animate-spin h-8 w-8 text-indigo-500 mx-auto mb-3" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
      </svg>
      <p class="text-sm text-gray-400">Memuat data…</p>
    </div>

    <!-- ══ MAIN EDITOR ═══════════════════════════════════════════ -->
    <div v-else class="flex gap-0 bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden flex-1">

      <!-- ── SIDEBAR TABS ─────────────────────────────────────── -->
      <nav class="w-44 shrink-0 border-r border-gray-100 bg-gray-50/60 p-3 flex flex-col gap-1">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="activeTab === tab.id
            ? 'bg-indigo-600 text-white font-semibold'
            : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'"
          class="flex items-center gap-2.5 px-3 py-2 rounded-xl text-sm font-medium transition-all duration-150 w-full text-left"
        >
          <span class="text-base leading-none">{{ tab.icon }}</span>
          <span class="flex-1">{{ tab.label }}</span>
          <span
            v-if="tab.id === 'stats' || tab.id === 'values' || tab.id === 'gallery'"
            :class="activeTab === tab.id ? 'bg-white/20 text-white' : 'bg-gray-200 text-gray-500'"
            class="text-[10px] font-bold font-mono px-1.5 py-0.5 rounded-full min-w-[20px] text-center"
          >
            {{ tab.id === 'stats' ? form.stats.length : tab.id === 'values' ? form.values.length : gallery.length }}
          </span>
        </button>
      </nav>

      <!-- ── PANEL ────────────────────────────────────────────── -->
      <div class="flex-1 p-6 overflow-y-auto w-full">

        <!-- ─── HERO ─────────────────────────────────── -->
        <section v-show="activeTab === 'hero'">
          <div class="mb-6 pb-5 border-b border-gray-100">
            <h2 class="text-base font-bold text-gray-900 uppercase tracking-wide">Hero Section</h2>
            <p class="text-sm text-gray-500 mt-0.5">Teks utama yang muncul di bagian atas halaman About Us.</p>
          </div>

          <div class="space-y-4">
            <div>
              <label for="hero_badge_text" class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5">Badge Text</label>
              <input
                id="hero_badge_text"
                name="hero_badge_text"
                v-model="form.hero_badge_text"
                class="input-field"
                placeholder="Partner Keamanan Anda"
                maxlength="100"
              />
              <p class="text-xs text-gray-400 mt-1">Max 100 karakter · tampil sebagai label kecil di atas judul</p>
            </div>

            <div>
              <label for="hero_heading" class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5">
                Heading Utama <span class="text-rose-500">*</span>
              </label>
              <textarea
                id="hero_heading"
                name="hero_heading"
                v-model="form.hero_heading"
                class="input-field resize-none"
                rows="3"
                placeholder="Jangan Pertaruhkan Aset Anda Pada Instalasi Amatir."
              ></textarea>
              <p class="text-xs text-gray-400 mt-1">{{ form.hero_heading.length }} karakter</p>
            </div>

            <div>
              <label for="hero_subheading" class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5">
                Sub-heading <span class="text-gray-400 font-normal normal-case tracking-normal">opsional</span>
              </label>
              <textarea
                id="hero_subheading"
                name="hero_subheading"
                v-model="form.hero_subheading"
                class="input-field resize-none"
                rows="4"
                placeholder="Deskripsi singkat yang menjelaskan proposisi nilai utama…"
              ></textarea>
            </div>

            <!-- Preview Hero -->
            <div class="mt-2 rounded-xl overflow-hidden border border-gray-200">
              <div class="px-4 py-2 bg-gray-50 border-b border-gray-200">
                <p class="text-[10px] font-semibold uppercase tracking-widest text-gray-400">Preview Hero</p>
              </div>
              <div class="p-6 bg-gray-950">
                <div class="inline-flex items-center gap-1.5 border border-gray-700 px-2.5 py-1 mb-4">
                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#888" stroke-width="2.5">
                    <path :d="getIconPath('lucide:shield-check')" />
                  </svg>
                  <span class="text-[10px] font-bold uppercase tracking-widest text-gray-500">
                    {{ form.hero_badge_text || "Badge text" }}
                  </span>
                </div>
                <p class="font-bold text-2xl text-gray-100 uppercase leading-tight mb-3 whitespace-pre-wrap">
                  {{ form.hero_heading || "Heading akan muncul di sini" }}
                </p>
                <p class="text-sm text-gray-500 leading-relaxed max-w-md">
                  {{ form.hero_subheading || "Sub-heading opsional…" }}
                </p>
              </div>
            </div>
          </div>
        </section>

        <!-- ─── STATS ─────────────────────────────────── -->
        <section v-show="activeTab === 'stats'">
          <div class="mb-6 pb-5 border-b border-gray-100">
            <h2 class="text-base font-bold text-gray-900 uppercase tracking-wide">Statistics Bar</h2>
            <p class="text-sm text-gray-500 mt-0.5">Angka-angka kepercayaan yang tampil di bawah hero.</p>
          </div>

          <div class="space-y-3 mb-4">
            <div
              v-for="(stat, i) in form.stats"
              :key="i"
              class="flex items-center gap-3 bg-gray-50 border border-gray-200 rounded-xl p-3"
            >
              <span class="text-[10px] font-bold font-mono text-gray-400 w-5 text-center">{{ i + 1 }}</span>
              <label :for="`stat_value_${i}`" class="sr-only">Nilai stat {{ i + 1 }}</label>
              <input
                :id="`stat_value_${i}`"
                :name="`stat_value_${i}`"
                v-model="stat.value"
                class="input-field-sm flex-1"
                placeholder="1,200+"
                maxlength="50"
              />
              <label :for="`stat_label_${i}`" class="sr-only">Label stat {{ i + 1 }}</label>
              <input
                :id="`stat_label_${i}`"
                :name="`stat_label_${i}`"
                v-model="stat.label"
                class="input-field-sm flex-1"
                placeholder="Kamera Aktif"
                maxlength="100"
              />
              <button
                @click="removeStat(i)"
                :aria-label="`Hapus stat ${i + 1}`"
                class="p-1.5 text-gray-400 hover:text-rose-500 hover:bg-rose-50 rounded-lg transition-colors"
              >
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
                  <polyline points="3 6 5 6 21 6"/>
                  <path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/>
                  <path d="M10 11v6M14 11v6M9 6V4h6v2"/>
                </svg>
              </button>
            </div>

            <div v-if="!form.stats.length"
              class="text-center py-8 text-sm text-gray-400 border border-dashed border-gray-200 rounded-xl bg-white">
              Belum ada stat. Minimal 1 harus diisi.
            </div>
          </div>

          <button @click="addStat"
            class="w-full py-2.5 border border-dashed border-gray-300 rounded-xl text-sm font-semibold text-gray-600 hover:bg-gray-50 hover:border-indigo-300 hover:text-indigo-600 transition-all flex items-center justify-center gap-1.5 mb-5">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            Tambah Stat
          </button>

          <!-- Preview Stats -->
          <div v-if="form.stats.length" class="rounded-xl overflow-hidden border border-gray-200">
            <div class="px-4 py-2 bg-gray-50 border-b border-gray-200">
              <p class="text-[10px] font-semibold uppercase tracking-widest text-gray-400">Preview Stats Bar</p>
            </div>
            <div class="p-6 bg-gray-900 flex flex-wrap gap-8 justify-around">
              <div v-for="(s, i) in form.stats" :key="i" class="flex flex-col items-center gap-1">
                <span class="text-3xl font-black text-gray-100 leading-none">{{ s.value || "—" }}</span>
                <span class="text-[10px] font-bold uppercase tracking-widest text-gray-500">{{ s.label || "Label" }}</span>
              </div>
            </div>
          </div>
        </section>

        <!-- ─── VALUES ────────────────────────────────── -->
        <section v-show="activeTab === 'values'">
          <div class="mb-6 pb-5 border-b border-gray-100">
            <h2 class="text-base font-bold text-gray-900 uppercase tracking-wide">Value Cards</h2>
            <p class="text-sm text-gray-500 mt-0.5">Kartu keunggulan "Mengapa Memilih Kami" dengan icon Lucide.</p>
          </div>

          <div class="space-y-4 mb-4">
            <div
              v-for="(val, i) in form.values"
              :key="i"
              class="bg-gray-50 border border-gray-200 rounded-xl p-4"
            >
              <div class="flex items-center justify-between mb-4">
                <span class="text-[10px] font-bold font-mono text-gray-400 border border-gray-200 rounded px-1.5 py-0.5">
                  {{ i + 1 }}
                </span>
                <button @click="removeValue(i)"
                  class="p-1.5 text-gray-400 hover:text-rose-500 hover:bg-rose-50 rounded-lg transition-colors">
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                  </svg>
                </button>
              </div>

              <div class="flex items-center gap-3 mb-3">
                <label :for="`val_icon_${i}`" class="sr-only">Icon value card {{ i + 1 }}</label>
                <select
                  :id="`val_icon_${i}`"
                  :name="`val_icon_${i}`"
                  v-model="val.icon"
                  class="input-field flex-1 text-sm"
                >
                  <option v-for="ic in ICONS" :key="ic" :value="ic">{{ ic }}</option>
                </select>
                <div class="w-9 h-9 rounded-lg border border-gray-200 bg-indigo-50 flex items-center justify-center shrink-0" aria-hidden="true">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#4f46e5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path :d="getIconPath(val.icon)" />
                  </svg>
                </div>
              </div>

              <div class="space-y-3">
                <div>
                  <label :for="`val_title_${i}`" class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Judul</label>
                  <input
                    :id="`val_title_${i}`"
                    :name="`val_title_${i}`"
                    v-model="val.title"
                    class="input-field"
                    placeholder="Zero Blind-Spot Design"
                    maxlength="150"
                  />
                </div>
                <div>
                  <label :for="`val_desc_${i}`" class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Deskripsi</label>
                  <textarea
                    :id="`val_desc_${i}`"
                    :name="`val_desc_${i}`"
                    v-model="val.desc"
                    class="input-field resize-none"
                    rows="3"
                    placeholder="Penjelasan singkat keunggulan…"
                  ></textarea>
                </div>
              </div>
            </div>

            <div v-if="!form.values.length"
              class="text-center py-8 text-sm text-gray-400 border border-dashed border-gray-200 rounded-xl bg-white">
              Belum ada value card.
            </div>
          </div>

          <button @click="addValue"
            class="w-full py-2.5 border border-dashed border-gray-300 rounded-xl text-sm font-semibold text-gray-600 hover:bg-gray-50 hover:border-indigo-300 hover:text-indigo-600 transition-all flex items-center justify-center gap-1.5">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            Tambah Value Card
          </button>
        </section>

        <!-- ─── GALLERY ───────────────────────────────── -->
        <section v-show="activeTab === 'gallery'">
          <div class="mb-6 pb-5 border-b border-gray-100">
            <h2 class="text-base font-bold text-gray-900 uppercase tracking-wide">Gallery</h2>
            <p class="text-sm text-gray-500 mt-0.5">Foto hasil kerja lapangan yang tampil di swiper gallery.</p>
          </div>

          <!-- Upload Box -->
          <div class="bg-indigo-50/60 border border-indigo-100 rounded-xl p-4 mb-5 space-y-3">
            <p class="text-sm font-semibold text-indigo-800 flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
                <polyline points="17 8 12 3 7 8"/>
                <line x1="12" y1="3" x2="12" y2="15"/>
              </svg>
              Upload Gambar Baru
            </p>
            <div class="flex gap-3 flex-wrap">
              <div class="flex-1 min-w-[160px]">
                <label for="gallery_file" class="sr-only">Pilih file gambar</label>
                <input
                  id="gallery_file"
                  name="gallery_file"
                  ref="galleryFileInput"
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  class="input-field cursor-pointer"
                />
              </div>
              <div class="flex-1 min-w-[160px]">
                <label for="gallery_alt" class="sr-only">Caption gambar</label>
                <input
                  id="gallery_alt"
                  name="gallery_alt"
                  v-model="galleryAlt"
                  class="input-field"
                  placeholder="Caption gambar (Alt text)"
                  maxlength="200"
                />
              </div>
              <button
                @click="uploadGallery"
                :disabled="galleryUploading"
                class="inline-flex items-center gap-2 px-4 py-2.5 bg-indigo-600 text-white text-sm font-semibold rounded-xl hover:bg-indigo-700 active:scale-95 disabled:opacity-60 transition-all"
              >
                <svg v-if="galleryUploading" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
                {{ galleryUploading ? "Uploading…" : "Upload" }}
              </button>
            </div>
            <p class="text-xs text-indigo-500">JPEG / PNG / WebP · maks. 5 MB per file</p>
          </div>

          <!-- Gallery Grid -->
          <div v-if="gallery.length" class="grid grid-cols-3 gap-3">
            <div
              v-for="img in gallery"
              :key="img.id"
              class="relative aspect-square rounded-xl overflow-hidden border border-gray-200 bg-gray-100 group"
            >
              <img :src="img.cdn_url" :alt="img.alt" class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105" loading="lazy" />
              <div class="absolute inset-0 bg-black/55 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center gap-2 p-2">
                <span class="text-[10px] text-white text-center leading-tight line-clamp-2">{{ img.alt }}</span>
                <button @click="deleteGallery(img.id)"
                  class="p-1.5 bg-rose-600 hover:bg-rose-700 text-white rounded-lg transition-colors">
                  <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                    <polyline points="3 6 5 6 21 6"/>
                    <path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/>
                    <path d="M10 11v6M14 11v6M9 6V4h6v2"/>
                  </svg>
                </button>
              </div>
              <div class="absolute top-2 left-2 bg-black/60 text-white text-[9px] font-bold font-mono px-1.5 py-0.5 rounded">
                {{ img.order + 1 }}
              </div>
            </div>
          </div>

          <div v-else
            class="text-center py-10 text-sm text-gray-400 border border-dashed border-gray-200 rounded-xl bg-white">
            Belum ada foto gallery. Upload gambar pertama kamu.
          </div>
        </section>

        <!-- ─── CTA ───────────────────────────────────── -->
        <section v-show="activeTab === 'cta'">
          <div class="mb-6 pb-5 border-b border-gray-100">
            <h2 class="text-base font-bold text-gray-900 uppercase tracking-wide">CTA Section</h2>
            <p class="text-sm text-gray-500 mt-0.5">Seksi garansi dengan tombol ajakan bertindak di bagian bawah.</p>
          </div>

          <div class="space-y-4">
            <div>
              <label for="cta_heading" class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5">Heading CTA</label>
              <input
                id="cta_heading"
                name="cta_heading"
                v-model="form.cta_heading"
                class="input-field"
                placeholder="Garansi Ganti Baru Tanpa Debat"
                maxlength="200"
              />
            </div>

            <div>
              <label for="cta_body" class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5">
                Body CTA <span class="text-gray-400 font-normal normal-case tracking-normal">opsional</span>
              </label>
              <textarea
                id="cta_body"
                name="cta_body"
                v-model="form.cta_body"
                class="input-field resize-none"
                rows="4"
                placeholder="Kamera mati tiba-tiba? NVR rusak? Kami berikan jaminan ganti unit baru…"
              ></textarea>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label for="cta_primary_text" class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5">Teks Tombol Utama</label>
                <input
                  id="cta_primary_text"
                  name="cta_primary_text"
                  v-model="form.cta_primary_text"
                  class="input-field"
                  placeholder="Jadwalkan Survey Gratis"
                  maxlength="80"
                />
              </div>
              <div>
                <label for="cta_secondary_text" class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5">Teks Tombol Sekunder</label>
                <input
                  id="cta_secondary_text"
                  name="cta_secondary_text"
                  v-model="form.cta_secondary_text"
                  class="input-field"
                  placeholder="Lihat Harga Paket"
                  maxlength="80"
                />
              </div>
            </div>

            <div>
              <label for="cta_secondary_url" class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5">URL Tombol Sekunder</label>
              <input
                id="cta_secondary_url"
                name="cta_secondary_url"
                v-model="form.cta_secondary_url"
                class="input-field"
                placeholder="/services/booking"
                maxlength="200"
              />
            </div>

            <!-- Preview CTA -->
            <div class="rounded-xl overflow-hidden border border-gray-200 mt-2">
              <div class="px-4 py-2 bg-gray-50 border-b border-gray-200">
                <p class="text-[10px] font-semibold uppercase tracking-widest text-gray-400">Preview CTA</p>
              </div>
              <div class="p-8 bg-rose-600 text-center">
                <p class="text-xl font-black uppercase text-white mb-3 leading-tight">
                  {{ form.cta_heading || "Heading CTA" }}
                </p>
                <p class="text-sm text-rose-100 mb-5 leading-relaxed max-w-md mx-auto">
                  {{ form.cta_body || "Body teks CTA opsional…" }}
                </p>
                <div class="flex gap-3 justify-center flex-wrap">
                  <span class="inline-flex px-4 py-2 bg-black text-white text-xs font-bold uppercase tracking-wide rounded">
                    {{ form.cta_primary_text || "Tombol Utama" }}
                  </span>
                  <span class="inline-flex px-4 py-2 bg-white text-rose-600 text-xs font-bold uppercase tracking-wide rounded">
                    {{ form.cta_secondary_text || "Tombol Sekunder" }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </section>

      </div>
    </div>

    <!-- ══ IMAGE SECTION PREVIEW ══════════════════════════════════ -->
    <ImageSectionPreview
      v-model="showPreview"
      :section="pageData"
      :hide-mode-picker="true"
      :extra-presets="[{ label: 'About', icon: '👤', url: previewStore.resolveUrl('/about') }]"
      :initial-url="previewStore.resolveUrl('/about')"
    />

    <!-- ══ TOAST ══════════════════════════════════════════════════ -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="opacity-0 translate-y-2 scale-95"
        enter-to-class="opacity-100 translate-y-0 scale-100"
        leave-active-class="transition duration-200 ease-in"
        leave-from-class="opacity-100 translate-y-0 scale-100"
        leave-to-class="opacity-0 translate-y-2 scale-95"
      >
        <div
          v-if="toast"
          class="fixed bottom-6 right-6 z-[100] flex items-center gap-3 px-4 py-3 rounded-2xl shadow-lg border max-w-sm"
          :class="toast.type === 'error'
            ? 'bg-rose-600 border-rose-500 text-white'
            : 'bg-gray-900 border-gray-700 text-white'"
        >
          <svg v-if="toast.type === 'error'" class="w-5 h-5 shrink-0 text-rose-200" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <svg v-else class="w-5 h-5 shrink-0 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
          </svg>
          <p class="text-sm font-medium">{{ toast.message }}</p>
        </div>
      </Transition>
    </Teleport>

  </div>
</template>

<style scoped>
@reference "tailwindcss";

.input-field {
  @apply block w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-800 placeholder-gray-400 focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all;
}

.input-field-sm {
  @apply block w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all;
}
</style>