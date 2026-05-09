<template>
  <section
    v-if="section && section.items.length > 0"
    class="bs"
    :class="`bs--${resolvedMode}`"
    :data-id="identifier"
    :aria-label="section.title || identifier"
    itemscope
    itemtype="https://schema.org/ItemList"
  >
    <h2 v-if="showTitle && section.title" class="bs__title" itemprop="name">
      {{ section.title }}
    </h2>

    <!-- ══ SINGLE (infinite slider) ══ -->
    <div
      v-if="resolvedMode === 'single'"
      class="sl"
      role="region"
      :aria-label="`${section.title || 'Banner'} slider`"
    >
      <div
        class="sl__track"
        ref="trackEl"
        :style="trackStyle"
        @transitionend="onTransitionEnd"
      >
        <!-- clone last -->
        <div class="sl__slide" aria-hidden="true">
          <BannerLink :item="clonedLast" class="sl__link">
            <div class="sl__frame">
              <NuxtImg v-bind="imgProps(clonedLast, 1440, 500, false)" class="sl__img" />
            </div>
          </BannerLink>
        </div>

        <!-- real slides -->
        <div
          v-for="(item, i) in section.items"
          :key="item.uuid"
          class="sl__slide"
          :aria-hidden="i !== realActiveIndex"
          itemprop="itemListElement"
          itemscope
          itemtype="https://schema.org/ListItem"
        >
          <meta itemprop="position" :content="String(i + 1)" />
          <BannerLink :item="item" class="sl__link">
            <div class="sl__frame">
              <NuxtImg
                v-bind="imgProps(item, 1440, 500, i === 0)"
                class="sl__img"
                itemprop="image"
              />
            </div>
          </BannerLink>
        </div>

        <!-- clone first -->
        <div class="sl__slide" aria-hidden="true">
          <BannerLink :item="clonedFirst" class="sl__link">
            <div class="sl__frame">
              <NuxtImg v-bind="imgProps(clonedFirst, 1440, 500, false)" class="sl__img" />
            </div>
          </BannerLink>
        </div>
      </div>

      <template v-if="section.items.length > 1">
        <button
          class="sl__arrow sl__arrow--prev"
          @click="slidePrev"
          aria-label="Previous"
        >
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
          >
            <polyline points="15 18 9 12 15 6" />
          </svg>
        </button>
        <button class="sl__arrow sl__arrow--next" @click="slideNext" aria-label="Next">
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
          >
            <polyline points="9 18 15 12 9 6" />
          </svg>
        </button>
        <div class="sl__dots" role="tablist">
          <button
            v-for="(_, i) in section.items"
            :key="i"
            class="sl__dot"
            :class="{ 'sl__dot--active': realActiveIndex === i }"
            role="tab"
            :aria-selected="realActiveIndex === i"
            :aria-label="`Slide ${i + 1}`"
            @click="goTo(i)"
          />
        </div>
      </template>
    </div>

    <!-- ══ DOUBLE ══ -->
    <div v-else-if="resolvedMode === 'double'" class="layout-double">
      <BannerLink
        v-for="(item, i) in section.items.slice(0, 2)"
        :key="item.uuid"
        :item="item"
        class="layout-double__item"
        itemprop="itemListElement"
        itemscope
        itemtype="https://schema.org/ListItem"
      >
        <meta itemprop="position" :content="String(i + 1)" />
        <div class="img-frame">
          <NuxtImg
            v-bind="imgProps(item, 720, 400, i === 0)"
            class="cover-img"
            itemprop="image"
          />
        </div>
      </BannerLink>
    </div>

    <!-- ══ MIXED (1 large + 2 stacked) ══ -->
    <div v-else-if="resolvedMode === 'mixed'" class="layout-mixed">
      <BannerLink
        v-if="section.items[0]"
        :item="section.items[0]"
        class="layout-mixed__main"
      >
        <div class="img-frame">
          <NuxtImg
            v-bind="imgProps(section.items[0], 960, 560, true)"
            class="cover-img"
          />
        </div>
      </BannerLink>
      <div class="layout-mixed__side">
        <BannerLink
          v-for="(item, i) in section.items.slice(1, 3)"
          :key="item.uuid"
          :item="item"
          class="layout-mixed__sub"
        >
          <div class="img-frame">
            <NuxtImg v-bind="imgProps(item, 480, 270, false)" class="cover-img" />
          </div>
        </BannerLink>
      </div>
    </div>

    <!-- ══ TRIPLE ══ -->
    <div v-else-if="resolvedMode === 'triple'" class="layout-triple">
      <BannerLink
        v-for="(item, i) in section.items.slice(0, 3)"
        :key="item.uuid"
        :item="item"
        class="layout-triple__item"
      >
        <div class="img-frame">
          <NuxtImg v-bind="imgProps(item, 480, 320, i === 0)" class="cover-img" />
        </div>
      </BannerLink>
    </div>

    <!-- ══ QUAD ══ -->
    <div v-else-if="resolvedMode === 'quad'" class="layout-quad">
      <BannerLink
        v-for="(item, i) in section.items.slice(0, 4)"
        :key="item.uuid"
        :item="item"
        class="layout-quad__item"
      >
        <div class="img-frame">
          <NuxtImg v-bind="imgProps(item, 720, 400, i < 2)" class="cover-img" />
        </div>
      </BannerLink>
    </div>

    <!-- ══ ASYM LEFT ══ -->
    <div v-else-if="resolvedMode === 'asymLeft'" class="layout-asym layout-asym--left">
      <BannerLink
        v-if="section.items[0]"
        :item="section.items[0]"
        class="layout-asym__main"
      >
        <div class="img-frame">
          <NuxtImg
            v-bind="imgProps(section.items[0], 960, 540, true)"
            class="cover-img"
          />
        </div>
      </BannerLink>
      <div class="layout-asym__stack">
        <BannerLink
          v-for="(item, i) in section.items.slice(1, 3)"
          :key="item.uuid"
          :item="item"
          class="layout-asym__sub"
        >
          <div class="img-frame">
            <NuxtImg v-bind="imgProps(item, 480, 260, false)" class="cover-img" />
          </div>
        </BannerLink>
      </div>
    </div>

    <!-- ══ ASYM RIGHT ══ -->
    <div v-else-if="resolvedMode === 'asymRight'" class="layout-asym layout-asym--right">
      <div class="layout-asym__stack">
        <BannerLink
          v-for="(item, i) in section.items.slice(0, 2)"
          :key="item.uuid"
          :item="item"
          class="layout-asym__sub"
        >
          <div class="img-frame">
            <NuxtImg v-bind="imgProps(item, 480, 260, i === 0)" class="cover-img" />
          </div>
        </BannerLink>
      </div>
      <BannerLink
        v-if="section.items[2]"
        :item="section.items[2]"
        class="layout-asym__main"
      >
        <div class="img-frame">
          <NuxtImg
            v-bind="imgProps(section.items[2], 960, 540, false)"
            class="cover-img"
          />
        </div>
      </BannerLink>
    </div>

    <!-- ══ HERO STRIP ══ -->
    <div v-else-if="resolvedMode === 'heroStrip'" class="layout-herostrip">
      <BannerLink
        v-if="section.items[0]"
        :item="section.items[0]"
        class="layout-herostrip__hero"
      >
        <div class="img-frame">
          <NuxtImg
            v-bind="imgProps(section.items[0], 1440, 480, true)"
            class="cover-img"
          />
        </div>
      </BannerLink>
      <div class="layout-herostrip__row">
        <BannerLink
          v-for="(item, i) in section.items.slice(1, 4)"
          :key="item.uuid"
          :item="item"
          class="layout-herostrip__cell"
        >
          <div class="img-frame">
            <NuxtImg v-bind="imgProps(item, 480, 200, false)" class="cover-img" />
          </div>
        </BannerLink>
      </div>
    </div>

    <!-- ══ SPOTLIGHT ══ -->
    <div v-else-if="resolvedMode === 'spotlight'" class="layout-spotlight">
      <BannerLink
        v-if="section.items[0]"
        :item="section.items[0]"
        class="layout-spotlight__wrap"
      >
        <div class="img-frame img-frame--wide">
          <NuxtImg
            v-bind="imgProps(section.items[0], 1440, 560, true)"
            class="cover-img"
            itemprop="image"
          />
        </div>
      </BannerLink>
    </div>

    <!-- ══ MOSAIC ══ -->
    <div v-else-if="resolvedMode === 'mosaic'" class="layout-mosaic">
      <BannerLink
        v-for="(item, i) in section.items.slice(0, 5)"
        :key="item.uuid"
        :item="item"
        :class="['layout-mosaic__item', `layout-mosaic__item--${i}`]"
      >
        <div class="img-frame">
          <NuxtImg
            v-bind="
              imgProps(
                item,
                [960, 480, 480, 480, 480][i],
                [500, 250, 250, 250, 250][i],
                i === 0
              )
            "
            class="cover-img"
          />
        </div>
      </BannerLink>
    </div>

    <!-- ══ RIBBON (horizontal scroll) ══ -->
    <div
      v-else-if="resolvedMode === 'ribbon'"
      class="layout-ribbon"
      ref="ribbonEl"
      @wheel.prevent="onRibbonWheel"
    >
      <div class="layout-ribbon__track" :style="ribbonStyle">
        <BannerLink
          v-for="(item, i) in section.items"
          :key="item.uuid"
          :item="item"
          class="layout-ribbon__item"
        >
          <div class="img-frame img-frame--ribbon">
            <NuxtImg v-bind="imgProps(item, 640, 340, i < 2)" class="cover-img" />
          </div>
        </BannerLink>
      </div>
      <button
        class="rb__arrow rb__arrow--prev"
        @click="ribbonScroll(-1)"
        aria-label="Scroll left"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
        >
          <polyline points="15 18 9 12 15 6" />
        </svg>
      </button>
      <button
        class="rb__arrow rb__arrow--next"
        @click="ribbonScroll(1)"
        aria-label="Scroll right"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
        >
          <polyline points="9 18 15 12 9 6" />
        </svg>
      </button>
    </div>

    <!-- ══ FEATURE WIDE ══ -->
    <div v-else-if="resolvedMode === 'featureWide'" class="layout-featurewide">
      <BannerLink
        v-if="section.items[0]"
        :item="section.items[0]"
        class="layout-featurewide__wrap"
      >
        <div class="img-frame img-frame--wide">
          <NuxtImg
            v-bind="imgProps(section.items[0], 1440, 400, true)"
            class="cover-img"
          />
        </div>
      </BannerLink>
    </div>

    <!-- ══ CINEMATIC ══ -->
    <div v-else-if="resolvedMode === 'cinematic'" class="layout-cinematic">
      <BannerLink
        v-if="section.items[0]"
        :item="section.items[0]"
        class="layout-cinematic__wrap"
      >
        <div class="img-frame img-frame--cinema">
          <NuxtImg
            v-bind="imgProps(section.items[0], 1440, 580, true)"
            class="cover-img"
            itemprop="image"
          />
          <div class="layout-cinematic__vignette" />
        </div>
      </BannerLink>
    </div>

    <!-- ══ STACK (click to cycle) ══ -->
    <div v-else-if="resolvedMode === 'stack'" class="layout-stack">
      <div
        class="layout-stack__deck"
        @click="stackNext"
        role="button"
        aria-label="Next banner"
      >
        <div
          v-for="(item, i) in stackItems"
          :key="item.uuid + i"
          class="layout-stack__card"
          :class="{ 'layout-stack__card--top': i === 0 }"
          :style="stackCardStyle(i)"
        >
          <BannerLink :item="item" class="layout-stack__link">
            <div class="img-frame img-frame--stack">
              <NuxtImg v-bind="imgProps(item, 1200, 480, i === 0)" class="cover-img" />
            </div>
          </BannerLink>
        </div>
      </div>
      <div class="layout-stack__hint">
        <span>{{ realStackIndex + 1 }} / {{ section.items.length }}</span>
      </div>
    </div>

    <!-- ══ MARQUEE (auto-scroll) ══ -->
    <div
      v-else-if="resolvedMode === 'marquee'"
      class="layout-marquee"
      aria-label="Auto-scrolling banner"
    >
      <div class="layout-marquee__track" :style="{ '--dur': `${marqueeSpeed}s` }">
        <BannerLink
          v-for="(item, i) in [...section.items, ...section.items]"
          :key="`mq-${i}`"
          :item="item"
          class="layout-marquee__item"
          :aria-hidden="i >= section.items.length ? 'true' : 'false'"
        >
          <div class="img-frame img-frame--marquee">
            <NuxtImg v-bind="imgProps(item, 560, 300, i < 2)" class="cover-img" />
          </div>
        </BannerLink>
      </div>
      <div class="layout-marquee__fade layout-marquee__fade--l" aria-hidden="true" />
      <div class="layout-marquee__fade layout-marquee__fade--r" aria-hidden="true" />
    </div>

    <!-- ══ FILM STRIP ══ -->
    <div
      v-else-if="resolvedMode === 'filmStrip'"
      class="layout-film"
      ref="filmEl"
      @wheel.prevent="onFilmWheel"
    >
      <div class="layout-film__reel" :style="filmStyle">
        <BannerLink
          v-for="(item, i) in section.items"
          :key="item.uuid"
          :item="item"
          class="layout-film__frame"
          :class="{ 'layout-film__frame--active': i === filmActive }"
          @click.prevent="goToFilm(i)"
        >
          <div class="img-frame img-frame--film">
            <NuxtImg v-bind="imgProps(item, 640, 400, i < 2)" class="cover-img" />
          </div>
        </BannerLink>
      </div>
      <button
        class="rb__arrow rb__arrow--prev"
        @click="filmScroll(-1)"
        aria-label="Previous"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
        >
          <polyline points="15 18 9 12 15 6" />
        </svg>
      </button>
      <button class="rb__arrow rb__arrow--next" @click="filmScroll(1)" aria-label="Next">
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
        >
          <polyline points="9 18 15 12 9 6" />
        </svg>
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import {
  ref,
  computed,
  onMounted,
  onUnmounted,
  resolveComponent,
  defineComponent,
  h,
} from "vue";

// ─────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────
interface BannerItem {
  uuid: string;
  image_url: string;
  target_url?: string | null;
  alt_text?: string | null;
}
interface BannerSection {
  title?: string;
  mode?: string;
  items: BannerItem[];
}

type LayoutMode =
  | "single"
  | "double"
  | "mixed"
  | "triple"
  | "quad"
  | "asymLeft"
  | "asymRight"
  | "heroStrip"
  | "spotlight"
  | "mosaic"
  | "ribbon"
  | "featureWide"
  | "cinematic"
  | "stack"
  | "marquee"
  | "filmStrip";

// ─────────────────────────────────────────────
// Props
// ─────────────────────────────────────────────
const props = withDefaults(
  defineProps<{
    identifier: string;
    mode?: "auto" | LayoutMode;
    showTitle?: boolean;
    autoplayDelay?: number;
  }>(),
  {
    mode: "auto",
    showTitle: false,
    autoplayDelay: 4500,
  }
);

// ─────────────────────────────────────────────
// Fetch
// ─────────────────────────────────────────────
const { data: section } = await useFetch<BannerSection>(
  () => `/api/banner/${encodeURIComponent(props.identifier)}`,
  {
    key: `bs-${props.identifier}`,
    transform: (r: any) => r?.data ?? null,
    server: true,
    lazy: false,
  }
);

// ─────────────────────────────────────────────
// BannerLink — handles internal / external URLs
// ─────────────────────────────────────────────
const BannerLink = defineComponent({
  props: { item: Object },
  setup(p, { slots }) {
    const isExt = (url?: string | null) => !!url && /^https?:\/\//i.test(url);
    const normalize = (url?: string | null) => {
      if (!url) return "/";
      if (isExt(url)) return url;
      const s = url.trim().replace(/^https?:\/\/[^/]+/i, "");
      return s.startsWith("/") ? s : `/${s}`;
    };
    return () => {
      const href = normalize(p.item?.target_url);
      if (isExt(href)) {
        return h(
          "a",
          { href, target: "_blank", rel: "noopener noreferrer", class: "blink" },
          slots.default?.()
        );
      }
      const NL = resolveComponent("NuxtLink") as any;
      return h(NL, { to: href, class: "blink" }, slots.default);
    };
  },
});

// ─────────────────────────────────────────────
// Image props helper
// ─────────────────────────────────────────────
function imgProps(item: BannerItem, w: number, h: number, eager: boolean) {
  return {
    src: item.image_url,
    alt: item.alt_text || "",
    width: w,
    height: h,
    format: "webp",
    quality: "85",
    loading: eager ? "eager" : "lazy",
    fetchpriority: eager ? "high" : "auto",
    ...(eager ? { preload: true } : {}),
  };
}

// ─────────────────────────────────────────────
// Mode resolution — prop > section.mode > auto
// ─────────────────────────────────────────────
function resolveAutoMode(count: number): LayoutMode {
  if (count === 1) return "cinematic";
  if (count === 2) return "double";
  if (count === 3) return "mixed";
  if (count === 4) return "quad";
  if (count === 5) return "heroStrip";
  return "single";
}

const resolvedMode = computed(
  (): LayoutMode => {
    // 1. Explicit prop (not "auto")
    if (props.mode && props.mode !== "auto") return props.mode as LayoutMode;
    // 2. Backend-defined mode
    const backendMode = section.value?.mode;
    if (backendMode && backendMode !== "auto") return backendMode as LayoutMode;
    // 3. Auto by count
    return resolveAutoMode(section.value?.items?.length ?? 0);
  }
);

// ═══════════════════════════════════════════════════════
// SLIDER — infinite clone-based
// ═══════════════════════════════════════════════════════
const trackEl = ref<HTMLElement | null>(null);
const trackIndex = ref(1);
const sliding = ref(true);

const realActiveIndex = computed(() => {
  const n = section.value?.items?.length ?? 0;
  if (!n) return 0;
  return (((trackIndex.value - 1) % n) + n) % n;
});

const clonedFirst = computed(
  () => section.value?.items?.[0] ?? { uuid: "_cf", image_url: "", target_url: "/" }
);
const clonedLast = computed(() => {
  const items = section.value?.items ?? [];
  return items[items.length - 1] ?? { uuid: "_cl", image_url: "", target_url: "/" };
});

const trackStyle = computed(() => ({
  transform: `translateX(-${trackIndex.value * 100}%)`,
  transition: sliding.value ? "transform 600ms cubic-bezier(0.4, 0, 0.2, 1)" : "none",
}));

function onTransitionEnd() {
  const n = section.value?.items?.length ?? 0;
  if (!n) return;
  if (trackIndex.value === n + 1) {
    sliding.value = false;
    trackIndex.value = 1;
    setTimeout(() => {
      sliding.value = true;
    }, 16);
  }
  if (trackIndex.value === 0) {
    sliding.value = false;
    trackIndex.value = n;
    setTimeout(() => {
      sliding.value = true;
    }, 16);
  }
}

function slideNext() {
  trackIndex.value++;
  resetAutoplay();
}
function slidePrev() {
  trackIndex.value--;
  resetAutoplay();
}
function goTo(i: number) {
  trackIndex.value = i + 1;
  resetAutoplay();
}

let autoTimer: ReturnType<typeof setInterval> | null = null;
function startAutoplay() {
  const n = section.value?.items?.length ?? 0;
  if (props.autoplayDelay <= 0 || n <= 1) return;
  autoTimer = setInterval(slideNext, props.autoplayDelay);
}
function stopAutoplay() {
  if (autoTimer) {
    clearInterval(autoTimer);
    autoTimer = null;
  }
}
function resetAutoplay() {
  stopAutoplay();
  startAutoplay();
}

let touchStartX = 0;

onMounted(() => {
  if (resolvedMode.value === "single") {
    startAutoplay();
    const el = trackEl.value?.parentElement;
    if (el) {
      el.addEventListener(
        "touchstart",
        (e) => {
          touchStartX = e.touches[0].clientX;
        },
        { passive: true }
      );
      el.addEventListener(
        "touchend",
        (e) => {
          const dx = e.changedTouches[0].clientX - touchStartX;
          if (Math.abs(dx) > 40) dx < 0 ? slideNext() : slidePrev();
        },
        { passive: true }
      );
      el.addEventListener("mouseenter", stopAutoplay);
      el.addEventListener("mouseleave", startAutoplay);
    }
  }
});
onUnmounted(stopAutoplay);

// ─────────────────────────────────────────────
// STACK
// ─────────────────────────────────────────────
const stackActiveIdx = ref(0);
const realStackIndex = computed(() => stackActiveIdx.value);

const stackItems = computed(() => {
  const items = section.value?.items ?? [];
  const n = items.length;
  if (!n) return [];
  return [0, 1, 2].map((off) => items[(stackActiveIdx.value + off) % n]);
});

function stackCardStyle(i: number) {
  return {
    transform: `translateY(${[0, 8, 16][i] ?? 24}px) scale(${[1, 0.97, 0.94][i] ?? 0.9})`,
    opacity: [1, 0.5, 0.25][i] ?? 0,
    zIndex: 3 - i,
    transition: "transform 400ms cubic-bezier(0.4, 0, 0.2, 1), opacity 400ms",
    pointerEvents: i === 0 ? "auto" : "none",
  };
}
function stackNext() {
  const n = section.value?.items?.length ?? 0;
  if (n) stackActiveIdx.value = (stackActiveIdx.value + 1) % n;
}

// ─────────────────────────────────────────────
// MARQUEE
// ─────────────────────────────────────────────
const marqueeSpeed = computed(() =>
  Math.max(18, (section.value?.items?.length ?? 1) * 7)
);

// ─────────────────────────────────────────────
// RIBBON
// ─────────────────────────────────────────────
const ribbonEl = ref<HTMLElement | null>(null);
const ribbonOffset = ref(0);
const RIBBON_ITEM_W = 320 + 12; // width + gap

const ribbonStyle = computed(() => ({
  transform: `translateX(${ribbonOffset.value}px)`,
  transition: "transform 400ms cubic-bezier(0.4, 0, 0.2, 1)",
}));

function ribbonScroll(dir: -1 | 1) {
  const total = section.value?.items?.length ?? 0;
  const maxOff = -(total - 1) * RIBBON_ITEM_W;
  ribbonOffset.value = Math.max(
    maxOff,
    Math.min(0, ribbonOffset.value - dir * RIBBON_ITEM_W)
  );
}
function onRibbonWheel(e: WheelEvent) {
  ribbonScroll(e.deltaY > 0 ? 1 : -1);
}

// ─────────────────────────────────────────────
// FILM STRIP
// ─────────────────────────────────────────────
const filmEl = ref<HTMLElement | null>(null);
const filmOffset = ref(0);
const filmActive = ref(0);
const FILM_ITEM_W = 300 + 12;

const filmStyle = computed(() => ({
  transform: `translateX(${filmOffset.value}px)`,
  transition: "transform 400ms cubic-bezier(0.4, 0, 0.2, 1)",
}));

function goToFilm(i: number) {
  filmActive.value = i;
  filmOffset.value = -(i * FILM_ITEM_W);
}
function filmScroll(dir: -1 | 1) {
  const n = section.value?.items?.length ?? 0;
  goToFilm(Math.max(0, Math.min(n - 1, filmActive.value + dir)));
}
function onFilmWheel(e: WheelEvent) {
  filmScroll(e.deltaY > 0 ? 1 : -1);
}
</script>

<style scoped>
/* ═══════════════════════════════════════════════════
   DESIGN TOKENS
═══════════════════════════════════════════════════ */
.bs {
  --gap: 8px;
  --radius: 6px;
  --radius-sm: 4px;
  --transition: 200ms cubic-bezier(0.4, 0, 0.2, 1);
  --arrow-bg: rgba(255, 255, 255, 0.96);
  --arrow-border: rgba(0, 0, 0, 0.1);
  --arrow-color: #111;

  position: relative;
  width: 100%;
  margin-bottom: 24px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  -webkit-font-smoothing: antialiased;
}

/* ═══════════════════════════════════════════════════
   SECTION TITLE
═══════════════════════════════════════════════════ */
.bs__title {
  font-size: 16px;
  font-weight: 600;
  color: #111;
  margin: 0 0 12px;
  letter-spacing: -0.1px;
}

/* ═══════════════════════════════════════════════════
   SHARED — link reset, img frame, cover-img
═══════════════════════════════════════════════════ */
:deep(.blink) {
  display: block;
  text-decoration: none;
  color: inherit;
  outline-offset: 2px;
}
:deep(.blink:focus-visible) {
  outline: 2px solid #0066cc;
  border-radius: var(--radius);
}

.img-frame {
  position: relative;
  overflow: hidden;
  border-radius: var(--radius);
  background: #f0f0f0;
  width: 100%;
  height: 100%;
}

/* Hover: subtle lift on the image */
:deep(.blink:hover) .cover-img {
  transform: scale(1.03);
}

.cover-img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 400ms cubic-bezier(0.4, 0, 0.2, 1);
  will-change: transform;
}

/* ═══════════════════════════════════════════════════
   SHARED ARROW BUTTON (slider + ribbon + film)
═══════════════════════════════════════════════════ */
.sl__arrow,
.rb__arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 20;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--arrow-bg);
  border: 1px solid var(--arrow-border);
  color: var(--arrow-color);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0;
  transition: background var(--transition), box-shadow var(--transition),
    transform var(--transition);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}
.sl__arrow:hover,
.rb__arrow:hover {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.14);
  transform: translateY(-50%) scale(1.06);
}
.sl__arrow--prev,
.rb__arrow--prev {
  left: 12px;
}
.sl__arrow--next,
.rb__arrow--next {
  right: 12px;
}

/* ═══════════════════════════════════════════════════
   SINGLE SLIDER
═══════════════════════════════════════════════════ */
.sl {
  position: relative;
  width: 100%;
  aspect-ratio: 1440 / 480;
  overflow: hidden;
  border-radius: var(--radius);
}
.sl__track {
  display: flex;
  height: 100%;
  will-change: transform;
}
.sl__slide {
  flex: 0 0 100%;
  height: 100%;
}
.sl__link {
  display: block;
  height: 100%;
}
.sl__frame {
  height: 100%;
  border-radius: 0;
  overflow: hidden;
  background: #f0f0f0;
}
.sl__img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 400ms cubic-bezier(0.4, 0, 0.2, 1);
}
:deep(.sl__link:hover) .sl__img {
  transform: scale(1.03);
}

/* Dots */
.sl__dots {
  position: absolute;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 6px;
  z-index: 10;
}
.sl__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  border: none;
  cursor: pointer;
  padding: 0;
  transition: all 200ms;
}
.sl__dot--active {
  width: 20px;
  border-radius: 3px;
  background: #fff;
}

/* ═══════════════════════════════════════════════════
   DOUBLE
═══════════════════════════════════════════════════ */
.layout-double {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--gap);
}
.layout-double__item {
  aspect-ratio: 720 / 400;
}
.layout-double__item .img-frame {
  height: 100%;
}

/* ═══════════════════════════════════════════════════
   MIXED
═══════════════════════════════════════════════════ */
.layout-mixed {
  display: grid;
  grid-template-columns: 3fr 2fr;
  gap: var(--gap);
}
.layout-mixed__main {
  aspect-ratio: 960 / 560;
}
.layout-mixed__main .img-frame {
  height: 100%;
}
.layout-mixed__side {
  display: flex;
  flex-direction: column;
  gap: var(--gap);
}
.layout-mixed__sub {
  flex: 1;
  min-height: 0;
}
.layout-mixed__sub .img-frame {
  height: 100%;
}

/* ═══════════════════════════════════════════════════
   TRIPLE
═══════════════════════════════════════════════════ */
.layout-triple {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--gap);
}
.layout-triple__item {
  aspect-ratio: 480 / 320;
}
.layout-triple__item .img-frame {
  height: 100%;
}

/* ═══════════════════════════════════════════════════
   QUAD
═══════════════════════════════════════════════════ */
.layout-quad {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--gap);
}
.layout-quad__item {
  aspect-ratio: 720 / 400;
}
.layout-quad__item .img-frame {
  height: 100%;
}

/* ═══════════════════════════════════════════════════
   ASYM LEFT / RIGHT
═══════════════════════════════════════════════════ */
.layout-asym {
  display: grid;
  gap: var(--gap);
}
.layout-asym--left {
  grid-template-columns: 3fr 2fr;
}
.layout-asym--right {
  grid-template-columns: 2fr 3fr;
}

.layout-asym__main {
  aspect-ratio: 960 / 540;
}
.layout-asym__main .img-frame {
  height: 100%;
}

.layout-asym__stack {
  display: flex;
  flex-direction: column;
  gap: var(--gap);
}
.layout-asym__sub {
  flex: 1;
  min-height: 0;
}
.layout-asym__sub .img-frame {
  height: 100%;
}

/* ═══════════════════════════════════════════════════
   HERO STRIP
═══════════════════════════════════════════════════ */
.layout-herostrip {
  display: flex;
  flex-direction: column;
  gap: var(--gap);
}
.layout-herostrip__hero {
  aspect-ratio: 1440 / 440;
}
.layout-herostrip__hero .img-frame {
  height: 100%;
}
.layout-herostrip__row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--gap);
}
.layout-herostrip__cell {
  aspect-ratio: 480 / 200;
}
.layout-herostrip__cell .img-frame {
  height: 100%;
}

/* ═══════════════════════════════════════════════════
   SPOTLIGHT
═══════════════════════════════════════════════════ */
.layout-spotlight__wrap {
  display: block;
}
.img-frame--wide {
  aspect-ratio: 1440 / 500;
  border-radius: var(--radius);
}

/* ═══════════════════════════════════════════════════
   MOSAIC (5-cell bento grid)
═══════════════════════════════════════════════════ */
.layout-mosaic {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: auto auto;
  gap: var(--gap);
}
.layout-mosaic__item {
  display: block;
}
.layout-mosaic__item .img-frame {
  height: 100%;
  aspect-ratio: unset;
}

.layout-mosaic__item--0 {
  grid-column: 1 / 3;
  aspect-ratio: 960 / 500;
}
.layout-mosaic__item--1,
.layout-mosaic__item--2,
.layout-mosaic__item--3,
.layout-mosaic__item--4 {
  aspect-ratio: 480 / 250;
}

/* ═══════════════════════════════════════════════════
   RIBBON (horizontal scroll strip)
═══════════════════════════════════════════════════ */
.layout-ribbon {
  position: relative;
  overflow: hidden;
}
.layout-ribbon__track {
  display: flex;
  gap: var(--gap);
  padding: 2px 1px;
}
.layout-ribbon__item {
  flex: 0 0 320px;
}
.img-frame--ribbon {
  aspect-ratio: 320 / 180;
  border-radius: var(--radius);
}

/* ═══════════════════════════════════════════════════
   FEATURE WIDE
═══════════════════════════════════════════════════ */
.layout-featurewide__wrap {
  display: block;
}

/* ═══════════════════════════════════════════════════
   CINEMATIC
═══════════════════════════════════════════════════ */
.layout-cinematic__wrap {
  display: block;
}
.img-frame--cinema {
  aspect-ratio: 1440 / 540;
  border-radius: var(--radius);
}
.layout-cinematic__vignette {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, transparent 55%, rgba(0, 0, 0, 0.35) 100%);
  pointer-events: none;
  border-radius: var(--radius);
}

/* ═══════════════════════════════════════════════════
   STACK
═══════════════════════════════════════════════════ */
.layout-stack {
  position: relative;
  user-select: none;
}
.layout-stack__deck {
  position: relative;
  aspect-ratio: 1440 / 480;
  cursor: pointer;
}
.layout-stack__card {
  position: absolute;
  inset: 0;
  will-change: transform, opacity;
  transform-origin: center bottom;
}
.layout-stack__link {
  display: block;
  height: 100%;
}
.img-frame--stack {
  height: 100%;
  border-radius: var(--radius);
  overflow: hidden;
  background: #f0f0f0;
}
.img-frame--stack .cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.layout-stack__hint {
  margin-top: 28px;
  text-align: center;
  font-size: 12px;
  color: #888;
  letter-spacing: 0.3px;
}

/* ═══════════════════════════════════════════════════
   MARQUEE
═══════════════════════════════════════════════════ */
@keyframes marquee-run {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-50%);
  }
}
.layout-marquee {
  position: relative;
  overflow: hidden;
}
.layout-marquee__track {
  display: flex;
  gap: var(--gap);
  width: max-content;
  animation: marquee-run var(--dur, 28s) linear infinite;
}
.layout-marquee__track:hover {
  animation-play-state: paused;
}
.layout-marquee__item {
  flex: 0 0 300px;
}
.img-frame--marquee {
  aspect-ratio: 300 / 160;
  border-radius: var(--radius);
}
.layout-marquee__fade {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 80px;
  pointer-events: none;
  z-index: 5;
}
.layout-marquee__fade--l {
  left: 0;
  background: linear-gradient(90deg, #fff 0%, transparent 100%);
}
.layout-marquee__fade--r {
  right: 0;
  background: linear-gradient(270deg, #fff 0%, transparent 100%);
}

/* ═══════════════════════════════════════════════════
   FILM STRIP
═══════════════════════════════════════════════════ */
.layout-film {
  position: relative;
  overflow: hidden;
}
.layout-film__reel {
  display: flex;
  gap: var(--gap);
  padding: 2px 1px;
}
.layout-film__frame {
  flex: 0 0 300px;
  cursor: pointer;
  transition: opacity var(--transition);
  opacity: 0.55;
}
.layout-film__frame--active {
  opacity: 1;
}
.img-frame--film {
  aspect-ratio: 300 / 190;
  border-radius: var(--radius);
  outline: 2px solid transparent;
  transition: outline-color var(--transition);
}
.layout-film__frame--active .img-frame--film {
  outline-color: #0066cc;
}

/* ═══════════════════════════════════════════════════
   RESPONSIVE
═══════════════════════════════════════════════════ */
@media (max-width: 1024px) {
  .layout-mosaic {
    grid-template-columns: repeat(2, 1fr);
  }
  .layout-mosaic__item--0 {
    grid-column: 1 / 3;
  }
}

@media (max-width: 768px) {
  .bs {
    --gap: 6px;
  }

  .sl__arrow,
  .rb__arrow {
    display: none;
  }

  .layout-double,
  .layout-triple,
  .layout-quad {
    grid-template-columns: 1fr 1fr;
  }

  .layout-triple__item:nth-child(3) {
    display: none;
  }

  .layout-mixed {
    grid-template-columns: 1fr;
  }
  .layout-mixed__side {
    flex-direction: row;
  }
  .layout-mixed__sub {
    aspect-ratio: 480 / 270;
  }

  .layout-asym--left,
  .layout-asym--right {
    grid-template-columns: 1fr;
  }
  .layout-asym__stack {
    flex-direction: row;
  }

  .layout-herostrip__row {
    grid-template-columns: 1fr 1fr;
  }
  .layout-herostrip__cell:last-child {
    display: none;
  }

  .layout-mosaic {
    grid-template-columns: 1fr 1fr;
  }
  .layout-mosaic__item--0 {
    grid-column: 1 / 3;
  }
}

@media (max-width: 480px) {
  .bs {
    --gap: 4px;
  }

  .sl {
    aspect-ratio: 16 / 9;
  }

  .layout-double {
    grid-template-columns: 1fr;
  }
  .layout-double__item:nth-child(2) {
    display: none;
  }

  .layout-triple,
  .layout-quad {
    grid-template-columns: 1fr;
  }
  .layout-triple__item:not(:first-child),
  .layout-quad__item:not(:first-child):not(:nth-child(2)) {
    display: none;
  }

  .layout-mixed__side,
  .layout-asym__stack {
    display: none;
  }

  .layout-herostrip__row {
    grid-template-columns: 1fr;
  }
  .layout-herostrip__cell:not(:first-child) {
    display: none;
  }

  .layout-mosaic {
    grid-template-columns: 1fr;
  }
  .layout-mosaic__item--0 {
    grid-column: 1 / 2;
  }
  .layout-mosaic__item--3,
  .layout-mosaic__item--4 {
    display: none;
  }

  .layout-ribbon__item {
    flex: 0 0 80vw;
  }
  .layout-film__frame {
    flex: 0 0 80vw;
  }
  .layout-marquee__item {
    flex: 0 0 72vw;
  }

  .layout-marquee__fade {
    width: 40px;
  }
}

/* ═══════════════════════════════════════════════════
   REDUCED MOTION
═══════════════════════════════════════════════════ */
@media (prefers-reduced-motion: reduce) {
  .cover-img,
  .sl__img,
  .sl__track,
  .layout-ribbon__track,
  .layout-film__reel,
  .layout-marquee__track,
  .layout-stack__card {
    transition: none !important;
    animation: none !important;
  }
}
</style>
