<template>
  <div class="min-h-screen bg-aroma-dark">
    <Header />
    <div class="pt-20 max-w-7xl mx-auto px-6 py-16">
      <div v-if="loading" class="grid grid-cols-2 gap-16">
        <div class="aspect-square bg-aroma-surface animate-pulse" />
        <div class="space-y-4">
          <div class="h-6 bg-aroma-surface animate-pulse w-1/2" />
          <div class="h-10 bg-aroma-surface animate-pulse" />
        </div>
      </div>

      <div v-else-if="product" class="grid grid-cols-1 md:grid-cols-2 gap-16">
        <!-- Images -->
        <div>
          <div class="aspect-square bg-aroma-surface overflow-hidden mb-4">
            <img v-if="product.images?.[selectedImage]"
              :src="product.images[selectedImage]"
              :alt="product.name"
              class="w-full h-full object-cover" />
            <div v-else class="w-full h-full flex items-center justify-center">
              <span class="text-aroma-muted text-xs tracking-widest uppercase">Imagen pendiente</span>
            </div>
          </div>
          <div v-if="product.images?.length > 1" class="flex gap-3">
            <div v-for="(img, i) in product.images" :key="i"
              @click="selectedImage = i"
              class="w-20 h-20 bg-aroma-surface cursor-pointer border-2 transition-colors overflow-hidden"
              :class="i === selectedImage ? 'border-gold' : 'border-transparent hover:border-aroma-border'">
              <img :src="img" :alt="`${product.name} ${i+1}`" class="w-full h-full object-cover" />
            </div>
          </div>
        </div>

        <!-- Info -->
        <div>
          <div class="mb-2">
            <router-link :to="`/shop?brand=${product.brand_id}`"
              class="text-[10px] tracking-widest uppercase text-gold hover:underline">
              {{ product.brand_name }}
            </router-link>
          </div>
          <h1 class="font-display text-5xl text-aroma-text mb-2">{{ product.name }}</h1>

          <!-- Rating -->
          <div v-if="product.review_count > 0" class="flex items-center gap-2 mb-6">
            <div class="flex gap-0.5">
              <svg v-for="i in 5" :key="i" class="w-4 h-4"
                :class="i <= Math.round(product.average_rating) ? 'fill-gold text-gold' : 'fill-transparent text-aroma-border'"
                viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
              </svg>
            </div>
            <span class="text-aroma-muted text-xs">{{ product.average_rating }} ({{ product.review_count }} reseñas)</span>
          </div>

          <!-- Price -->
          <p class="font-display text-4xl text-aroma-text mb-8">
            ${{ selectedVariant?.price?.toFixed(2) || '—' }}
          </p>

          <!-- Olfactory notes -->
          <div v-if="product.olfactory_notes?.length" class="mb-8">
            <p class="text-[10px] tracking-widest uppercase text-aroma-muted mb-3">{{ $t('product.olfactory_notes') }}</p>
            <div class="flex gap-2 flex-wrap">
              <span v-for="note in product.olfactory_notes" :key="note"
                class="border border-aroma-border text-aroma-muted text-[10px] tracking-widest uppercase px-3 py-1">
                {{ note }}
              </span>
            </div>
          </div>

          <!-- Size selector -->
          <div class="mb-6">
            <p class="text-[10px] tracking-widest uppercase text-aroma-muted mb-3">{{ $t('product.size') }}</p>
            <div class="flex gap-3">
              <button v-for="v in product.variants" :key="v.id"
                @click="selectedVariantId = v.id"
                class="px-4 py-2 text-sm border transition-colors"
                :class="v.id === selectedVariantId
                  ? 'border-gold bg-gold text-aroma-dark'
                  : v.stock === 0
                    ? 'border-aroma-border text-aroma-muted opacity-40 cursor-not-allowed'
                    : 'border-aroma-border text-aroma-muted hover:border-gold hover:text-gold'"
                :disabled="v.stock === 0">
                {{ v.size_ml }}ml
              </button>
            </div>
          </div>

          <!-- Quantity -->
          <div class="flex items-center gap-4 mb-8">
            <p class="text-[10px] tracking-widest uppercase text-aroma-muted">{{ $t('product.quantity') }}</p>
            <div class="flex items-center border border-aroma-border">
              <button @click="qty = Math.max(1, qty - 1)"
                class="w-10 h-10 flex items-center justify-center text-aroma-muted hover:text-aroma-text transition-colors">
                −
              </button>
              <span class="w-10 text-center text-aroma-text text-sm">{{ qty }}</span>
              <button @click="qty++"
                class="w-10 h-10 flex items-center justify-center text-aroma-muted hover:text-aroma-text transition-colors">
                +
              </button>
            </div>
          </div>

          <!-- Add to cart -->
          <button @click="handleAddToCart"
            :disabled="!selectedVariant || selectedVariant.stock === 0"
            class="btn-gold w-full py-4 disabled:opacity-40">
            {{ selectedVariant?.stock === 0 ? $t('shop.out_of_stock') : $t('product.add_to_cart') }}
          </button>

          <!-- Description -->
          <div v-if="product.description" class="mt-10 pt-8 border-t border-aroma-border">
            <p class="text-[10px] tracking-widest uppercase text-aroma-muted mb-4">{{ $t('product.description') }}</p>
            <p class="text-aroma-muted leading-relaxed text-sm">{{ product.description }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Related Products -->
    <div class="max-w-7xl mx-auto px-6 pb-16">
      <section v-if="relatedProducts.length > 0" class="mt-16 border-t border-gray-800 pt-12">
        <h2 class="text-xl tracking-widest text-white uppercase mb-8">{{ $t('product.related_products') }}</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div
            v-for="p in relatedProducts.slice(0, 4)"
            :key="p.id"
            class="group"
          >
            <RouterLink :to="`/product/${p.id}`">
              <div class="aspect-square overflow-hidden bg-gray-900 mb-3">
                <img
                  v-if="p.images && p.images[0]"
                  :src="p.images[0]"
                  :alt="p.name"
                  class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <div v-else class="w-full h-full flex items-center justify-center text-gray-700">
                  <svg class="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                  </svg>
                </div>
              </div>
              <p class="text-xs text-gray-500 mb-1">{{ p.brand_name }}</p>
              <p class="text-sm text-white group-hover:text-[#c9a84c] transition-colors">{{ p.name }}</p>
              <p v-if="p.variants && p.variants[0]" class="text-[#c9a84c] text-sm mt-1">${{ p.variants[0].price }}</p>
            </RouterLink>
          </div>
        </div>
      </section>

      <!-- Fragrance Profile Recommendations -->
      <section v-if="fragranceProfile.length > 0" class="mt-12 border-t border-gray-800 pt-12">
        <h2 class="text-xl tracking-widest text-white uppercase mb-2">{{ $t('product.if_you_like') }}</h2>
        <p class="text-sm text-gray-500 mb-8">{{ $t('product.fragrance_match_subtitle', { name: product?.name }) }}</p>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div
            v-for="p in fragranceProfile"
            :key="p.id"
            class="group relative"
          >
            <RouterLink :to="`/product/${p.id}`">
              <div class="absolute top-2 left-2 z-10 bg-[#c9a84c] text-black text-xs px-2 py-0.5 font-bold">
                {{ p.match_pct }}% match
              </div>
              <div class="aspect-square overflow-hidden bg-gray-900 mb-3">
                <img
                  v-if="p.primary_image"
                  :src="p.primary_image"
                  :alt="p.name"
                  class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <div v-else class="w-full h-full bg-gray-800"></div>
              </div>
              <p class="text-xs text-gray-500 mb-1">{{ p.brand }}</p>
              <p class="text-sm text-white group-hover:text-[#c9a84c] transition-colors">{{ p.name }}</p>
              <p v-if="p.price" class="text-[#c9a84c] text-sm mt-1">${{ p.price }}</p>
              <p v-if="p.common_notes?.length" class="text-xs text-gray-600 mt-1 capitalize">
                {{ p.common_notes.slice(0, 2).join(' · ') }}
              </p>
            </RouterLink>
          </div>
        </div>
      </section>
    </div>

    <Footer />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import Header from '../components/layout/Header.vue'
import Footer from '../components/layout/Footer.vue'
import { useCartStore } from '../stores/cart'
import api from '../router/api'

const route = useRoute()
const cart = useCartStore()

const product = ref(null)
const loading = ref(true)
const selectedImage = ref(0)
const selectedVariantId = ref(null)
const qty = ref(1)
const relatedProducts = ref([])
const fragranceProfile = ref([])

const selectedVariant = computed(() =>
  product.value?.variants?.find(v => v.id === selectedVariantId.value)
)

function handleAddToCart() {
  if (product.value && selectedVariant.value) {
    cart.addItem(product.value, selectedVariant.value, qty.value)
  }
}

async function loadRelated(productId) {
  try {
    const { data } = await api.get(`/products/${productId}/related`)
    relatedProducts.value = data.items || []
  } catch {
    relatedProducts.value = []
  }
}

async function loadFragranceProfile(productId) {
  try {
    const { data } = await api.get(`/products/${productId}/fragrance-profile`)
    fragranceProfile.value = data || []
  } catch {
    fragranceProfile.value = []
  }
}

onMounted(async () => {
  try {
    const id = route.params.id
    const { data } = await api.get(`/products/${id}`)
    product.value = data
    if (data.variants?.length) {
      selectedVariantId.value = data.variants[0].id
    }
    await Promise.all([loadRelated(id), loadFragranceProfile(id)])
  } finally {
    loading.value = false
  }
})
</script>
