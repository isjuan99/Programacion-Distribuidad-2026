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
import { formatCOP } from '../../utils/currency'

const props = defineProps({
  product: { type: Object, required: true },
  light: { type: Boolean, default: false },
})

const cart = useCartStore()

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

function handleAddToCart() {
  if (baseVariant.value) {
    cart.addItem(props.product, baseVariant.value, 1)
  }
}
</script>
