<template>
  <AdminSidebar>
    <div class="p-8 max-w-2xl">
      <h1 class="font-display text-3xl text-aroma-dark mb-2">Configuración</h1>
      <p class="text-gray-400 text-sm mb-10">Ajustes generales de la tienda.</p>

      <div class="space-y-8">
        <!-- Store info -->
        <section class="bg-white border border-gray-100 p-6 rounded-sm">
          <h2 class="text-sm font-medium text-aroma-dark mb-5 pb-3 border-b border-gray-100">Información de la Tienda</h2>
          <div class="space-y-4">
            <div>
              <label class="text-xs text-gray-500 block mb-2">Nombre de la tienda</label>
              <input v-model="settings.store_name" class="w-full border border-gray-200 px-3 py-2.5 text-sm text-aroma-dark focus:outline-none focus:border-gold-dark" />
            </div>
            <div>
              <label class="text-xs text-gray-500 block mb-2">Correo de contacto</label>
              <input v-model="settings.contact_email" type="email" class="w-full border border-gray-200 px-3 py-2.5 text-sm text-aroma-dark focus:outline-none focus:border-gold-dark" />
            </div>
            <div>
              <label class="text-xs text-gray-500 block mb-2">Moneda</label>
              <select v-model="settings.currency" class="w-full border border-gray-200 px-3 py-2.5 text-sm text-aroma-dark bg-white focus:outline-none">
                <option value="USD">USD — Dólar Americano</option>
                <option value="COP">COP — Peso Colombiano</option>
                <option value="EUR">EUR — Euro</option>
              </select>
            </div>
          </div>
        </section>

        <!-- Shipping -->
        <section class="bg-white border border-gray-100 p-6 rounded-sm">
          <h2 class="text-sm font-medium text-aroma-dark mb-5 pb-3 border-b border-gray-100">Envíos</h2>
          <div class="space-y-4">
            <div>
              <label class="text-xs text-gray-500 block mb-2">Monto mínimo para envío gratis ($)</label>
              <input v-model.number="settings.free_shipping_threshold" type="number" class="w-full border border-gray-200 px-3 py-2.5 text-sm text-aroma-dark focus:outline-none focus:border-gold-dark" />
            </div>
            <div>
              <label class="text-xs text-gray-500 block mb-2">Costo envío express ($)</label>
              <input v-model.number="settings.express_shipping_cost" type="number" class="w-full border border-gray-200 px-3 py-2.5 text-sm text-aroma-dark focus:outline-none focus:border-gold-dark" />
            </div>
            <div>
              <label class="text-xs text-gray-500 block mb-2">Tasa de impuesto (%)</label>
              <input v-model.number="settings.tax_rate" type="number" step="0.1" class="w-full border border-gray-200 px-3 py-2.5 text-sm text-aroma-dark focus:outline-none focus:border-gold-dark" />
            </div>
          </div>
        </section>

        <div class="flex gap-3">
          <button @click="saveSettings"
            class="bg-gold text-aroma-dark px-8 py-3 text-xs tracking-widest uppercase hover:bg-gold-light">
            Guardar Cambios
          </button>
          <span v-if="saved" class="flex items-center text-xs text-green-500">✓ Guardado</span>
        </div>
      </div>
    </div>
  </AdminSidebar>
</template>

<script setup>
import { ref } from 'vue'
import AdminSidebar from '../../components/layout/AdminSidebar.vue'

const saved = ref(false)
const settings = ref({
  store_name: 'Aroma-Distribuido',
  contact_email: 'hola@aroma-distribuido.com',
  currency: 'USD',
  free_shipping_threshold: 250,
  express_shipping_cost: 25,
  tax_rate: 8,
})

function saveSettings() {
  // Persist to backend as needed
  saved.value = true
  setTimeout(() => saved.value = false, 2000)
}
</script>
