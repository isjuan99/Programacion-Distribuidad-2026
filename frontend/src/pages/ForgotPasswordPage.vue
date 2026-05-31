<template>
  <div class="min-h-screen bg-aroma-darker flex flex-col items-center justify-center px-4">
    <!-- Logo above card for reset flow -->
    <div class="text-center mb-8" v-if="isReset">
      <h1 class="font-display text-2xl tracking-ultra text-aroma-text">AROMA</h1>
      <p class="text-[10px] tracking-widest uppercase text-aroma-muted mt-1">{{ $t('auth.exclusivity') }}</p>
    </div>

    <div class="w-full max-w-sm bg-aroma-text rounded-sm p-10 shadow-2xl">
      <h2 class="font-display text-2xl text-aroma-dark text-center mb-8">
        {{ isReset ? $t('auth.reset_title') : $t('auth.forgot_title') }}
      </h2>

      <!-- Forgot password flow -->
      <template v-if="!isReset && !sent">
        <p class="text-aroma-muted text-xs text-center mb-6 leading-relaxed">
          Ingresa tu correo y te enviaremos instrucciones para restablecer tu contraseña.
        </p>
        <form @submit.prevent="handleForgot" class="space-y-4">
          <input v-model="email" type="email" required
            class="w-full border border-gray-200 text-aroma-dark placeholder-gray-400 px-4 py-3 text-sm
                   focus:outline-none focus:border-gold-dark transition-colors"
            placeholder="tu@email.com" />
          <p v-if="error" class="text-red-500 text-xs">{{ error }}</p>
          <button type="submit" :disabled="loading"
            class="w-full bg-gold text-aroma-dark py-3 text-xs tracking-widest uppercase font-sans font-medium
                   hover:bg-gold-light transition-colors disabled:opacity-50">
            {{ loading ? $t('common.loading') : 'Enviar Instrucciones' }}
          </button>
        </form>
      </template>

      <!-- Sent confirmation -->
      <template v-if="sent && !isReset">
        <div class="text-center py-4">
          <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
          </div>
          <p class="text-aroma-muted text-sm leading-relaxed">
            Revisa tu correo electrónico. Si existe una cuenta con esa dirección, recibirás instrucciones en breve.
          </p>
        </div>
      </template>

      <!-- Reset password flow -->
      <template v-if="isReset">
        <form @submit.prevent="handleReset" class="space-y-4">
          <!-- New password -->
          <div>
            <label class="text-[10px] tracking-widest uppercase text-aroma-muted block mb-2">
              {{ $t('auth.new_password') }}
            </label>
            <div class="relative">
              <input v-model="newPassword" :type="showPwd ? 'text' : 'password'" required
                class="w-full border border-gray-200 text-aroma-dark placeholder-gray-400 px-4 pr-10 py-3 text-sm
                       focus:outline-none focus:border-gold-dark transition-colors"
                placeholder="••••••••" />
              <button type="button" @click="showPwd = !showPwd"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-aroma-muted">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                </svg>
              </button>
            </div>
            <!-- Strength bar -->
            <div v-if="newPassword" class="flex gap-1 mt-1.5 h-1">
              <div v-for="i in 4" :key="i" class="flex-1 rounded-full"
                :class="passwordStrength >= i ? strengthColor : 'bg-gray-200'" />
            </div>
            <p v-if="newPassword && newPassword.length < 8" class="text-red-400 text-[10px] mt-1">
              {{ $t('auth.too_short') }}
            </p>
          </div>

          <!-- Confirm -->
          <div>
            <label class="text-[10px] tracking-widest uppercase text-aroma-muted block mb-2">
              {{ $t('auth.confirm_new_password') }}
            </label>
            <div class="relative">
              <input v-model="confirmPassword" :type="showConfirm ? 'text' : 'password'" required
                class="w-full border border-gray-200 text-aroma-dark placeholder-gray-400 px-4 pr-10 py-3 text-sm
                       focus:outline-none focus:border-gold-dark transition-colors"
                placeholder="••••••••" />
              <button type="button" @click="showConfirm = !showConfirm"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-aroma-muted">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                </svg>
              </button>
            </div>
          </div>

          <p v-if="error" class="text-red-500 text-xs">{{ error }}</p>

          <button type="submit" :disabled="loading"
            class="w-full bg-gold text-aroma-dark py-3 text-xs tracking-widest uppercase font-sans font-medium
                   hover:bg-gold-light transition-colors disabled:opacity-50">
            {{ loading ? $t('common.loading') : $t('auth.reset_btn') }}
          </button>
        </form>
      </template>
    </div>

    <router-link to="/login"
      class="mt-6 text-xs text-aroma-muted hover:text-aroma-text transition-colors">
      {{ $t('auth.back_to_login') }}
    </router-link>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const isReset = computed(() => !!route.query.token)
const email = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const showPwd = ref(false)
const showConfirm = ref(false)
const loading = ref(false)
const sent = ref(false)
const error = ref('')

const passwordStrength = computed(() => {
  const p = newPassword.value
  if (!p) return 0
  let score = 0
  if (p.length >= 8) score++
  if (/[A-Z]/.test(p)) score++
  if (/[0-9]/.test(p)) score++
  if (/[^A-Za-z0-9]/.test(p)) score++
  return score
})

const strengthColor = computed(() => {
  if (passwordStrength.value <= 1) return 'bg-red-400'
  if (passwordStrength.value === 2) return 'bg-yellow-400'
  if (passwordStrength.value === 3) return 'bg-blue-400'
  return 'bg-green-500'
})

async function handleForgot() {
  error.value = ''
  loading.value = true
  try {
    await auth.forgotPassword(email.value)
    sent.value = true
  } catch (e) {
    error.value = e.response?.data?.detail || 'Error al enviar el correo'
  } finally {
    loading.value = false
  }
}

async function handleReset() {
  error.value = ''
  if (newPassword.value !== confirmPassword.value) {
    error.value = 'Las contraseñas no coinciden'
    return
  }
  loading.value = true
  try {
    await auth.resetPassword(route.query.token, newPassword.value)
    router.push('/login')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Token inválido o expirado'
  } finally {
    loading.value = false
  }
}
</script>
