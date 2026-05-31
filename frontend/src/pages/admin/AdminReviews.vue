<template>
  <AdminSidebar>
    <div class="p-8">
      <h1 class="font-display text-3xl text-aroma-dark mb-2">Reseñas</h1>
      <p class="text-gray-400 text-sm mb-8">Moderación de reseñas de productos.</p>

      <div class="flex gap-3 mb-6">
        <button @click="filter = 'pending'"
          class="px-4 py-2 text-xs tracking-widest uppercase border transition-colors"
          :class="filter === 'pending' ? 'border-gold text-gold' : 'border-gray-200 text-gray-500'">
          Pendientes
        </button>
        <button @click="filter = 'approved'"
          class="px-4 py-2 text-xs tracking-widest uppercase border transition-colors"
          :class="filter === 'approved' ? 'border-gold text-gold' : 'border-gray-200 text-gray-500'">
          Aprobadas
        </button>
      </div>

      <div class="space-y-3">
        <div v-for="r in reviews" :key="r.id" class="bg-white border border-gray-100 p-5 rounded-sm">
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <div class="flex gap-0.5">
                  <svg v-for="i in 5" :key="i" class="w-4 h-4"
                    :class="i <= r.rating ? 'text-gold fill-gold' : 'text-gray-200 fill-gray-200'"
                    viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                  </svg>
                </div>
                <span class="text-xs text-gray-400">{{ r.user_name }}</span>
                <span class="text-[10px] text-gray-400">Producto #{{ r.product_id }}</span>
              </div>
              <p v-if="r.title" class="font-medium text-aroma-dark text-sm mb-1">{{ r.title }}</p>
              <p class="text-gray-600 text-sm">{{ r.body }}</p>
            </div>
            <button v-if="!r.is_approved" @click="approve(r.id)"
              class="ml-4 bg-gold text-aroma-dark px-4 py-1.5 text-xs tracking-widest uppercase hover:bg-gold-light shrink-0">
              Aprobar
            </button>
            <span v-else class="ml-4 text-xs text-green-500 shrink-0">✓ Aprobada</span>
          </div>
        </div>
        <p v-if="reviews.length === 0" class="text-center text-gray-400 py-12">Sin reseñas {{ filter === 'pending' ? 'pendientes' : 'aprobadas' }}</p>
      </div>
    </div>
  </AdminSidebar>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import AdminSidebar from '../../components/layout/AdminSidebar.vue'
import api from '../../router/api'

const reviews = ref([])
const filter = ref('pending')

async function load() {
  const approved = filter.value === 'approved' ? true : false
  try {
    const { data } = await api.get('/admin/reviews', { params: { is_approved: approved, per_page: 50 } })
    reviews.value = data.items || []
  } catch {
    reviews.value = []
  }
}

async function approve(id) {
  await api.patch(`/reviews/${id}/approve`)
  await load()
}

watch(filter, load)
onMounted(load)
</script>
