<template>
  <AdminSidebar>
    <div class="p-8">
      <h1 class="font-display text-3xl text-aroma-dark mb-2">Inventario</h1>
      <p class="text-gray-400 text-sm mb-8">Control de stock por variante.</p>

      <div class="bg-white border border-gray-100 rounded-sm overflow-hidden">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-gray-100 bg-gray-50">
              <th class="text-left p-4 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Producto</th>
              <th class="text-left p-4 text-[10px] tracking-widest uppercase text-gray-400 font-normal">SKU</th>
              <th class="text-left p-4 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Tamaño</th>
              <th class="text-left p-4 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Precio</th>
              <th class="text-left p-4 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Stock</th>
              <th class="text-left p-4 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="6" class="p-8 text-center text-gray-400">Cargando...</td>
            </tr>
            <tr v-for="row in inventory" :key="row.variant_id" class="border-b border-gray-50 hover:bg-gray-50">
              <td class="p-4 text-aroma-dark font-medium">{{ row.product_name }}</td>
              <td class="p-4 text-gray-500 font-mono text-xs">{{ row.sku || '—' }}</td>
              <td class="p-4 text-gray-600">{{ row.size_ml }}ml</td>
              <td class="p-4 text-aroma-dark">${{ row.price.toFixed(2) }}</td>
              <td class="p-4">
                <span :class="row.stock <= 5 ? 'text-red-500 font-medium' : 'text-aroma-dark'">
                  {{ row.stock }}
                </span>
              </td>
              <td class="p-4">
                <span :class="row.stock === 0 ? 'bg-red-50 text-red-500' : row.stock <= 5 ? 'bg-yellow-50 text-yellow-700' : 'bg-green-50 text-green-700'"
                  class="text-[10px] px-2 py-1 rounded-full">
                  {{ row.stock === 0 ? 'Agotado' : row.stock <= 5 ? 'Stock bajo' : 'Disponible' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </AdminSidebar>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AdminSidebar from '../../components/layout/AdminSidebar.vue'
import api from '../../router/api'

const inventory = ref([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const { data } = await api.get('/products', { params: { per_page: 100, status: undefined } })
    const rows = []
    for (const p of data.items) {
      for (const v of (p.variants || [])) {
        rows.push({
          variant_id: v.id,
          product_name: p.name,
          sku: v.sku,
          size_ml: v.size_ml,
          price: v.price,
          stock: v.stock,
        })
      }
    }
    inventory.value = rows.sort((a, b) => a.stock - b.stock)
  } finally {
    loading.value = false
  }
})
</script>
