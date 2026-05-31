<template>
  <div class="min-h-screen bg-white">
    <Header />
    <div class="pt-24 pb-24">
      <!-- Page header -->
      <div class="text-center py-12 border-b border-gray-200">
        <p v-if="pageLabel" class="text-[10px] tracking-[4px] uppercase text-gold mb-3">Perfumes para</p>
        <h1 class="font-display text-5xl text-[#1a1a1a] mb-3">
          {{ pageLabel || $t('shop.title') }}
        </h1>
        <p class="text-gray-500 text-sm max-w-md mx-auto">{{ $t('shop.subtitle') }}</p>
        <div v-if="pageLabel" class="flex items-center justify-center gap-2 mt-4 text-[10px] tracking-widest uppercase text-gray-400">
          <router-link to="/shop" class="hover:text-gold transition-colors">Todos</router-link>
          <span>/</span>
          <span class="text-gold">{{ pageLabel }}</span>
        </div>
      </div>

      <div class="max-w-7xl mx-auto px-6 mt-10 flex gap-10">
        <!-- Sidebar filters -->
        <aside class="w-56 shrink-0 hidden md:block">
          <!-- Category -->
          <div class="mb-8">
            <h4 class="text-[10px] tracking-widest uppercase text-gold mb-4">{{ $t('shop.category') }}</h4>
            <div class="space-y-2">
              <label v-for="cat in categories" :key="cat.id"
                class="flex items-center gap-3 cursor-pointer group">
                <input type="checkbox" :value="cat.id" v-model="filters.categories"
                  class="accent-gold" />
                <span class="text-sm text-gray-500 group-hover:text-[#1a1a1a] transition-colors">
                  {{ cat.name }} ({{ cat.product_count }})
                </span>
              </label>
            </div>
          </div>

          <hr class="border-gray-200 mb-8" />

          <!-- Price range -->
          <div class="mb-8">
            <h4 class="text-[10px] tracking-widest uppercase text-gold mb-4">{{ $t('shop.price_range') }}</h4>
            <input type="range" v-model="filters.maxPrice" min="50" max="500" step="10"
              class="w-full accent-gold" />
            <div class="flex justify-between text-xs text-gray-500 mt-2">
              <span>{{ formatCOP(50) }}</span><span>{{ formatCOP(filters.maxPrice) }}+</span>
            </div>
          </div>

          <hr class="border-gray-200 mb-8" />

          <!-- Size -->
          <div>
            <h4 class="text-[10px] tracking-widest uppercase text-gold mb-4">{{ $t('shop.size') }}</h4>
            <div class="flex gap-2 flex-wrap">
              <button @click="selectSize(null)"
                class="px-3 py-1.5 text-xs border transition-colors"
                :class="filters.sizes.length === 0
                  ? 'border-gold bg-gold text-aroma-dark'
                  : 'border-gray-300 text-gray-500 hover:border-gray-500'">
                Todos
              </button>
              <button v-for="size in [30, 50, 100, 150]" :key="size"
                @click="selectSize(size)"
                class="px-3 py-1.5 text-xs border transition-colors"
                :class="filters.sizes.includes(size)
                  ? 'border-gold bg-gold text-aroma-dark'
                  : 'border-gray-300 text-gray-500 hover:border-gray-500'">
                {{ size }}ml
              </button>
            </div>
          </div>

          <!-- Notas Olfativas -->
          <div class="border-t border-gray-200 pt-5 mt-5">
            <h3 class="text-xs tracking-widest text-gray-500 uppercase mb-3">{{ $t('shop.olfactory_notes') }}</h3>

            <!-- Tags seleccionados -->
            <div v-if="selectedNotes.length" class="flex flex-wrap gap-1.5 mb-3">
              <button
                v-for="note in selectedNotes"
                :key="note"
                @click="removeNote(note)"
                class="flex items-center gap-1 bg-gold/20 text-gold text-[10px] px-2.5 py-1 border border-gold/30 hover:bg-gold/30 transition-colors"
              >
                <span class="capitalize tracking-wide">{{ note }}</span>
                <svg class="w-2.5 h-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>

            <!-- Todas las notas visibles verticalmente (sin scroll) -->
            <div class="space-y-0.5">
              <label
                v-for="note in availableNotes"
                :key="note"
                class="flex items-center gap-2 text-xs text-gray-500 cursor-pointer hover:text-[#1a1a1a] transition-colors py-1 group"
              >
                <input
                  type="checkbox"
                  :checked="selectedNotes.includes(note)"
                  @change="toggleNote(note)"
                  class="accent-gold shrink-0"
                />
                <span class="capitalize group-hover:font-medium transition-all">{{ note }}</span>
              </label>
            </div>
          </div>
        </aside>

        <!-- Products area -->
        <div class="flex-1">
          <!-- Toolbar -->
          <div class="flex items-center justify-between mb-8">
            <p class="text-gray-500 text-xs">
              Mostrando {{ products.length }} de {{ total }} resultados
            </p>
            <div class="flex items-center gap-3">
              <span class="text-[10px] tracking-widest uppercase text-gray-500">{{ $t('shop.sort_by') }}</span>
              <select v-model="filters.sort"
                class="bg-white border border-gray-300 text-[#1a1a1a] text-xs px-3 py-2
                       focus:outline-none focus:border-gold appearance-none pr-8">
                <option value="created_at_desc">{{ $t('shop.newest') }}</option>
                <option value="name_asc">{{ $t('shop.best_selling') }}</option>
              </select>
            </div>
          </div>

          <!-- Grid -->
          <div v-if="loading" class="grid grid-cols-2 lg:grid-cols-3 gap-8">
            <div v-for="i in 9" :key="i" class="bg-gray-100 animate-pulse aspect-[3/4]" />
          </div>

          <div v-else-if="products.length === 0" class="text-center py-24 text-gray-500">
            <p v-if="filters.sizes.length > 0">
              No hay productos disponibles en tamaño {{ filters.sizes[0] }}ml.
            </p>
            <p v-else>No se encontraron fragancias con los filtros seleccionados.</p>
          </div>

          <div v-else class="grid grid-cols-2 lg:grid-cols-3 gap-8">
            <ProductCard v-for="p in products" :key="p.id" :product="p" :light="true" />
          </div>

          <!-- Pagination -->
          <div v-if="pages > 1" class="flex justify-center gap-2 mt-16">
            <button @click="changePage(currentPage - 1)" :disabled="currentPage === 1"
              class="w-9 h-9 border border-gray-300 text-gray-500 hover:border-gold hover:text-gold
                     disabled:opacity-30 disabled:cursor-not-allowed transition-colors flex items-center justify-center">
              ‹
            </button>
            <button v-for="p in pages" :key="p" @click="changePage(p)"
              class="w-9 h-9 border text-xs transition-colors"
              :class="p === currentPage
                ? 'border-gold bg-gold text-aroma-dark'
                : 'border-gray-300 text-gray-500 hover:border-gold hover:text-gold'">
              {{ p }}
            </button>
            <button @click="changePage(currentPage + 1)" :disabled="currentPage === pages"
              class="w-9 h-9 border border-gray-300 text-gray-500 hover:border-gold hover:text-gold
                     disabled:opacity-30 disabled:cursor-not-allowed transition-colors flex items-center justify-center">
              ›
            </button>
          </div>
        </div>
      </div>
    </div>
    <Footer />
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import Header from '../components/layout/Header.vue'
import Footer from '../components/layout/Footer.vue'
import ProductCard from '../components/ui/ProductCard.vue'
import { useProductsStore } from '../stores/products'
import { formatCOP } from '../utils/currency'
import api from '../router/api'

const route = useRoute()
const store = useProductsStore()

const products = computed(() => store.products)
const total = computed(() => store.total)
const pages = computed(() => store.pages)
const currentPage = computed(() => store.page)
const loading = computed(() => store.loading)
const categories = computed(() => store.categories)

const filters = reactive({
  categories: [],
  maxPrice: 500,
  sizes: [],
  sort: 'created_at_desc',
  page: 1,
})

const availableNotes = ref([])
const selectedNotes = ref([])

async function loadOlfactoryNotes() {
  try {
    const { data } = await api.get('/filters/olfactory-notes')
    availableNotes.value = data
  } catch { /* ignore */ }
}

function toggleNote(note) {
  const idx = selectedNotes.value.indexOf(note)
  if (idx >= 0) {
    selectedNotes.value.splice(idx, 1)
  } else {
    selectedNotes.value.push(note)
  }
  load()
}

function removeNote(note) {
  selectedNotes.value = selectedNotes.value.filter(n => n !== note)
  load()
}

const VALID_GENDERS = ['hombre', 'mujer', 'unisex']

// Título dinámico: muestra nombre de categoría o género activo
const pageLabel = computed(() => {
  const catId = route.query.category_id ? Number(route.query.category_id) : null
  if (catId) {
    const cat = store.categories.find(c => c.id === catId)
    return cat?.name ?? null
  }
  const g = route.query.gender?.toLowerCase()
  return g ? ({ hombre: 'Hombre', mujer: 'Mujer', unisex: 'Unisex' }[g] ?? null) : null
})

function applyUrlFilters() {
  const catId = route.query.category_id
  if (catId) {
    filters.categories = [Number(catId)]
  }
}

async function load() {
  const params = {
    page: filters.page,
    per_page: 9,
    sort: filters.sort,
    status: 'active',
  }

  if (filters.categories.length === 1) {
    params.category_id = filters.categories[0]
  }
  // Filtro de género — usa el campo gender del producto, independiente de la categoría
  const g = route.query.gender?.toLowerCase()
  if (g && VALID_GENDERS.includes(g)) {
    params.gender = g
  }

  if (filters.maxPrice < 500) params.max_price = filters.maxPrice
  if (filters.sizes.length > 0) params.size_ml = filters.sizes[0]
  if (route.query.q) params.search = route.query.q
  if (selectedNotes.value.length) params.top_notes = selectedNotes.value.join(',')
  await store.fetchProducts(params)
}

function selectSize(size) {
  filters.sizes = filters.sizes[0] === size ? [] : [size]
  filters.page = 1
}

function changePage(p) {
  filters.page = p
}

watch(filters, () => load(), { deep: true })
watch(() => route.query.q, () => load())

// Cambio de category_id en URL (desde el dropdown del Header)
watch(() => route.query.category_id, (newId) => {
  filters.categories = newId ? [Number(newId)] : []
  filters.page = 1
})

// Cambio de gender en URL (fallback cuando no hay category_id)
watch(() => route.query.gender, () => {
  filters.categories = []
  filters.page = 1
  load()
})

onMounted(async () => {
  await store.fetchCategories()
  await loadOlfactoryNotes()
  applyUrlFilters()   // pre-selecciona category_id si viene en la URL
  await load()
})
</script>
