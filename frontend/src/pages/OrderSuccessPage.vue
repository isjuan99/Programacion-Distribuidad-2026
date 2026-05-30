<template>
  <div class="min-h-screen bg-[#0a0a0a] py-20 px-4">
    <div class="max-w-2xl mx-auto">

      <div v-if="loading" class="text-center py-20">
        <div class="w-12 h-12 mx-auto border-2 border-[#c9a84c] border-t-transparent rounded-full animate-spin"></div>
      </div>

      <template v-else-if="order">
        <!-- Logo -->
        <div class="text-center mb-10">
          <h1 class="text-2xl tracking-[8px] text-[#c9a84c]">AROMA</h1>
          <p class="text-xs tracking-[4px] text-gray-500 mt-1">DISTRIBUIDO</p>
        </div>

        <!-- Success animation -->
        <div class="text-center mb-12">
          <div class="w-24 h-24 mx-auto bg-[#c9a84c]/10 rounded-full flex items-center justify-center mb-6 success-bounce">
            <svg class="w-12 h-12 text-[#c9a84c]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 13l4 4L19 7"/>
            </svg>
          </div>
          <h2 class="text-3xl font-light text-white tracking-widest mb-3">{{ $t('order_success.title') }}</h2>
          <p class="text-gray-400">{{ $t('order_success.subtitle') }}</p>
        </div>

        <!-- Order number -->
        <div class="border border-[#c9a84c]/30 bg-[#c9a84c]/5 p-6 text-center mb-8">
          <p class="text-xs tracking-[4px] text-gray-400 mb-2 uppercase">{{ $t('order_success.order_number') }}</p>
          <p class="text-2xl tracking-widest text-[#c9a84c] font-light">#{{ order.order_number }}</p>
          <p class="text-sm text-gray-500 mt-2">{{ $t('order_success.email_sent', { email: order.shipping_email }) }}</p>
        </div>

        <!-- Order items -->
        <div class="border border-gray-800 mb-6">
          <div class="border-b border-gray-800 px-6 py-4">
            <h3 class="text-sm tracking-widest text-white uppercase">{{ $t('order_success.your_order') }}</h3>
          </div>
          <div class="divide-y divide-gray-800">
            <div
              v-for="item in order.items"
              :key="item.id"
              class="flex items-center justify-between px-6 py-4 gap-4"
            >
              <div class="flex-1 min-w-0">
                <p class="text-sm text-white truncate">{{ item.product_name }}</p>
                <p class="text-xs text-gray-500">{{ item.size_ml }}ml · {{ $t('common.qty') }}: {{ item.quantity }}</p>
              </div>
              <p class="text-sm text-[#c9a84c] shrink-0">${{ item.total_price.toFixed(2) }}</p>
            </div>
          </div>
          <!-- Totals -->
          <div class="border-t border-gray-800 px-6 py-4 space-y-2">
            <div class="flex justify-between text-sm text-gray-400">
              <span>{{ $t('cart.subtotal') }}</span>
              <span>${{ order.subtotal.toFixed(2) }}</span>
            </div>
            <div class="flex justify-between text-sm text-gray-400">
              <span>{{ $t('cart.shipping') }}</span>
              <span>{{ order.shipping_cost === 0 ? $t('common.free') : `$${order.shipping_cost.toFixed(2)}` }}</span>
            </div>
            <div class="flex justify-between text-sm text-gray-400">
              <span>{{ $t('cart.tax') }}</span>
              <span>${{ order.tax.toFixed(2) }}</span>
            </div>
            <div v-if="order.discount > 0" class="flex justify-between text-sm text-green-400">
              <span>{{ $t('cart.discount') }}</span>
              <span>-${{ order.discount.toFixed(2) }}</span>
            </div>
            <div class="flex justify-between text-base text-white border-t border-gray-800 pt-3">
              <span class="tracking-widest">{{ $t('cart.total') }}</span>
              <span class="text-[#c9a84c]">${{ order.total.toFixed(2) }}</span>
            </div>
          </div>
        </div>

        <!-- Shipping address -->
        <div class="border border-gray-800 px-6 py-5 mb-8">
          <h3 class="text-xs tracking-widest text-gray-400 uppercase mb-3">{{ $t('order_success.shipping_to') }}</h3>
          <p class="text-sm text-gray-300">{{ order.shipping_first_name }} {{ order.shipping_last_name }}</p>
          <p class="text-sm text-gray-500 mt-1 leading-relaxed">
            {{ order.shipping_address }}<br>
            {{ order.shipping_city }}, {{ order.shipping_postal_code }}<br>
            {{ order.shipping_country }}
          </p>
        </div>

        <!-- Actions -->
        <div class="flex flex-col sm:flex-row gap-4">
          <RouterLink
            to="/account"
            class="flex-1 text-center bg-[#c9a84c] text-black py-4 text-sm tracking-widest hover:bg-[#b8943e] transition-colors"
          >
            {{ $t('order_success.track_order') }}
          </RouterLink>
          <RouterLink
            to="/shop"
            class="flex-1 text-center border border-gray-700 text-gray-300 py-4 text-sm tracking-widest hover:border-gray-500 transition-colors"
          >
            {{ $t('order_success.continue_shopping') }}
          </RouterLink>
        </div>
      </template>

      <!-- Error -->
      <div v-else class="text-center py-20">
        <p class="text-gray-400 mb-4">{{ $t('order_success.not_found') }}</p>
        <RouterLink to="/" class="text-[#c9a84c] text-sm underline">{{ $t('common.go_home') }}</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useCartStore } from '../stores/cart'
import api from '../router/api'

const route = useRoute()
const cart = useCartStore()
const order = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await api.get(`/orders/${route.params.orderId}/confirmation`)
    order.value = data
    cart.clearCart()
  } catch {
    order.value = null
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
@keyframes success-bounce {
  0%, 100% { transform: translateY(0); }
  40% { transform: translateY(-12px); }
  60% { transform: translateY(-6px); }
}
.success-bounce {
  animation: success-bounce 0.8s ease-out;
}
</style>
