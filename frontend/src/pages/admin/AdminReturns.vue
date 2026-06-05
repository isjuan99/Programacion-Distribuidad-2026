<template>
  <AdminSidebar>
  <div class="p-6 lg:p-8 max-w-7xl mx-auto">
    <div class="mb-8">
      <h1 class="text-2xl font-light tracking-widest text-[#111010]">{{ $t('admin.returns') }}</h1>
      <p class="text-gray-500 text-sm mt-1">{{ $t('admin.returns_subtitle') }}</p>
    </div>

    <!-- Filtros de estado -->
    <div class="flex gap-1 mb-6 border-b border-gray-200 overflow-x-auto">
      <button v-for="tab in statusTabs" :key="tab.value"
        @click="activeStatus = tab.value; loadReturns()"
        class="px-4 py-2 text-sm transition-colors shrink-0"
        :class="activeStatus === tab.value
          ? 'text-[#c9a84c] border-b-2 border-[#c9a84c]'
          : 'text-gray-500 hover:text-gray-700'">
        {{ tab.label }}
      </button>
    </div>

    <div v-if="loading" class="text-center py-16 text-gray-500 text-sm">{{ $t('common.loading') }}</div>

    <!-- Tabla -->
    <div v-else-if="returns.length" class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-gray-200 bg-gray-50">
            <th class="text-left py-3 px-4 text-xs tracking-widest text-gray-500 font-normal">ID</th>
            <th class="text-left py-3 px-4 text-xs tracking-widest text-gray-500 font-normal">Pedido</th>
            <th class="text-left py-3 px-4 text-xs tracking-widest text-gray-500 font-normal">Motivo</th>
            <th class="text-left py-3 px-4 text-xs tracking-widest text-gray-500 font-normal">Fotos</th>
            <th class="text-left py-3 px-4 text-xs tracking-widest text-gray-500 font-normal">Guía</th>
            <th class="text-left py-3 px-4 text-xs tracking-widest text-gray-500 font-normal">Estado</th>
            <th class="text-left py-3 px-4 text-xs tracking-widest text-gray-500 font-normal">Fecha</th>
            <th class="text-left py-3 px-4 text-xs tracking-widest text-gray-500 font-normal">Acción</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="ret in returns" :key="ret.id" class="hover:bg-gray-50 transition-colors">
            <td class="py-3 px-4 text-[#111010] font-medium">#{{ ret.id }}</td>
            <td class="py-3 px-4 text-[#111010] font-medium">#{{ ret.order_id }}</td>
            <td class="py-3 px-4 text-gray-700 max-w-[160px] truncate">{{ ret.reason }}</td>
            <td class="py-3 px-4">
              <div v-if="ret.images?.length" class="flex gap-1">
                <img v-for="(img, i) in ret.images.slice(0, 3)" :key="i"
                  :src="img" class="w-10 h-10 object-cover border border-gray-300 rounded-sm cursor-pointer hover:border-[#c9a84c] transition-colors"
                  @click="lightboxImg = img" />
              </div>
              <span v-else class="text-gray-400 text-xs">—</span>
            </td>
            <td class="py-3 px-4">
              <span v-if="ret.tracking_number" class="font-mono text-xs text-blue-600">{{ ret.tracking_number }}</span>
              <span v-else class="text-gray-400 text-xs">—</span>
            </td>
            <td class="py-3 px-4">
              <span class="text-xs px-2 py-1 rounded-sm"
                :class="{
                  'bg-yellow-100 text-yellow-700': ret.status === 'pending',
                  'bg-green-100 text-green-700':   ret.status === 'approved',
                  'bg-red-100 text-red-700':        ret.status === 'rejected',
                  'bg-blue-100 text-blue-700':      ret.status === 'shipped',
                  'bg-amber-100 text-amber-700':    ret.status === 'received',
                  'bg-[#c9a84c]/15 text-[#a07830]': ret.status === 'refunded',
                }">
                {{ statusLabel(ret.status) }}
              </span>
            </td>
            <td class="py-3 px-4 text-gray-600 text-xs">{{ formatDate(ret.created_at) }}</td>
            <td class="py-3 px-4">
              <button @click="openReturn(ret)"
                class="text-xs text-[#c9a84c] border border-[#c9a84c]/40 px-3 py-1 hover:bg-[#c9a84c]/10 transition-colors">
                Gestionar
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else class="text-center py-16 text-gray-500 text-sm">{{ $t('admin.no_returns') }}</div>

    <!-- Modal de gestión -->
    <div v-if="selectedReturn" class="fixed inset-0 bg-black/80 flex items-center justify-center z-50 px-4"
      @click.self="selectedReturn = null">
      <div class="bg-[#111] border border-gray-800 p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-white font-light text-lg">Devolución #{{ selectedReturn.id }}</h3>
          <button @click="selectedReturn = null" class="text-gray-500 hover:text-white text-xl leading-none">×</button>
        </div>

        <!-- Info del cliente -->
        <div class="space-y-4 mb-6">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-xs text-gray-500 mb-1 uppercase tracking-widest">Motivo</p>
              <p class="text-sm text-gray-200">{{ selectedReturn.reason }}</p>
            </div>
            <div>
              <p class="text-xs text-gray-500 mb-1 uppercase tracking-widest">Pedido</p>
              <p class="text-sm text-gray-200">#{{ selectedReturn.order_id }}</p>
            </div>
          </div>
          <div v-if="selectedReturn.comments">
            <p class="text-xs text-gray-500 mb-1 uppercase tracking-widest">Comentarios</p>
            <p class="text-sm text-gray-400 leading-relaxed">{{ selectedReturn.comments }}</p>
          </div>
          <div v-if="selectedReturn.tracking_number">
            <p class="text-xs text-gray-500 mb-1 uppercase tracking-widest">Número de guía</p>
            <p class="text-sm font-mono text-blue-400">{{ selectedReturn.tracking_number }}</p>
          </div>
          <!-- Fotos -->
          <div v-if="selectedReturn.images?.length">
            <p class="text-xs text-gray-500 mb-2 uppercase tracking-widest">Fotos del cliente</p>
            <div class="flex gap-2 flex-wrap">
              <img v-for="(img, i) in selectedReturn.images" :key="i"
                :src="img" class="w-20 h-20 object-cover border border-gray-700 rounded-sm cursor-pointer hover:border-[#c9a84c] transition-colors"
                @click="lightboxImg = img" />
            </div>
          </div>
        </div>

        <!-- Formulario de actualización -->
        <form @submit.prevent="updateReturnStatus" class="space-y-4 border-t border-gray-800 pt-5">
          <!-- Estado -->
          <div>
            <label class="block text-xs text-gray-400 mb-1 uppercase tracking-widest">Actualizar estado</label>
            <select v-model="statusForm.status"
              class="w-full bg-[#0a0a0a] border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none">
              <option value="pending">Pendiente</option>
              <option value="approved">Aprobada</option>
              <option value="rejected">Rechazada</option>
              <option value="shipped">Enviada por cliente</option>
              <option value="received">Recibida</option>
              <option value="refunded">Reembolsada</option>
            </select>
          </div>

          <!-- Notas del admin -->
          <div>
            <label class="block text-xs text-gray-400 mb-1 uppercase tracking-widest">Notas para el cliente</label>
            <textarea v-model="statusForm.admin_notes" rows="2"
              class="w-full bg-[#0a0a0a] border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none resize-none"
              placeholder="Mensaje que verá el cliente..."></textarea>
          </div>

          <!-- Instrucciones de envío (cuando se aprueba) -->
          <div v-if="statusForm.status === 'approved'" class="border border-[#c9a84c]/20 bg-[#c9a84c]/5 p-4 space-y-3">
            <p class="text-xs text-[#c9a84c] uppercase tracking-widest font-medium">Instrucciones de envío</p>
            <div class="flex gap-3">
              <label class="flex items-center gap-1.5 cursor-pointer text-xs text-gray-300">
                <input type="checkbox" v-model="statusForm.include_address" class="accent-[#c9a84c]" />
                Dar dirección
              </label>
              <label class="flex items-center gap-1.5 cursor-pointer text-xs text-gray-300">
                <input type="checkbox" v-model="statusForm.include_label" class="accent-[#c9a84c]" />
                Subir etiqueta
              </label>
            </div>
            <div v-if="statusForm.include_address">
              <label class="block text-xs text-gray-400 mb-1">Dirección de devolución</label>
              <textarea v-model="statusForm.return_address" rows="3"
                class="w-full bg-[#0a0a0a] border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none resize-none"
                placeholder="Calle 123 #45-67&#10;Bogotá, Colombia&#10;CP: 110111"/>
            </div>
            <div v-if="statusForm.include_label">
              <label class="block text-xs text-gray-400 mb-1">URL de la etiqueta prepagada</label>
              <input v-model="statusForm.return_label_url" type="url"
                class="w-full bg-[#0a0a0a] border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none"
                placeholder="https://..." />
            </div>
          </div>

          <!-- Tipo de reembolso (cuando se reembolsa) -->
          <div v-if="statusForm.status === 'refunded'" class="border border-[#c9a84c]/20 bg-[#c9a84c]/5 p-4 space-y-3">
            <p class="text-xs text-[#c9a84c] uppercase tracking-widest font-medium">Tipo de reembolso</p>
            <div class="flex gap-4">
              <label v-for="opt in refundTypes" :key="opt.value"
                class="flex items-center gap-1.5 cursor-pointer text-xs text-gray-300">
                <input type="radio" :value="opt.value" v-model="statusForm.refund_type" class="accent-[#c9a84c]" />
                {{ opt.label }}
              </label>
            </div>
            <div>
              <label class="block text-xs text-gray-400 mb-1">Monto a reembolsar (COP)</label>
              <input v-model="statusForm.refund_amount" type="number" step="1000"
                class="w-full bg-[#0a0a0a] border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none"
                placeholder="0" />
            </div>
            <p v-if="statusForm.refund_type === 'points' && statusForm.refund_amount"
              class="text-xs text-[#c9a84c]">
              = {{ Math.floor(statusForm.refund_amount / 10) }} puntos de lealtad
            </p>
          </div>

          <button type="submit"
            class="w-full bg-[#c9a84c] text-black py-3 text-sm tracking-widest hover:bg-[#b8943e] transition-colors font-medium">
            Guardar cambios
          </button>
        </form>
      </div>
    </div>

    <!-- Lightbox fotos -->
    <div v-if="lightboxImg" class="fixed inset-0 bg-black/90 flex items-center justify-center z-[60]"
      @click="lightboxImg = null">
      <img :src="lightboxImg" class="max-w-full max-h-[90vh] object-contain" @click.stop />
      <button @click="lightboxImg = null" class="absolute top-4 right-4 text-white hover:text-[#c9a84c] text-2xl">×</button>
    </div>
  </div>
  </AdminSidebar>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import AdminSidebar from '../../components/layout/AdminSidebar.vue'
import api from '../../router/api'

const { t } = useI18n()
const returns = ref([])
const loading = ref(false)
const selectedReturn = ref(null)
const activeStatus = ref('')
const lightboxImg = ref(null)

const statusForm = ref({
  status: 'pending',
  admin_notes: '',
  refund_amount: null,
  return_label_url: '',
  return_address: '',
  refund_type: 'card',
  include_address: false,
  include_label: false,
})

const refundTypes = [
  { value: 'card',     label: 'Tarjeta' },
  { value: 'points',   label: 'Puntos' },
  { value: 'exchange', label: 'Cambio' },
]

const statusTabs = [
  { label: 'Todos',        value: '' },
  { label: 'Pendientes',   value: 'pending' },
  { label: 'Aprobadas',    value: 'approved' },
  { label: 'Rechazadas',   value: 'rejected' },
  { label: 'En camino',    value: 'shipped' },
  { label: 'Recibidas',    value: 'received' },
  { label: 'Reembolsadas', value: 'refunded' },
]

function statusLabel(status) {
  return {
    pending:  'Pendiente',
    approved: 'Aprobada',
    rejected: 'Rechazada',
    shipped:  'En camino',
    received: 'Recibida',
    refunded: 'Reembolsada',
  }[status] || status
}

async function loadReturns() {
  loading.value = true
  try {
    const params = activeStatus.value ? `?status=${activeStatus.value}` : ''
    const { data } = await api.get(`/returns${params}`)
    returns.value = data
  } catch {
    returns.value = []
  } finally {
    loading.value = false
  }
}

function openReturn(ret) {
  selectedReturn.value = ret
  statusForm.value = {
    status:         ret.status,
    admin_notes:    ret.admin_notes || '',
    refund_amount:  ret.refund_amount ?? null,
    return_label_url: ret.return_label_url || '',
    return_address: ret.return_address || '',
    refund_type:    ret.refund_type || 'card',
    include_address: !!ret.return_address,
    include_label:   !!ret.return_label_url,
  }
}

async function updateReturnStatus() {
  try {
    const payload = {
      status:      statusForm.value.status,
      admin_notes: statusForm.value.admin_notes || null,
      refund_amount:    statusForm.value.refund_amount || null,
      refund_type:      statusForm.value.status === 'refunded' ? statusForm.value.refund_type : null,
      return_address:   statusForm.value.include_address ? statusForm.value.return_address : null,
      return_label_url: statusForm.value.include_label   ? statusForm.value.return_label_url : null,
    }
    await api.put(`/returns/${selectedReturn.value.id}/status`, payload)
    selectedReturn.value = null
    await loadReturns()
  } catch (e) {
    alert(e.response?.data?.detail || t('common.error'))
  }
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('es-CO', { year: 'numeric', month: 'short', day: 'numeric' })
}

onMounted(loadReturns)
</script>
