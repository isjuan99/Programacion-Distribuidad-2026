<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="auth.authModal.show"
        class="fixed inset-0 z-[200] flex items-center justify-center px-4"
        @click.self="auth.closeAuthModal()">

        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="auth.closeAuthModal()" />

        <!-- Panel -->
        <div class="relative z-10 w-full max-w-sm bg-white rounded-sm shadow-2xl max-h-[90vh] overflow-y-auto">

          <!-- Cerrar -->
          <button @click="auth.closeAuthModal()"
            class="absolute top-4 right-4 text-gray-400 hover:text-gray-700 transition-colors p-1 z-10">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>

          <!-- Logo -->
          <div class="text-center pt-8 pb-4 px-8">
            <h1 class="font-display text-2xl tracking-ultra text-aroma-dark">AROMA</h1>
          </div>

          <!-- Tabs -->
          <div class="flex border-b border-gray-200 mx-8">
            <button @click="activeTab = 'login'; resetForms()"
              class="flex-1 py-2.5 text-xs tracking-widest uppercase transition-colors"
              :class="activeTab === 'login'
                ? 'border-b-2 border-gold text-aroma-dark font-medium'
                : 'text-gray-400 hover:text-gray-600'">
              Iniciar Sesión
            </button>
            <button @click="activeTab = 'register'; resetForms()"
              class="flex-1 py-2.5 text-xs tracking-widest uppercase transition-colors"
              :class="activeTab === 'register'
                ? 'border-b-2 border-gold text-aroma-dark font-medium'
                : 'text-gray-400 hover:text-gray-600'">
              Crear Cuenta
            </button>
          </div>

          <div class="px-8 py-6">

            <!-- ── LOGIN ─────────────────────────────── -->
            <template v-if="activeTab === 'login'">
              <form @submit.prevent="handleLogin" class="space-y-4">
                <div class="relative">
                  <span class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                        d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                    </svg>
                  </span>
                  <input v-model="loginForm.email" type="email" required
                    class="w-full border border-gray-200 text-aroma-dark placeholder-gray-400 pl-10 pr-4 py-3 text-sm focus:outline-none focus:border-gold transition-colors"
                    placeholder="Correo electrónico" />
                </div>

                <div class="relative">
                  <span class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                        d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                    </svg>
                  </span>
                  <input v-model="loginForm.password" :type="showLoginPwd ? 'text' : 'password'" required
                    class="w-full border border-gray-200 text-aroma-dark placeholder-gray-400 pl-10 pr-12 py-3 text-sm focus:outline-none focus:border-gold transition-colors"
                    placeholder="Contraseña" />
                  <button type="button" @click="showLoginPwd = !showLoginPwd"
                    class="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-gold transition-colors">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path v-if="showLoginPwd" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                        d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
                      <template v-else>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                          d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                      </template>
                    </svg>
                  </button>
                </div>

                <div class="flex items-center justify-between text-xs">
                  <label class="flex items-center gap-2 text-gray-500 cursor-pointer">
                    <input type="checkbox" v-model="loginForm.remember" class="accent-gold" />
                    Recordarme
                  </label>
                  <router-link to="/forgot-password" @click="auth.closeAuthModal()"
                    class="text-gray-400 hover:text-gold transition-colors">
                    ¿Olvidaste tu contraseña?
                  </router-link>
                </div>

                <p v-if="loginError" class="text-red-500 text-xs text-center">{{ loginError }}</p>

                <div v-if="showUnverified" class="bg-amber-50 border border-amber-200 rounded p-3 text-sm space-y-2">
                  <p class="text-amber-700 text-xs">Debes verificar tu correo antes de iniciar sesión.</p>
                  <button v-if="!resendDone" type="button" :disabled="resendLoading"
                    @click="handleResend"
                    class="text-xs text-gold underline underline-offset-2 hover:text-gold-dark disabled:opacity-50">
                    {{ resendLoading ? 'Enviando...' : 'Reenviar correo de verificación' }}
                  </button>
                  <p v-else class="text-green-600 text-xs">Correo enviado. Revisa tu bandeja.</p>
                </div>

                <button type="submit" :disabled="loginLoading"
                  class="w-full bg-gold text-aroma-dark py-3 text-xs tracking-widest uppercase font-medium hover:bg-gold-light transition-colors disabled:opacity-50">
                  {{ loginLoading ? 'Ingresando...' : 'Iniciar Sesión' }}
                </button>
              </form>

              <div class="mt-5">
                <OAuthButtons @error="oauthError = $event" />
                <p v-if="oauthError" class="text-red-500 text-xs text-center mt-2">{{ oauthError }}</p>
              </div>
            </template>

            <!-- ── REGISTRO ───────────────────────────── -->
            <template v-else>

              <!-- Estado post-registro -->
              <div v-if="registered" class="text-center space-y-5 py-4">
                <div class="w-16 h-16 mx-auto bg-gold/10 rounded-full flex items-center justify-center">
                  <svg class="w-8 h-8 text-gold" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                      d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                  </svg>
                </div>
                <div>
                  <h3 class="font-display text-lg text-aroma-dark mb-1">Revisa tu correo</h3>
                  <p class="text-gray-500 text-xs leading-relaxed">
                    Enviamos un enlace de verificación a <span class="font-medium text-aroma-dark">{{ registeredEmail }}</span>.
                    Confirma tu cuenta para iniciar sesión.
                  </p>
                </div>
                <button @click="activeTab = 'login'; registered = false"
                  class="text-xs text-gold underline underline-offset-2 hover:text-gold-dark">
                  Volver al inicio de sesión
                </button>
              </div>

              <template v-else>
                <div class="mb-5">
                  <OAuthButtons @error="oauthError = $event" />
                  <p v-if="oauthError" class="text-red-500 text-xs text-center mt-2">{{ oauthError }}</p>
                </div>

                <form @submit.prevent="handleRegister" class="space-y-3">
                  <div class="grid grid-cols-2 gap-3">
                    <div class="relative">
                      <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                            d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                        </svg>
                      </span>
                      <input v-model="regForm.first_name" type="text" required
                        class="w-full border border-gray-200 text-aroma-dark placeholder-gray-400 pl-9 pr-3 py-3 text-sm focus:outline-none focus:border-gold transition-colors"
                        placeholder="Nombre" />
                    </div>
                    <div class="relative">
                      <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                            d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                        </svg>
                      </span>
                      <input v-model="regForm.last_name" type="text" required
                        class="w-full border border-gray-200 text-aroma-dark placeholder-gray-400 pl-9 pr-3 py-3 text-sm focus:outline-none focus:border-gold transition-colors"
                        placeholder="Apellido" />
                    </div>
                  </div>

                  <div class="relative">
                    <span class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                          d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                      </svg>
                    </span>
                    <input v-model="regForm.email" type="email" required
                      class="w-full border border-gray-200 text-aroma-dark placeholder-gray-400 pl-10 pr-4 py-3 text-sm focus:outline-none focus:border-gold transition-colors"
                      placeholder="Correo electrónico" />
                  </div>

                  <div class="relative">
                    <span class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                          d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
                      </svg>
                    </span>
                    <input v-model="regForm.phone" type="tel"
                      class="w-full border border-gray-200 text-aroma-dark placeholder-gray-400 pl-10 pr-4 py-3 text-sm focus:outline-none focus:border-gold transition-colors"
                      placeholder="Teléfono (opcional)" />
                  </div>

                  <div class="relative">
                    <span class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                          d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                      </svg>
                    </span>
                    <input v-model="regForm.password" :type="showRegPwd ? 'text' : 'password'" required
                      class="w-full border border-gray-200 text-aroma-dark placeholder-gray-400 pl-10 pr-12 py-3 text-sm focus:outline-none focus:border-gold transition-colors"
                      placeholder="Contraseña" />
                    <button type="button" @click="showRegPwd = !showRegPwd"
                      class="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-gold transition-colors">
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path v-if="showRegPwd" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                          d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
                        <template v-else>
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                            d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                        </template>
                      </svg>
                    </button>
                  </div>

                  <div v-if="regForm.password" class="flex gap-1 h-1">
                    <div v-for="i in 4" :key="i" class="flex-1 rounded-full transition-colors"
                      :class="passwordStrength >= i ? strengthColor : 'bg-gray-200'" />
                  </div>

                  <div class="relative">
                    <span class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                          d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                      </svg>
                    </span>
                    <input v-model="regForm.confirm" :type="showRegConfirm ? 'text' : 'password'" required
                      class="w-full border border-gray-200 text-aroma-dark placeholder-gray-400 pl-10 pr-12 py-3 text-sm focus:outline-none focus:border-gold transition-colors"
                      placeholder="Confirmar contraseña" />
                    <button type="button" @click="showRegConfirm = !showRegConfirm"
                      class="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-gold transition-colors">
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path v-if="showRegConfirm" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                          d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
                        <template v-else>
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                            d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                        </template>
                      </svg>
                    </button>
                  </div>

                  <label class="flex items-start gap-2 text-xs text-gray-500 cursor-pointer">
                    <input type="checkbox" v-model="regForm.terms" required class="mt-0.5 accent-gold" />
                    <span>
                      Acepto los
                      <router-link to="/terms" @click="auth.closeAuthModal()" class="underline hover:text-gold">Términos</router-link>
                      y la
                      <router-link to="/privacy" @click="auth.closeAuthModal()" class="underline hover:text-gold">Política de privacidad</router-link>
                    </span>
                  </label>

                  <p v-if="registerError" class="text-red-500 text-xs text-center">{{ registerError }}</p>

                  <button type="submit" :disabled="registerLoading"
                    class="w-full bg-gold text-aroma-dark py-3 text-xs tracking-widest uppercase font-medium hover:bg-gold-light transition-colors disabled:opacity-50">
                    {{ registerLoading ? 'Creando cuenta...' : 'Crear Cuenta' }}
                  </button>
                </form>
              </template>
            </template>

          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import OAuthButtons from './OAuthButtons.vue'

const router = useRouter()
const auth = useAuthStore()

const activeTab = ref('login')
const oauthError = ref('')

// Login
const loginForm = ref({ email: '', password: '', remember: false })
const showLoginPwd = ref(false)
const loginLoading = ref(false)
const loginError = ref('')
const showUnverified = ref(false)
const unverifiedEmail = ref('')
const resendLoading = ref(false)
const resendDone = ref(false)

// Registro
const regForm = ref({ first_name: '', last_name: '', email: '', phone: '', password: '', confirm: '', terms: false })
const showRegPwd = ref(false)
const showRegConfirm = ref(false)
const registerLoading = ref(false)
const registerError = ref('')
const registered = ref(false)
const registeredEmail = ref('')

const passwordStrength = computed(() => {
  const p = regForm.value.password
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

watch(() => auth.authModal.show, (show) => {
  if (show) {
    activeTab.value = auth.authModal.tab || 'login'
    resetForms()
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})

function resetForms() {
  loginForm.value = { email: '', password: '', remember: false }
  showLoginPwd.value = false
  loginError.value = ''
  showUnverified.value = false
  resendDone.value = false
  regForm.value = { first_name: '', last_name: '', email: '', phone: '', password: '', confirm: '', terms: false }
  showRegPwd.value = false
  showRegConfirm.value = false
  registerError.value = ''
  registered.value = false
  oauthError.value = ''
}

async function handleLogin() {
  loginError.value = ''
  showUnverified.value = false
  loginLoading.value = true
  try {
    await auth.login(loginForm.value.email, loginForm.value.password)
    const redirect = auth.authModal.redirect || '/'
    auth.closeAuthModal()
    if (auth.isAdmin) {
      router.push('/admin/dashboard')
    } else {
      router.push(redirect)
    }
  } catch (e) {
    const detail = e.response?.data?.detail
    if (detail === 'EMAIL_NOT_VERIFIED') {
      showUnverified.value = true
      unverifiedEmail.value = loginForm.value.email
    } else {
      loginError.value = detail || 'Correo o contraseña incorrectos'
    }
  } finally {
    loginLoading.value = false
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

async function handleRegister() {
  registerError.value = ''
  if (regForm.value.password !== regForm.value.confirm) {
    registerError.value = 'Las contraseñas no coinciden'
    return
  }
  registerLoading.value = true
  try {
    await auth.register({
      first_name: regForm.value.first_name,
      last_name: regForm.value.last_name,
      email: regForm.value.email,
      phone: regForm.value.phone || undefined,
      password: regForm.value.password,
    })
    registeredEmail.value = regForm.value.email
    registered.value = true
  } catch (e) {
    registerError.value = e.response?.data?.detail || 'Error al crear la cuenta'
  } finally {
    registerLoading.value = false
  }
}
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}
.modal-enter-active .relative,
.modal-leave-active .relative {
  transition: transform 0.2s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
