<template>
  <AdminSidebar>
    <div class="p-8">
      <div class="mb-8">
        <h1 class="font-display text-3xl text-aroma-dark">{{ $t('admin.dashboard') }}</h1>
        <p class="text-gray-400 text-sm mt-1">Vista general del negocio</p>
      </div>

      <!-- KPI Cards -->
      <div class="grid grid-cols-4 gap-4 mb-10" v-if="stats">
        <div v-for="card in kpiCards" :key="card.label"
          class="bg-white border border-gray-100 p-5 rounded-sm">
          <p class="text-[10px] tracking-widest uppercase text-gray-400 mb-2">{{ card.label }}</p>
          <p class="font-display text-3xl text-aroma-dark">{{ card.value }}</p>
          <p v-if="card.sub" class="text-xs mt-1" :class="card.subColor">{{ card.sub }}</p>
        </div>
      </div>
      <div v-else class="grid grid-cols-4 gap-4 mb-10">
        <div v-for="i in 4" :key="i" class="bg-gray-100 animate-pulse h-28 rounded-sm" />
      </div>

      <!-- Low Stock Alert -->
      <div class="mb-8">
        <div v-if="lowStockProducts.length > 0"
          class="bg-red-50 border border-red-200 rounded-sm p-5">
          <div class="flex items-center gap-2 mb-4">
            <svg class="w-5 h-5 text-red-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
            </svg>
            <h3 class="text-sm font-medium text-red-800">
              ⚠️ Productos con stock bajo: {{ lowStockProducts.length }} productos
            </h3>
          </div>
          <div class="space-y-2">
            <div v-for="p in lowStockProducts" :key="p.id"
              class="flex items-center justify-between bg-white border border-red-100 rounded px-4 py-2">
              <div>
                <span class="text-sm text-aroma-dark font-medium">{{ p.name }}</span>
                <div class="flex gap-2 mt-0.5">
                  <span v-for="v in p.variants.filter(v => v.stock < 5)" :key="v.id"
                    class="text-[10px] text-red-600">
                    {{ v.size_ml }}ml: {{ v.stock }} und{{ v.stock !== 1 ? 's' : '' }}
                  </span>
                </div>
              </div>
              <router-link to="/admin/products"
                class="text-xs text-gold hover:underline shrink-0">
                Editar →
              </router-link>
            </div>
          </div>
        </div>
        <div v-else-if="stats"
          class="bg-green-50 border border-green-200 rounded-sm px-5 py-3 flex items-center gap-2">
          <svg class="w-4 h-4 text-green-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
          </svg>
          <p class="text-sm text-green-800">✅ Todos los productos tienen stock suficiente</p>
        </div>
      </div>

      <!-- Charts row -->
      <div class="grid grid-cols-[2fr_1fr] gap-6 mb-8" v-if="stats">
        <!-- Revenue bar chart -->
        <div class="bg-white border border-gray-100 p-6 rounded-sm">
          <h3 class="text-sm font-medium text-aroma-dark mb-6">Ingresos últimos 6 meses</h3>
          <div class="flex items-end gap-3 h-40">
            <div v-for="m in stats.monthly_revenue" :key="m.month" class="flex-1 flex flex-col items-center gap-2">
              <span class="text-[10px] text-gray-400">${{ (m.revenue / 1000).toFixed(1) }}k</span>
              <div class="w-full bg-gold/20 relative overflow-hidden rounded-sm"
                :style="{ height: barHeight(m.revenue) + 'px' }">
                <div class="absolute inset-0 bg-gold rounded-sm opacity-80" />
              </div>
              <span class="text-[10px] text-gray-400 tracking-wider">{{ m.month }}</span>
            </div>
          </div>
        </div>

        <!-- Top products -->
        <div class="bg-white border border-gray-100 p-6 rounded-sm">
          <h3 class="text-sm font-medium text-aroma-dark mb-4">Top Productos</h3>
          <div class="space-y-3">
            <div v-for="(p, i) in stats.top_products" :key="p.name" class="flex items-center gap-3">
              <span class="text-[10px] text-gray-400 w-4">{{ i + 1 }}</span>
              <div class="flex-1 min-w-0">
                <p class="text-xs text-aroma-dark truncate">{{ p.name }}</p>
                <p class="text-[10px] text-gray-400">{{ p.units }} uds · ${{ p.revenue }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent orders -->
      <div class="bg-white border border-gray-100 rounded-sm p-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-sm font-medium text-aroma-dark">Pedidos Recientes</h3>
          <router-link to="/admin/orders" class="text-xs text-gold hover:underline">Ver todos →</router-link>
        </div>
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-gray-100">
              <th class="text-left pb-3 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Order ID</th>
              <th class="text-left pb-3 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Cliente</th>
              <th class="text-left pb-3 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Total</th>
              <th class="text-left pb-3 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in recentOrders" :key="order.id" class="border-b border-gray-50">
              <td class="py-3 text-aroma-dark font-mono text-xs">#{{ order.order_number }}</td>
              <td class="py-3 text-gray-600 text-xs">{{ order.shipping_first_name }} {{ order.shipping_last_name }}</td>
              <td class="py-3 text-aroma-dark">${{ order.total.toFixed(2) }}</td>
              <td class="py-3">
                <span class="text-[10px] px-2 py-1 rounded-full"
                  :class="statusClass(order.status)">
                  {{ order.status }}
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
import { ref, computed, onMounted } from 'vue'
import AdminSidebar from '../../components/layout/AdminSidebar.vue'
import api from '../../router/api'

const stats = ref(null)
const recentOrders = ref([])
const lowStockProducts = ref([])

const maxRevenue = computed(() =>
  stats.value ? Math.max(...stats.value.monthly_revenue.map(m => m.revenue), 1) : 1
)

function barHeight(revenue) {
  return Math.max(8, (revenue / maxRevenue.value) * 140)
}

const kpiCards = computed(() => {
  if (!stats.value) return []
  const growth = stats.value.revenue_growth
  return [
    {
      label: 'Ingresos Totales',
      value: `$${(stats.value.total_revenue / 1000).toFixed(1)}k`,
      sub: null,
    },
    {
      label: 'Ingresos del Mes',
      value: `$${(stats.value.month_revenue / 1000).toFixed(1)}k`,
      sub: growth >= 0 ? `+${growth}% vs mes anterior` : `${growth}% vs mes anterior`,
      subColor: growth >= 0 ? 'text-green-500' : 'text-red-400',
    },
    {
      label: 'Pedidos Totales',
      value: stats.value.total_orders,
      sub: `${stats.value.pending_orders} pendientes`,
      subColor: 'text-gold',
    },
    {
      label: 'Clientes',
      value: stats.value.total_customers,
      sub: null,
    },
  ]
})

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

onMounted(async () => {
  try {
    const [dashRes, ordersRes, productsRes] = await Promise.all([
      api.get('/reports/dashboard'),
      api.get('/orders', { params: { per_page: 5 } }),
      api.get('/products', { params: { per_page: 100 } }),
    ])
    stats.value = dashRes.data
    recentOrders.value = ordersRes.data.items ?? []
    const allProducts = productsRes.data.items ?? []
    lowStockProducts.value = allProducts.filter(p =>
      p.variants?.some(v => v.stock < 5)
    )
  } catch {
    recentOrders.value = []
    lowStockProducts.value = []
  }
})
</script>
