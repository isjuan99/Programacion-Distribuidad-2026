<template>
  <header class="fixed top-0 left-0 right-0 z-50 border-b border-aroma-border"
    :class="scrolled ? 'bg-aroma-dark/95 backdrop-blur-md' : 'bg-transparent'">
    <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
      <!-- Search (left) -->
      <div class="hidden md:block w-56 lg:w-72">
        <SearchAutocomplete />
      </div>

      <!-- Logo (center) -->
      <router-link to="/" class="font-display text-xl tracking-widest text-aroma-text hover:text-gold transition-colors">
        Aroma-Distribuido
      </router-link>

      <!-- Nav + Icons (right) -->
      <div class="flex items-center gap-6 w-48 justify-end">
        <nav class="hidden md:flex items-center gap-6">
          <router-link v-for="link in navLinks" :key="link.to"
            :to="link.to"
            class="text-xs tracking-widest uppercase text-aroma-muted hover:text-aroma-text transition-colors"
            active-class="text-aroma-text border-b border-gold pb-0.5">
            {{ $t(link.i18n) }}
          </router-link>
        </nav>
        <div class="flex items-center gap-4">
          <router-link :to="auth.isAuthenticated ? '/account' : '/login'"
            class="text-aroma-muted hover:text-gold transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
            </svg>
          </router-link>
          <router-link to="/cart" class="relative text-aroma-muted hover:text-gold transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/>
            </svg>
            <span v-if="cart.count > 0"
              class="absolute -top-2 -right-2 bg-gold text-aroma-dark text-[10px] w-4 h-4 rounded-full flex items-center justify-center font-bold">
              {{ cart.count }}
            </span>
          </router-link>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useCartStore } from '../../stores/cart'
import SearchAutocomplete from '../ui/SearchAutocomplete.vue'

const auth = useAuthStore()
const cart = useCartStore()

const scrolled = ref(false)

const navLinks = [
  { to: '/shop', i18n: 'nav.catalog' },
  { to: '/shop', i18n: 'nav.collections' },
  { to: '/contact', i18n: 'nav.contact' },
]

function onScroll() {
  scrolled.value = window.scrollY > 20
}

onMounted(() => window.addEventListener('scroll', onScroll))
onUnmounted(() => window.removeEventListener('scroll', onScroll))
</script>

