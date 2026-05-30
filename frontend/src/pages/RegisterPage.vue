<template>
  <div class="min-h-screen bg-aroma-darker flex items-center justify-center py-12 px-4">
    <div class="w-full max-w-sm bg-aroma-text rounded-sm p-10 shadow-2xl">
      <div class="text-center mb-8">
        <h1 class="font-display text-2xl tracking-ultra text-aroma-dark">AROMA</h1>
      </div>

      <h2 class="font-display text-xl text-aroma-dark text-center mb-2">{{ $t('auth.register_title') }}</h2>
      <p class="text-aroma-muted text-xs text-center mb-8 leading-relaxed">{{ $t('auth.register_subtitle') }}</p>

      <!-- Success state - shown after registration -->
      <div v-if="registered" class="text-center space-y-6 py-8">
        <div class="w-20 h-20 mx-auto bg-[#c9a84c]/10 rounded-full flex items-center justify-center">
          <svg class="w-10 h-10 text-[#c9a84c]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
          </svg>
        </div>
        <h2 class="text-2xl font-light text-white">{{ $t('auth.check_email_title') }}</h2>
        <p class="text-gray-400 text-sm leading-relaxed">
          {{ $t('auth.check_email_message', { email: registeredEmail }) }}
        </p>
        <RouterLink to="/login" class="inline-block text-[#c9a84c] text-sm underline underline-offset-4">
          {{ $t('auth.back_to_login') }}
        </RouterLink>
      </div>

      <!-- Register form + OAuth (shown when not yet registered) -->
      <template v-else>
        <!-- OAuth Buttons -->
        <div class="mb-6">
          <OAuthButtons @error="oauthError = $event" />
          <p v-if="oauthError" class="text-red-400 text-sm text-center mt-2">{{ oauthError }}</p>
        </div>

        <form @submit.prevent="handleRegister" class="space-y-3">
        <div class="grid grid-cols-2 gap-3">
          <div class="relative">
            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-aroma-muted">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
            </span>
            <input v-model="form.first_name" type="text" required
              class="w-full border border-gray-200 text-aroma-dark placeholder-gray-400 pl-9 pr-3 py-3 text-sm
                     focus:outline-none focus:border-gold-dark transition-colors"
              :placeholder="$t('auth.first_name')" />
          </div>
          <div class="relative">
            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-aroma-muted">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
            </span>
            <input v-model="form.last_name" type="text" required
              class="w-full border border-gray-200 text-aroma-dark placeholder-gray-400 pl-9 pr-3 py-3 text-sm
                     focus:outline-none focus:border-gold-dark transition-colors"
              :placeholder="$t('auth.last_name')" />
          </div>
        </div>

        <!-- Email -->
        <div class="relative">
          <span class="absolute left-4 top-1/2 -translate-y-1/2 text-aroma-muted">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
            </svg>
          </span>
          <input v-model="form.email" type="email" required
            class="w-full border border-gray-200 text-aroma-dark placeholder-gray-400 pl-10 pr-4 py-3 text-sm
                   focus:outline-none focus:border-gold-dark transition-colors"
            :placeholder="$t('auth.email')" />
        </div>

        <!-- Phone -->
        <div class="relative">
          <span class="absolute left-4 top-1/2 -translate-y-1/2 text-aroma-muted">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
            </svg>
          </span>
          <input v-model="form.phone" type="tel"
            class="w-full border border-gray-200 text-aroma-dark placeholder-gray-400 pl-10 pr-4 py-3 text-sm
                   focus:outline-none focus:border-gold-dark transition-colors"
            :placeholder="$t('auth.phone')" />
        </div>

        <!-- Password -->
        <div class="relative">
          <span class="absolute left-4 top-1/2 -translate-y-1/2 text-aroma-muted">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
            </svg>
          </span>
          <input v-model="form.password" :type="showPwd ? 'text' : 'password'" required
            class="w-full border border-gray-200 text-aroma-dark placeholder-gray-400 pl-10 pr-10 py-3 text-sm
                   focus:outline-none focus:border-gold-dark transition-colors"
            :placeholder="$t('auth.password')" />
          <button type="button" @click="showPwd = !showPwd"
            class="absolute right-4 top-1/2 -translate-y-1/2 text-aroma-muted">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
            </svg>
          </button>
        </div>

        <!-- Password strength bar -->
        <div v-if="form.password" class="flex gap-1 h-1">
          <div v-for="i in 4" :key="i"
            class="flex-1 rounded-full transition-colors"
            :class="passwordStrength >= i ? strengthColor : 'bg-gray-200'" />
        </div>

        <!-- Confirm -->
        <div class="relative">
          <span class="absolute left-4 top-1/2 -translate-y-1/2 text-aroma-muted">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
            </svg>
          </span>
          <input v-model="form.confirm" :type="showConfirm ? 'text' : 'password'" required
            class="w-full border border-gray-200 text-aroma-dark placeholder-gray-400 pl-10 pr-10 py-3 text-sm
                   focus:outline-none focus:border-gold-dark transition-colors"
            :placeholder="$t('auth.confirm_password')" />
          <button type="button" @click="showConfirm = !showConfirm"
            class="absolute right-4 top-1/2 -translate-y-1/2 text-aroma-muted">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
            </svg>
          </button>
        </div>

        <!-- Checkboxes -->
        <label class="flex items-start gap-2 text-xs text-aroma-muted cursor-pointer">
          <input type="checkbox" v-model="form.terms" required class="mt-0.5 accent-gold-dark" />
          <span>
            {{ $t('auth.terms_accept') }}
            <router-link to="/terms" class="underline">{{ $t('auth.terms') }}</router-link>
            {{ $t('auth.and') }}
            <router-link to="/privacy" class="underline">{{ $t('auth.privacy') }}</router-link>
          </span>
        </label>
        <label class="flex items-center gap-2 text-xs text-aroma-muted cursor-pointer">
          <input type="checkbox" v-model="form.newsletter" class="accent-gold-dark" />
          {{ $t('auth.newsletter') }}
        </label>

        <p v-if="error" class="text-red-500 text-xs text-center">{{ error }}</p>

        <button type="submit" :disabled="loading"
          class="w-full bg-gold text-aroma-dark py-3 text-xs tracking-widest uppercase font-sans font-medium
                 hover:bg-gold-light transition-colors disabled:opacity-50">
          {{ loading ? $t('common.loading') : $t('auth.register_btn') }}
        </button>
      </form>
      </template>

      <p class="text-center text-xs text-aroma-muted mt-6">
        {{ $t('auth.have_account') }}
        <router-link to="/login" class="font-bold text-aroma-dark hover:underline">
          {{ $t('auth.login_link') }}
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import OAuthButtons from '../components/auth/OAuthButtons.vue'

const auth = useAuthStore()

const form = ref({
  first_name: '', last_name: '', email: '', phone: '',
  password: '', confirm: '', terms: false, newsletter: false,
})
const showPwd = ref(false)
const showConfirm = ref(false)
const loading = ref(false)
const error = ref('')
const oauthError = ref('')
const registered = ref(false)
const registeredEmail = ref('')

const passwordStrength = computed(() => {
  const p = form.value.password
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

async function handleRegister() {
  error.value = ''
  if (form.value.password !== form.value.confirm) {
    error.value = 'Las contraseñas no coinciden'
    return
  }
  loading.value = true
  try {
    await auth.register({
      first_name: form.value.first_name,
      last_name: form.value.last_name,
      email: form.value.email,
      phone: form.value.phone || undefined,
      password: form.value.password,
    })
    registeredEmail.value = form.value.email
    registered.value = true
  } catch (e) {
    error.value = e.response?.data?.detail || 'Error al crear la cuenta'
  } finally {
    loading.value = false
  }
}
</script>
