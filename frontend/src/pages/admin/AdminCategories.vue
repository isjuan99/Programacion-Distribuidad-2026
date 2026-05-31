<template>
  <AdminSidebar>
    <div class="p-8">
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="font-display text-3xl text-aroma-dark">Categorías</h1>
          <p class="text-gray-400 text-sm mt-1">Gestión de categorías del catálogo.</p>
        </div>
        <button @click="showCreate = true"
          class="bg-gold text-aroma-dark px-5 py-2.5 text-xs tracking-widest uppercase hover:bg-gold-light">
          + Categoría
        </button>
      </div>

      <div class="bg-white border border-gray-100 rounded-sm overflow-hidden mb-6">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-gray-100 bg-gray-50">
              <th class="text-left p-4 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Nombre</th>
              <th class="text-left p-4 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Slug</th>
              <th class="text-left p-4 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Productos</th>
              <th class="p-4" />
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in categories" :key="c.id" class="border-b border-gray-50 hover:bg-gray-50">
              <td class="p-4 text-aroma-dark">{{ c.name }}</td>
              <td class="p-4 text-gray-500 font-mono text-xs">{{ c.slug }}</td>
              <td class="p-4 text-gray-600">{{ c.product_count }}</td>
              <td class="p-4">
                <button @click="deleteCategory(c.id)" class="text-xs text-gray-400 hover:text-red-500">Eliminar</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Create form -->
      <div v-if="showCreate" class="bg-white border border-gray-100 rounded-sm p-6 max-w-md">
        <h3 class="text-sm font-medium text-aroma-dark mb-4">Nueva categoría</h3>
        <div class="space-y-3">
          <input v-model="newCat.name" placeholder="Nombre" class="w-full border border-gray-200 px-3 py-2.5 text-sm text-aroma-dark focus:outline-none focus:border-gold-dark" />
          <input v-model="newCat.slug" placeholder="slug-url" class="w-full border border-gray-200 px-3 py-2.5 text-sm text-aroma-dark focus:outline-none focus:border-gold-dark" />
          <input v-model="newCat.description" placeholder="Descripción (opcional)" class="w-full border border-gray-200 px-3 py-2.5 text-sm text-aroma-dark focus:outline-none focus:border-gold-dark" />
          <div class="flex gap-3">
            <button @click="createCategory" class="bg-gold text-aroma-dark px-5 py-2 text-xs tracking-widest uppercase hover:bg-gold-light">Crear</button>
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

const categories = ref([])
const showCreate = ref(false)
const newCat = ref({ name: '', slug: '', description: '' })

async function load() {
  const { data } = await api.get('/categories')
  categories.value = data
}

async function createCategory() {
  await api.post('/categories', newCat.value)
  newCat.value = { name: '', slug: '', description: '' }
  showCreate.value = false
  await load()
}

async function deleteCategory(id) {
  if (!confirm('¿Eliminar esta categoría?')) return
  await api.delete(`/categories/${id}`)
  await load()
}

onMounted(load)
</script>
