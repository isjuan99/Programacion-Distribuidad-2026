<template>
  <div class="min-h-screen bg-white">
    <Header />
    <div class="pt-32 pb-24">
      <div class="max-w-5xl mx-auto px-6">
        <div class="text-center mb-12">
          <h1 class="font-display text-4xl text-[#111010]">{{ $t('checkout.title') }}</h1>
          <p class="text-gray-500 text-sm mt-2">{{ $t('checkout.subtitle') }}</p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-[1fr_380px] gap-10">
          <!-- Columna izquierda -->
          <div class="space-y-8">

            <!-- Tu selección -->
            <section class="bg-gray-50 border border-gray-200 p-6 rounded-sm">
              <h2 class="font-display text-xl text-[#111010] mb-5">{{ $t('checkout.your_selection') }}</h2>
              <div class="space-y-4">
                <div v-for="item in cart.items" :key="item.variant_id" class="flex items-center gap-4">
                  <div class="w-16 h-16 bg-white border border-gray-200 shrink-0 overflow-hidden rounded-sm">
                    <img v-if="item.image" :src="item.image" :alt="item.name" class="w-full h-full object-cover" />
                    <svg v-else class="w-6 h-6 text-gray-300 m-auto mt-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
                    </svg>
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="font-medium text-[#111010] text-sm truncate">{{ item.name }}</p>
                    <p class="text-gray-400 text-xs">{{ item.brand }} · {{ item.size_ml }}ml</p>
                    <div class="flex items-center gap-2 mt-1.5">
                      <button @click="cart.updateQuantity(item.variant_id, item.quantity - 1)"
                        class="w-6 h-6 border border-gray-300 flex items-center justify-center text-sm text-gray-500 hover:border-gold hover:text-gold transition-colors">−</button>
                      <span class="text-sm w-4 text-center text-[#111010] font-medium">{{ item.quantity }}</span>
                      <button @click="cart.updateQuantity(item.variant_id, item.quantity + 1)"
                        class="w-6 h-6 border border-gray-300 flex items-center justify-center text-sm text-gray-500 hover:border-gold hover:text-gold transition-colors">+</button>
                    </div>
                  </div>
                  <div class="text-right shrink-0">
                    <p class="text-[#111010] font-semibold text-sm">{{ formatCOP(item.price * item.quantity) }}</p>
                    <button @click="cart.removeItem(item.variant_id)" class="text-xs text-red-400 hover:text-red-600 mt-1">
                      {{ $t('cart.remove') }}
                    </button>
                  </div>
                </div>
              </div>
            </section>

            <!-- Datos de envío -->
            <section class="bg-gray-50 border border-gray-200 p-6 rounded-sm">
              <h2 class="font-display text-xl text-[#111010] mb-5">{{ $t('checkout.shipping_details') }}</h2>
              <div class="space-y-3">
                <input v-model="form.email" type="email" required
                  class="w-full border border-gray-300 text-[#111010] placeholder-gray-400 bg-white px-4 py-3 text-sm focus:outline-none focus:border-gold transition-colors rounded-sm"
                  :placeholder="$t('checkout.email')" />
                <div class="grid grid-cols-2 gap-3">
                  <input v-model="form.first_name" type="text" required
                    class="border border-gray-300 text-[#111010] placeholder-gray-400 bg-white px-4 py-3 text-sm focus:outline-none focus:border-gold transition-colors rounded-sm"
                    :placeholder="$t('checkout.first_name')" />
                  <input v-model="form.last_name" type="text" required
                    class="border border-gray-300 text-[#111010] placeholder-gray-400 bg-white px-4 py-3 text-sm focus:outline-none focus:border-gold transition-colors rounded-sm"
                    :placeholder="$t('checkout.last_name')" />
                </div>
                <input v-model="form.address" type="text" required
                  class="w-full border border-gray-300 text-[#111010] placeholder-gray-400 bg-white px-4 py-3 text-sm focus:outline-none focus:border-gold transition-colors rounded-sm"
                  :placeholder="$t('checkout.address')" />
                <div class="grid grid-cols-2 gap-3">
                  <input v-model="form.city" type="text" required
                    class="border border-gray-300 text-[#111010] placeholder-gray-400 bg-white px-4 py-3 text-sm focus:outline-none focus:border-gold transition-colors rounded-sm"
                    :placeholder="$t('checkout.city')" />
                  <input v-model="form.postal_code" type="text" required
                    class="border border-gray-300 text-[#111010] placeholder-gray-400 bg-white px-4 py-3 text-sm focus:outline-none focus:border-gold transition-colors rounded-sm"
                    :placeholder="$t('checkout.postal_code')" />
                </div>
                <select v-model="form.country" required
                  class="w-full border border-gray-300 text-[#111010] px-4 py-3 text-sm focus:outline-none focus:border-gold bg-white appearance-none rounded-sm">
                  <option value="">{{ $t('checkout.country') }}</option>
                  <option value="CO">Colombia</option>
                  <option value="MX">México</option>
                  <option value="US">United States</option>
                  <option value="ES">España</option>
                  <option value="AR">Argentina</option>
                </select>
              </div>
            </section>

            <!-- Método de envío -->
            <section class="bg-gray-50 border border-gray-200 p-6 rounded-sm">
              <h2 class="font-display text-xl text-[#111010] mb-5">{{ $t('checkout.shipping_method') }}</h2>
              <div class="space-y-3">
                <label class="flex items-center justify-between border bg-white p-4 cursor-pointer rounded-sm transition-colors"
                  :class="form.shipping_method === 'standard' ? 'border-gold' : 'border-gray-200 hover:border-gray-400'">
                  <div class="flex items-center gap-3">
                    <input type="radio" v-model="form.shipping_method" value="standard" class="accent-gold" />
                    <div>
                      <p class="text-sm text-[#111010] font-medium">{{ $t('checkout.standard_shipping') }}</p>
                      <p class="text-xs text-gray-400">{{ $t('checkout.standard_days') }}</p>
                    </div>
                  </div>
                  <span class="text-sm text-gold font-medium">{{ $t('checkout.complimentary') }}</span>
                </label>
                <label class="flex items-center justify-between border bg-white p-4 cursor-pointer rounded-sm transition-colors"
                  :class="form.shipping_method === 'express' ? 'border-gold' : 'border-gray-200 hover:border-gray-400'">
                  <div class="flex items-center gap-3">
                    <input type="radio" v-model="form.shipping_method" value="express" class="accent-gold" />
                    <div>
                      <p class="text-sm text-[#111010] font-medium">{{ $t('checkout.express_shipping') }}</p>
                      <p class="text-xs text-gray-400">{{ $t('checkout.express_days') }}</p>
                    </div>
                  </div>
                  <span class="text-sm text-[#111010] font-medium">{{ formatCOP(25000) }}</span>
                </label>
              </div>
            </section>

            <!-- Pago -->
            <section class="bg-gray-50 border border-gray-200 p-6 rounded-sm">
              <h2 class="font-display text-xl text-[#111010] mb-5">{{ $t('checkout.payment') }}</h2>
              <div class="border border-gray-200 rounded-sm overflow-hidden bg-white">
                <label class="flex items-center justify-between p-4 cursor-pointer border-b border-gray-100">
                  <div class="flex items-center gap-3">
                    <input type="radio" v-model="form.payment_method" value="card" class="accent-gold" checked />
                    <span class="text-sm text-[#111010] font-medium">{{ $t('checkout.credit_card') }}</span>
                  </div>
                  <div class="flex gap-1">
                    <div class="w-8 h-5 bg-blue-600 rounded-sm text-white text-[8px] flex items-center justify-center font-bold">VISA</div>
                    <div class="w-8 h-5 bg-orange-500 rounded-sm text-white text-[8px] flex items-center justify-center font-bold">MC</div>
                  </div>
                </label>
                <div v-if="form.payment_method === 'card'" class="p-4 space-y-3 bg-gray-50">
                  <input v-model="form.card_number" type="text" placeholder="•••• •••• •••• ••••"
                    class="w-full border border-gray-300 px-4 py-3 text-sm text-[#111010] bg-white focus:outline-none focus:border-gold rounded-sm" />
                  <div class="grid grid-cols-2 gap-3">
                    <input v-model="form.card_expiry" placeholder="MM / AA"
                      class="border border-gray-300 px-4 py-3 text-sm text-[#111010] bg-white focus:outline-none focus:border-gold rounded-sm" />
                    <input v-model="form.card_cvc" placeholder="CVC"
                      class="border border-gray-300 px-4 py-3 text-sm text-[#111010] bg-white focus:outline-none focus:border-gold rounded-sm" />
                  </div>
                  <input v-model="form.card_name" placeholder="Nombre en la tarjeta"
                    class="w-full border border-gray-300 px-4 py-3 text-sm text-[#111010] bg-white focus:outline-none focus:border-gold rounded-sm" />
                </div>
                <label class="flex items-center justify-between p-4 cursor-pointer">
                  <div class="flex items-center gap-3">
                    <input type="radio" v-model="form.payment_method" value="paypal" class="accent-gold" />
                    <span class="text-sm text-[#111010] font-medium">PayPal</span>
                  </div>
                  <svg class="w-6 h-6 text-blue-500" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M7.076 21.337H2.47a.641.641 0 0 1-.633-.74L4.944 3.72a.77.77 0 0 1 .76-.65h6.64c2.2 0 3.8.48 4.756 1.43.42.41.73.88.918 1.41.19.54.247 1.15.168 1.84v.35l.023.14c-.005.04-.01.08-.01.12-.386 2.19-1.69 3.72-3.874 4.55-1.04.4-2.3.6-3.77.6H9.27a.77.77 0 0 0-.76.65l-.88 5.61a.64.64 0 0 1-.634.56l.08-.02Z"/>
                  </svg>
                </label>
              </div>
            </section>
          </div>

          <!-- Resumen del pedido (derecha sticky) -->
          <div class="lg:sticky lg:top-24 self-start">
            <div class="border border-gray-200 p-6 bg-white rounded-sm shadow-sm">
              <h3 class="font-display text-xl text-[#111010] mb-6">{{ $t('checkout.order_summary') }}</h3>

              <!-- Cupón -->
              <div class="flex gap-2 mb-6">
                <input v-model="couponCode" type="text"
                  class="flex-1 border border-gray-300 text-sm px-3 py-2 text-[#111010] placeholder-gray-400 bg-white focus:outline-none focus:border-gold transition-colors rounded-sm"
                  :placeholder="$t('cart.coupon_placeholder')" />
                <button @click="applyCoupon"
                  class="bg-[#111010] text-white text-xs px-4 tracking-widest uppercase hover:bg-gray-800 transition-colors rounded-sm">
                  {{ $t('cart.apply') }}
                </button>
              </div>

              <!-- Totales -->
              <div class="space-y-2.5 text-sm border-t border-gray-200 pt-4">
                <div class="flex justify-between text-gray-500">
                  <span>{{ $t('checkout.subtotal') }}</span>
                  <span class="text-[#111010] font-medium">{{ formatCOP(cart.subtotal) }}</span>
                </div>
                <div class="flex justify-between text-gray-500">
                  <span>{{ $t('checkout.shipping_cost') }}</span>
                  <span :class="form.shipping_method === 'standard' ? 'text-gold font-medium' : 'text-[#111010] font-medium'">
                    {{ form.shipping_method === 'standard' ? $t('checkout.complimentary') : formatCOP(25000) }}
                  </span>
                </div>
                <div class="flex justify-between text-gray-500">
                  <span>{{ $t('checkout.estimated_tax') }}</span>
                  <span class="text-[#111010]">{{ formatCOP(tax) }}</span>
                </div>
                <div v-if="discount > 0" class="flex justify-between text-green-600">
                  <span>Descuento</span>
                  <span>-{{ formatCOP(discount) }}</span>
                </div>
              </div>

              <div class="flex justify-between items-end mt-5 pt-4 border-t border-gray-200">
                <div>
                  <p class="text-[10px] tracking-widest uppercase text-gray-400">Total</p>
                  <span class="text-2xl font-display text-[#111010]">{{ formatCOP(grandTotal) }}</span>
                </div>
                <span class="text-[10px] text-gray-400 bg-gray-100 px-2 py-1 rounded">COP</span>
              </div>

              <p v-if="error" class="text-red-500 text-xs mt-3 bg-red-50 p-2 rounded">{{ error }}</p>

              <button @click="placeOrder" :disabled="loading || cart.items.length === 0"
                class="w-full bg-gold text-white py-4 text-sm tracking-widest uppercase font-medium
                       hover:bg-gold-dark transition-colors mt-5 disabled:opacity-50 rounded-sm">
                {{ loading ? $t('common.loading') : $t('checkout.place_order') }}
              </button>

              <!-- Badges de seguridad -->
              <div class="flex items-center justify-center gap-3 mt-4 pt-4 border-t border-gray-100">
                <div class="flex items-center gap-1 text-gray-400">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                  </svg>
                  <span class="text-[10px]">SSL</span>
                </div>
                <div class="flex items-center gap-1 text-gray-400">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
                  </svg>
                  <span class="text-[10px]">Pago seguro</span>
                </div>
              </div>
              <p class="text-[10px] text-gray-400 text-center mt-1">{{ $t('checkout.secure_message') }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    <Footer />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import Header from '../components/layout/Header.vue'
import Footer from '../components/layout/Footer.vue'
import { useCartStore } from '../stores/cart'
import { formatCOP } from '../utils/currency'
import api from '../router/api'

const router = useRouter()
const cart = useCartStore()

const form = ref({
  email: '', first_name: '', last_name: '', address: '', city: '',
  postal_code: '', country: '', shipping_method: 'standard', payment_method: 'card',
  card_number: '', card_expiry: '', card_cvc: '', card_name: '',
})

const couponCode = ref('')
const discount = ref(0)
const loading = ref(false)
const error = ref('')

const shippingCost = computed(() => form.value.shipping_method === 'express' ? 25000 : 0)
const tax = computed(() => (cart.subtotal - discount.value) * 0.08)
const grandTotal = computed(() => cart.subtotal - discount.value + shippingCost.value + tax.value)

async function applyCoupon() {
  try {
    const { data } = await api.get('/coupons/validate', { params: { code: couponCode.value } })
    if (data.discount_type === 'percentage') {
      discount.value = cart.subtotal * (data.discount_value / 100)
    } else {
      discount.value = data.discount_value
    }
  } catch {
    error.value = 'Cupón inválido'
  }
}

async function placeOrder() {
  error.value = ''
  loading.value = true
  try {
    const payload = {
      items: cart.items.map(i => ({ variant_id: i.variant_id, quantity: i.quantity })),
      shipping: {
        email: form.value.email,
        first_name: form.value.first_name,
        last_name: form.value.last_name,
        address: form.value.address,
        city: form.value.city,
        postal_code: form.value.postal_code,
        country: form.value.country,
      },
      shipping_method: form.value.shipping_method,
      coupon_code: couponCode.value || undefined,
      payment_method: form.value.payment_method,
    }
    const { data } = await api.post('/orders', payload)
    router.push(`/order/success/${data.id}`)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Error al procesar el pedido'
  } finally {
    loading.value = false
  }
}
</script>
