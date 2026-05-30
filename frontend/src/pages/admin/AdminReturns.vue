<template>
  <div class="p-6 lg:p-8 max-w-7xl mx-auto">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-2xl font-light tracking-widest text-white">{{ $t('admin.returns') }}</h1>
      <p class="text-gray-500 text-sm mt-1">{{ $t('admin.returns_subtitle') }}</p>
    </div>

    <!-- Status filter tabs -->
    <div class="flex gap-1 mb-6 border-b border-gray-800 overflow-x-auto">
      <button
        v-for="tab in statusTabs"
        :key="tab.value"
        @click="activeStatus = tab.value; loadReturns()"
        class="px-4 py-2 text-sm transition-colors shrink-0"
        :class="activeStatus === tab.value
          ? 'text-[#c9a84c] border-b-2 border-[#c9a84c]'
          : 'text-gray-500 hover:text-gray-300'"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-16 text-gray-500 text-sm">{{ $t('common.loading') }}</div>

    <!-- Returns table -->
    <div v-else-if="returns.length" class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-gray-800">
            <th class="text-left py-3 px-4 text-xs tracking-widest text-gray-400 font-normal">ID</th>
            <th class="text-left py-3 px-4 text-xs tracking-widest text-gray-400 font-normal">{{ $t('admin.order') }}</th>
            <th class="text-left py-3 px-4 text-xs tracking-widest text-gray-400 font-normal">{{ $t('admin.reason') }}</th>
            <th class="text-left py-3 px-4 text-xs tracking-widest text-gray-400 font-normal">{{ $t('admin.status') }}</th>
            <th class="text-left py-3 px-4 text-xs tracking-widest text-gray-400 font-normal">{{ $t('common.date') }}</th>
            <th class="text-left py-3 px-4 text-xs tracking-widest text-gray-400 font-normal">{{ $t('common.actions') }}</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-800">
          <tr v-for="ret in returns" :key="ret.id" class="hover:bg-white/2 transition-colors">
            <td class="py-3 px-4 text-gray-400">#{{ ret.id }}</td>
            <td class="py-3 px-4 text-gray-300">{{ $t('admin.order') }} #{{ ret.order_id }}</td>
            <td class="py-3 px-4 text-gray-300 max-w-xs truncate">{{ ret.reason }}</td>
            <td class="py-3 px-4">
              <span
                class="text-xs px-2 py-1 rounded-sm"
                :class="{
                  'bg-yellow-500/20 text-yellow-400': ret.status === 'pending',
                  'bg-green-500/20 text-green-400': ret.status === 'approved' || ret.status === 'refunded',
                  'bg-red-500/20 text-red-400': ret.status === 'rejected',
                  'bg-blue-500/20 text-blue-400': ret.status === 'shipped',
                }"
              >
                {{ statusLabel(ret.status) }}
              </span>
            </td>
            <td class="py-3 px-4 text-gray-500 text-xs">{{ formatDate(ret.created_at) }}</td>
            <td class="py-3 px-4">
              <button
                @click="openReturn(ret)"
                class="text-xs text-[#c9a84c] border border-[#c9a84c]/30 px-3 py-1 hover:bg-[#c9a84c]/10 transition-colors"
              >
                {{ $t('common.review') }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else class="text-center py-16 text-gray-500 text-sm">{{ $t('admin.no_returns') }}</div>

    <!-- Review modal -->
    <div
      v-if="selectedReturn"
      class="fixed inset-0 bg-black/80 flex items-center justify-center z-50 px-4"
      @click.self="selectedReturn = null"
    >
      <div class="bg-[#111] border border-gray-800 p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-white font-light">{{ $t('returns.return_details') }} #{{ selectedReturn.id }}</h3>
          <button @click="selectedReturn = null" class="text-gray-500 hover:text-white text-xl leading-none">×</button>
        </div>

        <div class="space-y-4 mb-6">
          <div>
            <p class="text-xs text-gray-500 mb-1 uppercase tracking-widest">{{ $t('returns.reason') }}</p>
            <p class="text-sm text-gray-200">{{ selectedReturn.reason }}</p>
          </div>
          <div v-if="selectedReturn.comments">
            <p class="text-xs text-gray-500 mb-1 uppercase tracking-widest">{{ $t('returns.comments') }}</p>
            <p class="text-sm text-gray-400 leading-relaxed">{{ selectedReturn.comments }}</p>
          </div>
          <div v-if="selectedReturn.images?.length" class="flex gap-2 flex-wrap">
            <img
              v-for="(img, i) in selectedReturn.images"
              :key="i"
              :src="img"
              class="w-20 h-20 object-cover border border-gray-700"
            />
          </div>
        </div>

        <form @submit.prevent="updateReturnStatus" class="space-y-4 border-t border-gray-800 pt-4">
          <div>
            <label class="block text-xs text-gray-400 mb-1 uppercase tracking-widest">{{ $t('admin.update_status') }}</label>
            <select
              v-model="statusForm.status"
              class="w-full bg-[#0a0a0a] border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none"
            >
              <option value="pending">{{ $t('returns.status_pending') }}</option>
              <option value="approved">{{ $t('returns.status_approved') }}</option>
              <option value="rejected">{{ $t('returns.status_rejected') }}</option>
              <option value="shipped">{{ $t('returns.status_shipped') }}</option>
              <option value="refunded">{{ $t('returns.status_refunded') }}</option>
            </select>
          </div>
          <div>
            <label class="block text-xs text-gray-400 mb-1 uppercase tracking-widest">{{ $t('admin.admin_notes') }}</label>
            <textarea
              v-model="statusForm.admin_notes"
              rows="3"
              class="w-full bg-[#0a0a0a] border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none resize-none"
              :placeholder="$t('admin.notes_placeholder')"
            ></textarea>
          </div>
          <div v-if="statusForm.status === 'refunded'">
            <label class="block text-xs text-gray-400 mb-1 uppercase tracking-widest">{{ $t('returns.refund_amount') }}</label>
            <input
              v-model="statusForm.refund_amount"
              type="number"
              step="0.01"
              class="w-full bg-[#0a0a0a] border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none"
            />
          </div>
          <button
            type="submit"
            class="w-full bg-[#c9a84c] text-black py-3 text-sm tracking-widest hover:bg-[#b8943e] transition-colors"
          >
            {{ $t('admin.save_status') }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '../../router/api'

const { t } = useI18n()
const returns = ref([])
const loading = ref(false)
const selectedReturn = ref(null)
const activeStatus = ref('')
const statusForm = ref({ status: 'pending', admin_notes: '', refund_amount: null })

const statusTabs = [
  { label: t('common.all'), value: '' },
  { label: t('returns.status_pending'), value: 'pending' },
  { label: t('returns.status_approved'), value: 'approved' },
  { label: t('returns.status_rejected'), value: 'rejected' },
  { label: t('returns.status_refunded'), value: 'refunded' },
]

function statusLabel(status) {
  const map = {
    pending: t('returns.status_pending'),
    approved: t('returns.status_approved'),
    rejected: t('returns.status_rejected'),
    shipped: t('returns.status_shipped'),
    refunded: t('returns.status_refunded'),
  }
  return map[status] || status
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
    status: ret.status,
    admin_notes: ret.admin_notes || '',
    refund_amount: ret.refund_amount || null
  }
}

async function updateReturnStatus() {
  try {
    await api.put(`/returns/${selectedReturn.value.id}/status`, statusForm.value)
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
