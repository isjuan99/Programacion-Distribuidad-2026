<template>
  <div class="group cursor-pointer" @click="$router.push(`/product/${product.id}`)">
    <!-- Image -->
    <div class="relative overflow-hidden bg-aroma-surface aspect-[3/4] mb-4">
      <!-- Badge -->
      <span v-if="badge"
        class="absolute top-3 left-3 z-10 px-2 py-1 text-[10px] tracking-widest uppercase font-sans font-bold rounded-full"
        :class="badgeClass">
        {{ badge }}
      </span>

      <!-- Wishlist heart -->
      <button
        @click.stop="handleWishlist"
        class="absolute top-3 right-3 z-10 w-8 h-8 rounded-full bg-white/80 backdrop-blur-sm flex items-center justify-center shadow-sm hover:scale-110 transition-transform"
        :title="wished ? 'Quitar de favoritos' : 'Agregar a favoritos'"
      >
        <svg class="w-4 h-4 transition-colors" viewBox="0 0 24 24"
          :class="wished ? 'fill-red-500 text-red-500' : 'fill-transparent text-gray-400 stroke-gray-400'"
          stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round"
            d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
        </svg>
      </button>

      <img v-if="product.images?.[0]"
        :src="product.images[0]"
        :alt="product.name"
        class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105" />
      <div v-else class="w-full h-full flex items-center justify-center">
        <span class="text-aroma-muted text-xs tracking-widest uppercase">Image Pending</span>
      </div>

      <!-- Hover overlay -->
      <div class="absolute inset-0 bg-aroma-dark/40 opacity-0 group-hover:opacity-100 transition-opacity duration-300
                  flex items-end justify-center pb-6">
        <button v-if="product.status !== 'out_of_stock'"
          @click.stop="handleAddToCart"
          class="btn-ghost text-[10px] px-6 py-2 bg-aroma-dark/80 backdrop-blur-sm">
          {{ $t('shop.add_to_cart') }}
        </button>
        <span v-else class="text-aroma-muted text-[10px] tracking-widest uppercase">
          {{ $t('shop.out_of_stock') }}
        </span>
      </div>
    </div>

    <!-- Info -->
    <div class="text-center">
      <p class="text-[10px] tracking-widest uppercase mb-1"
        :class="light ? 'text-gray-500' : 'text-aroma-muted'">
        {{ product.brand_name }}
      </p>
      <h3 class="font-display text-lg group-hover:text-gold transition-colors"
        :class="light ? 'text-[#1a1a1a]' : 'text-aroma-text'">
        {{ product.name }}
      </h3>
      <div class="mt-2 flex items-center justify-center gap-3">
        <span v-if="originalPrice"
          class="text-sm line-through"
          :class="light ? 'text-gray-400' : 'text-aroma-muted'">
          {{ formatCOP(originalPrice) }}
        </span>
        <span v-if="basePrice != null" class="text-gold font-medium">{{ formatCOP(basePrice) }}</span>
        <span v-else
          class="text-xs tracking-widest uppercase"
          :class="light ? 'text-gray-400' : 'text-aroma-muted'">
          Consultar
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useCartStore } from '../../stores/cart'
import { useWishlistStore } from '../../stores/wishlist'
import { formatCOP } from '../../utils/currency'

const props = defineProps({
  product: { type: Object, required: true },
  light: { type: Boolean, default: false },
})

const cart = useCartStore()
const wishlist = useWishlistStore()

const baseVariant = computed(() => props.product.variants?.[0] || null)
const basePrice = computed(() => baseVariant.value?.price ?? null)
const compareAtPrice = computed(() => baseVariant.value?.compare_at_price ?? null)
const originalPrice = computed(() =>
  compareAtPrice.value && compareAtPrice.value > (basePrice.value ?? 0)
    ? compareAtPrice.value
    : null
)
const discountPct = computed(() => {
  if (originalPrice.value && basePrice.value) {
    return Math.round((1 - basePrice.value / originalPrice.value) * 100)
  }
  return null
})

const badge = computed(() => {
  if (props.product.status === 'out_of_stock') return 'SOLD OUT'
  if (discountPct.value) return `-${discountPct.value}%`
  if (props.product.is_new) return 'NEW'
  return null
})

const badgeClass = computed(() => ({
  'bg-gold text-aroma-dark': badge.value === 'NEW',
  'bg-aroma-dark text-aroma-text border border-aroma-border': badge.value === 'SOLD OUT',
  'bg-[#e85d04] text-white': badge.value?.includes('%'),
}))

const wished = computed(() => wishlist.isWished(props.product.id))

function handleAddToCart() {
  if (baseVariant.value) {
    cart.addItem(props.product, baseVariant.value, 1)
  }
}

function handleWishlist() {
  wishlist.toggle(props.product)
}
</script>
