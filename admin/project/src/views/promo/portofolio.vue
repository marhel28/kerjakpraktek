<template>
  <div class="portfolio-admin">

    <!-- ══════════════════════════════════════════════════════
           HEADER
      ══════════════════════════════════════════════════════ -->
    <div class="page-header">
      <div class="page-header__left">
        <div class="page-header__icon">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3 21h18M3.75 3h16.5M4.5 3v18m15-18v18" />
          </svg>
        </div>
        <div>
          <h1 class="page-header__title">Portfolio Management</h1>
          <p class="page-header__sub">Kelola galeri project, gambar, dan testimoni klien.</p>
        </div>
      </div>
      <div class="page-header__actions">
        <button class="btn btn--ghost" @click="openPreview">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" width="15" height="15">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          Preview Halaman
        </button>
        <button class="btn btn--primary" @click="openProjectModal()">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" width="15" height="15">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          Tambah Project
        </button>
      </div>
    </div>

    <!-- ══════════════════════════════════════════════════════
           TABS
      ══════════════════════════════════════════════════════ -->
    <div class="tabs">
      <button v-for="tab in tabs" :key="tab.key" class="tabs__btn"
        :class="{ 'tabs__btn--active': activeTab === tab.key }" @click="activeTab = tab.key">
        <span class="tabs__icon">{{ tab.icon }}</span>
        {{ tab.label }}
        <span v-if="tab.count" class="tabs__badge">{{ tab.count }}</span>
      </button>
    </div>

    <!-- ══════════════════════════════════════════════════════
           TAB: PROJECTS
      ══════════════════════════════════════════════════════ -->
    <div v-if="activeTab === 'projects'">

      <!-- Skeleton -->
      <div v-if="isLoadingProjects" class="grid grid-5">
        <div v-for="i in 6" :key="i" class="skeleton-card">
          <div class="skeleton-img"></div>
          <div class="skeleton-line" style="width:70%"></div>
          <div class="skeleton-line" style="width:45%"></div>
        </div>
      </div>

      <!-- Empty -->
      <div v-else-if="projects.length === 0" class="empty-state">
        <div class="empty-state__icon">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.2">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909" />
          </svg>
        </div>
        <h3>Belum ada project</h3>
        <p>Tambahkan project pertama untuk ditampilkan di halaman portofolio.</p>
        <button class="btn btn--primary" @click="openProjectModal()">+ Tambah Project</button>
      </div>

      <!-- Grid -->
      <div v-else class="grid grid-3">
        <div v-for="project in projects" :key="project.id" class="project-card"
          :class="{ 'project-card--featured': project.is_featured }">

          <!-- Featured badge -->
          <span v-if="project.is_featured" class="badge badge--featured">⭐ Featured</span>

          <!-- Cover image -->
          <div class="project-card__cover" @click="selectProject(project)">
            <img v-if="getCoverImage(project)" :src="getCoverImage(project)" :alt="project.title" loading="lazy" />
            <div v-else class="project-card__no-img">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" width="32" height="32">
                <path stroke-linecap="round" stroke-linejoin="round"
                  d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909" />
              </svg>
              <span>Belum ada gambar</span>
            </div>
            <div class="project-card__overlay">
              <span>Kelola Gambar</span>
            </div>
          </div>

          <!-- Info -->
          <div class="project-card__body">
            <div class="project-card__meta">
              <span class="tag">{{ project.category }}</span>
              <span class="project-card__cam">📷 {{ project.cameras }} kamera</span>
            </div>
            <h3 class="project-card__title">{{ project.title }}</h3>
            <p class="project-card__loc">📍 {{ project.location }}</p>
          </div>

          <!-- Actions -->
          <div class="project-card__actions">
            <button class="icon-btn icon-btn--image" title="Kelola Gambar" @click="selectProject(project)">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" width="14" height="14">
                <path stroke-linecap="round" stroke-linejoin="round"
                  d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3 21h18M3.75 3h16.5M4.5 3v18m15-18v18" />
              </svg>
            </button>
            <button class="icon-btn icon-btn--edit" title="Edit Project" @click="openProjectModal(project)">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" width="14" height="14">
                <path stroke-linecap="round" stroke-linejoin="round"
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button class="icon-btn icon-btn--delete" title="Hapus Project" @click="confirmDeleteProject(project.id)">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" width="14" height="14">
                <path stroke-linecap="round" stroke-linejoin="round"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ══════════════════════════════════════════════════════
           TAB: IMAGES (hanya muncul saat project dipilih)
      ══════════════════════════════════════════════════════ -->
    <div v-if="activeTab === 'images'">
      <div v-if="!selectedProject" class="empty-state">
        <div class="empty-state__icon">🖼️</div>
        <h3>Pilih project terlebih dahulu</h3>
        <p>Buka tab Project dan klik ikon gambar pada salah satu project.</p>
        <button class="btn btn--outline" @click="activeTab = 'projects'">← Ke Daftar Project</button>
      </div>

      <template v-else>
        <!-- Sub header -->
        <div class="sub-header">
          <div>
            <p class="sub-header__back" @click="activeTab = 'projects'">← Kembali</p>
            <h2 class="sub-header__title">{{ selectedProject.title }}</h2>
            <p class="sub-header__meta">{{ selectedProject.category }} · {{ selectedProject.location }}</p>
          </div>
          <button class="btn btn--primary" @click="openUploadModal">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" width="15" height="15">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
            </svg>
            Upload Gambar
          </button>
        </div>

        <!-- Images by role -->
        <div v-for="roleGroup in imageRoles" :key="roleGroup.value" class="role-section">
          <div class="role-section__head">
            <span class="role-section__icon">{{ roleGroup.icon }}</span>
            <h3>{{ roleGroup.label }}</h3>
            <span class="role-section__count">
              {{ getImagesByRole(roleGroup.value).length }}
            </span>
          </div>

          <div v-if="isLoadingImages" class="grid grid-4">
            <div v-for="i in 4" :key="i" class="skeleton-card">
              <div class="skeleton-img"></div>
            </div>
          </div>

          <div v-else-if="getImagesByRole(roleGroup.value).length === 0" class="role-section__empty">
            Belum ada gambar untuk role ini.
            <button class="link" @click="openUploadModal(roleGroup.value)">Upload sekarang →</button>
          </div>

          <div v-else class="grid grid-4">
            <div v-for="img in getImagesByRole(roleGroup.value)" :key="img.id" class="img-card">
              <div class="img-card__thumb">
                <img :src="img.url" :alt="img.alt_text || ''" loading="lazy" />
              </div>
              <div class="img-card__foot">
                <span class="img-card__role">{{ roleGroup.label }}</span>
                <button class="icon-btn icon-btn--delete" @click="confirmDeleteImage(img.id)">
                  <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" width="12" height="12">
                    <path stroke-linecap="round" stroke-linejoin="round"
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>

    <!-- ══════════════════════════════════════════════════════
           TAB: REVIEWS
      ══════════════════════════════════════════════════════ -->
    <div v-if="activeTab === 'reviews'">
      <div class="reviews-header">
        <p class="reviews-header__count">{{ reviews.length }} testimonial</p>
        <button class="btn btn--primary" @click="openReviewModal()">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" width="15" height="15">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          Tambah Testimonial
        </button>
      </div>

      <div v-if="isLoadingReviews" class="reviews-list">
        <div v-for="i in 4" :key="i" class="skeleton-review">
          <div class="skeleton-line" style="width:40%"></div>
          <div class="skeleton-line" style="width:80%"></div>
          <div class="skeleton-line" style="width:60%"></div>
        </div>
      </div>

      <div v-else-if="reviews.length === 0" class="empty-state">
        <div class="empty-state__icon">💬</div>
        <h3>Belum ada testimonial</h3>
        <p>Tambahkan ulasan dari klien yang sudah menggunakan jasa Anda.</p>
        <button class="btn btn--primary" @click="openReviewModal()">+ Tambah Testimonial</button>
      </div>

      <div v-else class="reviews-list">
        <div v-for="review in reviews" :key="review.id" class="review-card"
          :class="{ 'review-card--inactive': !review.is_active }">
          <div class="review-card__head">
            <div class="review-card__avatar">{{ review.name[0] }}</div>
            <div>
              <p class="review-card__name">{{ review.name }}</p>
              <p class="review-card__role">{{ review.role || '—' }}</p>
            </div>
            <div class="review-card__stars">
              <span v-for="s in 5" :key="s" :class="s <= review.rating ? 'star star--on' : 'star star--off'">★</span>
            </div>
            <div class="review-card__actions">
              <span v-if="!review.is_active" class="badge badge--inactive">Non-aktif</span>
              <button class="icon-btn icon-btn--edit" @click="openReviewModal(review)">
                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" width="13" height="13">
                  <path stroke-linecap="round" stroke-linejoin="round"
                    d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
              <button class="icon-btn icon-btn--delete" @click="confirmDeleteReview(review.id)">
                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" width="13" height="13">
                  <path stroke-linecap="round" stroke-linejoin="round"
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
          <p class="review-card__text">{{ review.text }}</p>
        </div>
      </div>
    </div>

    <!-- ══════════════════════════════════════════════════════
           MODAL: PROJECT FORM
      ══════════════════════════════════════════════════════ -->
    <Transition name="modal-fade">
      <div v-if="isProjectModalOpen" class="modal-backdrop" @click.self="closeProjectModal">
        <div class="modal">
          <div class="modal__head">
            <h3>{{ editingProjectId ? 'Edit Project' : 'Tambah Project Baru' }}</h3>
            <button class="icon-btn" @click="closeProjectModal">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" width="16" height="16">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div class="modal__body">
            <div class="form-group">
              <label>Judul Project *</label>
              <input v-model="projectForm.title" type="text" placeholder="Instalasi CCTV Gudang Logistik" />
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Kategori *</label>
                <select v-model="projectForm.category">
                  <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
                </select>
              </div>
              <div class="form-group">
                <label>Lokasi *</label>
                <input v-model="projectForm.location" type="text" placeholder="Jakarta Selatan" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Jumlah Kamera *</label>
                <input v-model.number="projectForm.cameras" type="number" min="0" />
              </div>
              <div class="form-group">
                <label>Package Slug <span class="opt">opsional</span></label>
                <input v-model="projectForm.package_slug" type="text" placeholder="paket-premium-16-ch" />
              </div>
            </div>

            <div class="divider"><span>Case Study (Featured)</span></div>

            <div class="form-group">
              <label>Tipe Klien</label>
              <input v-model="projectForm.client_type" type="text" placeholder="Pabrik & Manufaktur" />
            </div>
            <div class="form-group">
              <label>Problem</label>
              <textarea v-model="projectForm.problem" rows="2" placeholder="Masalah yang dihadapi klien..."></textarea>
            </div>
            <div class="form-group">
              <label>Solusi</label>
              <textarea v-model="projectForm.solution" rows="2" placeholder="Solusi yang kami berikan..."></textarea>
            </div>
            <div class="form-group">
              <label>Hasil</label>
              <textarea v-model="projectForm.result" rows="2" placeholder="Dampak setelah pemasangan..."></textarea>
            </div>

            <div class="form-toggle">
              <div>
                <p class="form-toggle__label">Jadikan Featured</p>
                <p class="form-toggle__sub">Tampil di bagian case study utama halaman portofolio.</p>
              </div>
              <button type="button" class="toggle" :class="{ 'toggle--on': projectForm.is_featured }"
                @click="projectForm.is_featured = !projectForm.is_featured">
                <span class="toggle__knob"></span>
              </button>
            </div>
          </div>
          <div class="modal__foot">
            <button class="btn btn--outline" @click="closeProjectModal" :disabled="isSubmitting">Batal</button>
            <button class="btn btn--primary" @click="saveProject" :disabled="isSubmitting">
              <svg v-if="isSubmitting" class="spin" fill="none" viewBox="0 0 24 24" width="14" height="14">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" class="opacity-25" />
                <path fill="currentColor" class="opacity-75"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              {{ isSubmitting ? 'Menyimpan...' : 'Simpan' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ══════════════════════════════════════════════════════
           MODAL: UPLOAD GAMBAR
      ══════════════════════════════════════════════════════ -->
    <Transition name="modal-fade">
      <div v-if="isUploadModalOpen" class="modal-backdrop" @click.self="isUploadModalOpen = false">
        <div class="modal modal--upload">
          <div class="modal__head">
            <h3>Upload Gambar</h3>
            <button class="icon-btn" @click="isUploadModalOpen = false">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" width="16" height="16">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div class="modal__body">
            <div class="form-group">
              <label>Role Gambar</label>
              <div class="role-selector">
                <button v-for="r in imageRoles" :key="r.value" class="role-btn"
                  :class="{ 'role-btn--active': uploadForm.role === r.value }" @click="uploadForm.role = r.value">
                  {{ r.icon }} {{ r.label }}
                </button>
              </div>
            </div>

            <!-- Drop zone -->
            <div class="drop-zone" :class="{ 'drop-zone--over': isDragOver }" @dragover.prevent="isDragOver = true"
              @dragleave="isDragOver = false" @drop.prevent="handleDrop" @click="triggerUploadInput">
              <div v-if="uploadPreviews.length === 0" class="drop-zone__placeholder">
                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" width="36" height="36">
                  <path stroke-linecap="round" stroke-linejoin="round"
                    d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                </svg>
                <p>Drag & drop atau <span class="link">pilih file</span></p>
                <p class="drop-zone__hint">JPEG / PNG / WebP · Maks 5MB per file · Maks 10 file</p>
              </div>
              <div v-else class="upload-previews">
                <div v-for="(p, i) in uploadPreviews" :key="i" class="upload-preview">
                  <img :src="p" />
                  <button class="upload-preview__remove" @click.stop="removePreview(i)">×</button>
                </div>
                <div class="upload-preview upload-preview--add" @click.stop="triggerUploadInput">+</div>
              </div>
              <input type="file" ref="uploadInput" class="hidden" accept="image/jpeg,image/png,image/webp" multiple
                @change="handleUploadChange" />
            </div>
          </div>
          <div class="modal__foot">
            <button class="btn btn--outline" @click="isUploadModalOpen = false" :disabled="isSubmitting">Batal</button>
            <button class="btn btn--primary" @click="uploadImages" :disabled="isSubmitting || uploadFiles.length === 0">
              <svg v-if="isSubmitting" class="spin" fill="none" viewBox="0 0 24 24" width="14" height="14">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" class="opacity-25" />
                <path fill="currentColor" class="opacity-75"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              {{ isSubmitting ? 'Mengupload...' : `Upload ${uploadFiles.length} File` }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ══════════════════════════════════════════════════════
           MODAL: REVIEW FORM
      ══════════════════════════════════════════════════════ -->
    <Transition name="modal-fade">
      <div v-if="isReviewModalOpen" class="modal-backdrop" @click.self="closeReviewModal">
        <div class="modal">
          <div class="modal__head">
            <h3>{{ editingReviewId ? 'Edit Testimonial' : 'Tambah Testimonial' }}</h3>
            <button class="icon-btn" @click="closeReviewModal">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" width="16" height="16">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div class="modal__body">
            <div class="form-row">
              <div class="form-group">
                <label>Nama *</label>
                <input v-model="reviewForm.name" type="text" placeholder="Bpk. Hendra" />
              </div>
              <div class="form-group">
                <label>Jabatan / Peran</label>
                <input v-model="reviewForm.role" type="text" placeholder="Pemilik Gudang" />
              </div>
            </div>
            <div class="form-group">
              <label>Rating</label>
              <div class="star-picker">
                <button v-for="s in 5" :key="s" type="button" class="star-pick"
                  :class="{ 'star-pick--on': s <= reviewForm.rating }" @click="reviewForm.rating = s">★</button>
              </div>
            </div>
            <div class="form-group">
              <label>Ulasan *</label>
              <textarea v-model="reviewForm.text" rows="4"
                placeholder="Kerjanya sangat rapi, kabel tidak ada yang berantakan..."></textarea>
            </div>
            <div class="form-group">
              <label>Project Terkait <span class="opt">opsional</span></label>
              <select v-model="reviewForm.project_id">
                <option value="">— Tidak dilinkkan ke project —</option>
                <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.title }}</option>
              </select>
            </div>
            <div class="form-toggle">
              <div>
                <p class="form-toggle__label">Aktifkan Testimonial</p>
                <p class="form-toggle__sub">Tampilkan di halaman publik portofolio.</p>
              </div>
              <button type="button" class="toggle" :class="{ 'toggle--on': reviewForm.is_active }"
                @click="reviewForm.is_active = !reviewForm.is_active">
                <span class="toggle__knob"></span>
              </button>
            </div>
          </div>
          <div class="modal__foot">
            <button class="btn btn--outline" @click="closeReviewModal" :disabled="isSubmitting">Batal</button>
            <button class="btn btn--primary" @click="saveReview" :disabled="isSubmitting">
              <svg v-if="isSubmitting" class="spin" fill="none" viewBox="0 0 24 24" width="14" height="14">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" class="opacity-25" />
                <path fill="currentColor" class="opacity-75"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              {{ isSubmitting ? 'Menyimpan...' : 'Simpan' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ══════════════════════════════════════════════════════
           MODAL: KONFIRMASI HAPUS
      ══════════════════════════════════════════════════════ -->
    <Transition name="modal-fade">
      <div v-if="isDeleteModalOpen" class="modal-backdrop" @click.self="isDeleteModalOpen = false">
        <div class="modal modal--sm">
          <div class="modal__delete-icon">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" width="24" height="24">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </div>
          <h3 class="modal__delete-title">Hapus Data?</h3>
          <p class="modal__delete-sub">Data yang dihapus tidak dapat dikembalikan.</p>
          <div class="modal__foot modal__foot--center">
            <button class="btn btn--outline" @click="isDeleteModalOpen = false" :disabled="isSubmitting">Batal</button>
            <button class="btn btn--danger" @click="executeDelete" :disabled="isSubmitting">
              <svg v-if="isSubmitting" class="spin" fill="none" viewBox="0 0 24 24" width="14" height="14">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" class="opacity-25" />
                <path fill="currentColor" class="opacity-75"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              {{ isSubmitting ? 'Menghapus...' : 'Hapus' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ══════════════════════════════════════════════════════
           PREVIEW PANEL (ImageSectionPreview.vue)
      ══════════════════════════════════════════════════════ -->
    <ImageSectionPreview v-model="isPreviewOpen" :section="previewSection" :hide-mode-picker="true" :extra-presets="[
      { label: 'Portfolio', icon: '🖼️', url: 'http://localhost:3000/portofolio' }
    ]" :initial-url="'http://localhost:3000/portofolio'" />

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useToastStore } from '@/stores/toast'
import api from '@/service/api'
import ImageSectionPreview from '@/components/ImageSectionPreview.vue'

const toastStore = useToastStore()

// ── API ──────────────────────────────────────────────────────────
const API = {
  projects: '/portfolio/projects',
  page: '/portfolio/page',
  reviews: '/portfolio/reviews',
  projectImages: (id) => `/portfolio/projects/${id}/images`,
  imageById: (id) => `/portfolio/images/${id}`,
  reviewById: (id) => `/portfolio/reviews/${id}`,
}

// ── Static Data ──────────────────────────────────────────────────
const categories = [
  'Residensial', 'Komersial', 'Retail', 'Korporat',
  'Fasilitas Umum', 'F&B', 'Manufaktur', 'Lainnya'
]

const imageRoles = [
  { value: 'cover', icon: '🖼️', label: 'Cover' },
  { value: 'before', icon: '⬅️', label: 'Before' },
  { value: 'after', icon: '➡️', label: 'After' },
  { value: 'gallery', icon: '📸', label: 'Gallery' },
]

// ── State: Tab ───────────────────────────────────────────────────
const activeTab = ref('projects')

const tabs = computed(() => [
  { key: 'projects', icon: '🏗️', label: 'Projects', count: projects.value.length },
  {
    key: 'images', icon: '🖼️', label: 'Gambar',
    count: selectedProject.value
      ? projectImages.value.length
      : null
  },
  { key: 'reviews', icon: '💬', label: 'Testimonial', count: reviews.value.length },
])

// ── State: Projects ──────────────────────────────────────────────
const projects = ref([])
const isLoadingProjects = ref(true)
const selectedProject = ref(null)

const fetchProjects = async () => {
  isLoadingProjects.value = true
  try {
    const { data } = await api.get(API.projects)
    projects.value = data
  } catch (e) {
    toastStore.error(e.response?.data?.detail || 'Gagal memuat project.')
  } finally {
    isLoadingProjects.value = false
  }
}

const getCoverImage = (project) => {
  if (project.cover_image) return project.cover_image
  const cover = project.images?.find(img => img.role === 'cover')
  return cover ? cover.url : (project.images?.[0]?.url || null)
}

const selectProject = (project) => {
  selectedProject.value = project
  activeTab.value = 'images'
  fetchProjectImages(project.id)
}

// ── State: Images ────────────────────────────────────────────────
const projectImages = ref([])
const isLoadingImages = ref(false)

const getImagesByRole = (role) => projectImages.value.filter(img => img.role === role)

const fetchProjectImages = async (projectId) => {
  isLoadingImages.value = true
  try {
    const { data } = await api.get(API.projects + `/${projectId}`)
    projectImages.value = data.images || []
  } catch (e) {
    toastStore.error(e.response?.data?.detail || 'Gagal memuat gambar.')
  } finally {
    isLoadingImages.value = false
  }
}

// ── State: Reviews ───────────────────────────────────────────────
const reviews = ref([])
const isLoadingReviews = ref(true)

const fetchReviews = async () => {
  isLoadingReviews.value = true
  try {
    const { data } = await api.get(API.reviews)
    reviews.value = data
  } catch (e) {
    toastStore.error(e.response?.data?.detail || 'Gagal memuat testimonial.')
  } finally {
    isLoadingReviews.value = false
  }
}

// ── State: Global ────────────────────────────────────────────────
const isSubmitting = ref(false)

// ── Modal: Project ───────────────────────────────────────────────
const isProjectModalOpen = ref(false)
const editingProjectId = ref(null)
const projectForm = reactive({
  title: '', category: 'Residensial', location: '', cameras: 0,
  package_slug: '', client_type: '', problem: '', solution: '',
  result: '', is_featured: false,
})

const openProjectModal = (project = null) => {
  if (project) {
    editingProjectId.value = project.id
    Object.assign(projectForm, {
      title: project.title,
      category: project.category,
      location: project.location,
      cameras: project.cameras,
      package_slug: project.package_slug || '',
      client_type: project.client_type || '',
      problem: project.problem || '',
      solution: project.solution || '',
      result: project.result || '',
      is_featured: project.is_featured,
    })
  } else {
    editingProjectId.value = null
    Object.assign(projectForm, {
      title: '', category: 'Residensial', location: '', cameras: 0,
      package_slug: '', client_type: '', problem: '', solution: '',
      result: '', is_featured: false,
    })
  }
  isProjectModalOpen.value = true
}

const closeProjectModal = () => {
  if (isSubmitting.value) return
  isProjectModalOpen.value = false
}

const saveProject = async () => {
  if (!projectForm.title || !projectForm.location) {
    toastStore.warning('Judul dan lokasi wajib diisi.')
    return
  }
  isSubmitting.value = true
  try {
    if (editingProjectId.value) {
      await api.patch(API.projects + `/${editingProjectId.value}`, projectForm)
    } else {
      await api.post(API.projects, projectForm)
    }
    await fetchProjects()
    closeProjectModal()
    toastStore.success('Project berhasil disimpan.')
  } catch (e) {
    toastStore.error(e.response?.data?.detail || 'Gagal menyimpan project.')
  } finally {
    isSubmitting.value = false
  }
}

// ── Modal: Upload Images ─────────────────────────────────────────
const isUploadModalOpen = ref(false)
const uploadInput = ref(null)
const uploadFiles = ref([])
const uploadPreviews = ref([])
const isDragOver = ref(false)
const uploadForm = reactive({ role: 'gallery' })

const openUploadModal = (role = 'gallery') => {
  uploadForm.role = role
  uploadFiles.value = []
  uploadPreviews.value = []
  isUploadModalOpen.value = true
}

const triggerUploadInput = () => uploadInput.value?.click()

const processFiles = (files) => {
  const valid = Array.from(files).filter(f => {
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(f.type)) {
      toastStore.error(`${f.name}: tipe tidak didukung`)
      return false
    }
    if (f.size > 5 * 1024 * 1024) {
      toastStore.error(`${f.name}: melebihi 5MB`)
      return false
    }
    return true
  })
  valid.forEach(f => {
    uploadFiles.value.push(f)
    const reader = new FileReader()
    reader.onload = (e) => uploadPreviews.value.push(e.target.result)
    reader.readAsDataURL(f)
  })
}

const handleUploadChange = (e) => processFiles(e.target.files)
const handleDrop = (e) => { isDragOver.value = false; processFiles(e.dataTransfer.files) }
const removePreview = (i) => {
  uploadFiles.value.splice(i, 1)
  uploadPreviews.value.splice(i, 1)
}

const uploadImages = async () => {
  if (!selectedProject.value || uploadFiles.value.length === 0) return
  isSubmitting.value = true
  try {
    const fd = new FormData()
    uploadFiles.value.forEach(f => fd.append('files', f))
    fd.append('role', uploadForm.role)
    await api.post(API.projectImages(selectedProject.value.id), fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    await fetchProjectImages(selectedProject.value.id)
    await fetchProjects() // refresh cover di grid
    isUploadModalOpen.value = false
    toastStore.success('Gambar berhasil diupload.')
  } catch (e) {
    toastStore.error(e.response?.data?.detail || 'Gagal upload gambar.')
  } finally {
    isSubmitting.value = false
  }
}

// ── Modal: Review ────────────────────────────────────────────────
const isReviewModalOpen = ref(false)
const editingReviewId = ref(null)
const reviewForm = reactive({
  name: '', role: '', rating: 5, text: '', project_id: '', is_active: true
})

const openReviewModal = (review = null) => {
  if (review) {
    editingReviewId.value = review.id
    Object.assign(reviewForm, {
      name: review.name,
      role: review.role || '',
      rating: review.rating,
      text: review.text,
      project_id: review.project_id || '',
      is_active: review.is_active,
    })
  } else {
    editingReviewId.value = null
    Object.assign(reviewForm, {
      name: '', role: '', rating: 5, text: '', project_id: '', is_active: true
    })
  }
  isReviewModalOpen.value = true
}

const closeReviewModal = () => {
  if (isSubmitting.value) return
  isReviewModalOpen.value = false
}

const saveReview = async () => {
  if (!reviewForm.name || !reviewForm.text) {
    toastStore.warning('Nama dan ulasan wajib diisi.')
    return
  }
  isSubmitting.value = true
  const payload = {
    ...reviewForm,
    project_id: reviewForm.project_id || null,
  }
  try {
    if (editingReviewId.value) {
      await api.patch(API.reviewById(editingReviewId.value), payload)
    } else {
      await api.post(API.reviews, payload)
    }
    await fetchReviews()
    closeReviewModal()
    toastStore.success('Testimonial berhasil disimpan.')
  } catch (e) {
    toastStore.error(e.response?.data?.detail || 'Gagal menyimpan testimonial.')
  } finally {
    isSubmitting.value = false
  }
}

// ── Modal: Delete ────────────────────────────────────────────────
const isDeleteModalOpen = ref(false)
const deleteTarget = ref({ type: null, id: null })

const confirmDeleteProject = (id) => {
  deleteTarget.value = { type: 'project', id }
  isDeleteModalOpen.value = true
}
const confirmDeleteImage = (id) => {
  deleteTarget.value = { type: 'image', id }
  isDeleteModalOpen.value = true
}
const confirmDeleteReview = (id) => {
  deleteTarget.value = { type: 'review', id }
  isDeleteModalOpen.value = true
}

const executeDelete = async () => {
  isSubmitting.value = true
  const { type, id } = deleteTarget.value
  try {
    if (type === 'project') await api.delete(API.projects + `/${id}`)
    if (type === 'image') await api.delete(API.imageById(id))
    if (type === 'review') await api.delete(API.reviewById(id))

    if (type === 'project') { await fetchProjects(); selectedProject.value = null }
    if (type === 'image') await fetchProjectImages(selectedProject.value.id)
    if (type === 'review') await fetchReviews()

    isDeleteModalOpen.value = false
    toastStore.success('Data berhasil dihapus.')
  } catch (e) {
    toastStore.error(e.response?.data?.detail || 'Gagal menghapus data.')
  } finally {
    isSubmitting.value = false
  }
}

// ── Preview Panel ────────────────────────────────────────────────
const isPreviewOpen = ref(false)
const previewSection = computed(() => ({
  identifier: 'portfolio',
  items: projects.value,
}))

const openPreview = () => { isPreviewOpen.value = true }

// ── Init ─────────────────────────────────────────────────────────
onMounted(() => {
  fetchProjects()
  fetchReviews()
})
</script>

<style scoped>
/* ── Base ───────────────────────────────────────────────── */
.portfolio-admin {
  font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif;
  color: #111827;
  min-height: 100%;
  padding-bottom: 40px;
}

/* ── Page Header ───────────────────────────────────────── */
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.page-header__left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.page-header__icon {
  width: 44px;
  height: 44px;
  background: #eef2ff;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #4f46e5;
  flex-shrink: 0;
}

.page-header__icon svg {
  width: 22px;
  height: 22px;
}

.page-header__title {
  font-size: 20px;
  font-weight: 800;
  margin: 0 0 2px;
  letter-spacing: -0.3px;
}

.page-header__sub {
  font-size: 13px;
  color: #6b7280;
  margin: 0;
}

.page-header__actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

/* ── Tabs ───────────────────────────────────────────────── */
.tabs {
  display: flex;
  gap: 4px;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 24px;
}

.tabs__btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  font-size: 13px;
  font-weight: 600;
  border: none;
  background: transparent;
  color: #6b7280;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  transition: color 150ms, border-color 150ms;
  white-space: nowrap;
}

.tabs__btn:hover {
  color: #111827;
}

.tabs__btn--active {
  color: #4f46e5;
  border-bottom-color: #4f46e5;
}

.tabs__icon {
  font-size: 14px;
}

.tabs__badge {
  background: #e5e7eb;
  color: #374151;
  font-size: 10px;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 20px;
  min-width: 18px;
  text-align: center;
}

.tabs__btn--active .tabs__badge {
  background: #e0e7ff;
  color: #4f46e5;
}

/* ── Grids ──────────────────────────────────────────────── */
.grid {
  display: grid;
  gap: 16px;
}

.grid-3 {
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
}

.grid-4 {
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
}

.grid-5 {
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
}

/* ── Project Card ───────────────────────────────────────── */
.project-card {
  position: relative;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  overflow: hidden;
  transition: box-shadow 200ms, border-color 200ms, transform 200ms;
}

.project-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, .1);
  border-color: #c7d2fe;
  transform: translateY(-2px);
}

.project-card--featured {
  border-color: #fcd34d;
  background: #fffbeb;
}

.project-card__cover {
  position: relative;
  width: 100%;
  height: 160px;
  background: #f3f4f6;
  cursor: pointer;
  overflow: hidden;
}

.project-card__cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 300ms;
}

.project-card:hover .project-card__cover img {
  transform: scale(1.04);
}

.project-card__no-img {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: #9ca3af;
}

.project-card__no-img span {
  font-size: 11px;
}

.project-card__overlay {
  position: absolute;
  inset: 0;
  background: rgba(79, 70, 229, .7);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  opacity: 0;
  transition: opacity 200ms;
}

.project-card:hover .project-card__overlay {
  opacity: 1;
}

.project-card__body {
  padding: 12px 14px 8px;
}

.project-card__meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.project-card__cam {
  font-size: 11px;
  color: #6b7280;
}

.project-card__title {
  font-size: 14px;
  font-weight: 700;
  margin: 0 0 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.project-card__loc {
  font-size: 12px;
  color: #6b7280;
  margin: 0;
}

.project-card__actions {
  display: flex;
  gap: 6px;
  padding: 8px 14px 12px;
  justify-content: flex-end;
}

/* ── Image Card ─────────────────────────────────────────── */
.img-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
}

.img-card__thumb {
  width: 100%;
  height: 120px;
  overflow: hidden;
  background: #f3f4f6;
}

.img-card__thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.img-card__foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 10px;
}

.img-card__role {
  font-size: 11px;
  color: #6b7280;
  font-weight: 500;
}

/* ── Role Section ───────────────────────────────────────── */
.role-section {
  margin-bottom: 28px;
}

.role-section__head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.role-section__head h3 {
  font-size: 14px;
  font-weight: 700;
  margin: 0;
}

.role-section__icon {
  font-size: 16px;
}

.role-section__count {
  background: #e5e7eb;
  color: #374151;
  font-size: 10px;
  font-weight: 700;
  padding: 1px 7px;
  border-radius: 20px;
}

.role-section__empty {
  padding: 20px;
  background: #f9fafb;
  border: 1px dashed #d1d5db;
  border-radius: 10px;
  font-size: 13px;
  color: #6b7280;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* ── Sub Header ─────────────────────────────────────────── */
.sub-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.sub-header__back {
  font-size: 12px;
  color: #6b7280;
  cursor: pointer;
  margin: 0 0 4px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.sub-header__back:hover {
  color: #4f46e5;
}

.sub-header__title {
  font-size: 18px;
  font-weight: 800;
  margin: 0 0 2px;
}

.sub-header__meta {
  font-size: 12px;
  color: #6b7280;
  margin: 0;
}

/* ── Reviews ────────────────────────────────────────────── */
.reviews-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.reviews-header__count {
  font-size: 13px;
  color: #6b7280;
  font-weight: 500;
}

.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.review-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  padding: 14px 16px;
  transition: box-shadow 150ms;
}

.review-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, .07);
}

.review-card--inactive {
  opacity: 0.6;
}

.review-card__head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.review-card__avatar {
  width: 36px;
  height: 36px;
  background: #e0e7ff;
  color: #4f46e5;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 14px;
  flex-shrink: 0;
}

.review-card__name {
  font-size: 14px;
  font-weight: 700;
  margin: 0 0 2px;
}

.review-card__role {
  font-size: 12px;
  color: #6b7280;
  margin: 0;
}

.review-card__stars {
  display: flex;
  margin-left: auto;
}

.star {
  font-size: 14px;
}

.star--on {
  color: #f59e0b;
}

.star--off {
  color: #e5e7eb;
}

.review-card__actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

.review-card__text {
  font-size: 13px;
  color: #374151;
  line-height: 1.6;
  margin: 0;
}

/* ── Upload UI ──────────────────────────────────────────── */
.drop-zone {
  border: 2px dashed #d1d5db;
  border-radius: 14px;
  padding: 24px;
  cursor: pointer;
  transition: border-color 200ms, background 200ms;
  min-height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.drop-zone:hover {
  border-color: #6366f1;
  background: #fafaff;
}

.drop-zone--over {
  border-color: #4f46e5;
  background: #eef2ff;
}

.drop-zone__placeholder {
  text-align: center;
  color: #6b7280;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.drop-zone__placeholder p {
  margin: 0;
  font-size: 13px;
}

.drop-zone__hint {
  font-size: 11px !important;
  color: #9ca3af !important;
}

.upload-previews {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.upload-preview {
  position: relative;
  width: 80px;
  height: 80px;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid #e5e7eb;
}

.upload-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upload-preview__remove {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 18px;
  height: 18px;
  background: rgba(0, 0, 0, .6);
  color: #fff;
  border: none;
  border-radius: 50%;
  font-size: 12px;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-preview--add {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  color: #9ca3af;
  background: #f9fafb;
  cursor: pointer;
  transition: background 150ms, color 150ms;
}

.upload-preview--add:hover {
  background: #e0e7ff;
  color: #4f46e5;
}

.role-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.role-btn {
  padding: 6px 14px;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  background: #fff;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  color: #374151;
  transition: all 150ms;
}

.role-btn:hover {
  border-color: #a5b4fc;
  background: #eef2ff;
}

.role-btn--active {
  border-color: #4f46e5;
  background: #4f46e5;
  color: #fff;
}

/* ── Empty State ────────────────────────────────────────── */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  background: #fff;
  border: 2px dashed #e5e7eb;
  border-radius: 16px;
  text-align: center;
}

.empty-state__icon {
  width: 56px;
  height: 56px;
  background: #f3f4f6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  font-size: 22px;
  margin-bottom: 14px;
}

.empty-state h3 {
  font-size: 16px;
  font-weight: 700;
  margin: 0 0 6px;
}

.empty-state p {
  font-size: 13px;
  color: #6b7280;
  margin: 0 0 20px;
  max-width: 340px;
}

/* ── Skeletons ──────────────────────────────────────────── */
.skeleton-card {
  background: #fff;
  border: 1px solid #f3f4f6;
  border-radius: 14px;
  padding: 14px;
  overflow: hidden;
}

.skeleton-img {
  width: 100%;
  height: 140px;
  background: #f3f4f6;
  border-radius: 10px;
  margin-bottom: 12px;
  animation: pulse 1.5s infinite;
}

.skeleton-line {
  height: 12px;
  background: #f3f4f6;
  border-radius: 6px;
  margin-bottom: 8px;
  animation: pulse 1.5s infinite;
}

.skeleton-review {
  background: #fff;
  border: 1px solid #f3f4f6;
  border-radius: 14px;
  padding: 16px;
}

@keyframes pulse {

  0%,
  100% {
    opacity: 1;
  }

  50% {
    opacity: 0.5;
  }
}

/* ── Buttons ────────────────────────────────────────────── */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 9px 18px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  transition: background 150ms, transform 100ms, opacity 150ms;
  white-space: nowrap;
  font-family: inherit;
}

.btn:active {
  transform: scale(0.97);
}

.btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.btn--primary {
  background: #4f46e5;
  color: #fff;
}

.btn--primary:hover:not(:disabled) {
  background: #4338ca;
}

.btn--ghost {
  background: #fff;
  color: #374151;
  border: 1px solid #e5e7eb;
}

.btn--ghost:hover {
  background: #f9fafb;
}

.btn--outline {
  background: transparent;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn--outline:hover {
  background: #f9fafb;
}

.btn--danger {
  background: #dc2626;
  color: #fff;
}

.btn--danger:hover:not(:disabled) {
  background: #b91c1c;
}

.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  background: #fff;
  color: #6b7280;
  cursor: pointer;
  padding: 0;
  transition: all 150ms;
  flex-shrink: 0;
}

.icon-btn:hover {
  background: #f3f4f6;
}

.icon-btn--edit:hover {
  color: #4f46e5;
  border-color: #a5b4fc;
  background: #eef2ff;
}

.icon-btn--delete:hover {
  color: #dc2626;
  border-color: #fca5a5;
  background: #fef2f2;
}

.icon-btn--image:hover {
  color: #0891b2;
  border-color: #a5f3fc;
  background: #ecfeff;
}

/* ── Tags & Badges ──────────────────────────────────────── */
.tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 5px;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  background: #e0e7ff;
  color: #3730a3;
}

.badge {
  display: inline-flex;
  align-items: center;
  padding: 3px 8px;
  border-radius: 5px;
  font-size: 10px;
  font-weight: 700;
}

.badge--featured {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 1;
  background: #fef3c7;
  color: #92400e;
  border: 1px solid #fcd34d;
}

.badge--inactive {
  background: #fee2e2;
  color: #991b1b;
}

/* ── Misc ───────────────────────────────────────────────── */
.link {
  color: #4f46e5;
  cursor: pointer;
  font-weight: 600;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.opt {
  font-size: 11px;
  color: #9ca3af;
  font-weight: 400;
}

.hidden {
  display: none;
}

/* ── Modal ──────────────────────────────────────────────── */
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 100;
  background: rgba(17, 24, 39, .5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.modal {
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, .2);
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal--sm {
  max-width: 380px;
  padding: 28px;
  text-align: center;
}

.modal--upload {
  max-width: 480px;
}

.modal__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px;
  border-bottom: 1px solid #f3f4f6;
}

.modal__head h3 {
  font-size: 16px;
  font-weight: 800;
  margin: 0;
}

.modal__body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.modal__foot {
  padding: 14px 20px;
  border-top: 1px solid #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
}

.modal__foot--center {
  justify-content: center;
}

.modal__delete-icon {
  width: 50px;
  height: 50px;
  background: #fee2e2;
  color: #dc2626;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 14px;
}

.modal__delete-title {
  font-size: 18px;
  font-weight: 800;
  margin: 0 0 6px;
}

.modal__delete-sub {
  font-size: 13px;
  color: #6b7280;
  margin: 0 0 20px;
}

/* ── Forms ──────────────────────────────────────────────── */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-group label {
  font-size: 12px;
  font-weight: 600;
  color: #374151;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 9px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  font-size: 13px;
  color: #111827;
  background: #f9fafb;
  outline: none;
  font-family: inherit;
  transition: border-color 150ms, background 150ms, box-shadow 150ms;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: #6366f1;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, .12);
}

.form-group textarea {
  resize: vertical;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.divider {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #9ca3af;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #e5e7eb;
}

.form-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 12px 14px;
  gap: 12px;
}

.form-toggle__label {
  font-size: 13px;
  font-weight: 600;
  margin: 0 0 2px;
}

.form-toggle__sub {
  font-size: 11px;
  color: #6b7280;
  margin: 0;
}

.toggle {
  position: relative;
  width: 44px;
  height: 24px;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  background: #d1d5db;
  transition: background 200ms;
  flex-shrink: 0;
  padding: 0;
}

.toggle--on {
  background: #4f46e5;
}

.toggle__knob {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: #fff;
  border-radius: 50%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, .2);
  transition: transform 200ms;
}

.toggle--on .toggle__knob {
  transform: translateX(20px);
}

/* ── Star Picker ────────────────────────────────────────── */
.star-picker {
  display: flex;
  gap: 4px;
}

.star-pick {
  font-size: 24px;
  background: none;
  border: none;
  cursor: pointer;
  color: #e5e7eb;
  padding: 0;
  transition: color 100ms, transform 100ms;
}

.star-pick:hover,
.star-pick--on {
  color: #f59e0b;
}

.star-pick:hover {
  transform: scale(1.15);
}

/* ── Transitions ────────────────────────────────────────── */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.25s ease;
}

.modal-fade-enter-active .modal,
.modal-fade-leave-active .modal {
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.25s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
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

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.spin {
  animation: spin 700ms linear infinite;
}

/* ── Responsive ─────────────────────────────────────────── */
@media (max-width: 640px) {
  .page-header {
    flex-direction: column;
  }

  .page-header__actions {
    width: 100%;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .grid-3 {
    grid-template-columns: 1fr;
  }

  .grid-4 {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>