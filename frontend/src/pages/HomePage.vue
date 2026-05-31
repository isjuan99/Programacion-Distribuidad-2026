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
        <p class="text-[10px] tracking-widest uppercase text-gold mb-4">Collection 2026</p>
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

    <!-- ── CATEGORÍAS ─────────────────────────────────────────────── -->
    <!-- NEGRO: fluye directo del hero, misma atmósfera oscura -->
    <section class="bg-aroma-dark border-t border-white/5 py-14">
      <div class="max-w-7xl mx-auto px-6">
        <p class="text-[10px] tracking-widest uppercase text-gold mb-8 text-center">Explora por Categorias</p>
        <div class="flex gap-10 overflow-x-auto scrollbar-hide justify-center">
          <router-link v-for="cat in categories" :key="cat.id"
            :to="`/shop?category=${cat.id}`"
            class="shrink-0 text-center group flex flex-col items-center gap-3">
            <div class="w-16 h-16 rounded-full border border-white/10 group-hover:border-gold/70
                        flex items-center justify-center transition-all duration-300
                        group-hover:bg-gold/10">
              <svg class="w-6 h-6 text-gold/70 group-hover:text-gold transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1"
                  d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
              </svg>
            </div>
            <p class="text-[9px] tracking-widest uppercase text-white/40 group-hover:text-white/80 transition-colors">
              {{ cat.name }}
            </p>
          </router-link>
        </div>
      </div>
    </section>

    <!-- ── PRODUCTOS DESTACADOS ────────────────────────────────────── -->
    <section class="bg-white py-28">
      <div class="max-w-7xl mx-auto px-6">
        <div class="flex items-end justify-between mb-14">
          <div>
            <p class="text-[10px] tracking-widest uppercase text-gold mb-3">Selección Curada</p>
            <h2 class="font-display text-5xl md:text-6xl text-[#1a1a1a] leading-none">{{ $t('home.featured_title') }}</h2>
          </div>
          <router-link to="/shop"
            class="hidden md:flex items-center gap-2 text-[10px] tracking-widest uppercase text-gray-400
                   hover:text-gold transition-colors border-b border-transparent hover:border-gold pb-0.5">
            Ver todo →
          </router-link>
        </div>

        <div v-if="loadingFeatured" class="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div v-for="i in 4" :key="i" class="bg-gray-100 animate-pulse aspect-[3/4] rounded-sm" />
        </div>
        <div v-else-if="featuredProducts.length === 0" class="text-center py-20">
          <p class="text-[10px] tracking-widest uppercase text-gray-400">Próximamente</p>
        </div>
        <div v-else class="grid grid-cols-2 md:grid-cols-4 gap-6">
          <ProductCard v-for="p in featuredProducts" :key="p.id" :product="p" :light="true" />
        </div>
      </div>
    </section>

    <!-- ── BANDA MARQUEE ───────────────────────────────────────────── -->
    <!-- DORADO: separador visual que rompe el negro y marca el cambio -->
    <div class="bg-gold py-4 overflow-hidden">
      <div class="flex gap-16 animate-marquee whitespace-nowrap">
        <span v-for="i in 8" :key="i" class="text-[9px] tracking-[3px] uppercase text-aroma-dark font-semibold flex gap-16">
          <span>Envío Premium</span><span>·</span>
          <span>Embalaje de Lujo</span><span>·</span>
          <span>Autenticidad Garantizada</span><span>·</span>
          <span>Devolución Fácil</span><span>·</span>
        </span>
      </div>
    </div>

    <!-- ── NUEVAS LLEGADAS ─────────────────────────────────────────── -->
    <section class="bg-white py-28">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-14">
          <p class="text-[10px] tracking-widest uppercase text-gold mb-3">Recién Llegado</p>
          <h2 class="font-display text-5xl md:text-6xl text-[#1a1a1a] leading-none">{{ $t('home.new_arrivals') }}</h2>
          <p class="text-gray-500 text-sm mt-4">Las últimas incorporaciones a nuestra colección exclusiva</p>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-3 gap-6">
          <ProductCard v-for="p in newProducts" :key="p.id" :product="p" :light="true" />
        </div>
        <div class="text-center mt-12">
          <router-link to="/shop" class="btn-outline-gold">Explorar catálogo completo</router-link>
        </div>
      </div>
    </section>

    <!-- ── PROPUESTA DE VALOR ──────────────────────────────────────── -->
    <!-- NEGRO: íconos dorados sobre negro = máximo contraste y elegancia -->
    <section class="bg-aroma-dark border-t border-white/5 py-20">
      <div class="max-w-7xl mx-auto px-6">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-10">
          <div v-for="prop in valueProps" :key="prop.title" class="text-center group">
            <div class="w-14 h-14 border border-gold/20 group-hover:border-gold/60 flex items-center justify-center mx-auto mb-5
                        transition-all duration-300 group-hover:bg-gold/5">
              <svg class="w-6 h-6 text-gold/60 group-hover:text-gold transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" :d="prop.icon"/>
              </svg>
            </div>
            <h3 class="text-[10px] tracking-widest uppercase text-white mb-2">{{ prop.title }}</h3>
            <p class="text-white/35 text-xs leading-relaxed">{{ prop.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ── FAQ ────────────────────────────────────────────────────── -->
    <!-- CREMA/BLANCO: el único bloque claro — hace que la página respire
         y el texto informativo se lea perfectamente -->
    <section class="bg-[#f5f0e8] py-28">
      <div class="max-w-3xl mx-auto px-6">

        <!-- Título -->
        <div class="text-center mb-16">
          <p class="text-[10px] tracking-widest uppercase text-[#c9a84c] mb-3">Soporte</p>
          <h2 class="font-display text-5xl md:text-6xl text-[#1a1a1a] leading-none">Preguntas Frecuentes</h2>
          <p class="text-[#6b6560] text-sm mt-5 leading-relaxed">
            Todo lo que necesitas saber sobre nuestros productos y servicios.
          </p>
        </div>

        <!-- Acordeón -->
        <div class="divide-y divide-[#1a1a1a]/10">
          <div v-for="(item, i) in faqItems" :key="i">
            <button
              @click="openFaq === i ? openFaq = null : openFaq = i"
              class="w-full flex items-center justify-between py-6 text-left group"
            >
              <span class="text-sm md:text-base tracking-wide pr-8 transition-colors duration-200"
                :class="openFaq === i ? 'text-[#c9a84c]' : 'text-[#1a1a1a] group-hover:text-[#c9a84c]'">
                {{ item.q }}
              </span>
              <span class="shrink-0 w-7 h-7 flex items-center justify-center border transition-all duration-200"
                :class="openFaq === i
                  ? 'border-[#c9a84c] bg-[#c9a84c]/10'
                  : 'border-[#1a1a1a]/20 group-hover:border-[#c9a84c]'">
                <svg class="w-3 h-3 text-[#c9a84c] transition-transform duration-300"
                  :class="openFaq === i ? 'rotate-45' : ''"
                  fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4"/>
                </svg>
              </span>
            </button>

            <div class="overflow-hidden transition-all duration-500"
              :style="openFaq === i ? 'max-height:600px;opacity:1' : 'max-height:0;opacity:0'">
              <p class="text-[#6b6560] text-sm leading-relaxed pb-7 pr-12">
                {{ item.a }}
              </p>
            </div>
          </div>
        </div>

        <!-- CTA de contacto -->
        <div class="mt-16 text-center bg-[#1a1a1a] p-10">
          <p class="text-[10px] tracking-widest uppercase text-[#c9a84c] mb-3">¿Más dudas?</p>
          <p class="text-white/70 text-sm mb-6 leading-relaxed">
            Nuestro equipo está disponible para ayudarte con cualquier consulta.
          </p>
          <a href="mailto:aromadistribuido@gmail.com"
            class="inline-block bg-[#c9a84c] text-[#0a0a0a] px-10 py-3 text-[10px] tracking-widest uppercase
                   font-semibold hover:bg-[#b8943e] transition-colors">
            Contáctanos
          </a>
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

// FAQ accordion state
const openFaq = ref(null)

const faqItems = [
  {
    q: 'Devoluciones y reembolsos',
    a: 'La satisfacción de nuestros clientes es nuestra prioridad número uno. Si hay algún problema con tu pedido, comunícate con nosotros por correo electrónico a aromadistribuido@gmail.com y lo resolveremos a la brevedad posible.',
  },
  {
    q: 'Seguridad de pago',
    a: 'Todas las pasarelas de pago directo cumplen con los estándares establecidos por PCI-DSS, administrados por el PCI Security Standards Council. Este es un esfuerzo conjunto de marcas líderes como Visa, MasterCard, American Express y Discover, garantizando que tu información financiera esté siempre protegida.',
  },
  {
    q: 'Tiempos de entrega',
    a: 'La entrega estándar suele tardar entre 7 y 10 días laborables. No ofrecemos garantías sobre tiempos de envío superiores al promedio y no aceptaremos reclamos por demoras fuera de nuestro control. El tiempo de envío se refiere al período comprendido entre la realización del pedido y la entrega al transportista. Si tu pedido no ha llegado después de dos semanas, contáctanos a aromadistribuido@gmail.com y analizaremos los detalles de tu caso.',
  },
  {
    q: 'Notificaciones de nuevo en stock',
    a: 'Los productos se reabastecen periódicamente según la disponibilidad de nuestros proveedores. Si un producto que deseas está agotado, te recomendamos agregarlo a tu lista de deseos o contactarnos a aromadistribuido@gmail.com para recibir una notificación personalizada cuando vuelva a estar disponible.',
  },
]

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
