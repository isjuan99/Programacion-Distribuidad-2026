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

      <!-- OAuth Buttons -->
      <div class="mt-6">
        <OAuthButtons @error="oauthError = $event" />
        <p v-if="oauthError" class="text-red-400 text-sm text-center mt-2">{{ oauthError }}</p>
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
import OAuthButtons from '../components/auth/OAuthButtons.vue'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const { t } = useI18n()

const form = ref({ email: '', password: '', remember: false })
const showPassword = ref(false)
const loading = ref(false)
const error = ref('')
const oauthError = ref('')
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
