<template>
  <div class="min-h-screen bg-aroma-dark">
    <Header />

    <!-- Hero Carousel -->
    <section class="relative min-h-screen flex items-end pb-24 overflow-hidden">
      <!-- Slides -->
      <div v-for="(img, i) in heroImages" :key="i"
        class="absolute inset-0 bg-cover bg-center transition-opacity duration-1000"
        :style="{ backgroundImage: `url('${img}')` }"
        :class="i === currentSlide ? 'opacity-65' : 'opacity-0'" />

      <!-- Overlay -->
      <div class="absolute inset-0 bg-gradient-to-t from-aroma-dark via-aroma-dark/40 to-transparent" />

      <!-- Arrow left -->
      <button @click="prevSlide(); resetAutoplay()"
        class="absolute left-4 md:left-8 top-1/2 -translate-y-1/2 z-20
               w-10 h-10 flex items-center justify-center
               bg-black/30 border border-white/20 text-white
               hover:bg-gold hover:border-gold hover:text-aroma-dark transition-colors">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
      </button>

      <!-- Arrow right -->
      <button @click="nextSlide(); resetAutoplay()"
        class="absolute right-4 md:right-8 top-1/2 -translate-y-1/2 z-20
               w-10 h-10 flex items-center justify-center
               bg-black/30 border border-white/20 text-white
               hover:bg-gold hover:border-gold hover:text-aroma-dark transition-colors">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
        </svg>
      </button>

      <!-- Content -->
      <div class="relative z-10 max-w-7xl mx-auto px-6 w-full pb-12">
        <p class="text-[10px] tracking-widest uppercase text-gold mb-4">Collection 2024</p>
        <h1 class="font-display text-6xl md:text-8xl text-aroma-text max-w-3xl leading-tight mb-6">
          {{ $t('home.hero_title') }}
        </h1>
        <p class="text-aroma-muted max-w-md leading-relaxed mb-10">{{ $t('home.hero_subtitle') }}</p>
        <div class="flex items-center gap-6 mb-12">
          <router-link to="/shop" class="btn-gold">{{ $t('home.hero_cta') }}</router-link>
          <router-link to="/shop" class="text-xs tracking-widest uppercase text-aroma-muted hover:text-aroma-text transition-colors">
            Ver Colecciones →
          </router-link>
        </div>

        <!-- Dots -->
        <div class="flex items-center gap-2">
          <button v-for="(_, i) in heroImages" :key="i"
            @click="goToSlide(i)"
            class="transition-all duration-300 rounded-full"
            :class="i === currentSlide
              ? 'w-6 h-2 bg-gold'
              : 'w-2 h-2 bg-white/40 hover:bg-white/70'" />
        </div>
      </div>
    </section>

    <!-- Categories strip -->
    <section class="border-t border-b border-aroma-border py-12">
      <div class="max-w-7xl mx-auto px-6">
        <div class="flex gap-8 overflow-x-auto scrollbar-hide">
          <router-link v-for="cat in categories" :key="cat.id"
            :to="`/shop?category=${cat.id}`"
            class="shrink-0 text-center group">
            <div class="w-20 h-20 bg-aroma-surface border border-aroma-border rounded-full flex items-center justify-center
                        mb-3 mx-auto group-hover:border-gold transition-colors">
              <svg class="w-7 h-7 text-gold" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1"
                  d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
              </svg>
            </div>
            <p class="text-[10px] tracking-widest uppercase text-aroma-muted group-hover:text-aroma-text transition-colors">
              {{ cat.name }}
            </p>
          </router-link>
        </div>
      </div>
    </section>

    <!-- Featured Products -->
    <section class="py-24">
      <div class="max-w-7xl mx-auto px-6">
        <div class="flex items-end justify-between mb-12">
          <div>
            <p class="text-[10px] tracking-widest uppercase text-gold mb-3">Selección Curada</p>
            <h2 class="font-display text-5xl text-aroma-text">{{ $t('home.featured_title') }}</h2>
          </div>
          <router-link to="/shop" class="btn-ghost hidden md:block">Ver todo</router-link>
        </div>

        <div v-if="loadingFeatured" class="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div v-for="i in 4" :key="i" class="bg-aroma-surface animate-pulse aspect-[3/4]" />
        </div>

        <div v-else-if="featuredProducts.length === 0" class="text-center py-16 text-aroma-muted">
          <p class="text-sm tracking-widest uppercase">Próximamente</p>
        </div>

        <div v-else class="grid grid-cols-2 md:grid-cols-4 gap-6">
          <ProductCard v-for="p in featuredProducts" :key="p.id" :product="p" />
        </div>
      </div>
    </section>

    <!-- Marquee band -->
    <div class="bg-gold py-4 overflow-hidden">
      <div class="flex gap-12 animate-marquee whitespace-nowrap">
        <span v-for="i in 6" :key="i" class="text-[10px] tracking-widest uppercase text-aroma-dark flex gap-12">
          <span>Envío Premium</span>
          <span>·</span>
          <span>Embalaje de Lujo</span>
          <span>·</span>
          <span>Autenticidad Garantizada</span>
          <span>·</span>
          <span>Devolución Fácil</span>
          <span>·</span>
        </span>
      </div>
    </div>

    <!-- New Arrivals -->
    <section class="py-24 bg-aroma-surface">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-12">
          <p class="text-[10px] tracking-widest uppercase text-gold mb-3">Recién Llegado</p>
          <h2 class="font-display text-5xl text-aroma-text">{{ $t('home.new_arrivals') }}</h2>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-3 gap-6">
          <ProductCard v-for="p in newProducts" :key="p.id" :product="p" />
        </div>
      </div>
    </section>

    <!-- Value props -->
    <section class="py-20 border-t border-aroma-border">
      <div class="max-w-7xl mx-auto px-6">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-8">
          <div v-for="prop in valueProps" :key="prop.title" class="text-center">
            <div class="w-12 h-12 border border-gold/30 flex items-center justify-center mx-auto mb-4">
              <svg class="w-5 h-5 text-gold" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" :d="prop.icon"/>
              </svg>
            </div>
            <h3 class="text-xs tracking-widest uppercase text-aroma-text mb-2">{{ prop.title }}</h3>
            <p class="text-aroma-muted text-xs leading-relaxed">{{ prop.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <Footer />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import Header from '../components/layout/Header.vue'
import Footer from '../components/layout/Footer.vue'
import ProductCard from '../components/ui/ProductCard.vue'
import api from '../router/api'

const heroImages = [
  // Perfume en pedestal con columnas clásicas — elegante arquitectónico
  'https://images.unsplash.com/photo-1721068642990-09a06f8fe261?w=1800&q=85&auto=format&fit=crop',
  // Frasco negro y dorado — lujo oscuro
  'https://images.unsplash.com/photo-1592842312573-dca0b185d2e0?w=1800&q=85&auto=format&fit=crop',
  // Perfume con flor — femenino floral
  'https://images.unsplash.com/photo-1708486235073-14879ff14c4c?w=1800&q=85&auto=format&fit=crop',
  // Prada — diseñador de tendencia
  'https://images.unsplash.com/photo-1704900164098-33c4abb6a579?w=1800&q=85&auto=format&fit=crop',
  // Zara Vibrant Leather — perfume moderno
  'https://images.unsplash.com/photo-1759793500110-e3cb1f0fe6ae?w=1800&q=85&auto=format&fit=crop',
]

const currentSlide = ref(0)
let autoplayTimer = null

function nextSlide() {
  currentSlide.value = (currentSlide.value + 1) % heroImages.length
}

function prevSlide() {
  currentSlide.value = (currentSlide.value - 1 + heroImages.length) % heroImages.length
}

function goToSlide(index) {
  currentSlide.value = index
  resetAutoplay()
}

function resetAutoplay() {
  clearInterval(autoplayTimer)
  autoplayTimer = setInterval(nextSlide, 4000)
}

const featuredProducts = ref([])
const newProducts = ref([])
const categories = ref([])
const loadingFeatured = ref(true)

const valueProps = [
  { title: 'Envío Premium', desc: 'Entrega discreta con firma requerida', icon: 'M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4' },
  { title: 'Autenticidad', desc: 'Fragancias 100% originales y certificadas', icon: 'M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z' },
  { title: 'Devolución fácil', desc: '30 días sin preguntas para devoluciones', icon: 'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15' },
  { title: 'Consultoría', desc: 'Asesoramiento experto para encontrar tu aroma', icon: 'M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z' },
]

onMounted(async () => {
  autoplayTimer = setInterval(nextSlide, 4000)
  try {
    const [feat, newest, cats] = await Promise.all([
      api.get('/products', { params: { featured: true, status: 'active', per_page: 4 } }),
      api.get('/products', { params: { status: 'active', per_page: 6, sort: 'created_at_desc' } }),
      api.get('/categories'),
    ])
    featuredProducts.value = feat.data.items ?? []
    newProducts.value = newest.data.items ?? []
    categories.value = cats.data ?? []
  } catch {
    featuredProducts.value = []
    newProducts.value = []
    categories.value = []
  } finally {
    loadingFeatured.value = false
  }
})

onUnmounted(() => {
  clearInterval(autoplayTimer)
})
</script>

<style scoped>
@keyframes marquee {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}
.animate-marquee {
  animation: marquee 20s linear infinite;
}
</style>
