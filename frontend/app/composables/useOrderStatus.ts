/**
 * useOrderStatus — Unified status badge tokens for dashboard (Amazon x Tokopedia style)
 * Reuses public palette tokens: #F0FBF2 (HomeBanner trust), #FFF0F2 (CardPerItems discount)
 * 4-state system: pending | progress | success | failed
 */

export type OrderStatusKey = "pending" | "progress" | "success" | "failed"

export interface OrderStatusConfig {
  label: string
  badge: string // tailwind classes for badge
}

const STATUS_MAP: Record<OrderStatusKey, OrderStatusConfig> = {
  pending: {
    label: "Menunggu Pembayaran",
    badge: "bg-amber-50 text-amber-700 border-amber-200",
  },
  progress: {
    label: "Diproses",
    badge: "bg-blue-50 text-blue-700 border-blue-200",
  },
  success: {
    label: "Selesai",
    badge: "bg-[#F0FBF2] text-emerald-800 border-[#D5EED9]",
  },
  failed: {
    label: "Dibatalkan",
    badge: "bg-[#FFF0F2] text-[#D62828] border-[#FCD5D8]",
  },
}

export function useOrderStatus() {
  /**
   * Resolve transaction + shipment status to unified badge config.
   * Mirrors orders/index.vue getStatusConfig logic but with 4-token palette.
   */
  function getOrderStatus(
    transactionStatus: string,
    shipmentStatus?: string,
    hasWaybill?: boolean,
  ): OrderStatusConfig {
    const t = (transactionStatus || "").toLowerCase()
    const s = (shipmentStatus || "").toLowerCase()

    // Failed states
    if (["expire", "cancel", "deny"].includes(t)) {
      return { ...STATUS_MAP.failed, label: "Dibatalkan" }
    }

    // Pending payment
    if (["pending", "pending_payment"].includes(t)) {
      return { ...STATUS_MAP.pending }
    }

    // Success states — check shipment progression
    if (["settlement", "success", "capture"].includes(t)) {
      if (["delivered", "completed"].includes(s)) {
        return { ...STATUS_MAP.success, label: "Selesai" }
      }
      if (s === "shipped" || hasWaybill) {
        return { ...STATUS_MAP.progress, label: "Dikirim" }
      }
      return { ...STATUS_MAP.progress, label: "Diproses" }
    }

    // Fallback
    return { ...STATUS_MAP.progress, label: t || "Proses" }
  }

  /**
   * Resolve booking/jasa status to unified badge config.
   * Maps jasa statuses (pending/confirmed/dp_paid/progress/done/lunas/cancel) to 4 tokens.
   */
  function getBookingStatus(status: string): OrderStatusConfig {
    const s = (status || "").toLowerCase()

    if (s === "cancel") return { ...STATUS_MAP.failed, label: "Dibatalkan" }
    if (["pending"].includes(s)) return { ...STATUS_MAP.pending, label: "Menunggu Konfirmasi" }
    if (["confirmed"].includes(s)) return { ...STATUS_MAP.pending, label: "Menunggu DP" }
    if (["dp_paid"].includes(s)) return { ...STATUS_MAP.progress, label: "DP Diterima" }
    if (["progress"].includes(s)) return { ...STATUS_MAP.progress, label: "Sedang Dikerjakan" }
    if (["done"].includes(s)) return { ...STATUS_MAP.success, label: "Selesai" }
    if (["lunas"].includes(s)) return { ...STATUS_MAP.success, label: "Lunas" }

    return { ...STATUS_MAP.progress, label: s || "Proses" }
  }

  return {
    getOrderStatus,
    getBookingStatus,
    STATUS_MAP,
  }
}
