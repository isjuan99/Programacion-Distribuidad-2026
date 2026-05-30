<template>
  <div class="min-h-screen bg-aroma-dark">
    <Header />
    <div class="pt-24 pb-24">
      <!-- Page header -->
      <div class="text-center py-12 border-b border-aroma-border">
        <h1 class="font-display text-5xl text-aroma-text mb-3">{{ $t('shop.title') }}</h1>
        <p class="text-aroma-muted text-sm max-w-md mx-auto">{{ $t('shop.subtitle') }}</p>
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
                <span class="text-sm text-aroma-muted group-hover:text-aroma-text transition-colors">
                  {{ cat.name }} ({{ cat.product_count }})
                </span>
              </label>
            </div>
          </div>

          <hr class="border-aroma-border mb-8" />

          <!-- Price range -->
          <div class="mb-8">
            <h4 class="text-[10px] tracking-widest uppercase text-gold mb-4">{{ $t('shop.price_range') }}</h4>
            <input type="range" v-model="filters.maxPrice" min="50" max="500" step="10"
              class="w-full accent-gold" />
            <div class="flex justify-between text-xs text-aroma-muted mt-2">
              <span>$50</span><span>${{ filters.maxPrice }}+</span>
            </div>
          </div>

          <hr class="border-aroma-border mb-8" />

          <!-- Size -->
          <div>
            <h4 class="text-[10px] tracking-widest uppercase text-gold mb-4">{{ $t('shop.size') }}</h4>
            <div class="flex gap-2 flex-wrap">
              <button @click="selectSize(null)"
                class="px-3 py-1.5 text-xs border transition-colors"
                :class="filters.sizes.length === 0
                  ? 'border-gold bg-gold text-aroma-dark'
                  : 'border-aroma-border text-aroma-muted hover:border-aroma-muted'">
                Todos
              </button>
              <button v-for="size in [30, 50, 100, 150]" :key="size"
                @click="selectSize(size)"
                class="px-3 py-1.5 text-xs border transition-colors"
                :class="filters.sizes.includes(size)
                  ? 'border-gold bg-gold text-aroma-dark'
                  : 'border-aroma-border text-aroma-muted hover:border-aroma-muted'">
                {{ size }}ml
              </button>
            </div>
          </div>

          <!-- Olfactory Notes Filter -->
          <div class="border-t border-gray-800 pt-5 mt-5">
            <h3 class="text-xs tracking-widest text-gray-400 uppercase mb-3">{{ $t('shop.olfactory_notes') }}</h3>

            <!-- Selected notes as removable tags -->
            <div v-if="selectedNotes.length" class="flex flex-wrap gap-2 mb-3">
              <button
                v-for="note in selectedNotes"
                :key="note"
                @click="removeNote(note)"
                class="flex items-center gap-1 bg-[#c9a84c]/20 text-[#c9a84c] text-xs px-2 py-1 border border-[#c9a84c]/30 hover:bg-[#c9a84c]/30 transition-colors"
              >
                <span class="capitalize">{{ note }}</span>
                <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>

            <!-- Available notes checkboxes -->
            <div class="space-y-1 max-h-48 overflow-y-auto pr-1">
              <label
                v-for="note in availableNotes.slice(0, 15)"
                :key="note"
                class="flex items-center gap-2 text-sm text-gray-400 cursor-pointer hover:text-white transition-colors py-0.5"
              >
                <input
                  type="checkbox"
                  :checked="selectedNotes.includes(note)"
                  @change="toggleNote(note)"
                  class="accent-[#c9a84c]"
                />
                <span class="capitalize">{{ note }}</span>
              </label>
            </div>
          </div>
        </aside>

        <!-- Products area -->
        <div class="flex-1">
          <!-- Toolbar -->
          <div class="flex items-center justify-between mb-8">
            <p class="text-aroma-muted text-xs">
              Mostrando {{ products.length }} de {{ total }} resultados
            </p>
            <div class="flex items-center gap-3">
              <span class="text-[10px] tracking-widest uppercase text-aroma-muted">{{ $t('shop.sort_by') }}</span>
              <select v-model="filters.sort"
                class="bg-transparent border border-aroma-border text-aroma-text text-xs px-3 py-2
                       focus:outline-none focus:border-gold appearance-none pr-8">
                <option value="created_at_desc">{{ $t('shop.newest') }}</option>
                <option value="name_asc">{{ $t('shop.best_selling') }}</option>
              </select>
            </div>
          </div>

          <!-- Grid -->
          <div v-if="loading" class="grid grid-cols-2 lg:grid-cols-3 gap-8">
            <div v-for="i in 9" :key="i" class="bg-aroma-surface animate-pulse aspect-[3/4]" />
          </div>

          <div v-else-if="products.length === 0" class="text-center py-24 text-aroma-muted">
            <p v-if="filters.sizes.length > 0">
              No hay productos disponibles en tamaño {{ filters.sizes[0] }}ml.
            </p>
            <p v-else>No se encontraron fragancias con los filtros seleccionados.</p>
          </div>

          <div v-else class="grid grid-cols-2 lg:grid-cols-3 gap-8">
            <ProductCard v-for="p in products" :key="p.id" :product="p" />
          </div>

          <!-- Pagination -->
          <div v-if="pages > 1" class="flex justify-center gap-2 mt-16">
            <button @click="changePage(currentPage - 1)" :disabled="currentPage === 1"
              class="w-9 h-9 border border-aroma-border text-aroma-muted hover:border-gold hover:text-gold
                     disabled:opacity-30 disabled:cursor-not-allowed transition-colors flex items-center justify-center">
              ‹
            </button>
            <button v-for="p in pages" :key="p" @click="changePage(p)"
              class="w-9 h-9 border text-xs transition-colors"
              :class="p === currentPage
                ? 'border-gold bg-gold text-aroma-dark'
                : 'border-aroma-border text-aroma-muted hover:border-gold hover:text-gold'">
              {{ p }}
            </button>
            <button @click="changePage(currentPage + 1)" :disabled="currentPage === pages"
              class="w-9 h-9 border border-aroma-border text-aroma-muted hover:border-gold hover:text-gold
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

async function load() {
  const params = {
    page: filters.page,
    per_page: 9,
    sort: filters.sort,
    status: 'active',
  }
  if (filters.categories.length === 1) params.category_id = filters.categories[0]
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

onMounted(async () => {
  await store.fetchCategories()
  await loadOlfactoryNotes()
  await load()
})
</script>
