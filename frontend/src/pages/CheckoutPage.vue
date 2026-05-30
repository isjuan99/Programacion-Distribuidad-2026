<template>
  <div class="min-h-screen bg-aroma-dark">
    <Header />
    <div class="pt-20 pb-24">
      <div class="max-w-5xl mx-auto px-6 py-12">
        <div class="text-center mb-12">
          <h1 class="font-display text-4xl text-aroma-text">{{ $t('checkout.title') }}</h1>
          <p class="text-aroma-muted text-sm mt-2">{{ $t('checkout.subtitle') }}</p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-[1fr_360px] gap-12">
          <!-- Left column -->
          <div class="space-y-10">
            <!-- Your Selection -->
            <section>
              <h2 class="font-display text-2xl text-aroma-text border-b border-aroma-border pb-4 mb-6">
                {{ $t('checkout.your_selection') }}
              </h2>
              <div class="space-y-4">
                <div v-for="item in cart.items" :key="item.variant_id"
                  class="flex items-center gap-4">
                  <div class="w-20 h-20 bg-aroma-surface flex items-center justify-center shrink-0 overflow-hidden border border-aroma-border/30">
                    <img v-if="item.image" :src="item.image" :alt="item.name" class="w-full h-full object-cover" />
                    <svg v-else class="w-8 h-8 text-aroma-border" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1"
                        d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
                    </svg>
                  </div>
                  <div class="flex-1">
                    <h3 class="font-display text-lg text-aroma-text">{{ item.name }}</h3>
                    <p class="text-aroma-muted text-xs">{{ item.brand }} · {{ item.size_ml }}ml</p>
                    <div class="flex items-center gap-3 mt-2">
                      <button @click="cart.updateQuantity(item.variant_id, item.quantity - 1)"
                        class="w-6 h-6 border border-aroma-border flex items-center justify-center text-sm text-aroma-text hover:border-gold-dark">−</button>
                      <span class="text-sm w-4 text-center text-aroma-text">{{ item.quantity }}</span>
                      <button @click="cart.updateQuantity(item.variant_id, item.quantity + 1)"
                        class="w-6 h-6 border border-aroma-border flex items-center justify-center text-sm text-aroma-text hover:border-gold-dark">+</button>
                    </div>
                  </div>
                  <div class="text-right">
                    <p class="text-aroma-text">${{ (item.price * item.quantity).toFixed(2) }}</p>
                    <button @click="cart.removeItem(item.variant_id)"
                      class="text-xs text-aroma-muted hover:text-red-400 mt-1 underline">
                      {{ $t('cart.remove') }}
                    </button>
                  </div>
                </div>
              </div>
            </section>

            <!-- Shipping Details -->
            <section>
              <h2 class="font-display text-2xl text-aroma-text border-b border-aroma-border pb-4 mb-6">
                {{ $t('checkout.shipping_details') }}
              </h2>
              <div class="space-y-4">
                <input v-model="form.email" type="email" required
                  class="w-full border border-aroma-border text-aroma-text placeholder-aroma-muted bg-aroma-surface px-4 py-3 text-sm
                         focus:outline-none focus:border-gold-dark"
                  :placeholder="$t('checkout.email')" />
                <div class="grid grid-cols-2 gap-4">
                  <input v-model="form.first_name" type="text" required
                    class="border border-aroma-border text-aroma-text placeholder-aroma-muted bg-aroma-surface px-4 py-3 text-sm
                           focus:outline-none focus:border-gold-dark"
                    :placeholder="$t('checkout.first_name')" />
                  <input v-model="form.last_name" type="text" required
                    class="border border-aroma-border text-aroma-text placeholder-aroma-muted bg-aroma-surface px-4 py-3 text-sm
                           focus:outline-none focus:border-gold-dark"
                    :placeholder="$t('checkout.last_name')" />
                </div>
                <input v-model="form.address" type="text" required
                  class="w-full border border-aroma-border text-aroma-text placeholder-aroma-muted bg-aroma-surface px-4 py-3 text-sm
                         focus:outline-none focus:border-gold-dark"
                  :placeholder="$t('checkout.address')" />
                <div class="grid grid-cols-2 gap-4">
                  <input v-model="form.city" type="text" required
                    class="border border-aroma-border text-aroma-text placeholder-aroma-muted bg-aroma-surface px-4 py-3 text-sm
                           focus:outline-none focus:border-gold-dark"
                    :placeholder="$t('checkout.city')" />
                  <input v-model="form.postal_code" type="text" required
                    class="border border-aroma-border text-aroma-text placeholder-aroma-muted bg-aroma-surface px-4 py-3 text-sm
                           focus:outline-none focus:border-gold-dark"
                    :placeholder="$t('checkout.postal_code')" />
                </div>
                <select v-model="form.country" required
                  class="w-full border border-aroma-border text-aroma-text px-4 py-3 text-sm
                         focus:outline-none focus:border-gold-dark bg-aroma-surface appearance-none">
                  <option value="">{{ $t('checkout.country') }}</option>
                  <option value="CO">Colombia</option>
                  <option value="MX">México</option>
                  <option value="US">United States</option>
                  <option value="ES">España</option>
                  <option value="AR">Argentina</option>
                </select>
              </div>
            </section>

            <!-- Shipping Method -->
            <section>
              <h2 class="font-display text-2xl text-aroma-text border-b border-aroma-border pb-4 mb-6">
                {{ $t('checkout.shipping_method') }}
              </h2>
              <div class="space-y-3">
                <label class="flex items-center justify-between border border-aroma-border p-4 cursor-pointer
                              hover:border-gold-dark transition-colors"
                  :class="form.shipping_method === 'standard' ? 'border-gold-dark' : ''">
                  <div class="flex items-center gap-3">
                    <input type="radio" v-model="form.shipping_method" value="standard" class="accent-gold-dark" />
                    <div>
                      <p class="text-sm text-aroma-text font-medium">{{ $t('checkout.standard_shipping') }}</p>
                      <p class="text-xs text-aroma-muted">{{ $t('checkout.standard_days') }}</p>
                    </div>
                  </div>
                  <span class="text-sm text-aroma-text">{{ $t('checkout.complimentary') }}</span>
                </label>
                <label class="flex items-center justify-between border border-aroma-border p-4 cursor-pointer
                              hover:border-gold-dark transition-colors"
                  :class="form.shipping_method === 'express' ? 'border-gold-dark' : ''">
                  <div class="flex items-center gap-3">
                    <input type="radio" v-model="form.shipping_method" value="express" class="accent-gold-dark" />
                    <div>
                      <p class="text-sm text-aroma-text font-medium">{{ $t('checkout.express_shipping') }}</p>
                      <p class="text-xs text-aroma-muted">{{ $t('checkout.express_days') }}</p>
                    </div>
                  </div>
                  <span class="text-sm text-aroma-text">$25.00</span>
                </label>
              </div>
            </section>

            <!-- Payment -->
            <section>
              <h2 class="font-display text-2xl text-aroma-text border-b border-aroma-border pb-4 mb-6">
                {{ $t('checkout.payment') }}
              </h2>
              <div class="border border-aroma-border">
                <label class="flex items-center justify-between p-4 cursor-pointer border-b border-aroma-border">
                  <div class="flex items-center gap-3">
                    <input type="radio" v-model="form.payment_method" value="card" class="accent-gold-dark" checked />
                    <span class="text-sm text-aroma-text">{{ $t('checkout.credit_card') }}</span>
                  </div>
                  <svg class="w-6 h-6 text-aroma-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                      d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"/>
                  </svg>
                </label>
                <div v-if="form.payment_method === 'card'" class="p-4 space-y-3 bg-aroma-surface/50">
                  <input v-model="form.card_number" type="text" placeholder="•••• •••• •••• ••••"
                    class="w-full border border-aroma-border px-4 py-3 text-sm text-aroma-text bg-aroma-surface
                           focus:outline-none focus:border-gold-dark" />
                  <div class="grid grid-cols-2 gap-3">
                    <input v-model="form.card_expiry" placeholder="MM / YY"
                      class="border border-aroma-border px-4 py-3 text-sm text-aroma-text bg-aroma-surface
                             focus:outline-none focus:border-gold-dark" />
                    <input v-model="form.card_cvc" placeholder="CVC"
                      class="border border-aroma-border px-4 py-3 text-sm text-aroma-text bg-aroma-surface
                             focus:outline-none focus:border-gold-dark" />
                  </div>
                  <input v-model="form.card_name" placeholder="Nombre en la Tarjeta"
                    class="w-full border border-aroma-border px-4 py-3 text-sm text-aroma-text bg-aroma-surface
                           focus:outline-none focus:border-gold-dark" />
                </div>
                <label class="flex items-center justify-between p-4 cursor-pointer">
                  <div class="flex items-center gap-3">
                    <input type="radio" v-model="form.payment_method" value="paypal" class="accent-gold-dark" />
                    <span class="text-sm text-aroma-text">PayPal</span>
                  </div>
                  <svg class="w-6 h-6 text-blue-400" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M7.076 21.337H2.47a.641.641 0 0 1-.633-.74L4.944 3.72a.77.77 0 0 1 .76-.65h6.64c2.2 0 3.8.48 4.756 1.43.42.41.73.88.918 1.41.19.54.247 1.15.168 1.84v.35l.023.14c-.005.04-.01.08-.01.12-.386 2.19-1.69 3.72-3.874 4.55-1.04.4-2.3.6-3.77.6H9.27a.77.77 0 0 0-.76.65l-.88 5.61a.64.64 0 0 1-.634.56l.08-.02Z"/>
                  </svg>
                </label>
              </div>
            </section>
          </div>

          <!-- Order Summary (sticky right) -->
          <div class="lg:sticky lg:top-24 self-start">
            <div class="border border-aroma-border p-6 bg-aroma-surface">
              <h3 class="font-display text-xl text-aroma-text mb-6">{{ $t('checkout.order_summary') }}</h3>

              <!-- Coupon -->
              <div class="flex gap-2 mb-6">
                <input v-model="couponCode" type="text"
                  class="flex-1 border border-aroma-border text-sm px-3 py-2 text-aroma-text bg-aroma-surface
                         focus:outline-none focus:border-gold-dark"
                  :placeholder="$t('cart.coupon_placeholder')" />
                <button @click="applyCoupon"
                  class="bg-aroma-border text-xs px-4 tracking-widest uppercase text-aroma-text
                         hover:bg-aroma-border/70 transition-colors">
                  {{ $t('cart.apply') }}
                </button>
              </div>

              <!-- Totals -->
              <div class="space-y-3 text-sm border-t border-aroma-border pt-4">
                <div class="flex justify-between text-aroma-muted">
                  <span>{{ $t('checkout.subtotal') }}</span>
                  <span>${{ cart.subtotal.toFixed(2) }}</span>
                </div>
                <div class="flex justify-between text-aroma-muted">
                  <span>{{ $t('checkout.shipping_cost') }}</span>
                  <span>{{ form.shipping_method === 'standard' ? $t('checkout.complimentary') : '$25.00' }}</span>
                </div>
                <div class="flex justify-between text-aroma-muted">
                  <span>{{ $t('checkout.estimated_tax') }}</span>
                  <span>${{ tax.toFixed(2) }}</span>
                </div>
                <div v-if="discount > 0" class="flex justify-between text-green-500">
                  <span>Descuento</span>
                  <span>-${{ discount.toFixed(2) }}</span>
                </div>
              </div>

              <div class="flex justify-between items-end mt-4 pt-4 border-t border-aroma-border">
                <div>
                  <p class="text-[10px] tracking-widest uppercase text-aroma-muted">Total</p>
                  <span class="text-2xl font-display text-aroma-text">${{ grandTotal.toFixed(2) }}</span>
                </div>
                <span class="text-[10px] text-aroma-muted">USD</span>
              </div>

              <p v-if="error" class="text-red-500 text-xs mt-3">{{ error }}</p>

              <button @click="placeOrder" :disabled="loading || cart.items.length === 0"
                class="w-full bg-gold text-aroma-dark py-4 text-xs tracking-widest uppercase font-sans font-medium
                       hover:bg-gold-light transition-colors mt-6 disabled:opacity-50">
                {{ loading ? $t('common.loading') : $t('checkout.place_order') }}
              </button>

              <!-- Security badges -->
              <div class="flex items-center justify-center gap-4 mt-4">
                <svg class="w-5 h-5 text-aroma-border" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                </svg>
                <svg class="w-5 h-5 text-aroma-border" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
                </svg>
                <svg class="w-5 h-5 text-aroma-border" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
                </svg>
              </div>
              <p class="text-[10px] text-aroma-muted text-center mt-2">{{ $t('checkout.secure_message') }}</p>
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

const shippingCost = computed(() => form.value.shipping_method === 'express' ? 25 : 0)
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
    const orderId = data.id
    router.push(`/order/success/${orderId}`)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Error al procesar el pedido'
  } finally {
    loading.value = false
  }
}
</script>
