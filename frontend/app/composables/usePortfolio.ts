/**
 * composables/usePortfolio.ts
 * ══════════════════════════════════════════════════════════════════
 * Tugas file ini:
 *   - Typed composable untuk semua request data portofolio
 *   - Semua request lewat Nitro server (/api/portfolio?type=...)
 *   - Export tipe TypeScript yang cocok dengan schema FastAPI
 * ══════════════════════════════════════════════════════════════════
 */

// ── Types (mirror FastAPI schemas) ──────────────────────────────

export type ImageRole = "cover" | "before" | "after" | "gallery";
export type ProjectCategory =
  | "Residensial" | "Komersial" | "Retail" | "Korporat"
  | "Fasilitas Umum" | "F&B" | "Manufaktur" | "Lainnya";

export interface ImageOut {
  id:          string;
  url:         string;
  r2_key:      string;
  role:        ImageRole;
  alt_text:    string | null;
  sort_order:  number;
  uploaded_at: string;
}

export interface ReviewOut {
  id:         string;
  project_id: string | null;
  name:       string;
  role:       string | null;
  rating:     number;
  text:       string;
  is_active:  boolean;
  created_at: string;
}

export interface ProjectListOut {
  id:           string;
  title:        string;
  category:     ProjectCategory;
  location:     string;
  cameras:      number;
  package_slug: string | null;
  is_featured:  boolean;
  cover_image:  string | null;
}

export interface ProjectOut extends ProjectListOut {
  client_type:  string | null;
  problem:      string | null;
  solution:     string | null;
  result:       string | null;
  is_active:    boolean;
  created_at:   string;
  updated_at:   string | null;
  images:       ImageOut[];
  reviews:      ReviewOut[];
}

export interface FeaturedProjectOut {
  id:           string;
  client_type:  string | null;
  title:        string;
  problem:      string | null;
  solution:     string | null;
  result:       string | null;
  before_image: string | null;
  after_image:  string | null;
}

export interface PortfolioPageOut {
  featured:     FeaturedProjectOut | null;
  projects:     ProjectListOut[];
  testimonials: ReviewOut[];
}

// ── Composables ─────────────────────────────────────────────────

export const usePortfolioPage = () =>
  useAsyncData<PortfolioPageOut>("portfolio-page", () =>
    $fetch("/api/portfolio?type=page")
  );

export const usePortfolioProjects = () =>
  useAsyncData<ProjectOut[]>("portfolio-projects", () =>
    $fetch("/api/portfolio?type=projects")
  );

export const usePortfolioProject = (id: string) =>
  useAsyncData<ProjectOut>(`portfolio-project-${id}`, () =>
    $fetch(`/api/portfolio?type=project&id=${id}`)
  );