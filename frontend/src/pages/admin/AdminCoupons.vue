<template>
  <AdminSidebar>
    <div class="p-8">
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="font-display text-3xl text-aroma-dark">Cupones</h1>
          <p class="text-gray-400 text-sm mt-1">Descuentos y códigos promocionales.</p>
        </div>
        <button @click="showCreate = true"
          class="bg-gold text-aroma-dark px-5 py-2.5 text-xs tracking-widest uppercase hover:bg-gold-light">
          + Cupón
        </button>
      </div>

      <div class="bg-white border border-gray-100 rounded-sm overflow-hidden mb-6">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-gray-100 bg-gray-50">
              <th class="text-left p-4 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Código</th>
              <th class="text-left p-4 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Tipo</th>
              <th class="text-left p-4 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Valor</th>
              <th class="text-left p-4 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Usos</th>
              <th class="text-left p-4 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in coupons" :key="c.id" class="border-b border-gray-50">
              <td class="p-4 font-mono text-sm text-aroma-dark">{{ c.code }}</td>
              <td class="p-4 text-gray-600">{{ c.discount_type === 'percentage' ? 'Porcentaje' : 'Fijo' }}</td>
              <td class="p-4 text-gold">{{ c.discount_type === 'percentage' ? c.discount_value + '%' : '$' + c.discount_value }}</td>
              <td class="p-4 text-gray-500">{{ c.used_count }}{{ c.max_uses ? ' / ' + c.max_uses : '' }}</td>
              <td class="p-4">
                <span :class="c.is_active ? 'bg-green-50 text-green-700' : 'bg-gray-100 text-gray-500'"
                  class="text-[10px] px-2 py-1 rounded-full">
                  {{ c.is_active ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="showCreate" class="bg-white border border-gray-100 rounded-sm p-6 max-w-md">
        <h3 class="text-sm font-medium text-aroma-dark mb-4">Nuevo cupón</h3>
        <div class="space-y-3">
          <input v-model="form.code" placeholder="CÓDIGO (ej: VERANO20)" class="w-full border border-gray-200 px-3 py-2.5 text-sm font-mono text-aroma-dark focus:outline-none focus:border-gold-dark uppercase" />
          <select v-model="form.discount_type" class="w-full border border-gray-200 px-3 py-2.5 text-sm text-aroma-dark bg-white focus:outline-none">
            <option value="percentage">Porcentaje (%)</option>
            <option value="fixed">Fijo ($)</option>
          </select>
          <input v-model.number="form.discount_value" type="number" step="0.01" placeholder="Valor del descuento" class="w-full border border-gray-200 px-3 py-2.5 text-sm text-aroma-dark focus:outline-none focus:border-gold-dark" />
          <input v-model.number="form.min_order_amount" type="number" step="0.01" placeholder="Pedido mínimo ($0 = sin mínimo)" class="w-full border border-gray-200 px-3 py-2.5 text-sm text-aroma-dark focus:outline-none focus:border-gold-dark" />
          <input v-model.number="form.max_uses" type="number" placeholder="Usos máximos (vacío = ilimitado)" class="w-full border border-gray-200 px-3 py-2.5 text-sm text-aroma-dark focus:outline-none focus:border-gold-dark" />
          <div class="flex gap-3">
            <button @click="createCoupon" class="bg-gold text-aroma-dark px-5 py-2 text-xs tracking-widest uppercase hover:bg-gold-light">Crear</button>
            <button @click="showCreate = false" class="border border-gray-200 px-5 py-2 text-xs text-gray-600 hover:border-gray-400">Cancelar</button>
          </div>
        </div>
      </div>
    </div>
  </AdminSidebar>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AdminSidebar from '../../components/layout/AdminSidebar.vue'
import api from '../../router/api'

const coupons = ref([])
const showCreate = ref(false)
const form = ref({ code: '', discount_type: 'percentage', discount_value: 10, min_order_amount: 0, max_uses: null })

async function load() {
  const { data } = await api.get('/coupons')
  coupons.value = data
}

async function createCoupon() {
  await api.post('/coupons', { ...form.value, code: form.value.code.toUpperCase() })
  showCreate.value = false
  await load()
}

onMounted(load)
</script>
