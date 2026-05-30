<template>
  <div class="min-h-screen bg-aroma-darker">
    <Header />
    <div class="pt-16 min-h-screen">
      <div class="max-w-5xl mx-auto px-6 py-12 grid grid-cols-[240px_1fr] gap-8">
        <!-- Sidebar -->
        <aside class="card-aroma p-6 self-start sticky top-24">
          <div class="mb-6">
            <p class="text-[10px] tracking-widest uppercase text-gold mb-1">{{ $t('account.title') }}</p>
            <p class="text-xs text-aroma-muted">{{ $t('account.member') }}</p>
          </div>
          <nav class="space-y-1">
            <button v-for="item in menuItems" :key="item.tab"
              @click="activeTab = item.tab"
              class="w-full flex items-center gap-3 px-3 py-2.5 text-sm text-left transition-colors rounded-sm"
              :class="activeTab === item.tab
                ? 'bg-aroma-border text-aroma-text border-l-2 border-gold'
                : 'text-aroma-muted hover:text-aroma-text'">
              <component :is="item.icon" class="w-4 h-4" />
              {{ $t(item.i18n) }}
            </button>
          </nav>
          <button @click="handleLogout"
            class="mt-8 w-full btn-gold text-[10px] py-2">
            {{ $t('account.book_consultation') }}
          </button>
        </aside>

        <!-- Main content -->
        <main>
          <!-- Profile Tab -->
          <div v-if="activeTab === 'profile'">
            <h1 class="font-display text-4xl text-aroma-text mb-1">
              {{ $t('account.welcome') }}
              <span class="text-gold">{{ auth.user?.first_name }}</span>
            </h1>
            <p class="text-aroma-muted text-sm mb-8">{{ $t('account.profile_subtitle') }}</p>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
              <!-- Last Order Card -->
              <div class="card-aroma p-6 flex gap-4 items-start">
                <div class="w-20 h-20 bg-aroma-surface shrink-0 overflow-hidden">
                  <img v-if="lastOrder?.items?.[0]" src="https://images.unsplash.com/photo-1541643600914-78b084683702?w=200"
                    class="w-full h-full object-cover" alt="Last order" />
                </div>
                <div class="flex-1">
                  <div class="flex items-start justify-between mb-2">
                    <p class="text-aroma-muted text-xs">{{ $t('account.last_order') }}</p>
                    <span v-if="lastOrder" class="text-[10px] px-2 py-0.5 border"
                      :class="lastOrder.status === 'shipped' ? 'border-gold text-gold' : 'border-aroma-border text-aroma-muted'">
                      {{ statusLabel(lastOrder.status) }}
                    </span>
                  </div>
                  <p v-if="lastOrder" class="text-xs text-aroma-muted mb-1">Pedido #{{ lastOrder.order_number }}</p>
                  <p class="font-display text-2xl text-aroma-text">${{ lastOrder?.total?.toFixed(2) || '—' }}</p>
                  <button v-if="lastOrder" class="text-xs text-gold mt-3 hover:underline">
                    {{ $t('account.track_order') }} →
                  </button>
                </div>
              </div>

              <!-- Stats column -->
              <div class="space-y-4">
                <!-- Loyalty points -->
                <div class="card-aroma p-4 text-center">
                  <div class="w-8 h-8 border border-gold rounded-full flex items-center justify-center mx-auto mb-2">
                    <svg class="w-4 h-4 text-gold" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                    </svg>
                  </div>
                  <p class="font-display text-3xl text-aroma-text">{{ auth.user?.loyalty_points || 0 }}</p>
                  <p class="text-[10px] tracking-widest uppercase text-aroma-muted mt-1">{{ $t('account.loyalty_points') }}</p>
                </div>

                <!-- Default address -->
                <div class="card-aroma p-4">
                  <div class="flex items-center gap-2 mb-2">
                    <svg class="w-4 h-4 text-gold" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                        d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
                    </svg>
                    <p class="text-xs font-medium text-aroma-text">{{ $t('account.default_address') }}</p>
                  </div>
                  <p class="text-xs text-aroma-muted leading-relaxed">Sin dirección guardada</p>
                </div>
              </div>
            </div>

            <!-- Recent Order History -->
            <div>
              <h2 class="font-display text-2xl text-aroma-text mb-6">{{ $t('account.recent_history') }}</h2>
              <div v-if="loadingOrders" class="animate-pulse space-y-3">
                <div v-for="i in 3" :key="i" class="h-12 bg-aroma-surface" />
              </div>
              <table v-else class="w-full text-sm">
                <thead>
                  <tr class="border-b border-aroma-border">
                    <th class="text-left pb-3 text-[10px] tracking-widest uppercase text-aroma-muted font-normal">{{ $t('account.order_id') }}</th>
                    <th class="text-left pb-3 text-[10px] tracking-widest uppercase text-aroma-muted font-normal">{{ $t('account.date') }}</th>
                    <th class="text-left pb-3 text-[10px] tracking-widest uppercase text-aroma-muted font-normal">{{ $t('account.total') }}</th>
                    <th class="text-left pb-3 text-[10px] tracking-widest uppercase text-aroma-muted font-normal">{{ $t('account.status') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <template v-for="order in orders" :key="order.id">
                    <tr class="border-b border-aroma-border/50 hover:bg-aroma-surface/30" :class="{ 'border-b-0': order.tracking_number }">
                      <td class="py-4 text-aroma-text">#{{ order.order_number }}</td>
                      <td class="py-4 text-aroma-muted">{{ formatDate(order.created_at) }}</td>
                      <td class="py-4 text-aroma-text">${{ order.total.toFixed(2) }}</td>
                      <td class="py-4">
                        <span :class="statusClass(order.status)">{{ statusLabel(order.status) }}</span>
                      </td>
                    </tr>
                    <tr v-if="order.tracking_number" class="border-b border-aroma-border/50">
                      <td colspan="4" class="pb-4 pt-0">
                        <!-- Tracking info -->
                        <div class="mt-2 bg-blue-900/10 border border-blue-500/20 rounded p-3">
                          <p class="text-xs tracking-widest text-gray-400 mb-1 uppercase">{{ $t('account.tracking') }}</p>
                          <p class="text-sm text-white">
                            {{ order.tracking_company }} ·
                            <span class="text-[#c9a84c]">{{ order.tracking_number }}</span>
                          </p>
                          <a
                            v-if="order.tracking_url"
                            :href="order.tracking_url"
                            target="_blank"
                            rel="noopener"
                            class="inline-block mt-1 text-xs text-[#c9a84c] border border-[#c9a84c]/30 px-3 py-1 hover:bg-[#c9a84c]/10 transition-colors"
                          >
                            {{ $t('account.track_package') }} →
                          </a>
                        </div>
                      </td>
                    </tr>
                  </template>
                  <tr v-if="orders.length === 0">
                    <td colspan="4" class="py-8 text-center text-aroma-muted text-xs">Sin pedidos aún</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Orders Tab -->
          <div v-if="activeTab === 'orders'" class="space-y-4">
            <h3 class="text-lg text-white font-light">{{ $t('account.orders') }}</h3>
            <div v-if="loadingOrders" class="animate-pulse space-y-3">
              <div v-for="i in 3" :key="i" class="h-12 bg-aroma-surface" />
            </div>
            <div v-else-if="orders.length === 0" class="text-center py-12 text-gray-500 text-sm">
              Sin pedidos aún
            </div>
            <div v-else class="space-y-3">
              <div
                v-for="order in orders"
                :key="order.id"
                class="border border-gray-800 p-4"
              >
                <div class="flex items-center justify-between gap-4">
                  <div class="min-w-0">
                    <p class="text-sm text-gray-300">#{{ order.order_number }}</p>
                    <p class="text-xs text-gray-500 mt-1">{{ formatDate(order.created_at) }}</p>
                  </div>
                  <div class="flex items-center gap-3 shrink-0">
                    <span class="text-sm text-aroma-text">${{ order.total.toFixed(2) }}</span>
                    <span :class="statusClass(order.status)" class="text-xs">{{ statusLabel(order.status) }}</span>
                  </div>
                </div>
                <div v-if="order.tracking_number" class="mt-3 bg-blue-900/10 border border-blue-500/20 rounded p-3">
                  <p class="text-xs tracking-widest text-gray-400 mb-1 uppercase">{{ $t('account.tracking') }}</p>
                  <p class="text-sm text-white">
                    {{ order.tracking_company }} ·
                    <span class="text-[#c9a84c]">{{ order.tracking_number }}</span>
                  </p>
                  <a
                    v-if="order.tracking_url"
                    :href="order.tracking_url"
                    target="_blank"
                    rel="noopener"
                    class="inline-block mt-1 text-xs text-[#c9a84c] border border-[#c9a84c]/30 px-3 py-1 hover:bg-[#c9a84c]/10 transition-colors"
                  >
                    {{ $t('account.track_package') }} →
                  </a>
                </div>
                <button
                  v-if="order.status === 'delivered'"
                  @click="openReturnForm(order.id)"
                  class="text-xs text-gray-400 border border-gray-700 px-3 py-1 hover:border-gray-500 hover:text-white transition-colors mt-2 inline-block"
                >
                  {{ $t('account.request_return') }}
                </button>
              </div>
            </div>
          </div>

          <!-- Addresses Tab -->
          <div v-if="activeTab === 'addresses'" class="space-y-4">
            <div class="flex items-center justify-between">
              <h3 class="text-lg text-white font-light">{{ $t('account.my_addresses') }}</h3>
              <button
                @click="openNewAddress"
                class="flex items-center gap-2 text-sm text-[#c9a84c] border border-[#c9a84c]/30 px-4 py-2 hover:bg-[#c9a84c]/10 transition-colors"
              >
                + {{ $t('account.add_address') }}
              </button>
            </div>

            <div v-if="addressLoading" class="text-center py-8 text-gray-500 text-sm">{{ $t('common.loading') }}</div>
            <div v-else-if="addresses.length === 0" class="text-center py-12 text-gray-500 text-sm">
              {{ $t('account.no_addresses') }}
            </div>
            <div v-else class="grid gap-3 sm:grid-cols-2">
              <div
                v-for="addr in addresses"
                :key="addr.id"
                class="border rounded p-4 space-y-2"
                :class="addr.is_default ? 'border-[#c9a84c]/50 bg-[#c9a84c]/5' : 'border-gray-800'"
              >
                <div class="flex items-start justify-between gap-2">
                  <div>
                    <span class="text-xs tracking-widest text-gray-400 uppercase">{{ addr.label }}</span>
                    <span v-if="addr.is_default" class="ml-2 text-xs text-[#c9a84c]">★ {{ $t('account.default') }}</span>
                  </div>
                  <div class="flex gap-2 shrink-0">
                    <button @click="openEditAddress(addr)" class="text-xs text-gray-400 hover:text-white transition-colors">{{ $t('common.edit') }}</button>
                    <button @click="deleteAddress(addr.id)" class="text-xs text-gray-400 hover:text-red-400 transition-colors">{{ $t('common.delete') }}</button>
                  </div>
                </div>
                <p v-if="addr.first_name || addr.last_name" class="text-sm text-gray-300">{{ addr.first_name }} {{ addr.last_name }}</p>
                <p class="text-sm text-gray-400 leading-relaxed">
                  {{ addr.address }}<br>
                  {{ addr.city }}<span v-if="addr.state">, {{ addr.state }}</span> {{ addr.postal_code }}<br>
                  {{ addr.country }}
                </p>
                <p v-if="addr.phone" class="text-xs text-gray-500">{{ addr.phone }}</p>
                <button
                  v-if="!addr.is_default"
                  @click="setDefaultAddress(addr.id)"
                  class="text-xs text-[#c9a84c]/70 hover:text-[#c9a84c] transition-colors"
                >
                  {{ $t('account.set_default') }}
                </button>
              </div>
            </div>

            <!-- Address form modal -->
            <div
              v-if="showAddressForm"
              class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 px-4"
              @click.self="showAddressForm = false"
            >
              <div class="bg-[#111] border border-gray-800 p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto">
                <h3 class="text-white font-light mb-6">
                  {{ editingAddress ? $t('account.edit_address') : $t('account.new_address') }}
                </h3>
                <form @submit.prevent="saveAddress" class="space-y-4">
                  <div>
                    <label class="block text-xs tracking-widest text-gray-400 mb-1 uppercase">{{ $t('account.address_label') }}</label>
                    <input v-model="addressForm.label" type="text" required
                      class="w-full bg-transparent border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none"/>
                  </div>
                  <div class="grid grid-cols-2 gap-3">
                    <div>
                      <label class="block text-xs tracking-widest text-gray-400 mb-1 uppercase">{{ $t('checkout.first_name') }}</label>
                      <input v-model="addressForm.first_name" type="text"
                        class="w-full bg-transparent border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none"/>
                    </div>
                    <div>
                      <label class="block text-xs tracking-widest text-gray-400 mb-1 uppercase">{{ $t('checkout.last_name') }}</label>
                      <input v-model="addressForm.last_name" type="text"
                        class="w-full bg-transparent border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none"/>
                    </div>
                  </div>
                  <div>
                    <label class="block text-xs tracking-widest text-gray-400 mb-1 uppercase">{{ $t('checkout.address') }}</label>
                    <input v-model="addressForm.address" type="text" required
                      class="w-full bg-transparent border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none"/>
                  </div>
                  <div class="grid grid-cols-2 gap-3">
                    <div>
                      <label class="block text-xs tracking-widest text-gray-400 mb-1 uppercase">{{ $t('checkout.city') }}</label>
                      <input v-model="addressForm.city" type="text" required
                        class="w-full bg-transparent border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none"/>
                    </div>
                    <div>
                      <label class="block text-xs tracking-widest text-gray-400 mb-1 uppercase">{{ $t('account.state') }}</label>
                      <input v-model="addressForm.state" type="text"
                        class="w-full bg-transparent border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none"/>
                    </div>
                  </div>
                  <div class="grid grid-cols-2 gap-3">
                    <div>
                      <label class="block text-xs tracking-widest text-gray-400 mb-1 uppercase">{{ $t('checkout.postal_code') }}</label>
                      <input v-model="addressForm.postal_code" type="text" required
                        class="w-full bg-transparent border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none"/>
                    </div>
                    <div>
                      <label class="block text-xs tracking-widest text-gray-400 mb-1 uppercase">{{ $t('checkout.country') }}</label>
                      <input v-model="addressForm.country" type="text" required
                        class="w-full bg-transparent border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none"/>
                    </div>
                  </div>
                  <div>
                    <label class="block text-xs tracking-widest text-gray-400 mb-1 uppercase">{{ $t('account.phone') }}</label>
                    <input v-model="addressForm.phone" type="text"
                      class="w-full bg-transparent border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none"/>
                  </div>
                  <label class="flex items-center gap-2 text-sm text-gray-400 cursor-pointer">
                    <input v-model="addressForm.is_default" type="checkbox" class="accent-[#c9a84c]"/>
                    {{ $t('account.set_as_default') }}
                  </label>
                  <div class="flex gap-3 pt-2">
                    <button type="submit"
                      class="flex-1 bg-[#c9a84c] text-black py-3 text-sm tracking-widest hover:bg-[#b8943e] transition-colors">
                      {{ $t('common.save') }}
                    </button>
                    <button type="button" @click="showAddressForm = false"
                      class="px-6 border border-gray-700 text-gray-400 text-sm hover:border-gray-500 transition-colors">
                      {{ $t('common.cancel') }}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
          <!-- Returns tab -->
          <div v-if="activeTab === 'returns'" class="space-y-4">
            <h3 class="text-lg text-white font-light">{{ $t('account.my_returns') }}</h3>

            <div v-if="returns.length === 0" class="text-center py-12 text-gray-500 text-sm">
              {{ $t('account.no_returns') }}
            </div>
            <div v-else class="space-y-3">
              <div
                v-for="ret in returns"
                :key="ret.id"
                class="border border-gray-800 p-4 flex items-center justify-between gap-4"
              >
                <div class="min-w-0">
                  <p class="text-sm text-gray-300">Pedido #{{ ret.order_id }} · {{ ret.reason }}</p>
                  <p class="text-xs text-gray-500 mt-1">{{ formatDate(ret.created_at) }}</p>
                </div>
                <span
                  class="text-xs px-2 py-1 shrink-0 rounded-sm"
                  :class="{
                    'bg-yellow-500/20 text-yellow-400': ret.status === 'pending',
                    'bg-green-500/20 text-green-400': ret.status === 'approved' || ret.status === 'refunded',
                    'bg-red-500/20 text-red-400': ret.status === 'rejected',
                    'bg-blue-500/20 text-blue-400': ret.status === 'shipped',
                  }"
                >
                  {{ returnStatusLabel(ret.status) }}
                </span>
              </div>
            </div>

            <!-- Return request modal -->
            <div
              v-if="showReturnForm"
              class="fixed inset-0 bg-black/80 flex items-center justify-center z-50 px-4"
              @click.self="showReturnForm = false"
            >
              <div class="bg-[#111] border border-gray-800 p-6 w-full max-w-md">
                <h3 class="text-white font-light mb-6">{{ $t('account.request_return') }}</h3>
                <form @submit.prevent="submitReturn" class="space-y-4">
                  <div>
                    <label class="block text-xs text-gray-400 mb-1 uppercase tracking-widest">{{ $t('returns.reason') }}</label>
                    <select v-model="returnForm.reason" required
                      class="w-full bg-[#0a0a0a] border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none">
                      <option value="" disabled>{{ $t('returns.select_reason') }}</option>
                      <option v-for="r in returnReasons" :key="r" :value="r">{{ r }}</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-xs text-gray-400 mb-1 uppercase tracking-widest">{{ $t('returns.comments') }} ({{ $t('common.optional') }})</label>
                    <textarea v-model="returnForm.comments" rows="3"
                      class="w-full bg-[#0a0a0a] border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none resize-none"
                    ></textarea>
                  </div>
                  <div class="flex gap-3">
                    <button type="submit"
                      class="flex-1 bg-[#c9a84c] text-black py-3 text-sm tracking-widest hover:bg-[#b8943e] transition-colors">
                      {{ $t('account.submit_return') }}
                    </button>
                    <button type="button" @click="showReturnForm = false"
                      class="px-5 border border-gray-700 text-gray-400 text-sm hover:border-gray-500 transition-colors">
                      {{ $t('common.cancel') }}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
    <Footer />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Header from '../components/layout/Header.vue'
import Footer from '../components/layout/Footer.vue'
import { useAuthStore } from '../stores/auth'
import api from '../router/api'

const router = useRouter()
const auth = useAuthStore()
const { t } = useI18n()

const activeTab = ref('profile')
const orders = ref([])
const loadingOrders = ref(false)

// Address management
const addresses = ref([])
const addressLoading = ref(false)
const showAddressForm = ref(false)
const editingAddress = ref(null)
const addressForm = ref({
  label: 'Casa',
  first_name: '',
  last_name: '',
  phone: '',
  address: '',
  city: '',
  state: '',
  postal_code: '',
  country: '',
  is_default: false
})

async function loadAddresses() {
  addressLoading.value = true
  try {
    const { data } = await api.get('/users/me/addresses')
    addresses.value = data
  } catch {
    addresses.value = []
  } finally {
    addressLoading.value = false
  }
}

function openNewAddress() {
  editingAddress.value = null
  addressForm.value = {
    label: 'Casa', first_name: '', last_name: '', phone: '',
    address: '', city: '', state: '', postal_code: '', country: '', is_default: false
  }
  showAddressForm.value = true
}

function openEditAddress(addr) {
  editingAddress.value = addr
  addressForm.value = { ...addr }
  showAddressForm.value = true
}

async function saveAddress() {
  try {
    if (editingAddress.value) {
      await api.put(`/users/me/addresses/${editingAddress.value.id}`, addressForm.value)
    } else {
      await api.post('/users/me/addresses', addressForm.value)
    }
    showAddressForm.value = false
    await loadAddresses()
  } catch (e) {
    alert(e.response?.data?.detail || 'Error guardando dirección')
  }
}

async function deleteAddress(id) {
  if (!confirm(t('account.confirm_delete_address'))) return
  try {
    await api.delete(`/users/me/addresses/${id}`)
    await loadAddresses()
  } catch (e) {
    alert(e.response?.data?.detail || 'Error eliminando dirección')
  }
}

async function setDefaultAddress(id) {
  try {
    await api.put(`/users/me/addresses/${id}/default`)
    await loadAddresses()
  } catch (e) {
    alert(e.response?.data?.detail || 'Error')
  }
}

// Returns
const returns = ref([])
const showReturnForm = ref(false)
const returnOrderId = ref(null)
const returnForm = ref({ reason: '', comments: '' })
const returnReasons = [
  'Producto dañado',
  'No coincide con la descripción',
  'Cambio de opinión',
  'Producto incorrecto recibido',
  'Calidad insatisfactoria',
]

async function loadReturns() {
  try {
    const { data } = await api.get('/returns/my-returns')
    returns.value = data
  } catch {
    returns.value = []
  }
}

function openReturnForm(orderId) {
  returnOrderId.value = orderId
  returnForm.value = { reason: '', comments: '' }
  showReturnForm.value = true
}

async function submitReturn() {
  try {
    await api.post('/returns', {
      order_id: returnOrderId.value,
      reason: returnForm.value.reason,
      comments: returnForm.value.comments,
    })
    showReturnForm.value = false
    await loadReturns()
    alert(t('account.return_submitted'))
  } catch (e) {
    alert(e.response?.data?.detail || t('common.error'))
  }
}

function returnStatusLabel(status) {
  const map = {
    pending: t('returns.status_pending'),
    approved: t('returns.status_approved'),
    rejected: t('returns.status_rejected'),
    shipped: t('returns.status_shipped'),
    refunded: t('returns.status_refunded'),
  }
  return map[status] || status
}

const lastOrder = computed(() => orders.value[0] || null)

const menuItems = [
  { tab: 'profile', i18n: 'account.profile', icon: 'span' },
  { tab: 'orders', i18n: 'account.orders', icon: 'span' },
  { tab: 'addresses', i18n: 'account.addresses', icon: 'span' },
  { tab: 'returns', i18n: 'account.my_returns', icon: 'span' },
  { tab: 'payment', i18n: 'account.payment', icon: 'span' },
  { tab: 'wishlist', i18n: 'account.wishlist', icon: 'span' },
]

function formatDate(d) {
  return new Date(d).toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric' })
}

function statusLabel(s) {
  const map = { shipped: 'En camino', delivered: 'Entregado', pending: 'Pendiente', processing: 'Procesando' }
  return map[s] || s
}

function statusClass(s) {
  if (s === 'shipped' || s === 'processing') return 'text-gold text-xs'
  if (s === 'delivered') return 'text-aroma-muted text-xs'
  return 'text-aroma-muted text-xs'
}

async function handleLogout() {
  await auth.logout()
  router.push('/')
}

onMounted(async () => {
  loadingOrders.value = true
  try {
    const { data } = await api.get('/orders/my-orders', { params: { per_page: 10 } })
    orders.value = data.items
  } catch {
    // not authenticated
  } finally {
    loadingOrders.value = false
  }
  await loadAddresses()
  await loadReturns()
})
</script>
