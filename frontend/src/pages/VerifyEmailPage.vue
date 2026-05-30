<template>
  <div class="min-h-screen bg-[#0a0a0a] flex items-center justify-center px-4">
    <div class="max-w-md w-full text-center">
      <div class="mb-10">
        <h1 class="text-3xl tracking-[10px] text-[#c9a84c]">AROMA</h1>
        <p class="text-xs tracking-[4px] text-gray-500 mt-1">DISTRIBUIDO</p>
      </div>

      <div v-if="state === 'loading'" class="space-y-4">
        <div class="w-16 h-16 mx-auto border-2 border-[#c9a84c] border-t-transparent rounded-full animate-spin"></div>
        <p class="text-gray-400">{{ $t('auth.verifying') }}</p>
      </div>

      <div v-else-if="state === 'success'" class="space-y-6">
        <div class="w-20 h-20 mx-auto bg-green-500/10 rounded-full flex items-center justify-center">
          <svg class="w-10 h-10 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
          </svg>
        </div>
        <h2 class="text-2xl font-light text-white">{{ $t('auth.verified_title') }}</h2>
        <p class="text-gray-400">{{ $t('auth.verified_message') }}</p>
        <RouterLink
          to="/"
          class="inline-block bg-[#c9a84c] text-black px-10 py-3 text-sm tracking-widest hover:bg-[#b8943e] transition-colors"
        >
          {{ $t('auth.go_to_shop') }}
        </RouterLink>
      </div>

      <div v-else-if="state === 'error'" class="space-y-6">
        <div class="w-20 h-20 mx-auto bg-red-500/10 rounded-full flex items-center justify-center">
          <svg class="w-10 h-10 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </div>
        <h2 class="text-2xl font-light text-white">{{ $t('auth.verify_error_title') }}</h2>
        <p class="text-gray-400">{{ $t('auth.verify_error_message') }}</p>
        <RouterLink
          to="/login"
          class="inline-block border border-[#c9a84c] text-[#c9a84c] px-10 py-3 text-sm tracking-widest hover:bg-[#c9a84c] hover:text-black transition-colors"
        >
          {{ $t('auth.back_to_login') }}
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const auth = useAuthStore()
const state = ref('loading')

onMounted(async () => {
  const token = route.query.token
  if (!token) {
    state.value = 'error'
    return
  }
  try {
    await auth.verifyEmail(token)
    state.value = 'success'
  } catch {
    state.value = 'error'
  }
})
</script>
