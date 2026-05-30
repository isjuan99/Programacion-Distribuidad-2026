<template>
  <div class="min-h-screen bg-aroma-dark flex items-center justify-center relative overflow-hidden">
    <!-- Blurred BG image slot -->
    <div class="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1541643600914-78b084683702?w=1600')]
      bg-cover bg-center opacity-20 blur-sm scale-105" />
    <div class="absolute inset-0 bg-aroma-dark/60" />

    <!-- Card -->
    <div class="relative z-10 w-full max-w-sm mx-4 bg-aroma-text rounded-sm p-10 shadow-2xl">
      <!-- Logo -->
      <div class="text-center mb-8">
        <h1 class="font-display text-2xl tracking-ultra text-aroma-dark">AROMA</h1>
      </div>

      <h2 class="font-display text-xl text-aroma-dark text-center mb-2">{{ $t('auth.login_title') }}</h2>
      <p class="text-aroma-muted text-xs text-center mb-8 leading-relaxed px-4">{{ $t('auth.login_subtitle') }}</p>

      <form @submit.prevent="handleLogin" class="space-y-4">
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

        <!-- Password -->
        <div class="relative">
          <span class="absolute left-4 top-1/2 -translate-y-1/2 text-aroma-muted">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
            </svg>
          </span>
          <input v-model="form.password" :type="showPassword ? 'text' : 'password'" required
            class="w-full border border-gray-200 text-aroma-dark placeholder-gray-400 pl-10 pr-10 py-3 text-sm
                   focus:outline-none focus:border-gold-dark transition-colors"
            :placeholder="$t('auth.password')" />
          <button type="button" @click="showPassword = !showPassword"
            class="absolute right-4 top-1/2 -translate-y-1/2 text-aroma-muted hover:text-gold-dark">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path v-if="showPassword" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
          </button>
        </div>

        <!-- Remember + Forgot -->
        <div class="flex items-center justify-between text-xs">
          <label class="flex items-center gap-2 text-aroma-muted cursor-pointer">
            <input type="checkbox" v-model="form.remember" class="accent-gold-dark" />
            {{ $t('auth.remember_me') }}
          </label>
          <router-link to="/forgot-password" class="text-aroma-muted hover:text-gold-dark transition-colors">
            {{ $t('auth.forgot_password') }}
          </router-link>
        </div>

        <!-- Error -->
        <p v-if="error" class="text-red-500 text-xs text-center">{{ error }}</p>

        <!-- Unverified email alert -->
        <div v-if="showUnverified" class="bg-amber-900/20 border border-amber-600/40 rounded p-4 text-sm space-y-2">
          <p class="text-amber-400">{{ $t('auth.email_not_verified') }}</p>
          <button
            v-if="!resendDone"
            type="button"
            :disabled="resendLoading"
            @click="handleResend"
            class="text-[#c9a84c] underline underline-offset-2 hover:text-[#b8943e] disabled:opacity-50"
          >
            {{ resendLoading ? $t('auth.resending') : $t('auth.resend_verification') }}
          </button>
          <p v-else class="text-green-400">{{ $t('auth.verification_sent') }}</p>
        </div>

        <!-- Submit -->
        <button type="submit" :disabled="loading"
          class="w-full bg-gold text-aroma-dark py-3 text-xs tracking-widest uppercase font-sans font-medium
                 hover:bg-gold-light transition-colors disabled:opacity-50">
          {{ loading ? $t('common.loading') : $t('auth.login_btn') }}
        </button>
      </form>

      <!-- Divider -->
      <div class="flex items-center gap-4 my-6">
        <hr class="flex-1 border-gray-200" />
        <span class="text-[10px] tracking-widest text-aroma-muted">{{ $t('auth.or_continue') }}</span>
        <hr class="flex-1 border-gray-200" />
      </div>

      <!-- Social -->
      <div class="grid grid-cols-2 gap-3">
        <button class="border border-gray-200 py-2.5 text-xs text-aroma-dark flex items-center justify-center gap-2
                       hover:border-gold-dark transition-colors">
          <svg class="w-4 h-4" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          {{ $t('auth.google') }}
        </button>
        <button class="border border-gray-200 py-2.5 text-xs text-aroma-dark flex items-center justify-center gap-2
                       hover:border-gold-dark transition-colors bg-aroma-dark text-aroma-text">
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
            <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.8-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/>
          </svg>
          {{ $t('auth.apple') }}
        </button>
      </div>

      <p class="text-center text-xs text-aroma-muted mt-6">
        {{ $t('auth.no_account') }}
        <router-link to="/register" class="text-gold-dark font-medium hover:underline">
          {{ $t('auth.register_link') }}
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const { t } = useI18n()

const form = ref({ email: '', password: '', remember: false })
const showPassword = ref(false)
const loading = ref(false)
const error = ref('')
const showUnverified = ref(false)
const unverifiedEmail = ref('')
const resendLoading = ref(false)
const resendDone = ref(false)

async function handleLogin() {
  error.value = ''
  showUnverified.value = false
  loading.value = true
  try {
    await auth.login(form.value.email, form.value.password)
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (e) {
    const detail = e.response?.data?.detail
    if (detail === 'EMAIL_NOT_VERIFIED') {
      showUnverified.value = true
      unverifiedEmail.value = form.value.email
    } else {
      error.value = detail || t('auth.login_error')
    }
  } finally {
    loading.value = false
  }
}

async function handleResend() {
  resendLoading.value = true
  try {
    await auth.resendVerification(unverifiedEmail.value)
    resendDone.value = true
  } finally {
    resendLoading.value = false
  }
}
</script>
