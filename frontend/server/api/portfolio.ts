/**
 * server/api/portfolio.ts
 * ══════════════════════════════════════════════════════════════════
 * Tugas file ini (Nitro Server Route):
 *   - Menjadi proxy antara Nuxt frontend dan FastAPI backend
 *   - Menangani semua request GET /api/portfolio
 *   - Query params yang didukung:
 *       ?type=page          → GET /portfolio/page (aggregated, Redis-cached)
 *       ?type=projects      → GET /portfolio/projects (list)
 *       ?type=project&id=X  → GET /portfolio/projects/:id
 *       ?type=reviews       → GET /portfolio/reviews
 *   - Tambah cache header agar CDN/browser bisa cache response
 * ══════════════════════════════════════════════════════════════════
 */

import { defineEventHandler, getQuery, createError } from "h3";
const config = useRuntimeConfig()
const API_BASE = config.public.apiBase ?? "http://localhost:8000";

export default defineEventHandler(async (event) => {
  const query = getQuery(event);
  const type  = (query.type as string) ?? "page";
  const id    = query.id as string | undefined;

  let path = "";

  switch (type) {
    case "page":
      path = "/portfolio/page";
      break;
    case "projects":
      path = "/portfolio/projects";
      break;
    case "project":
      if (!id) throw createError({ statusCode: 400, message: "id diperlukan untuk type=project" });
      path = `/portfolio/projects/${id}`;
      break;
    case "reviews":
      path = "/portfolio/reviews";
      break;
    default:
      throw createError({ statusCode: 400, message: `type tidak dikenal: ${type}` });
  }

  try {
    const res = await $fetch<unknown>(`${API_BASE}${path}`, {
      headers: { Accept: "application/json" },
    });

    // Cache di browser 30 detik, di CDN 5 menit
    setResponseHeader(event, "Cache-Control", "public, s-maxage=300, max-age=30");
    return res;
  } catch (err: any) {
    const status  = err?.response?.status  ?? 502;
    const message = err?.response?._data?.detail ?? "Gagal menghubungi server.";
    throw createError({ statusCode: status, message });
  }
});