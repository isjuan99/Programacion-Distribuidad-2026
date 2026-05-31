<template>
  <div class="min-h-screen bg-white">
    <Header />
    <div class="pt-32 max-w-5xl mx-auto px-6 pb-24">
      <h1 class="font-display text-5xl text-[#111010] mb-12">{{ $t('cart.title') }}</h1>

      <!-- Carrito vacío -->
      <div v-if="cart.items.length === 0" class="text-center py-24">
        <div class="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <svg class="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/>
          </svg>
        </div>
        <p class="text-gray-500 mb-8 text-lg">{{ $t('cart.empty') }}</p>
        <router-link to="/shop" class="btn-gold">{{ $t('cart.empty_cta') }}</router-link>
      </div>

      <div v-else class="grid grid-cols-1 lg:grid-cols-[1fr_360px] gap-10">
        <!-- Items -->
        <div>
          <!-- Cabecera tabla -->
          <div class="border-b border-gray-200 pb-3 mb-4 grid grid-cols-[1fr_auto_auto_auto] gap-4 items-center">
            <span class="text-[10px] tracking-widest uppercase text-gray-400">Producto</span>
            <span class="text-[10px] tracking-widest uppercase text-gray-400">Precio</span>
            <span class="text-[10px] tracking-widest uppercase text-gray-400">Cantidad</span>
            <span class="text-[10px] tracking-widest uppercase text-gray-400">Total</span>
          </div>

          <!-- Fila de cada producto -->
          <div v-for="item in cart.items" :key="item.variant_id"
            class="grid grid-cols-[1fr_auto_auto_auto] gap-4 items-center py-5 border-b border-gray-100 bg-gray-50/50 px-4 rounded-sm mb-2">
            <div class="flex items-center gap-4">
              <div class="w-20 h-20 bg-white border border-gray-200 overflow-hidden shrink-0 rounded-sm">
                <img v-if="item.image" :src="item.image" :alt="item.name" class="w-full h-full object-cover" />
                <svg v-else class="w-8 h-8 text-gray-300 m-auto mt-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
                </svg>
              </div>
              <div>
                <p class="text-[10px] tracking-widest uppercase text-gray-400">{{ item.brand }}</p>
                <p class="font-display text-lg text-[#111010]">{{ item.name }}</p>
                <p class="text-xs text-gray-400 mt-0.5">{{ item.size_ml }}ml</p>
                <button @click="cart.removeItem(item.variant_id)"
                  class="text-[10px] text-red-400 hover:text-red-600 mt-2 transition-colors flex items-center gap-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                  </svg>
                  {{ $t('cart.remove') }}
                </button>
              </div>
            </div>

            <span class="text-[#374151] font-medium text-sm">{{ formatCOP(item.price) }}</span>

            <!-- Controles cantidad -->
            <div class="flex items-center border border-gray-300 rounded-sm">
              <button @click="cart.updateQuantity(item.variant_id, item.quantity - 1)"
                class="w-8 h-8 flex items-center justify-center text-gray-500 hover:text-[#111010] hover:bg-gray-100 transition-colors text-lg">−</button>
              <span class="w-8 text-center text-[#111010] text-sm font-medium">{{ item.quantity }}</span>
              <button @click="cart.updateQuantity(item.variant_id, item.quantity + 1)"
                class="w-8 h-8 flex items-center justify-center text-gray-500 hover:text-[#111010] hover:bg-gray-100 transition-colors text-lg">+</button>
            </div>

            <span class="text-[#111010] font-semibold text-sm">{{ formatCOP(item.price * item.quantity) }}</span>
          </div>

          <div class="mt-8 flex items-center justify-between">
            <router-link to="/shop"
              class="flex items-center gap-2 text-xs tracking-widest uppercase text-[#374151] border border-gray-300 px-5 py-2.5 hover:border-[#111010] transition-colors">
              ← {{ $t('cart.continue_shopping') }}
            </router-link>
          </div>
        </div>

        <!-- Resumen del carrito -->
        <div class="bg-white border border-gray-200 p-6 self-start sticky top-24 rounded-sm shadow-sm">
          <h3 class="font-display text-2xl text-[#111010] mb-6">Resumen</h3>

          <!-- Cupón -->
          <div class="flex gap-2 mb-6">
            <input v-model="couponCode" type="text"
              class="flex-1 border border-gray-300 text-[#111010] placeholder-gray-400 px-3 py-2 text-sm
                     focus:outline-none focus:border-gold transition-colors"
              :placeholder="$t('cart.coupon_placeholder')" />
            <button @click="applyCoupon"
              class="bg-[#111010] text-white px-4 text-xs tracking-widest uppercase hover:bg-gray-800 transition-colors">
              {{ $t('cart.apply') }}
            </button>
          </div>

          <div class="space-y-3 text-sm border-t border-gray-200 pt-4">
            <div class="flex justify-between text-gray-500">
              <span>{{ $t('cart.subtotal') }}</span>
              <span class="text-[#111010] font-medium">{{ formatCOP(cart.subtotal) }}</span>
            </div>
            <div class="flex justify-between text-gray-500">
              <span>{{ $t('cart.shipping') }}</span>
              <span class="text-gold font-medium">{{ $t('common.free') }}</span>
            </div>
          </div>

          <div class="flex justify-between items-center mt-6 pt-5 border-t border-gray-200">
            <span class="text-[10px] tracking-widest uppercase text-gray-400">{{ $t('cart.total') }}</span>
            <span class="font-display text-3xl text-[#111010]">{{ formatCOP(cart.subtotal) }}</span>
          </div>

          <router-link to="/checkout"
            class="block w-full text-center mt-6 py-4 bg-gold text-white text-xs tracking-widest uppercase font-medium
                   hover:bg-gold-dark transition-colors">
            {{ $t('cart.checkout') }}
          </router-link>

          <p class="text-[10px] text-center text-gray-400 mt-4 flex items-center justify-center gap-1">
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
            </svg>
            {{ $t('cart.free_shipping') }}
          </p>
        </div>
      </div>
    </div>
    <Footer />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Header from '../components/layout/Header.vue'
import Footer from '../components/layout/Footer.vue'
import { useCartStore } from '../stores/cart'
import { formatCOP } from '../utils/currency'
import api from '../router/api'

const cart = useCartStore()
const couponCode = ref('')

async function applyCoupon() {
  try {
    await api.get('/coupons/validate', { params: { code: couponCode.value } })
    alert('Cupón aplicado. Disponible en el checkout.')
  } catch {
    alert('Cupón inválido')
  }
}
</script>
