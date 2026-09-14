<template>
  <div class="dashboard">

    <header class="dash-header">
      <div class="dash-header__left">
        <div class="dash-header__breadcrumb">
          <span class="dash-header__breadcrumb-root">Padjajaran CCTV</span>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m9 18 6-6-6-6"/></svg>
          <span class="dash-header__breadcrumb-current">Dashboard</span>
        </div>
        <h1 class="dash-header__title">Overview</h1>
      </div>
      <div class="dash-header__right">
        <div class="dash-header__date">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
          {{ todayLabel }}
        </div>
        <div class="poll-indicator">
          <span class="poll-dot" :class="{ 'poll-dot--syncing': isRefreshing }"></span>
          <span class="poll-label">{{ isRefreshing ? 'Memperbarui…' : `Update ${pollCountdown}d` }}</span>
        </div>
        <button class="dash-header__refresh" @click="manualRefresh" :class="{ spinning: isRefreshing }">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
          Refresh
        </button>
      </div>
    </header>

    <main class="dash-main">

      <div class="range-tabs">
        <button
          v-for="t in rangeTabs"
          :key="t.value"
          class="range-tab"
          :class="{ active: activeRange === t.value }"
          @click="setRange(t.value)"
        >{{ t.label }}</button>
      </div>

      <section class="kpi-grid">
        <div
          v-for="(card, i) in kpiCards"
          :key="card.key"
          class="kpi-card"
          :class="[`kpi-card--${card.color}`, { 'cursor-pointer': card.link }]"
          :style="{ animationDelay: `${i * 60}ms` }"
          @click="card.link && $router.push(card.link)"
        >
          <div class="kpi-card__top">
            <div class="kpi-card__icon-wrap" :class="`kpi-card__icon-wrap--${card.color}`">
              <span class="kpi-card__icon" v-html="card.icon"></span>
            </div>
            <div class="kpi-card__badge" v-if="card.badge" :class="`kpi-card__badge--${card.badgeType}`">
              {{ card.badge }}
            </div>
          </div>
          <div class="kpi-card__body">
            <div class="kpi-card__value">
              <span v-if="summaryLoading" class="skeleton skeleton--value"></span>
              <span v-else>{{ card.formatted }}</span>
            </div>
            <div class="kpi-card__label">{{ card.label }}</div>
            <div class="kpi-card__sub" v-if="card.sub">{{ card.sub }}</div>
          </div>
        </div>
      </section>

      <div class="content-grid">

        <div class="content-col content-col--main">

          <div class="card card--chart">
            <div class="card__header">
              <div>
                <h2 class="card__title">Revenue</h2>
                <p class="card__subtitle">Pendapatan bersih dari transaksi terkonfirmasi</p>
              </div>
              <div class="chart-tabs">
                <button
                  v-for="r in chartRanges"
                  :key="r.value"
                  class="chart-tab"
                  :class="{ active: chartRange === r.value }"
                  @click="setChartRange(r.value)"
                >{{ r.label }}</button>
              </div>
            </div>

            <div class="chart-legend-row">
              <span class="legend-item">
                <span class="legend-line legend-line--blue"></span> Gross Revenue
              </span>
              <span class="legend-item">
                <span class="legend-line legend-line--green legend-line--dash"></span> Net Revenue
              </span>
              <span class="legend-item">
                <span class="legend-dot-sm legend-dot-sm--amber"></span> Target
              </span>
            </div>

            <div class="chart-area" v-if="chartLoading">
              <div class="chart-skeleton">
                <div v-for="h in 8" :key="h" class="chart-skeleton__bar" :style="{ height: (30 + Math.random() * 50) + '%' }"></div>
              </div>
            </div>
            <div class="chart-area" v-else>
              <svg ref="revSvgEl" class="rev-svg"></svg>
              <div class="d3-tooltip" ref="tooltipEl">
                <div class="tt-date" ref="ttDate"></div>
                <div class="tt-row"><span class="tt-dot" style="background:#3b5bdb"></span><span class="tt-lbl">Gross</span><span class="tt-val" ref="ttGross"></span></div>
                <div class="tt-row"><span class="tt-dot" style="background:#12b886"></span><span class="tt-lbl">Net</span><span class="tt-val" ref="ttNet"></span></div>
                <div class="tt-row"><span class="tt-dot" style="background:#f59f00"></span><span class="tt-lbl">Target</span><span class="tt-val" ref="ttTarget"></span></div>
                <div class="tt-row"><span class="tt-dot" style="background:#868e96"></span><span class="tt-lbl">Orders</span><span class="tt-val" ref="ttOrders"></span></div>
              </div>
            </div>

            <div class="chart-summary">
              <div class="chart-summary__item">
                <span class="chart-summary__label">Total Gross</span>
                <span class="chart-summary__value">{{ fmtRp(chartTotalGross) }}</span>
              </div>
              <div class="chart-summary__item">
                <span class="chart-summary__label">Total Net</span>
                <span class="chart-summary__value chart-summary__value--green">{{ fmtRp(chartTotalNet) }}</span>
              </div>
              <div class="chart-summary__item">
                <span class="chart-summary__label">Total Order</span>
                <span class="chart-summary__value">{{ chartTotalOrders.toLocaleString('id') }}</span>
              </div>
              <div class="chart-summary__item">
                <span class="chart-summary__label">Avg Order</span>
                <span class="chart-summary__value">{{ fmtRp(chartAvgOrder) }}</span>
              </div>
            </div>
          </div>

          <div class="card card--table">
            <div class="card__header">
              <div>
                <h2 class="card__title">Aktivitas Terbaru</h2>
                <p class="card__subtitle">Transaksi & booking terkini</p>
              </div>
              <div class="activity-filter">
                <button
                  v-for="f in activityFilters"
                  :key="f.value"
                  class="filter-btn"
                  :class="{ active: activityFilter === f.value }"
                  @click="activityFilter = f.value"
                >{{ f.label }}</button>
              </div>
            </div>
            <div class="table-wrap">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Order / Booking</th>
                    <th>Pelanggan</th>
                    <th>Kategori</th>
                    <th>Status</th>
                    <th class="text-right">Nominal</th>
                    <th class="text-right">Waktu</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="activityLoading" v-for="n in 6" :key="`sk-${n}`" class="skeleton-row">
                    <td><span class="skeleton skeleton--text"></span></td>
                    <td><span class="skeleton skeleton--text skeleton--short"></span></td>
                    <td><span class="skeleton skeleton--text skeleton--short"></span></td>
                    <td><span class="skeleton skeleton--badge"></span></td>
                    <td><span class="skeleton skeleton--text skeleton--short" style="margin-left:auto"></span></td>
                    <td><span class="skeleton skeleton--text skeleton--short" style="margin-left:auto"></span></td>
                  </tr>
                  <tr
                    v-else
                    v-for="item in filteredActivity"
                    :key="item.id"
                    class="data-row"
                  >
                    <td>
                      <div class="order-cell">
                        <div class="order-cell__icon" :class="`order-cell__icon--${item.statusColor}`">
                          <span v-html="item.type === 'booking' ? iconBooking : (item.type === 'promo' ? iconPromo : iconOrder)"></span>
                        </div>
                        <div>
                          <div class="order-cell__id">{{ item.id }}</div>
                          <div class="order-cell__type">{{ 
                            item.type === 'booking' ? 'Jasa CCTV' : 
                            (item.type === 'promo' ? 'Promo' : 'Produk') 
                          }}</div>
                        </div>
                      </div>
                    </td>
                    <td class="text-cell">{{ item.customer }}</td>
                    <td><span class="cat-tag">{{ item.category }}</span></td>
                    <td>
                      <span class="status-badge" :class="`status-badge--${item.statusColor}`">
                        <span class="status-badge__dot"></span>
                        {{ item.statusLabel }}
                      </span>
                    </td>
                    <td class="text-right mono">{{ fmtRp(item.amount) }}</td>
                    <td class="text-right text-muted text-sm">{{ item.time }}</td>
                  </tr>
                  <tr v-if="!activityLoading && filteredActivity.length === 0">
                    <td colspan="6" class="empty-row">Tidak ada data</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="content-col content-col--side">

          <div class="card card--donut">
            <div class="card__header card__header--compact">
              <h2 class="card__title">Status Booking</h2>
            </div>
            <div class="donut-container">
              <svg ref="donutSvgEl" class="donut-svg"></svg>
              <div class="donut-tooltip" ref="donutTooltipEl">
                <div class="dt-label" ref="dtLabel"></div>
                <div class="dt-val" ref="dtVal"></div>
                <div class="dt-pct" ref="dtPct"></div>
              </div>
            </div>
            <div class="donut-legend">
              <div v-for="seg in donutLegendItems" :key="seg.label" class="donut-legend__item">
                <span class="donut-legend__dot" :style="{ background: seg.color }"></span>
                <span class="donut-legend__label">{{ seg.label }}</span>
                <span class="donut-legend__count">{{ seg.count }}</span>
              </div>
            </div>
          </div>

          <div class="card card--alerts">
            <div class="card__header card__header--compact">
              <h2 class="card__title">
                Alert
                <span v-if="alertCount > 0" class="alert-badge-pill">{{ alertCount }}</span>
              </h2>
            </div>
            <div v-if="alertsLoading" class="alerts-list">
              <div v-for="n in 3" :key="n" class="alert-item">
                <span class="skeleton skeleton--badge"></span>
                <span class="skeleton skeleton--text" style="flex:1; margin-left:8px"></span>
              </div>
            </div>
            <div v-else class="alerts-list">
              <div v-if="pendingLama.length > 0" class="alert-item alert-item--warn">
                <div class="alert-item__icon">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                </div>
                <div class="alert-item__body">
                  <div class="alert-item__title">{{ pendingLama.length }} booking pending &gt;24 jam</div>
                  <div class="alert-item__sub">Butuh konfirmasi segera</div>
                </div>
              </div>
              <div v-if="dpExpireSoon.length > 0" class="alert-item alert-item--red">
                <div class="alert-item__icon">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                </div>
                <div class="alert-item__body">
                  <div class="alert-item__title">{{ dpExpireSoon.length }} payment hampir expire</div>
                  <div class="alert-item__sub">Kurang dari 2 jam</div>
                </div>
              </div>
              <div v-if="slotPenuh.length > 0" class="alert-item alert-item--blue">
                <div class="alert-item__icon">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                </div>
                <div class="alert-item__body">
                  <div class="alert-item__title">{{ slotPenuh.length }} slot besok penuh</div>
                  <div class="alert-item__sub">Pertimbangkan tambah kapasitas</div>
                </div>
              </div>
              <div v-if="pendingPayment > 0" class="alert-item alert-item--orange">
                <div class="alert-item__icon">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="1" y="4" width="22" height="16" rx="2"/><line x1="1" y1="10" x2="23" y2="10"/></svg>
                </div>
                <div class="alert-item__body">
                  <div class="alert-item__title">{{ pendingPayment }} order belum bayar</div>
                  <div class="alert-item__sub">Menunggu pembayaran user</div>
                </div>
              </div>
              <div v-if="alertCount === 0" class="alert-empty">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#12b886" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                <span>Semua clear!</span>
              </div>
            </div>
          </div>

          <div class="card card--stock">
            <div class="card__header card__header--compact">
              <h2 class="card__title">Stok Produk</h2>
            </div>
            <div v-if="stockLoading" class="stock-list">
              <div v-for="n in 4" :key="n" class="stock-row">
                <span class="skeleton skeleton--text" style="flex:1"></span>
                <span class="skeleton skeleton--badge"></span>
              </div>
            </div>
            <div v-else class="stock-list">
              <div class="stock-row">
                <div class="stock-row__label"><span class="stock-dot stock-dot--blue"></span>Total Produk</div>
                <span class="stock-row__val">{{ stockSummary.total_products?.toLocaleString('id') || '—' }}</span>
              </div>
              <div class="stock-row">
                <div class="stock-row__label"><span class="stock-dot stock-dot--green"></span>Aktif</div>
                <span class="stock-row__val stock-row__val--green">{{ stockSummary.active_products?.toLocaleString('id') || '—' }}</span>
              </div>
              <div class="stock-row">
                <div class="stock-row__label"><span class="stock-dot stock-dot--orange"></span>Hampir Habis</div>
                <span class="stock-row__val stock-row__val--orange">{{ stockSummary.low_stock_count || '—' }}</span>
              </div>
              <div class="stock-row">
                <div class="stock-row__label"><span class="stock-dot stock-dot--red"></span>Stok Habis</div>
                <span class="stock-row__val stock-row__val--red">{{ stockSummary.out_of_stock_count || '—' }}</span>
              </div>
              <div class="stock-row stock-row--total">
                <div class="stock-row__label"><span class="stock-dot stock-dot--indigo"></span>Total Terjual</div>
                <span class="stock-row__val">{{ stockSummary.total_terjual?.toLocaleString('id') || '—' }}</span>
              </div>
            </div>
            <div class="rev-potential" v-if="!stockLoading && stockSummary.revenue_potential">
              <div class="rev-potential__label">
                <span>Potensi Revenue</span>
                <span class="rev-potential__val">{{ fmtRp(stockSummary.revenue_potential) }}</span>
              </div>
              <div class="rev-potential__bar">
                <div class="rev-potential__fill" :style="{ width: revPotentialPct + '%' }"></div>
              </div>
            </div>
          </div>

          <div class="card card--today">
            <div class="card__header card__header--compact">
              <h2 class="card__title">Hari Ini</h2>
              <span class="today-date">{{ todayShort }}</span>
            </div>
            <div v-if="todayLoading" class="today-slots">
              <div v-for="n in 3" :key="n" class="today-slot">
                <span class="skeleton skeleton--text"></span>
              </div>
            </div>
            <div v-else class="today-slots">
              <div
                v-for="(info, slot) in todaySlots"
                :key="slot"
                class="today-slot"
                :class="{ 'today-slot--full': info.is_full, 'today-slot--empty': info.booked === 0 }"
              >
                <div class="today-slot__time">{{ slotShort(slot) }}</div>
                <div class="today-slot__bar-wrap">
                  <div class="today-slot__bar">
                    <div
                      class="today-slot__fill"
                      :class="{ 'today-slot__fill--full': info.is_full }"
                      :style="{ width: (info.booked / 3 * 100) + '%' }"
                    ></div>
                  </div>
                </div>
                <div class="today-slot__count">
                  <span :class="info.is_full ? 'text-red' : 'text-muted'">{{ info.booked }}/3</span>
                </div>
              </div>
              <div class="today-summary">
                <div class="today-summary__item">
                  <span class="today-summary__num">{{ todayData.total_today || 0 }}</span>
                  <span class="today-summary__lbl">Total</span>
                </div>
                <div class="today-summary__item">
                  <span class="today-summary__num today-summary__num--green">{{ todayData.dp_paid_today || 0 }}</span>
                  <span class="today-summary__lbl">DP Lunas</span>
                </div>
                <div class="today-summary__item">
                  <span class="today-summary__num today-summary__num--blue">{{ todayData.progress_today || 0 }}</span>
                  <span class="today-summary__lbl">On-site</span>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>

      <div class="section-divider">
        <h2 class="section-divider__title">Promo & Campaigns</h2>
      </div>

      <section class="kpi-grid kpi-grid--promo">
        <div class="kpi-card kpi-card--violet">
          <div class="kpi-card__top">
            <div class="kpi-card__icon-wrap kpi-card__icon-wrap--violet">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>
            </div>
          </div>
          <div class="kpi-card__body">
            <div class="kpi-card__value">
              <span v-if="promoDashLoading" class="skeleton skeleton--value"></span>
              <span v-else>{{ promoDashData.summary?.active_promos || 0 }}</span>
            </div>
            <div class="kpi-card__label">Promo Aktif</div>
          </div>
        </div>

        <div class="kpi-card kpi-card--blue">
          <div class="kpi-card__top">
            <div class="kpi-card__icon-wrap kpi-card__icon-wrap--blue">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
            </div>
          </div>
          <div class="kpi-card__body">
            <div class="kpi-card__value">
              <span v-if="promoDashLoading" class="skeleton skeleton--value"></span>
              <span v-else>{{ (promoDashData.summary?.total_orders || 0).toLocaleString('id') }}</span>
            </div>
            <div class="kpi-card__label">Total Order Promo</div>
          </div>
        </div>

        <div class="kpi-card kpi-card--green">
          <div class="kpi-card__top">
            <div class="kpi-card__icon-wrap kpi-card__icon-wrap--green">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
            </div>
          </div>
          <div class="kpi-card__body">
            <div class="kpi-card__value">
              <span v-if="promoDashLoading" class="skeleton skeleton--value"></span>
              <span v-else>{{ fmtRp(promoDashData.summary?.total_revenue || 0) }}</span>
            </div>
            <div class="kpi-card__label">Revenue Promo</div>
          </div>
        </div>

        <div class="kpi-card kpi-card--orange">
          <div class="kpi-card__top">
            <div class="kpi-card__icon-wrap kpi-card__icon-wrap--orange">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            </div>
          </div>
          <div class="kpi-card__body">
            <div class="kpi-card__value">
              <span v-if="promoDashLoading" class="skeleton skeleton--value"></span>
              <span v-else>{{ fmtRp(promoDashData.summary?.total_savings || 0) }}</span>
            </div>
            <div class="kpi-card__label">Total Hemat Pelanggan</div>
          </div>
        </div>
      </section>

      <div class="content-grid mt-4">
        <div class="content-col content-col--main">
          <div class="card card--table">
            <div class="card__header">
              <div>
                <h2 class="card__title">Aktivitas Promo Terbaru</h2>
                <p class="card__subtitle">Transaksi terkini yang menggunakan promo</p>
              </div>
            </div>
            <div class="table-wrap">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Order ID</th>
                    <th>Pelanggan</th>
                    <th>Promo</th>
                    <th>Status</th>
                    <th class="text-right">Hemat</th>
                    <th class="text-right">Waktu</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="promoDashLoading" v-for="n in 5" :key="`psk-${n}`" class="skeleton-row">
                    <td colspan="6"><span class="skeleton skeleton--text"></span></td>
                  </tr>
                  <tr v-else v-for="act in promoDashData.recent_activities" :key="act.order_id" class="data-row">
                    <td class="mono" style="font-size: 11px;">{{ act.order_id }}</td>
                    <td class="text-cell">{{ act.username }}</td>
                    <td><span class="cat-tag">{{ act.promo_name }}</span></td>
                    <td>
                      <span class="status-badge" :class="`status-badge--${STATUS_COLOR_MAP[act.status] || 'gray'}`">
                        <span class="status-badge__dot"></span>
                        {{ STATUS_LABEL_MAP[act.status] || act.status }}
                      </span>
                    </td>
                    <td class="text-right text-green font-semibold">{{ fmtRp(act.total_discount) }}</td>
                    <td class="text-right text-muted text-sm">{{ relTime(act.created_at) }}</td>
                  </tr>
                  <tr v-if="!promoDashLoading && (!promoDashData.recent_activities || promoDashData.recent_activities.length === 0)">
                    <td colspan="6" class="empty-row">Belum ada aktivitas promo</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="content-col content-col--side">
          <div class="card card--stock">
            <div class="card__header card__header--compact">
              <h2 class="card__title">Top Promos</h2>
            </div>
            <div v-if="promoDashLoading" class="stock-list">
              <div v-for="n in 4" :key="`tpsk-${n}`" class="stock-row">
                <span class="skeleton skeleton--text" style="flex:1"></span>
              </div>
            </div>
            <div v-else class="stock-list pb-2">
              <div v-for="(p, i) in promoDashData.top_promos" :key="p.uuid" class="stock-row">
                <div class="stock-row__label">
                  <span class="stock-dot" :class="i === 0 ? 'stock-dot--orange' : 'stock-dot--blue'"></span>
                  {{ p.name }}
                </div>
                <span class="stock-row__val">{{ p.used_count }}x</span>
              </div>
              <div v-if="!promoDashData.top_promos || promoDashData.top_promos.length === 0" class="empty-row" style="padding: 16px;">
                Belum ada data promo
              </div>
            </div>
          </div>

          <div class="card card--trend mt-4">
            <div class="card__header card__header--compact">
              <h2 class="card__title">Trend Promo (7 Hari)</h2>
            </div>
            <div class="trend-chart-html">
              <div v-if="promoDashLoading" class="w-full flex items-end justify-center" style="height: 100%;">
                <span class="skeleton skeleton--text" style="width:80%; margin-bottom: 20px;"></span>
              </div>
              <div v-else-if="!promoDashData.trend_7_days || promoDashData.trend_7_days.length === 0" class="empty-row w-full flex items-center justify-center">
                Belum ada data trend
              </div>
              <div v-else class="html-bars">
                <div v-for="day in promoDashData.trend_7_days" :key="day.date" class="html-bar-col" :title="`${day.date}\nOrder: ${day.order_count}\nRev: ${fmtRp(day.revenue)}`">
                  <div class="html-bar-fill" :style="{ height: getBarHeight(day.revenue) + '%' }"></div>
                  <div class="html-bar-label">{{ day.date.slice(-2) }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as d3 from 'd3'
import api from '@/service/api'

// ── Helpers ──────────────────────────────────────────────────────
const fmtRp = (n) => {
  if (!n && n !== 0) return '—'
  if (n >= 1_000_000_000) return `Rp ${(n / 1_000_000_000).toFixed(1)}M`
  if (n >= 1_000_000)     return `Rp ${(n / 1_000_000).toFixed(1)}jt`
  if (n >= 1_000)         return `Rp ${(n / 1_000).toFixed(0)}rb`
  return `Rp ${n.toLocaleString('id')}`
}
const relTime = (iso) => {
  if (!iso) return '—'
  const diff = (Date.now() - new Date(iso)) / 1000
  if (diff < 60)    return 'baru saja'
  if (diff < 3600)  return `${Math.floor(diff / 60)} mnt lalu`
  if (diff < 86400) return `${Math.floor(diff / 3600)} jam lalu`
  return `${Math.floor(diff / 86400)} hr lalu`
}

const STATUS_COLOR_MAP = {
  settlement:'green', capture:'green', lunas:'green', done:'green',
  pending_payment:'orange', pending:'orange',
  confirmed:'blue', dp_paid:'blue', progress:'blue',
  cancel:'red', deny:'red', expire:'red',
}
const STATUS_LABEL_MAP = {
  settlement:'Lunas', capture:'Lunas', lunas:'Lunas', done:'Selesai',
  pending_payment:'Menunggu Bayar', pending:'Pending',
  confirmed:'Dikonfirmasi', dp_paid:'DP Dibayar', progress:'Proses',
  cancel:'Dibatalkan', deny:'Ditolak', expire:'Kadaluarsa',
}

// ── Polling ───────────────────────────────────────────────────────
const POLL_INTERVAL = 60
const isRefreshing  = ref(false)
const pollCountdown = ref(POLL_INTERVAL)
let pollTimer = null, countdownTimer = null

const startCountdown = () => {
  pollCountdown.value = POLL_INTERVAL
  clearInterval(countdownTimer)
  countdownTimer = setInterval(() => { if (pollCountdown.value > 0) pollCountdown.value-- }, 1000)
}
const startPolling = () => {
  clearInterval(pollTimer)
  pollTimer = setInterval(async () => { await refreshAll(); startCountdown() }, POLL_INTERVAL * 1000)
  startCountdown()
}

// ── State ─────────────────────────────────────────────────────────
const summaryLoading   = ref(true)
const chartLoading     = ref(true)
const activityLoading  = ref(true)
const alertsLoading    = ref(true)
const stockLoading     = ref(true)
const todayLoading     = ref(true)
const bookingLoading   = ref(true)
const promoDashLoading = ref(true)

const summaryData   = ref({})
const chartData     = ref([])
const activityData  = ref([])
const alertsData    = ref({})
const stockSummary  = ref({})
const todayData     = ref({})
const bookingKpi    = ref({})
const bookingStatus = ref([])
const promoDashData = ref({
  summary: {},
  trend_7_days: [],
  recent_activities: [],
  top_promos: []
})

const activeRange    = ref('all')
const chartRange     = ref('30d')
const activityFilter = ref('all')

// ── D3 refs ───────────────────────────────────────────────────────
const revSvgEl       = ref(null)
const tooltipEl      = ref(null)
const ttDate         = ref(null)
const ttGross        = ref(null)
const ttNet          = ref(null)
const ttTarget       = ref(null)
const ttOrders       = ref(null)
const donutSvgEl     = ref(null)
const donutTooltipEl = ref(null)
const dtLabel        = ref(null)
const dtVal          = ref(null)
const dtPct          = ref(null)

// ── Date labels ───────────────────────────────────────────────────
const todayLabel = computed(() => new Date().toLocaleDateString('id-ID', { weekday:'long', day:'numeric', month:'long', year:'numeric' }))
const todayShort = computed(() => new Date().toLocaleDateString('id-ID', { day:'numeric', month:'short' }))

// ── Tabs & filters ────────────────────────────────────────────────
const rangeTabs = [
  { value:'all', label:'Semua' },
  { value:'today', label:'Hari Ini' },
  { value:'week', label:'7 Hari' },
  { value:'month', label:'Bulan Ini' },
]
const chartRanges = [
  { value:'7d', label:'7H' },
  { value:'30d', label:'30H' },
  { value:'12m', label:'12B' },
]
const activityFilters = [
  { value:'all', label:'Semua' },
  { value:'order', label:'Produk' },
  { value:'booking', label:'Jasa' },
  { value:'promo', label:'Promo' },
]

// ── KPI cards ─────────────────────────────────────────────────────
const kpiCards = computed(() => {
  const s  = summaryData.value  || {}
  const bk = bookingKpi.value?.data || {}
  const rangeRevKey = { all:'total_revenue', today:'revenue_today', week:'revenue_this_week', month:'revenue_this_month' }[activeRange.value]
  const rev = s[rangeRevKey] ?? 0
  return [
    {
      key:'revenue', label:'Total Revenue', color:'blue',
      formatted: fmtRp(rev),
      icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>`,
      badge: activeRange.value !== 'all' ? '+' + fmtRp((s.revenue_this_month || 0) * 0.08) : 'Detail Laku ➜',
      badgeType: activeRange.value !== 'all' ? 'green' : 'blue',
      sub: `${(s.settlement_count||0).toLocaleString('id')} order sukses (Klik untuk rincian)`,
      link: '/transaksi/list?status=settlement'
    },
    {
      key:'orders', label:'Total Order', color:'indigo',
      formatted: (s.total_orders||0).toLocaleString('id'),
      icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>`,
      badge: s.orders_today ? `+${s.orders_today} hari ini` : 'Rincian ➜',
      badgeType:'blue', 
      sub: `${(s.pending_payment_count||0)} pending payment (Klik untuk rincian)`,
      link: '/transaksi/list'
    },
    {
      key:'booking', label:'Total Booking', color:'violet',
      formatted: (bk.total_booking||0).toLocaleString('id'),
      icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>`,
      badge: bk.booking_hari_ini ? `${bk.booking_hari_ini} hari ini` : 'Rincian ➜',
      badgeType:'violet', 
      sub: `${(bk.pending_count||0)} menunggu konfirmasi (Klik untuk rincian)`,
      link: '/jasa/booking'
    },
    {
      key:'shipped', label:'Dikirim', color:'green',
      formatted: (s.shipped_count||0).toLocaleString('id'),
      icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="3" width="15" height="13"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>`,
      badge: s.processing_shipment ? `${s.processing_shipment} diproses` : 'Rincian ➜',
      badgeType:'blue', 
      sub: `${(s.delivered_count||0)} terkirim (Klik untuk rincian)`,
      link: '/transaksi/shipping'
    },
    {
      key:'sold', label:'Item Terjual', color:'teal',
      formatted: (s.total_items_sold||0).toLocaleString('id'),
      icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>`,
      badge: 'Rincian ➜', 
      badgeType:'green', 
      sub: `AOV ${fmtRp(s.avg_order_value)} (Klik untuk rincian)`,
      link: '/transaksi/list?status=settlement'
    },
    {
      key:'revenue_booking', label:'Revenue Jasa', color:'orange',
      formatted: fmtRp(bk.total_revenue||0),
      icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>`,
      badge: 'Rincian ➜', 
      badgeType:'orange', 
      sub: `${(bk.lunas_count||0)} lunas (Klik untuk rincian)`,
      link: '/jasa/booking?status=lunas'
    },
  ]
})

// ── Chart computed ────────────────────────────────────────────────
const chartTotalGross  = computed(() => chartData.value.reduce((s, d) => s + (d.gross_revenue || 0), 0))
const chartTotalNet    = computed(() => chartData.value.reduce((s, d) => s + (d.net_revenue   || 0), 0))
const chartTotalOrders = computed(() => chartData.value.reduce((s, d) => s + (d.order_count   || 0), 0))
const chartAvgOrder    = computed(() => chartTotalOrders.value ? Math.round(chartTotalGross.value / chartTotalOrders.value) : 0)

// ── Activity feed ─────────────────────────────────────────────────
const iconBooking = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="3" y1="10" x2="21" y2="10"/></svg>`
const iconOrder   = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/></svg>`
const iconPromo   = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>`

const allActivity = computed(() =>
  (activityData.value || []).map(t => ({
    id: t.reference_id,
    type: t.activity_type,
    customer: t.title,
    category: t.description,
    statusLabel: t.status?.toUpperCase() || 'OK',
    statusColor: t.color || 'gray',
    icon: t.icon || 'i-heroicons-shopping-cart',
    amount: t.amount || 0,
    time: relTime(t.created_at),
  }))
)
const filteredActivity = computed(() => {
  if (activityFilter.value === 'all') return allActivity.value
  return allActivity.value.filter(a => a.type === activityFilter.value)
})

// ── Promo Chart Helpers ───────────────────────────────────────────
const maxTrendRevenue = computed(() => {
  if (!promoDashData.value.trend_7_days || promoDashData.value.trend_7_days.length === 0) return 0;
  return Math.max(...promoDashData.value.trend_7_days.map(d => d.revenue));
});

const getBarHeight = (revenue) => {
  const max = maxTrendRevenue.value;
  if (max === 0) return 0;
  // min height 5% agar terlihat bar nya walau sangat kecil
  return Math.max(5, (revenue / max) * 100);
};

// ── Donut legend data ─────────────────────────────────────────────
const DONUT_COLORS = {
  pending:'#f59f00', confirmed:'#3b5bdb', dp_paid:'#12b886',
  progress:'#7950f2', done:'#20c997', lunas:'#2f9e44', cancel:'#fa5252',
}
const DONUT_LABELS = {
  pending:'Pending', confirmed:'Confirmed', dp_paid:'DP Bayar',
  progress:'Progress', done:'Done', lunas:'Lunas', cancel:'Cancel',
}
const donutLegendItems = computed(() =>
  (bookingStatus.value || [])
    .filter(d => d.count > 0)
    .map(d => ({
      label: DONUT_LABELS[d.status] || d.status,
      color: DONUT_COLORS[d.status] || '#adb5bd',
      count: d.count,
    }))
)

// ── Alerts ────────────────────────────────────────────────────────
const pendingLama    = computed(() => alertsData.value?.data?.pending_lama     || [])
const dpExpireSoon   = computed(() => alertsData.value?.data?.dp_expire_soon   || [])
const slotPenuh      = computed(() => alertsData.value?.data?.slot_penuh_besok || [])
const pendingPayment = computed(() => summaryData.value?.pending_payment_count  || 0)
const alertCount     = computed(() =>
  pendingLama.value.length + dpExpireSoon.value.length +
  slotPenuh.value.filter(s => s.is_full).length +
  (pendingPayment.value > 0 ? 1 : 0)
)

// ── Stock ─────────────────────────────────────────────────────────
const revPotentialPct = computed(() => Math.min((stockSummary.value?.revenue_potential || 0) / 500_000_000 * 100, 100))

// ── Today slots ───────────────────────────────────────────────────
const todaySlots = computed(() => todayData.value?.data?.slot_summary || {})
const slotShort  = (slot) => slot.split('-')[0]

// ══════════════════════════════════════════════════════════════════
// D3 Revenue Chart
// ══════════════════════════════════════════════════════════════════
let revSvgInstance = null

const drawRevenueChart = () => {
  const el = revSvgEl.value
  if (!el || !chartData.value.length) return

  const data = chartData.value
  const W    = el.parentElement.clientWidth || 700
  const H    = 220
  const ml   = 60, mr = 20, mt = 16, mb = 32
  const iw   = W - ml - mr
  const ih   = H - mt - mb

  // Clear
  d3.select(el).selectAll('*').remove()
  const svg = d3.select(el)
    .attr('width', W)
    .attr('height', H)
    .attr('viewBox', `0 0 ${W} ${H}`)
  revSvgInstance = svg

  // Defs
  const defs = svg.append('defs')
  defs.append('linearGradient').attr('id','rg-gross').attr('x1','0').attr('x2','0').attr('y1','0').attr('y2','1')
    .selectAll('stop').data([{o:.16,p:'0%'},{o:0,p:'100%'}]).join('stop')
    .attr('offset', d => d.p).attr('stop-color','#3b5bdb').attr('stop-opacity', d => d.o)
  defs.append('linearGradient').attr('id','rg-net').attr('x1','0').attr('x2','0').attr('y1','0').attr('y2','1')
    .selectAll('stop').data([{o:.12,p:'0%'},{o:0,p:'100%'}]).join('stop')
    .attr('offset', d => d.p).attr('stop-color','#12b886').attr('stop-opacity', d => d.o)

  // Clip
  defs.append('clipPath').attr('id','rev-clip')
    .append('rect').attr('id','rev-clip-rect').attr('height', ih + 10).attr('y', -5).attr('width', 0)

  const g = svg.append('g').attr('transform', `translate(${ml},${mt})`)

  // Scales
  const xScale = d3.scalePoint().domain(data.map(d => d.label)).range([0, iw]).padding(0.05)
  const maxVal = d3.max(data, d => Math.max(d.gross_revenue || 0, d.target || 0)) * 1.12
  const yScale = d3.scaleLinear().domain([0, maxVal]).range([ih, 0])

  // Grid lines
  const ticks = yScale.ticks(4)
  g.append('g').attr('class','grid')
    .selectAll('line').data(ticks).join('line')
    .attr('x1', 0).attr('x2', iw)
    .attr('y1', d => yScale(d)).attr('y2', d => yScale(d))
    .attr('stroke', '#e9ecef').attr('stroke-width', 1)

  // Y axis labels
  g.append('g').attr('class','y-axis')
    .selectAll('text').data(ticks).join('text')
    .attr('x', -8).attr('y', d => yScale(d)).attr('dy', '.35em')
    .attr('text-anchor','end').attr('font-size', 10).attr('fill','#adb5bd')
    .attr('font-family','DM Mono, monospace').text(d => fmtRp(d))

  // X axis labels
  const skipN = Math.max(1, Math.floor(data.length / 7))
  const xLabelData = data.filter((_, i) => i % skipN === 0 || i === data.length - 1)
  g.append('g').attr('class','x-axis')
    .selectAll('text').data(xLabelData).join('text')
    .attr('x', d => xScale(d.label)).attr('y', ih + 18)
    .attr('text-anchor','middle').attr('font-size', 10).attr('fill','#adb5bd')
    .attr('font-family','DM Sans, system-ui').text(d => d.label)

  // Generators
  const lineGen = (yKey) => d3.line()
    .x(d => xScale(d.label))
    .y(d => yScale(d[yKey] || 0))
    .curve(d3.curveCatmullRom.alpha(0.5))

  const areaGen = (yKey) => d3.area()
    .x(d => xScale(d.label))
    .y0(ih).y1(d => yScale(d[yKey] || 0))
    .curve(d3.curveCatmullRom.alpha(0.5))

  const clipG = g.append('g').attr('clip-path','url(#rev-clip)')

  // Target dashed line
  clipG.append('path').datum(data)
    .attr('fill','none').attr('stroke','#f59f00')
    .attr('stroke-width', 1.5).attr('stroke-dasharray','5,4').attr('opacity',.65)
    .attr('d', lineGen('target'))

  // Gross area
  clipG.append('path').datum(data)
    .attr('fill','url(#rg-gross)').attr('d', areaGen('gross_revenue'))

  // Net area
  clipG.append('path').datum(data)
    .attr('fill','url(#rg-net)').attr('d', areaGen('net_revenue'))

  // Net line
  clipG.append('path').datum(data)
    .attr('fill','none').attr('stroke','#12b886')
    .attr('stroke-width', 2).attr('stroke-linecap','round')
    .attr('d', lineGen('net_revenue'))

  // Gross line
  clipG.append('path').datum(data)
    .attr('fill','none').attr('stroke','#3b5bdb')
    .attr('stroke-width', 2.5).attr('stroke-linecap','round')
    .attr('d', lineGen('gross_revenue'))

  // Dots
  const dotsG = g.append('g').attr('class','dots')
  dotsG.selectAll('circle').data(data).join('circle')
    .attr('cx', d => xScale(d.label)).attr('cy', d => yScale(d.gross_revenue || 0))
    .attr('r', 0).attr('fill','#3b5bdb').attr('stroke','#fff').attr('stroke-width', 2)
    .style('cursor','pointer')
    .on('mouseenter', function(event, d) {
      d3.select(this).transition().duration(120).attr('r', 5.5)
      showRevTooltip(event, d, el)
    })
    .on('mouseleave', function() {
      d3.select(this).transition().duration(100).attr('r', 3.5)
      hideRevTooltip()
    })
    .transition().delay((_, i) => 700 + i * 25).duration(250).attr('r', 3.5)

  // Crosshair
  const crossG = g.append('g').attr('class','crosshair').style('pointer-events','none').style('opacity', 0)
  const crossLine = crossG.append('line')
    .attr('stroke','rgba(0,0,0,.1)').attr('stroke-width', 1).attr('stroke-dasharray','3,3')
    .attr('y1', 0).attr('y2', ih)
  const crossDotG = crossG.append('circle').attr('r', 5).attr('fill','#3b5bdb').attr('stroke','#fff').attr('stroke-width', 2)
  const crossDotN = crossG.append('circle').attr('r', 4).attr('fill','#12b886').attr('stroke','#fff').attr('stroke-width', 2)

  // Overlay for hover
  g.append('rect').attr('width', iw).attr('height', ih).attr('fill','transparent')
    .style('cursor','crosshair')
    .on('mousemove', (event) => {
      const [mx] = d3.pointer(event)
      const domain = xScale.domain()
      const step = iw / Math.max(domain.length - 1, 1)
      const idx = Math.min(Math.max(0, Math.round(mx / step)), domain.length - 1)
      const row = data[idx]
      if (!row) return
      const cx = xScale(row.label)
      crossLine.attr('x1', cx).attr('x2', cx)
      crossDotG.attr('cx', cx).attr('cy', yScale(row.gross_revenue || 0))
      crossDotN.attr('cx', cx).attr('cy', yScale(row.net_revenue || 0))
      crossG.style('opacity', 1)
      showRevTooltip(event, row, el)
    })
    .on('mouseleave', () => { crossG.style('opacity', 0); hideRevTooltip() })

  // Animate clip
  d3.select('#rev-clip-rect')
    .transition().duration(900).ease(d3.easeQuadInOut).attr('width', iw)
}

const showRevTooltip = (event, row, svgEl) => {
  const tt = tooltipEl.value
  if (!tt) return
  ttDate.value.textContent   = row.label
  ttGross.value.textContent  = fmtRp(row.gross_revenue || 0)
  ttNet.value.textContent    = fmtRp(row.net_revenue   || 0)
  ttTarget.value.textContent = fmtRp(row.target        || 0)
  ttOrders.value.textContent = (row.order_count || 0) + ' order'
  const rect = svgEl.parentElement.getBoundingClientRect()
  const [mx] = d3.pointer(event, svgEl.parentElement)
  const ttW = 172
  let left = mx + 16
  if (left + ttW > rect.width) left = mx - ttW - 8
  tt.style.left    = left + 'px'
  tt.style.top     = '20px'
  tt.style.opacity = '1'
}
const hideRevTooltip = () => {
  if (tooltipEl.value) tooltipEl.value.style.opacity = '0'
}

// ══════════════════════════════════════════════════════════════════
// D3 Donut Chart
// ══════════════════════════════════════════════════════════════════
const drawDonutChart = () => {
  const el = donutSvgEl.value
  if (!el) return

  const items = (bookingStatus.value || []).filter(d => d.count > 0)
  const total = items.reduce((s, d) => s + d.count, 0) || 1

  const SIZE = 180, R = 70, IR = 48
  d3.select(el).selectAll('*').remove()
  const svg = d3.select(el)
    .attr('width', SIZE).attr('height', SIZE)
    .attr('viewBox', `0 0 ${SIZE} ${SIZE}`)
  const g = svg.append('g').attr('transform', `translate(${SIZE/2},${SIZE/2})`)

  // Background ring
  g.append('circle').attr('r', R).attr('fill','none')
    .attr('stroke','#f1f3f5').attr('stroke-width', R - IR)

  // Center text
  const centerNum = g.append('text')
    .attr('text-anchor','middle').attr('dy','-.2em')
    .attr('font-size', 22).attr('font-weight', 700).attr('fill','#1a1d23')
    .attr('font-family','DM Sans, sans-serif')
    .text(total)
  g.append('text')
    .attr('text-anchor','middle').attr('dy','1.2em')
    .attr('font-size', 9).attr('fill','#868e96')
    .attr('font-family','DM Sans, sans-serif')
    .text('Total Booking')

  if (!items.length) return

  // Arc generator
  const pieGen = d3.pie().value(d => d.count).sort(null).padAngle(0.025)
  const arcGen = d3.arc().innerRadius(IR).outerRadius(R).cornerRadius(2)
  const arcHover = d3.arc().innerRadius(IR - 2).outerRadius(R + 4).cornerRadius(2)

  const arcs = g.selectAll('.arc').data(pieGen(items)).join('g').attr('class','arc')

  arcs.append('path')
    .attr('fill', d => DONUT_COLORS[d.data.status] || '#adb5bd')
    .attr('d', arcGen)
    .style('cursor','pointer')
    .style('transition','opacity .15s')
    .on('mouseenter', function(event, d) {
      d3.select(this).transition().duration(120).attr('d', arcHover)
      const pct = Math.round(d.data.count / total * 100)
      showDonutTooltip(
        DONUT_LABELS[d.data.status] || d.data.status,
        d.data.count,
        pct
      )
      centerNum.text(d.data.count)
    })
    .on('mouseleave', function() {
      d3.select(this).transition().duration(100).attr('d', arcGen)
      hideDonutTooltip()
      centerNum.text(total)
    })
    // Animate in
    .each(function(d) { this._current = { startAngle: d.startAngle, endAngle: d.startAngle } })
    .transition().duration(800).ease(d3.easeBackOut.overshoot(0.6))
    .attrTween('d', function(d) {
      const i = d3.interpolate(this._current, d)
      return t => arcGen(i(t))
    })
}

const showDonutTooltip = (label, count, pct) => {
  const tt = donutTooltipEl.value
  if (!tt) return
  dtLabel.value.textContent = label
  dtVal.value.textContent   = count + ' booking'
  dtPct.value.textContent   = pct + '%'
  tt.style.opacity = '1'
}
const hideDonutTooltip = () => {
  if (donutTooltipEl.value) donutTooltipEl.value.style.opacity = '0'
}

// ── Fetch functions ───────────────────────────────────────────────
const fetchSummary = async () => {
  summaryLoading.value = true
  try { summaryData.value = (await api.get('/admin/dashboard/summary'))?.data?.data || {} }
  catch (e) { console.warn('summary', e) }
  finally { summaryLoading.value = false }
}
const fetchChart = async () => {
  chartLoading.value = true
  try { chartData.value = (await api.get(`/admin/dashboard/revenue-chart?range=${chartRange.value}`))?.data?.data || [] }
  catch (e) { console.warn('chart', e) }
  finally {
    chartLoading.value = false
    await nextTick()
    drawRevenueChart()
  }
}
const fetchActivity = async () => {
  activityLoading.value = true
  try { 
    const res = await api.get('/admin/activities?limit=15')
    activityData.value = res?.data?.data || [] 
  }
  catch (e) { console.warn('activity', e) }
  finally { activityLoading.value = false }
}
const fetchAlerts = async () => {
  alertsLoading.value = true
  try { alertsData.value = await api.get('/admin/dashboard/booking/alerts').then(r => r.data) }
  catch (e) { console.warn('alerts', e) }
  finally { alertsLoading.value = false }
}
const fetchStock = async () => {
  stockLoading.value = true
  try { stockSummary.value = (await api.get('/admin/dashboard/stock/summary'))?.data?.data || {} }
  catch (e) { console.warn('stock', e) }
  finally { stockLoading.value = false }
}
const fetchToday = async () => {
  todayLoading.value = true
  try { todayData.value = (await api.get('/admin/dashboard/booking/today'))?.data || {} }
  catch (e) { console.warn('today', e) }
  finally { todayLoading.value = false }
}
const fetchBookingKpi = async () => {
  bookingLoading.value = true
  try { bookingKpi.value = (await api.get('/admin/dashboard/booking/kpi'))?.data || {} }
  catch (e) { console.warn('booking kpi', e) }
  finally { bookingLoading.value = false }
}
const fetchBookingStatus = async () => {
  try {
    bookingStatus.value = (await api.get('/admin/dashboard/booking/status'))?.data?.data || []
    await nextTick()
    drawDonutChart()
  }
  catch (e) { console.warn('booking status', e) }
}
const fetchPromoDashboard = async () => {
  promoDashLoading.value = true
  try {
    const res = await api.get('/admin/promos/dashboard')
    promoDashData.value = res?.data || {
      summary: {}, trend_7_days: [], recent_activities: [], top_promos: []
    }
  } catch (e) {
    console.warn('promo dashboard error', e)
  } finally {
    promoDashLoading.value = false
  }
}

const fetchAll = () => Promise.all([
  fetchSummary(), fetchChart(), fetchActivity(),
  fetchAlerts(), fetchStock(), fetchToday(),
  fetchBookingKpi(), fetchBookingStatus(), fetchPromoDashboard()
])

const refreshAll = async () => {
  isRefreshing.value = true
  await fetchAll()
  isRefreshing.value = false
}
const manualRefresh = async () => { await refreshAll(); startCountdown() }
const setRange      = (v) => { activeRange.value = v }
const setChartRange = (v) => { chartRange.value = v; fetchChart() }

watch(chartRange, fetchChart)

// Redraw on resize
let resizeObs = null
onMounted(async () => {
  await fetchAll()
  startPolling()
  resizeObs = new ResizeObserver(() => {
    if (!chartLoading.value) drawRevenueChart()
  })
  if (revSvgEl.value) resizeObs.observe(revSvgEl.value.parentElement)
})
onUnmounted(() => {
  clearInterval(pollTimer)
  clearInterval(countdownTimer)
  resizeObs?.disconnect()
})
</script>

<style scoped>
@reference "tailwindcss"; 
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* ── TOKENS ────────────────────────────────────────────────────── */
:root {
  --bg:           #f0f2f5;
  --surface:      #ffffff;
  --surface-2:    #f8f9fb;
  --border:       #e4e7ec;
  --text-primary: #1a1d23;
  --text-muted:   #6b7280;
  --text-light:   #9ca3af;
  --blue:         #3b5bdb;
  --blue-light:   #eef2ff;
  --indigo:       #4263eb;
  --violet:       #7950f2;
  --violet-light: #f3f0ff;
  --green:        #2f9e44;
  --green-light:  #ebfbee;
  --teal:         #0f9b8e;
  --teal-light:   #e6fcf5;
  --orange:       #e8590c;
  --orange-light: #fff4e6;
  --red:          #c92a2a;
  --red-light:    #fff5f5;
  --shadow-sm:    0 1px 3px rgba(0,0,0,.06), 0 1px 2px rgba(0,0,0,.04);
  --shadow-md:    0 4px 12px rgba(0,0,0,.07), 0 2px 4px rgba(0,0,0,.04);
  --radius:       16px;
  --radius-sm:    10px;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
.dashboard {
  font-family: 'DM Sans', sans-serif;
  background: var(--bg);
  min-height: 100vh;
  color: var(--text-primary);
}

/* ── HEADER ────────────────────────────────────────────────────── */
.dash-header {
  position: sticky; top: 0; z-index: 50;
  background: rgba(240,242,245,.9);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
  padding: 14px 32px;
  display: flex; align-items: center; justify-content: space-between;
}
.dash-header__breadcrumb {
  display: flex; align-items: center; gap: 6px;
  font-size: 12px; color: var(--text-muted); margin-bottom: 2px;
}
.dash-header__breadcrumb svg { color: var(--text-light); }
.dash-header__breadcrumb-current { color: var(--text-primary); font-weight: 500; }
.dash-header__title { font-size: 22px; font-weight: 700; letter-spacing: -.4px; }
.dash-header__right { display: flex; align-items: center; gap: 12px; }
.dash-header__date {
  display: flex; align-items: center; gap: 6px;
  font-size: 13px; color: var(--text-muted);
  background: var(--surface); border: 1px solid var(--border);
  padding: 6px 12px; border-radius: 8px;
}
.dash-header__refresh {
  display: flex; align-items: center; gap: 6px;
  font-size: 13px; font-weight: 500; color: var(--blue);
  background: var(--blue-light); border: none; cursor: pointer;
  padding: 7px 14px; border-radius: 8px;
  transition: all .15s; font-family: 'DM Sans', sans-serif;
}
.dash-header__refresh:hover { background: #dde4ff; }
.dash-header__refresh.spinning svg { animation: spin .7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.poll-indicator {
  display: flex; align-items: center; gap: 6px;
  font-size: 12px; color: var(--text-muted);
  background: var(--surface); border: 1px solid var(--border);
  padding: 5px 10px; border-radius: 8px;
}
.poll-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--green); flex-shrink: 0;
}
.poll-dot--syncing { background: var(--orange); animation: blink .7s ease-in-out infinite; }
@keyframes blink { 0%,100% { opacity:1; } 50% { opacity:.3; } }

/* ── MAIN ──────────────────────────────────────────────────────── */
.dash-main { max-width: 1400px; margin: 0 auto; padding: 28px 32px; }

/* ── RANGE TABS ────────────────────────────────────────────────── */
.range-tabs {
  display: flex; gap: 4px; margin-bottom: 24px;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 10px; padding: 4px; width: fit-content;
}
.range-tab {
  padding: 6px 16px; border-radius: 7px; border: none;
  font-size: 13px; font-weight: 500; cursor: pointer;
  background: transparent; color: var(--text-muted);
  transition: all .15s; font-family: 'DM Sans', sans-serif;
}
.range-tab.active { background: var(--blue); color: #fff; box-shadow: 0 2px 8px rgba(59,91,219,.3); }

/* ── KPI GRID ──────────────────────────────────────────────────── */
.kpi-grid {
  display: grid; grid-template-columns: repeat(6, 1fr);
  gap: 16px; margin-bottom: 24px;
}
@media (max-width: 1200px) { .kpi-grid { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 768px)  { .kpi-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 480px)  { .kpi-grid { grid-template-columns: 1fr; } }

.kpi-card {
  background: var(--surface); border-radius: var(--radius);
  padding: 20px; border: 1px solid var(--border);
  box-shadow: var(--shadow-sm); animation: fadeUp .4s ease both;
  transition: box-shadow .2s, transform .2s;
}
.kpi-card:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); }
@keyframes fadeUp { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:translateY(0); } }

.kpi-card__top { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 14px; }
.kpi-card__icon-wrap {
  width: 40px; height: 40px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
}
.kpi-card__icon-wrap--blue   { background: var(--blue-light);   color: var(--blue); }
.kpi-card__icon-wrap--indigo { background: #eef2ff;             color: var(--indigo); }
.kpi-card__icon-wrap--violet { background: var(--violet-light); color: var(--violet); }
.kpi-card__icon-wrap--green  { background: var(--green-light);  color: var(--green); }
.kpi-card__icon-wrap--teal   { background: var(--teal-light);   color: var(--teal); }
.kpi-card__icon-wrap--orange { background: var(--orange-light); color: var(--orange); }

.kpi-card__badge { font-size: 11px; font-weight: 600; padding: 3px 8px; border-radius: 20px; }
.kpi-card__badge--green  { background: var(--green-light);  color: var(--green); }
.kpi-card__badge--blue   { background: var(--blue-light);   color: var(--blue); }
.kpi-card__badge--violet { background: var(--violet-light); color: var(--violet); }
.kpi-card__badge--orange { background: var(--orange-light); color: var(--orange); }

.kpi-card__value { font-size: 26px; font-weight: 700; letter-spacing: -.6px; line-height: 1; margin-bottom: 5px; }
.kpi-card__label { font-size: 12px; color: var(--text-muted); font-weight: 500; margin-bottom: 3px; }
.kpi-card__sub   { font-size: 11px; color: var(--text-light); }

/* ── CONTENT GRID ──────────────────────────────────────────────── */
.content-grid { display: grid; grid-template-columns: 1fr 320px; gap: 20px; align-items: start; }
@media (max-width: 1024px) { .content-grid { grid-template-columns: 1fr; } }

/* ── CARD BASE ─────────────────────────────────────────────────── */
.card {
  background: var(--surface); border-radius: var(--radius);
  border: 1px solid var(--border); box-shadow: var(--shadow-sm); overflow: hidden;
}
.card__header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 20px 24px 0; margin-bottom: 16px;
}
.card__header--compact { padding: 16px 20px 0; margin-bottom: 12px; }
.card__title { font-size: 15px; font-weight: 700; letter-spacing: -.2px; display: flex; align-items: center; gap: 8px; }
.card__subtitle { font-size: 12px; color: var(--text-muted); margin-top: 2px; }

/* ── CHART CARD ────────────────────────────────────────────────── */
.card--chart { margin-bottom: 20px; }

.chart-tabs {
  display: flex; gap: 4px;
  background: var(--surface-2); border: 1px solid var(--border);
  border-radius: 8px; padding: 3px;
}
.chart-tab {
  padding: 5px 12px; border-radius: 6px; border: none;
  font-size: 12px; font-weight: 600; cursor: pointer;
  background: transparent; color: var(--text-muted);
  transition: all .15s; font-family: 'DM Sans', sans-serif;
}
.chart-tab.active { background: var(--surface); color: var(--blue); box-shadow: var(--shadow-sm); }

/* Legend row */
.chart-legend-row {
  display: flex; gap: 20px; padding: 0 24px 10px;
}
.legend-item {
  display: flex; align-items: center; gap: 7px;
  font-size: 12px; color: var(--text-muted); font-weight: 500;
}
.legend-line { width: 22px; height: 3px; border-radius: 2px; display: inline-block; }
.legend-line--blue  { background: #3b5bdb; }
.legend-line--green { background: none; border-bottom: 2px dashed #12b886; height: 0; }
.legend-line--dash  { }
.legend-dot-sm { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
.legend-dot-sm--amber { background: #f59f00; }

/* Chart area */
.chart-area {
  position: relative; padding: 0 16px 8px;
}
.rev-svg { display: block; width: 100%; overflow: visible; }

/* D3 Tooltip */
.d3-tooltip {
  position: absolute; pointer-events: none;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 10px; padding: 10px 14px;
  font-size: 12px; min-width: 170px;
  opacity: 0; transition: opacity .12s;
  z-index: 99; top: 20px; left: 0;
  box-shadow: var(--shadow-md);
}
.tt-date { font-size: 11px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: .5px; margin-bottom: 7px; }
.tt-row  { display: flex; align-items: center; gap: 7px; padding: 2px 0; }
.tt-dot  { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.tt-lbl  { flex: 1; color: var(--text-muted); font-size: 11px; }
.tt-val  { font-weight: 600; font-family: 'DM Mono', monospace; font-size: 12px; }

/* Chart skeleton */
.chart-skeleton {
  height: 220px; display: flex; align-items: flex-end; gap: 8px; padding: 0 16px 8px;
}
.chart-skeleton__bar {
  flex: 1; background: linear-gradient(180deg, #e9ecef 0%, #f1f3f5 100%);
  border-radius: 4px 4px 0 0; animation: pulse 1.4s ease-in-out infinite;
}
@keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:.4; } }

/* Chart summary */
.chart-summary {
  display: grid; grid-template-columns: repeat(4, 1fr);
  border-top: 1px solid var(--border);
}
.chart-summary__item {
  padding: 14px 20px; border-right: 1px solid var(--border);
  display: flex; flex-direction: column; gap: 3px;
}
.chart-summary__item:last-child { border-right: none; }
.chart-summary__label { font-size: 11px; color: var(--text-light); font-weight: 500; text-transform: uppercase; letter-spacing: .5px; }
.chart-summary__value { font-size: 15px; font-weight: 700; }
.chart-summary__value--green { color: var(--green); }

/* ── TABLE CARD ────────────────────────────────────────────────── */
.activity-filter {
  display: flex; gap: 4px;
  background: var(--surface-2); border: 1px solid var(--border);
  border-radius: 8px; padding: 3px;
}
.filter-btn {
  padding: 4px 10px; border-radius: 6px; border: none;
  font-size: 12px; font-weight: 500; cursor: pointer;
  background: transparent; color: var(--text-muted);
  transition: all .15s; font-family: 'DM Sans', sans-serif;
}
.filter-btn.active { background: var(--surface); color: var(--text-primary); box-shadow: var(--shadow-sm); }

.table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th {
  padding: 10px 24px; text-align: left; font-size: 11px;
  font-weight: 600; text-transform: uppercase; letter-spacing: .5px;
  color: var(--text-light); background: var(--surface-2);
  border-top: 1px solid var(--border);
}
.data-table td { padding: 12px 24px; border-bottom: 1px solid var(--border); vertical-align: middle; }
.data-row:last-child td { border-bottom: none; }
.data-row:hover td { background: var(--surface-2); }

.order-cell { display: flex; align-items: center; gap: 10px; }
.order-cell__icon {
  width: 30px; height: 30px; border-radius: 8px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
}
.order-cell__icon--blue   { background: var(--blue-light);   color: var(--blue); }
.order-cell__icon--violet { background: var(--violet-light); color: var(--violet); }
.order-cell__icon--purple { background: #f3f0ff; color: #7950f2; }
.order-cell__icon--green  { background: var(--green-light);  color: var(--green); }
.order-cell__icon--orange { background: var(--orange-light); color: var(--orange); }
.order-cell__icon--red    { background: var(--red-light);    color: var(--red); }
.order-cell__icon--gray   { background: #f1f3f5; color: var(--text-muted); }
.order-cell__id   { font-weight: 600; font-size: 12px; font-family: 'DM Mono', monospace; }
.order-cell__type { font-size: 11px; color: var(--text-light); }

.cat-tag {
  font-size: 11px; background: var(--surface-2); border: 1px solid var(--border);
  border-radius: 6px; padding: 3px 8px; color: var(--text-muted);
  white-space: nowrap; max-width: 120px; overflow: hidden; text-overflow: ellipsis; display: inline-block;
}
.status-badge {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: 11px; font-weight: 600; padding: 4px 9px;
  border-radius: 20px; white-space: nowrap;
}
.status-badge__dot { width: 5px; height: 5px; border-radius: 50%; background: currentColor; }
.status-badge--green  { background: var(--green-light);  color: var(--green); }
.status-badge--blue   { background: var(--blue-light);   color: var(--blue); }
.status-badge--orange { background: var(--orange-light); color: var(--orange); }
.status-badge--red    { background: var(--red-light);    color: var(--red); }
.status-badge--violet { background: var(--violet-light); color: var(--violet); }
.status-badge--gray   { background: #f1f3f5; color: var(--text-muted); }

.text-right { text-align: right; }
.text-muted { color: var(--text-muted); }
.text-sm    { font-size: 12px; }
.mono       { font-family: 'DM Mono', monospace; font-size: 12px; font-weight: 500; }
.text-cell  { max-width: 120px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.empty-row  { text-align: center; color: var(--text-light); padding: 32px; font-size: 13px; }

/* ── SIDE CARDS ────────────────────────────────────────────────── */
.content-col--side { display: flex; flex-direction: column; gap: 16px; }

/* ── D3 DONUT ──────────────────────────────────────────────────── */
.card--donut .card__header { padding-bottom: 0; }
.donut-container {
  display: flex; justify-content: center; align-items: center;
  padding: 12px 0 8px; position: relative;
}
.donut-svg { display: block; }
.donut-tooltip {
  position: absolute; pointer-events: none;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 10px; padding: 8px 12px; font-size: 12px;
  opacity: 0; transition: opacity .15s; text-align: center;
  box-shadow: var(--shadow-md); min-width: 100px;
  top: 50%; right: -110px; transform: translateY(-50%);
}
.dt-label { font-size: 11px; font-weight: 600; color: var(--text-muted); margin-bottom: 3px; }
.dt-val   { font-size: 14px; font-weight: 700; color: var(--text-primary); }
.dt-pct   { font-size: 11px; color: var(--text-muted); margin-top: 2px; }

.donut-legend { padding: 4px 20px 16px; display: flex; flex-direction: column; gap: 8px; }
.donut-legend__item { display: flex; align-items: center; gap: 8px; font-size: 12px; }
.donut-legend__dot   { width: 8px; height: 8px; border-radius: 2px; flex-shrink: 0; }
.donut-legend__label { flex: 1; color: var(--text-muted); }
.donut-legend__count { font-weight: 700; font-size: 13px; }

/* ── ALERTS ────────────────────────────────────────────────────── */
.alert-badge-pill {
  background: #c92a2a; color: #fff;
  font-size: 10px; font-weight: 700; padding: 1px 7px; border-radius: 20px;
}
.alerts-list { padding: 0 16px 16px; display: flex; flex-direction: column; gap: 8px; }
.alert-item {
  display: flex; align-items: flex-start; gap: 10px;
  padding: 10px 12px; border-radius: var(--radius-sm); border: 1px solid;
}
.alert-item--warn   { background: #fff9db; border-color: #ffe066; }
.alert-item--red    { background: var(--red-light);    border-color: #ffa8a8; }
.alert-item--blue   { background: var(--blue-light);   border-color: #a5b4fc; }
.alert-item--orange { background: var(--orange-light); border-color: #ffd8a8; }
.alert-item__icon {
  width: 28px; height: 28px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  background: rgba(255,255,255,.6);
}
.alert-item--warn   .alert-item__icon { color: #e67700; }
.alert-item--red    .alert-item__icon { color: var(--red); }
.alert-item--blue   .alert-item__icon { color: var(--blue); }
.alert-item--orange .alert-item__icon { color: var(--orange); }
.alert-item__title { font-size: 12px; font-weight: 600; }
.alert-item__sub   { font-size: 11px; color: var(--text-muted); margin-top: 1px; }
.alert-empty {
  display: flex; align-items: center; gap: 8px;
  padding: 16px; color: var(--green); font-size: 13px; font-weight: 500;
}

/* ── STOCK ─────────────────────────────────────────────────────── */
.stock-list { padding: 0 20px 4px; display: flex; flex-direction: column; }
.stock-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 9px 0; border-bottom: 1px solid var(--border); font-size: 13px;
}
.stock-row:last-child { border-bottom: none; }
.stock-row--total { padding-top: 12px; border-top: 1px solid var(--border); margin-top: 4px; border-bottom: none; }
.stock-row__label { display: flex; align-items: center; gap: 8px; color: var(--text-muted); }
.stock-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.stock-dot--blue   { background: var(--blue); }
.stock-dot--green  { background: var(--green); }
.stock-dot--orange { background: var(--orange); }
.stock-dot--red    { background: var(--red); }
.stock-dot--indigo { background: var(--indigo); }
.stock-dot--violet { background: var(--violet); }
.stock-row__val         { font-weight: 700; }
.stock-row__val--green  { color: var(--green); }
.stock-row__val--orange { color: var(--orange); }
.stock-row__val--red    { color: var(--red); }
.rev-potential { padding: 12px 20px 16px; }
.rev-potential__label {
  display: flex; justify-content: space-between; align-items: center;
  font-size: 11px; color: var(--text-muted); font-weight: 500; margin-bottom: 6px;
}
.rev-potential__val { font-weight: 700; color: var(--text-primary); font-size: 12px; }
.rev-potential__bar { height: 5px; background: var(--border); border-radius: 3px; overflow: hidden; }
.rev-potential__fill {
  height: 100%; border-radius: 3px; transition: width .8s ease;
  background: linear-gradient(90deg, var(--blue), var(--violet));
}

/* ── TODAY ─────────────────────────────────────────────────────── */
.card--today .card__header { padding-bottom: 0; }
.today-date { font-size: 12px; color: var(--text-muted); font-weight: 500; }
.today-slots { padding: 8px 20px 16px; display: flex; flex-direction: column; gap: 10px; }
.today-slot { display: flex; align-items: center; gap: 10px; font-size: 12px; }
.today-slot__time { width: 48px; font-weight: 600; color: var(--text-muted); font-family: 'DM Mono', monospace; font-size: 11px; }
.today-slot__bar-wrap { flex: 1; }
.today-slot__bar { height: 6px; background: var(--border); border-radius: 3px; overflow: hidden; }
.today-slot__fill { height: 100%; background: var(--blue); border-radius: 3px; transition: width .6s ease; }
.today-slot__fill--full { background: var(--red); }
.today-slot__count { width: 28px; text-align: right; font-weight: 600; }
.text-red { color: var(--red); }
.today-summary {
  display: grid; grid-template-columns: repeat(3, 1fr);
  border-top: 1px solid var(--border); margin-top: 6px; padding-top: 12px;
}
.today-summary__item { display: flex; flex-direction: column; align-items: center; gap: 2px; }
.today-summary__num  { font-size: 22px; font-weight: 700; }
.today-summary__num--green { color: var(--green); }
.today-summary__num--blue  { color: var(--blue); }
.today-summary__lbl { font-size: 10px; color: var(--text-light); text-transform: uppercase; letter-spacing: .4px; }

/* ── SKELETON ──────────────────────────────────────────────────── */
.skeleton {
  display: inline-block;
  background: linear-gradient(90deg, #f1f3f5 25%, #e9ecef 50%, #f1f3f5 75%);
  background-size: 400% 100%; border-radius: 6px;
  animation: shimmer 1.4s ease infinite;
}
@keyframes shimmer { to { background-position: -400% 0; } }
.skeleton--value { width: 80px; height: 30px; border-radius: 8px; }
.skeleton--text  { width: 100%; height: 14px; }
.skeleton--short { width: 60%; }
.skeleton--badge { width: 64px; height: 22px; border-radius: 20px; }
.skeleton-row td { padding: 14px 24px; }

/* ── PROMO CUSTOM STYLES ───────────────────────────────────────── */
.section-divider {
  margin: 40px 0 20px;
  padding-bottom: 12px;
  border-bottom: 2px dashed var(--border);
}
.section-divider__title {
  font-size: 18px; font-weight: 700; color: var(--text-primary);
}
.kpi-grid--promo {
  grid-template-columns: repeat(4, 1fr);
}
.text-green { color: var(--green); }
.font-semibold { font-weight: 600; }

/* HTML Bar Chart */
.trend-chart-html {
  padding: 16px 20px; height: 160px; display: flex; align-items: flex-end;
}
.html-bars {
  display: flex; gap: 8px; width: 100%; height: 100%;
  align-items: flex-end; justify-content: space-between;
}
.html-bar-col {
  flex: 1; display: flex; flex-direction: column; justify-content: flex-end;
  align-items: center; height: 100%; gap: 6px; cursor: pointer;
}
.html-bar-fill {
  width: 100%; max-width: 24px; background: var(--violet);
  border-radius: 4px 4px 0 0; min-height: 4px;
  transition: height .5s ease; opacity: 0.85;
}
.html-bar-col:hover .html-bar-fill { opacity: 1; }
.html-bar-label { font-size: 10px; color: var(--text-muted); font-family: 'DM Mono', monospace; }

/* ── RESPONSIVE ────────────────────────────────────────────────── */
@media (max-width: 1024px) {
  .content-col--side { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .kpi-grid--promo { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 640px) {
  .dash-main { padding: 16px; }
  .dash-header { padding: 12px 16px; }
  .dash-header__date { display: none; }
  .card__header { padding: 16px 16px 0; }
  .data-table th, .data-table td { padding: 10px 16px; }
  .chart-summary { grid-template-columns: 1fr 1fr; }
  .content-col--side { grid-template-columns: 1fr; }
  .donut-tooltip { right: auto; left: 50%; top: auto; bottom: -60px; transform: translateX(-50%); }
}
</style>