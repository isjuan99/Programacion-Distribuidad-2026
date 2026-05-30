<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center">
    <div class="w-full max-w-sm bg-white border border-gray-100 p-10 shadow-sm">
      <div class="text-center mb-8">
        <h1 class="font-display text-xl text-aroma-dark">Aroma-Distribuido</h1>
        <p class="text-[10px] tracking-widest uppercase text-gray-400 mt-1">Admin Console</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-4">
        <input v-model="email" type="email" required placeholder="admin@aroma.com"
          class="w-full border border-gray-200 text-aroma-dark placeholder-gray-400 px-4 py-3 text-sm
                 focus:outline-none focus:border-gold-dark" />
        <input v-model="password" type="password" required placeholder="Contraseña"
          class="w-full border border-gray-200 text-aroma-dark placeholder-gray-400 px-4 py-3 text-sm
                 focus:outline-none focus:border-gold-dark" />
        <p v-if="error" class="text-red-500 text-xs text-center">{{ error }}</p>
        <button type="submit" :disabled="loading"
          class="w-full bg-aroma-dark text-aroma-text py-3 text-xs tracking-widest uppercase hover:bg-black transition-colors disabled:opacity-50">
          {{ loading ? 'Iniciando...' : 'Iniciar sesión' }}
        </button>
      </form>

      <p class="text-center mt-6 text-xs text-gray-400">
        <router-link to="/" class="hover:underline">← Volver a la tienda</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    if (!auth.isAdmin) {
      await auth.logout()
      error.value = 'Sin permisos de administrador'
      return
    }
    auth.setAdminSession(true)
    router.push('/admin/dashboard')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Credenciales incorrectas'
  } finally {
    loading.value = false
  }
}
</script>
