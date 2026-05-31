<template>
  <AdminSidebar>
    <div class="p-8">
      <h1 class="font-display text-3xl text-aroma-dark mb-2">Analíticas</h1>
      <p class="text-gray-400 text-sm mb-8">Reportes de ventas e ingresos.</p>

      <div v-if="stats" class="space-y-8">
        <!-- KPIs -->
        <div class="grid grid-cols-4 gap-4">
          <div class="bg-white border border-gray-100 p-5 rounded-sm text-center">
            <p class="text-[10px] tracking-widest uppercase text-gray-400 mb-2">Ingresos Totales</p>
            <p class="font-display text-3xl text-aroma-dark">${{ (stats.total_revenue/1000).toFixed(1) }}k</p>
          </div>
          <div class="bg-white border border-gray-100 p-5 rounded-sm text-center">
            <p class="text-[10px] tracking-widest uppercase text-gray-400 mb-2">Este Mes</p>
            <p class="font-display text-3xl text-aroma-dark">${{ (stats.month_revenue/1000).toFixed(1) }}k</p>
            <p class="text-xs mt-1" :class="stats.revenue_growth >= 0 ? 'text-green-500' : 'text-red-400'">
              {{ stats.revenue_growth >= 0 ? '+' : '' }}{{ stats.revenue_growth }}% vs anterior
            </p>
          </div>
          <div class="bg-white border border-gray-100 p-5 rounded-sm text-center">
            <p class="text-[10px] tracking-widest uppercase text-gray-400 mb-2">Pedidos</p>
            <p class="font-display text-3xl text-aroma-dark">{{ stats.total_orders }}</p>
          </div>
          <div class="bg-white border border-gray-100 p-5 rounded-sm text-center">
            <p class="text-[10px] tracking-widest uppercase text-gray-400 mb-2">Clientes</p>
            <p class="font-display text-3xl text-aroma-dark">{{ stats.total_customers }}</p>
          </div>
        </div>

        <!-- Revenue chart -->
        <div class="bg-white border border-gray-100 p-6 rounded-sm">
          <h3 class="text-sm font-medium text-aroma-dark mb-6">Ingresos mensuales</h3>
          <div class="flex items-end gap-4 h-48">
            <div v-for="m in stats.monthly_revenue" :key="m.month" class="flex-1 flex flex-col items-center gap-2">
              <span class="text-xs text-gray-400">${{ m.revenue.toLocaleString() }}</span>
              <div class="w-full bg-gold/20 rounded-sm overflow-hidden"
                :style="{ height: Math.max(8, (m.revenue / maxRevenue) * 180) + 'px' }">
                <div class="h-full bg-gold rounded-sm" />
              </div>
              <span class="text-xs text-gray-500 tracking-wider">{{ m.month }}</span>
            </div>
          </div>
        </div>

        <!-- Top products table -->
        <div class="bg-white border border-gray-100 p-6 rounded-sm">
          <h3 class="text-sm font-medium text-aroma-dark mb-4">Top 5 Productos por Ingresos</h3>
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-gray-100">
                <th class="text-left pb-3 text-[10px] tracking-widest uppercase text-gray-400 font-normal">#</th>
                <th class="text-left pb-3 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Producto</th>
                <th class="text-left pb-3 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Unidades</th>
                <th class="text-left pb-3 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Ingresos</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(p, i) in stats.top_products" :key="p.name" class="border-b border-gray-50">
                <td class="py-3 text-gray-400">{{ i + 1 }}</td>
                <td class="py-3 text-aroma-dark">{{ p.name }}</td>
                <td class="py-3 text-gray-600">{{ p.units }}</td>
                <td class="py-3 text-gold font-medium">${{ p.revenue.toLocaleString() }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-else class="animate-pulse space-y-4">
        <div class="grid grid-cols-4 gap-4">
          <div v-for="i in 4" :key="i" class="h-24 bg-gray-100 rounded-sm" />
        </div>
        <div class="h-64 bg-gray-100 rounded-sm" />
      </div>
    </div>
  </AdminSidebar>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AdminSidebar from '../../components/layout/AdminSidebar.vue'
import api from '../../router/api'

const stats = ref(null)

const maxRevenue = computed(() =>
  stats.value ? Math.max(...stats.value.monthly_revenue.map(m => m.revenue), 1) : 1
)

onMounted(async () => {
  const { data } = await api.get('/reports/dashboard')
  stats.value = data
})
</script>
