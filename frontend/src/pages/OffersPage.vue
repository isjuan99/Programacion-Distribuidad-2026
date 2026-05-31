<template>
  <div class="min-h-screen bg-white">
    <Header />

    <!-- Banner -->
    <div class="bg-white pt-24 border-b border-gray-100">
      <div class="text-center py-14">
        <p class="text-[10px] tracking-[4px] uppercase text-[#c9a84c] mb-3">Descuentos Exclusivos</p>
        <h1 class="font-display text-6xl md:text-7xl text-[#1a1a1a]">Ofertas</h1>
        <p class="text-gray-500 text-sm mt-4 max-w-md mx-auto">
          Fragancias seleccionadas con precios especiales por tiempo limitado
        </p>
        <!-- Breadcrumb -->
        <div class="flex items-center justify-center gap-2 mt-6 text-[10px] tracking-widest uppercase text-gray-400">
          <router-link to="/" class="hover:text-[#c9a84c] transition-colors">Inicio</router-link>
          <span>/</span>
          <span class="text-[#c9a84c]">Ofertas</span>
        </div>
      </div>

      <!-- Marquee strip -->
      <div class="bg-gold py-3 overflow-hidden">
        <div class="flex gap-16 animate-marquee whitespace-nowrap">
          <span v-for="i in 10" :key="i" class="text-[9px] tracking-[3px] uppercase text-aroma-dark font-semibold flex gap-16">
            <span>Oferta por tiempo limitado</span><span>·</span>
            <span>Stock limitado</span><span>·</span>
            <span>Precios exclusivos</span><span>·</span>
          </span>
        </div>
      </div>
    </div>

    <!-- Products section -->
    <div class="max-w-7xl mx-auto px-6 py-14">

      <!-- Toolbar -->
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-10 pb-6 border-b border-gray-200">
        <div>
          <p class="text-[#1a1a1a] font-display text-2xl">{{ total }} perfumes en oferta</p>
          <p class="text-gray-500 text-xs mt-1">Precios válidos hasta agotar existencias</p>
        </div>
        <div class="flex items-center gap-3">
          <span class="text-[10px] tracking-widest uppercase text-gray-500">Ordenar por</span>
          <select v-model="sort"
            class="bg-white border border-gray-300 text-[#1a1a1a] text-xs px-3 py-2
                   focus:outline-none focus:border-gold appearance-none">
            <option value="discount_desc">Mayor descuento</option>
            <option value="price_asc">Menor precio</option>
            <option value="price_desc">Mayor precio</option>
            <option value="created_at_desc">Más recientes</option>
          </select>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
        <div v-for="i in 10" :key="i" class="bg-gray-100 animate-pulse aspect-[3/4] rounded-sm" />
      </div>

      <!-- Empty -->
      <div v-else-if="products.length === 0" class="text-center py-32">
        <div class="w-20 h-20 bg-gold/10 border border-gold/20 flex items-center justify-center mx-auto mb-6">
          <svg class="w-8 h-8 text-gold/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
              d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"/>
          </svg>
        </div>
        <p class="text-[10px] tracking-widest uppercase text-gray-400 mb-2">Sin ofertas activas</p>
        <p class="text-gray-500 text-sm mb-8">Vuelve pronto — actualizamos las ofertas constantemente</p>
        <router-link to="/shop" class="btn-gold">Ver catálogo completo</router-link>
      </div>

      <!-- Grid -->
      <div v-else class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
        <OfferCard
          v-for="p in sortedProducts"
          :key="p.id"
          :product="p"
        />
      </div>

      <!-- Pagination -->
      <div v-if="pages > 1" class="flex justify-center gap-2 mt-16">
        <button @click="changePage(page - 1)" :disabled="page === 1"
          class="w-9 h-9 border border-gray-300 text-gray-500 hover:border-gold hover:text-gold
                 disabled:opacity-30 disabled:cursor-not-allowed transition-colors flex items-center justify-center">
          ‹
        </button>
        <button v-for="p in pages" :key="p" @click="changePage(p)"
          class="w-9 h-9 border text-xs transition-colors"
          :class="p === page
            ? 'border-gold bg-gold text-aroma-dark'
            : 'border-gray-300 text-gray-500 hover:border-gold hover:text-gold'">
          {{ p }}
        </button>
        <button @click="changePage(page + 1)" :disabled="page === pages"
          class="w-9 h-9 border border-gray-300 text-gray-500 hover:border-gold hover:text-gold
                 disabled:opacity-30 disabled:cursor-not-allowed transition-colors flex items-center justify-center">
          ›
        </button>
      </div>
    </div>

    <Footer />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, defineComponent, h } from 'vue'
import { useRouter } from 'vue-router'
import Header from '../components/layout/Header.vue'
import Footer from '../components/layout/Footer.vue'
import { useCartStore } from '../stores/cart'
import { formatCOP } from '../utils/currency'
import api from '../router/api'

const router = useRouter()
const cart = useCartStore()

const products = ref([])
const total = ref(0)
const pages = ref(1)
const page = ref(1)
const loading = ref(true)
const sort = ref('discount_desc')

const sortedProducts = computed(() => {
  const list = [...products.value]
  if (sort.value === 'discount_desc') {
    return list.sort((a, b) => discountOf(b) - discountOf(a))
  }
  if (sort.value === 'price_asc') {
    return list.sort((a, b) => priceOf(a) - priceOf(b))
  }
  if (sort.value === 'price_desc') {
    return list.sort((a, b) => priceOf(b) - priceOf(a))
  }
  return list
})

function priceOf(p) {
  return p.variants?.[0]?.price ?? 0
}

function discountOf(p) {
  const v = p.variants?.[0]
  if (!v?.compare_at_price || v.compare_at_price <= v.price) return 0
  return Math.round((1 - v.price / v.compare_at_price) * 100)
}

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/products', {
      params: {
        on_sale: true,
        status: 'active',
        per_page: 40,
        page: page.value,
      }
    })
    products.value = data.items ?? []
    total.value = data.total ?? 0
    pages.value = data.pages ?? 1
  } catch {
    products.value = []
  } finally {
    loading.value = false
  }
}

function changePage(p) {
  page.value = p
  load()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(load)

// ── Inline OfferCard component ────────────────────────────────────────────
const OfferCard = defineComponent({
  name: 'OfferCard',
  props: { product: { type: Object, required: true } },
  setup(props) {
    const variant = computed(() => props.product.variants?.[0] || null)
    const price = computed(() => variant.value?.price ?? null)
    const compareAt = computed(() =>
      variant.value?.compare_at_price && variant.value.compare_at_price > (price.value ?? 0)
        ? variant.value.compare_at_price
        : null
    )
    const pct = computed(() =>
      compareAt.value && price.value
        ? Math.round((1 - price.value / compareAt.value) * 100)
        : null
    )
    function addToCart(e) {
      e.stopPropagation()
      if (variant.value) cart.addItem(props.product, variant.value, 1)
    }
    return () => h('div', {
      class: 'group cursor-pointer bg-white border border-gray-100 hover:border-gray-300 hover:shadow-md transition-all duration-300',
      onClick: () => router.push(`/product/${props.product.id}`),
    }, [
      // Image container
      h('div', { class: 'relative overflow-hidden bg-gray-50 aspect-[3/4]' }, [
        // Discount badge
        pct.value ? h('span', {
          class: 'absolute top-3 left-3 z-10 bg-[#e85d04] text-white text-[10px] font-bold px-2.5 py-1 rounded-full'
        }, `-${pct.value}%`) : null,
        // Product image
        props.product.images?.[0]
          ? h('img', {
              src: props.product.images[0],
              alt: props.product.name,
              class: 'w-full h-full object-cover transition-transform duration-700 group-hover:scale-105'
            })
          : h('div', { class: 'w-full h-full flex items-center justify-center' },
              h('svg', {
                class: 'w-12 h-12 text-gray-200',
                fill: 'none',
                stroke: 'currentColor',
                viewBox: '0 0 24 24'
              }, h('path', {
                'stroke-linecap': 'round',
                'stroke-linejoin': 'round',
                'stroke-width': '1',
                d: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4'
              }))
            ),
        // Add to cart overlay
        props.product.status !== 'out_of_stock'
          ? h('div', {
              class: 'absolute inset-0 bg-aroma-dark/30 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end justify-center pb-5'
            }, h('button', {
              class: 'bg-aroma-dark text-aroma-text border border-white/20 text-[10px] tracking-widest uppercase px-5 py-2 hover:bg-gold hover:text-aroma-dark hover:border-gold transition-colors',
              onClick: addToCart
            }, 'Agregar al carrito'))
          : null,
      ]),
      // Info
      h('div', { class: 'p-4' }, [
        h('p', { class: 'text-[9px] tracking-widest uppercase text-gray-400 mb-1' }, props.product.brand_name),
        h('h3', { class: 'text-sm text-[#1a1a1a] font-medium leading-tight group-hover:text-gold transition-colors line-clamp-2 mb-3' }, props.product.name),
        // Prices
        h('div', { class: 'flex items-center gap-2 flex-wrap' }, [
          compareAt.value
            ? h('span', { class: 'text-xs text-gray-400 line-through' }, formatCOP(compareAt.value))
            : null,
          price.value != null
            ? h('span', { class: 'text-base font-bold text-[#1a1a1a]' }, formatCOP(price.value))
            : h('span', { class: 'text-xs text-gray-400' }, 'Consultar'),
        ]),
        // Stock indicator
        variant.value?.stock > 0
          ? h('p', { class: 'text-[9px] text-gray-400 mt-2 flex items-center gap-1' }, [
              h('span', { class: 'w-1.5 h-1.5 rounded-full bg-[#e85d04] inline-block' }),
              `${variant.value.stock} disponibles`
            ])
          : h('p', { class: 'text-[9px] text-gray-400 mt-2' }, 'Sin stock'),
      ]),
    ])
  }
})
</script>

<style scoped>
@keyframes marquee {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}
.animate-marquee {
  animation: marquee 18s linear infinite;
}
</style>
