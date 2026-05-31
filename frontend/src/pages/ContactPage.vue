<template>
  <div class="min-h-screen bg-white">
    <Header />
    <div class="pt-36 max-w-3xl mx-auto px-6 pb-24">
      <h1 class="font-display text-5xl text-[#1a1a1a] mb-4">Contacto</h1>
      <p class="text-gray-500 mb-12">Estamos aquí para ayudarte con cualquier consulta sobre fragancias.</p>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-12">

        <!-- Formulario -->
        <form @submit.prevent="handleSubmit" class="space-y-4">

          <!-- Éxito -->
          <div v-if="success" class="bg-green-50 border border-green-200 p-4 text-sm text-green-800">
            ✓ Mensaje enviado. Te responderemos en 24–48 horas hábiles.
          </div>

          <!-- Error -->
          <div v-if="error" class="bg-red-50 border border-red-200 p-4 text-sm text-red-700">
            {{ error }}
          </div>

          <input
            v-model="form.name"
            :disabled="success"
            required
            minlength="2"
            class="w-full border border-gray-300 text-[#1a1a1a] placeholder-gray-400 bg-white px-4 py-3 text-sm
                   focus:outline-none focus:border-[#c9a84c] transition-colors duration-200 disabled:opacity-50"
            placeholder="Tu nombre" />

          <input
            v-model="form.email"
            type="email"
            :disabled="success"
            required
            class="w-full border border-gray-300 text-[#1a1a1a] placeholder-gray-400 bg-white px-4 py-3 text-sm
                   focus:outline-none focus:border-[#c9a84c] transition-colors duration-200 disabled:opacity-50"
            placeholder="tu@email.com" />

          <input
            v-model="form.subject"
            :disabled="success"
            class="w-full border border-gray-300 text-[#1a1a1a] placeholder-gray-400 bg-white px-4 py-3 text-sm
                   focus:outline-none focus:border-[#c9a84c] transition-colors duration-200 disabled:opacity-50"
            placeholder="Asunto (opcional)" />

          <textarea
            v-model="form.message"
            :disabled="success"
            required
            minlength="10"
            class="w-full border border-gray-300 text-[#1a1a1a] placeholder-gray-400 bg-white px-4 py-3 text-sm
                   focus:outline-none focus:border-[#c9a84c] transition-colors duration-200 h-32 resize-none disabled:opacity-50"
            placeholder="¿En qué podemos ayudarte?" />

          <button
            type="submit"
            :disabled="loading || success"
            class="btn-gold w-full py-4 disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            <span v-if="loading" class="w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin"></span>
            {{ loading ? 'Enviando...' : success ? 'Mensaje enviado ✓' : 'Enviar Mensaje' }}
          </button>
        </form>

        <!-- Info de contacto -->
        <div class="space-y-8">
          <div>
            <p class="text-[10px] tracking-widest uppercase text-[#c9a84c] mb-2">Email</p>
            <p class="text-gray-600 text-sm">aromadistribuido@gmail.com</p>
          </div>
          <div>
            <p class="text-[10px] tracking-widest uppercase text-[#c9a84c] mb-2">WhatsApp</p>
            <p class="text-gray-600 text-sm">+57 300 000 0000</p>
          </div>
          <div>
            <p class="text-[10px] tracking-widest uppercase text-[#c9a84c] mb-2">Horario</p>
            <p class="text-gray-600 text-sm">Lunes – Viernes, 9am – 6pm (COT)</p>
          </div>
        </div>

      </div>
    </div>
    <Footer />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Header from '../components/layout/Header.vue'
import Footer from '../components/layout/Footer.vue'
import api from '../router/api'

const form = ref({ name: '', email: '', subject: 'Consulta general', message: '' })
const loading = ref(false)
const success = ref(false)
const error = ref('')

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    await api.post('/contact', form.value)
    success.value = true
    form.value = { name: '', email: '', subject: 'Consulta general', message: '' }
  } catch (e) {
    error.value = e.response?.data?.detail || 'Error al enviar el mensaje. Inténtalo de nuevo.'
  } finally {
    loading.value = false
  }
}
</script>
