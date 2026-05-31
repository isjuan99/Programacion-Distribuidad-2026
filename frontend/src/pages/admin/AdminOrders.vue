<template>
  <AdminSidebar>
    <div class="p-8">
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="font-display text-3xl text-aroma-dark">{{ $t('admin.order_management') }}</h1>
          <p class="text-gray-400 text-sm mt-1">{{ $t('admin.manage_orders') }}</p>
        </div>
        <div class="flex gap-2">
          <button class="border border-gray-200 px-4 py-2 text-xs tracking-widest uppercase text-gray-600 hover:border-gray-400">
            {{ $t('admin.filter') }}
          </button>
          <div class="relative">
            <button
              @click="showExportMenu = !showExportMenu"
              class="flex items-center gap-2 border border-gray-700 text-gray-300 px-4 py-2 text-sm hover:border-gray-500 transition-colors"
            >
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
              </svg>
              {{ $t('admin.export') }}
            </button>
            <div v-if="showExportMenu" class="absolute right-0 top-full mt-1 bg-[#111] border border-gray-800 w-40 z-20 shadow-xl">
              <button @click="exportOrders('csv')" class="w-full text-left px-4 py-3 text-sm text-gray-300 hover:bg-white/5 transition-colors">CSV</button>
              <button @click="exportOrders('excel')" class="w-full text-left px-4 py-3 text-sm text-gray-300 hover:bg-white/5 transition-colors">Excel (.xlsx)</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Status tabs -->
      <div class="flex gap-0 mb-6 border-b border-gray-100">
        <button v-for="tab in statusTabs" :key="tab.value"
          @click="activeStatus = tab.value"
          class="px-5 py-3 text-xs tracking-widest uppercase transition-colors"
          :class="activeStatus === tab.value
            ? 'border-b-2 border-gold text-aroma-dark'
            : 'text-gray-400 hover:text-aroma-dark'">
          {{ tab.label }}
        </button>
      </div>

      <div class="bg-white border border-gray-100 rounded-sm overflow-hidden">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-gray-100 bg-gray-50">
              <th class="text-left p-4 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Order</th>
              <th class="text-left p-4 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Cliente</th>
              <th class="text-left p-4 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Fecha</th>
              <th class="text-left p-4 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Total</th>
              <th class="text-left p-4 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Envío</th>
              <th class="text-left p-4 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Estado</th>
              <th class="p-4" />
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="7" class="p-8 text-center text-gray-400">Cargando...</td>
            </tr>
            <tr v-else v-for="order in orders" :key="order.id"
              class="border-b border-gray-50 hover:bg-gray-50 cursor-pointer"
              @click="selectedOrder = order">
              <td class="p-4 font-mono text-xs text-aroma-dark">#{{ order.order_number }}</td>
              <td class="p-4">
                <p class="text-aroma-dark">{{ order.shipping_first_name }} {{ order.shipping_last_name }}</p>
                <p class="text-xs text-gray-400">{{ order.shipping_email }}</p>
              </td>
              <td class="p-4 text-gray-600 text-xs">{{ formatDate(order.created_at) }}</td>
              <td class="p-4 text-aroma-dark">${{ order.total.toFixed(2) }}</td>
              <td class="p-4">
                <span class="text-xs text-gray-500">{{ order.shipping_method === 'express' ? 'Express' : 'Estándar' }}</span>
              </td>
              <td class="p-4">
                <span :class="statusClass(order.status)" class="text-[10px] px-2 py-1 rounded-full">
                  {{ order.status }}
                </span>
              </td>
              <td class="p-4">
                <button @click.stop="selectedOrder = order" class="text-xs text-gray-400 hover:text-gold">Ver →</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Order detail panel -->
    <transition name="slide">
      <div v-if="selectedOrder"
        class="fixed inset-y-0 right-0 w-[400px] bg-white border-l border-gray-200 z-50 overflow-y-auto shadow-2xl">
        <div class="p-6">
          <div class="flex justify-between items-center mb-6">
            <h2 class="font-display text-xl text-aroma-dark">#{{ selectedOrder.order_number }}</h2>
            <button @click="selectedOrder = null">
              <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>

          <!-- Status update -->
          <div class="mb-6">
            <label class="text-xs text-gray-500 block mb-2">Actualizar estado</label>
            <div class="flex gap-2">
              <select v-model="newStatus"
                class="flex-1 border border-gray-200 text-aroma-dark px-3 py-2 text-xs bg-white focus:outline-none">
                <option value="pending">Pendiente</option>
                <option value="processing">Procesando</option>
                <option value="shipped">Enviado</option>
                <option value="delivered">Entregado</option>
                <option value="cancelled">Cancelado</option>
              </select>
              <button @click="updateStatus"
                class="bg-gold text-aroma-dark px-4 py-2 text-xs tracking-widest uppercase hover:bg-gold-light">
                OK
              </button>
            </div>
          </div>

          <!-- Shipping info -->
          <div class="bg-gray-50 p-4 mb-4 text-sm">
            <p class="text-xs text-gray-400 mb-2 uppercase tracking-wider">Envío a</p>
            <p class="text-aroma-dark">{{ selectedOrder.shipping_first_name }} {{ selectedOrder.shipping_last_name }}</p>
            <p class="text-gray-500 text-xs">{{ selectedOrder.shipping_email }}</p>
            <p class="text-gray-500 text-xs">{{ selectedOrder.shipping_address }}, {{ selectedOrder.shipping_city }}</p>
            <p class="text-gray-500 text-xs">{{ selectedOrder.shipping_postal_code }}, {{ selectedOrder.shipping_country }}</p>
          </div>

          <!-- Items -->
          <div class="space-y-3 mb-4">
            <div v-for="item in selectedOrder.items" :key="item.id"
              class="flex justify-between items-start text-sm">
              <div>
                <p class="text-aroma-dark">{{ item.product_name }}</p>
                <p class="text-xs text-gray-400">{{ item.size_ml }}ml × {{ item.quantity }}</p>
              </div>
              <span class="text-aroma-dark">${{ item.total_price.toFixed(2) }}</span>
            </div>
          </div>

          <!-- Totals -->
          <div class="border-t border-gray-100 pt-4 space-y-2 text-sm">
            <div class="flex justify-between text-gray-500">
              <span>Subtotal</span><span>${{ selectedOrder.subtotal.toFixed(2) }}</span>
            </div>
            <div class="flex justify-between text-gray-500">
              <span>Envío</span><span>${{ selectedOrder.shipping_cost.toFixed(2) }}</span>
            </div>
            <div class="flex justify-between text-gray-500">
              <span>IVA</span><span>${{ selectedOrder.tax.toFixed(2) }}</span>
            </div>
            <div class="flex justify-between font-medium text-aroma-dark pt-2 border-t border-gray-100">
              <span>Total</span><span>${{ selectedOrder.total.toFixed(2) }}</span>
            </div>
          </div>

          <!-- Tracking form (admin) -->
          <div class="mt-4 pt-4 border-t border-gray-200">
            <h4 class="text-xs tracking-widest text-gray-500 uppercase mb-3">{{ $t('admin.tracking_info') }}</h4>
            <div class="grid grid-cols-2 gap-3 mb-3">
              <div>
                <label class="block text-xs text-gray-500 mb-1">{{ $t('admin.tracking_company') }}</label>
                <select v-model="trackingForm.tracking_company" @change="onCompanyChange"
                  class="w-full bg-white border border-gray-300 text-gray-800 px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none">
                  <option value="">Seleccionar...</option>
                  <option v-for="c in carriers" :key="c.name" :value="c.name">{{ c.name }}</option>
                </select>
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">{{ $t('admin.tracking_number') }}</label>
                <input v-model="trackingForm.tracking_number" type="text" placeholder="Ej: 1Z9999999999"
                  class="w-full bg-white border border-gray-300 text-gray-800 px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none"/>
              </div>
            </div>
            <div class="mb-3">
              <label class="block text-xs text-gray-500 mb-1">{{ $t('admin.tracking_url') }}</label>
              <input v-model="trackingForm.tracking_url" type="url" placeholder="https://..."
                class="w-full bg-white border border-gray-300 text-gray-800 px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none"/>
            </div>
            <button
              @click="saveTracking(selectedOrder?.id)"
              :disabled="!trackingForm.tracking_number || !trackingForm.tracking_company"
              class="bg-[#c9a84c] text-black px-6 py-2 text-sm tracking-widest hover:bg-[#b8943e] transition-colors disabled:opacity-50"
            >
              {{ $t('admin.save_tracking') }}
            </button>
          </div>
        </div>
      </div>
    </transition>
    <div v-if="selectedOrder" @click="selectedOrder = null" class="fixed inset-0 bg-black/20 z-40" />
  </AdminSidebar>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import AdminSidebar from '../../components/layout/AdminSidebar.vue'
import api from '../../router/api'

const { t } = useI18n()

const orders = ref([])
const loading = ref(false)
const selectedOrder = ref(null)
const newStatus = ref('')
const activeStatus = ref('all')

const showExportMenu = ref(false)
const exportLoading = ref(false)

const trackingForm = ref({ tracking_number: '', tracking_company: '', tracking_url: '' })

const carriers = [
  { name: 'FedEx',        url: 'https://www.fedex.com/es-co/home.html' },
  { name: 'Servientrega', url: 'https://servientregainternacional.com/Forms/Rastreo' },
  { name: 'UPS',          url: 'https://www.ups.com/track?loc=es_CO&requester=ST/' },
  { name: 'DHL',          url: 'https://www.dhl.com/co-es/home/rastreo.html' },
  { name: 'Coordinadora', url: 'https://coordinadora.com/rastreo/rastreo-de-guia/detalle-de-rastreo-de-guia/' },
  { name: 'Envia',        url: 'https://envia.co/' },
]

function onCompanyChange() {
  const carrier = carriers.find(c => c.name === trackingForm.value.tracking_company)
  trackingForm.value.tracking_url = carrier ? carrier.url : ''
}

const statusTabs = [
  { value: 'all', label: 'Todos' },
  { value: 'pending', label: 'Pendientes' },
  { value: 'processing', label: 'Procesando' },
  { value: 'shipped', label: 'Enviados' },
  { value: 'delivered', label: 'Entregados' },
]

watch(selectedOrder, (o) => {
  if (o) {
    newStatus.value = o.status
    trackingForm.value = {
      tracking_number: o.tracking_number || '',
      tracking_company: o.tracking_company || '',
      tracking_url: o.tracking_url || ''
    }
  }
})

async function exportOrders(format) {
  showExportMenu.value = false
  try {
    const statusFilter = activeStatus.value !== 'all' ? activeStatus.value : ''
    const params = `format=${format}${statusFilter ? `&status=${statusFilter}` : ''}`
    const response = await api.get(`/orders/export?${params}`, { responseType: 'blob' })
    const today = new Date().toISOString().split('T')[0].replace(/-/g, '')
    const filename = `ordenes_aroma_${today}.${format === 'excel' ? 'xlsx' : 'csv'}`
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  } catch {
    alert(t('admin.export_error'))
  }
}

async function saveTracking(orderId) {
  try {
    await api.put(`/orders/${orderId}/tracking`, trackingForm.value)
    trackingForm.value = { tracking_number: '', tracking_company: '', tracking_url: '' }
    await load()
    alert(t('admin.tracking_saved') || 'Tracking guardado y email enviado al cliente')
  } catch (e) {
    alert(e.response?.data?.detail || t('common.error'))
  }
}

function formatDate(d) {
  return new Date(d).toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric' })
}

function statusClass(s) {
  const map = {
    pending: 'bg-yellow-50 text-yellow-700',
    processing: 'bg-blue-50 text-blue-700',
    shipped: 'bg-gold/10 text-gold-dark',
    delivered: 'bg-green-50 text-green-700',
    cancelled: 'bg-red-50 text-red-500',
  }
  return map[s] || 'bg-gray-100 text-gray-500'
}

async function updateStatus() {
  if (!selectedOrder.value) return
  await api.patch(`/orders/${selectedOrder.value.id}/status`, { status: newStatus.value })
  selectedOrder.value.status = newStatus.value
  await load()
}

async function load() {
  loading.value = true
  try {
    const params = { per_page: 50 }
    if (activeStatus.value !== 'all') params.status = activeStatus.value
    const { data } = await api.get('/orders', { params })
    orders.value = data.items
  } finally {
    loading.value = false
  }
}

watch(activeStatus, () => load())
onMounted(() => load())
</script>

<style scoped>
.slide-enter-active, .slide-leave-active { transition: transform 0.3s ease; }
.slide-enter-from, .slide-leave-to { transform: translateX(100%); }
</style>
