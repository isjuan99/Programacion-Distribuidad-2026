<template>
  <AdminSidebar>
    <div class="p-8">
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="font-display text-3xl text-aroma-dark">Marcas</h1>
          <p class="text-gray-400 text-sm mt-1">Casas y marcas del catálogo.</p>
        </div>
        <button @click="showCreate = true"
          class="bg-gold text-aroma-dark px-5 py-2.5 text-xs tracking-widest uppercase hover:bg-gold-light">
          + Marca
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        <div v-for="b in brands" :key="b.id" class="bg-white border border-gray-100 p-5 rounded-sm">
          <div class="flex justify-between items-start">
            <div>
              <p class="font-medium text-aroma-dark">{{ b.name }}</p>
              <p class="text-xs text-gray-400 font-mono mt-1">{{ b.slug }}</p>
              <p class="text-xs text-gold mt-2">{{ b.product_count }} productos</p>
            </div>
            <button @click="deleteBrand(b.id)" class="text-xs text-gray-300 hover:text-red-400">✕</button>
          </div>
        </div>
      </div>

      <div v-if="showCreate" class="bg-white border border-gray-100 rounded-sm p-6 max-w-md">
        <h3 class="text-sm font-medium text-aroma-dark mb-4">Nueva marca</h3>
        <div class="space-y-3">
          <input v-model="newBrand.name" placeholder="Nombre de la marca" class="w-full border border-gray-200 px-3 py-2.5 text-sm text-aroma-dark focus:outline-none focus:border-gold-dark" />
          <input v-model="newBrand.slug" placeholder="slug-url" class="w-full border border-gray-200 px-3 py-2.5 text-sm text-aroma-dark focus:outline-none focus:border-gold-dark" />
          <input v-model="newBrand.description" placeholder="Descripción" class="w-full border border-gray-200 px-3 py-2.5 text-sm text-aroma-dark focus:outline-none focus:border-gold-dark" />
          <div class="flex gap-3">
            <button @click="createBrand" class="bg-gold text-aroma-dark px-5 py-2 text-xs tracking-widest uppercase hover:bg-gold-light">Crear</button>
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

const brands = ref([])
const showCreate = ref(false)
const newBrand = ref({ name: '', slug: '', description: '' })

async function load() {
  const { data } = await api.get('/brands')
  brands.value = data
}

async function createBrand() {
  await api.post('/brands', newBrand.value)
  newBrand.value = { name: '', slug: '', description: '' }
  showCreate.value = false
  await load()
}

async function deleteBrand(id) {
  if (!confirm('¿Eliminar esta marca?')) return
  // No delete endpoint for brands yet — extend API
}

onMounted(load)
</script>
