<template>
  <AdminSidebar>
    <div class="p-8">
      <h1 class="font-display text-3xl text-aroma-dark mb-2">Clientes</h1>
      <p class="text-gray-400 text-sm mb-8">Gestión de usuarios registrados.</p>
      <div class="bg-white border border-gray-100 rounded-sm overflow-hidden">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-gray-100 bg-gray-50">
              <th class="text-left p-4 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Nombre</th>
              <th class="text-left p-4 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Email</th>
              <th class="text-left p-4 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Puntos</th>
              <th class="text-left p-4 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Estado</th>
              <th class="text-left p-4 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Registro</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="5" class="p-8 text-center text-gray-400">Cargando...</td>
            </tr>
            <tr v-for="u in users" :key="u.id" class="border-b border-gray-50 hover:bg-gray-50">
              <td class="p-4 text-aroma-dark">{{ u.first_name }} {{ u.last_name }}</td>
              <td class="p-4 text-gray-600">{{ u.email }}</td>
              <td class="p-4 text-gold">{{ u.loyalty_points }}</td>
              <td class="p-4">
                <span :class="u.is_active ? 'bg-green-50 text-green-700' : 'bg-gray-100 text-gray-500'"
                  class="text-[10px] px-2 py-1 rounded-full">
                  {{ u.is_active ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td class="p-4 text-gray-500 text-xs">{{ new Date(u.created_at).toLocaleDateString('es-ES') }}</td>
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

const users = ref([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const { data } = await api.get('/admin/users', { params: { per_page: 100 } })
    users.value = data.items || []
  } finally {
    loading.value = false
  }
})
</script>
