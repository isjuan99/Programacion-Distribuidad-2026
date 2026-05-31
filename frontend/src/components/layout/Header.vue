<template>
  <header
    class="fixed top-0 left-0 right-0 z-50 bg-aroma-dark/95 backdrop-blur-md border-b border-white/10 transition-shadow duration-300"
    :class="scrolled ? 'shadow-lg shadow-black/30' : ''"
  >
    <div class="max-w-7xl mx-auto px-8 h-18 flex items-center gap-10" style="height:68px;">

      <!-- Logo -->
      <router-link
        to="/"
        class="font-display text-xl tracking-widest text-aroma-text hover:text-gold transition-colors shrink-0"
      >
        Aroma-Distribuido
      </router-link>

      <!-- Search — centro -->
      <div class="hidden md:flex flex-1 justify-center">
        <div class="w-64 lg:w-80">
          <SearchAutocomplete />
        </div>
      </div>

      <!-- Nav + iconos — derecha -->
      <div class="flex items-center gap-8 shrink-0 ml-auto">
        <nav class="hidden md:flex items-center gap-7">

          <!-- Inicio -->
          <router-link
            to="/"
            class="text-xs tracking-widest uppercase text-aroma-muted hover:text-aroma-text transition-colors"
            active-class="text-gold border-b border-gold pb-0.5"
            :exact="true"
          >
            Inicio
          </router-link>

          <!-- Catálogo -->
          <router-link
            to="/shop"
            class="text-xs tracking-widest uppercase text-aroma-muted hover:text-aroma-text transition-colors"
            active-class="text-gold border-b border-gold pb-0.5"
          >
            Catálogo
          </router-link>

          <!-- Ofertas -->
          <router-link
            to="/offers"
            class="text-xs tracking-widest uppercase text-aroma-muted hover:text-aroma-text transition-colors"
            active-class="text-gold border-b border-gold pb-0.5"
          >
            Ofertas
          </router-link>

          <!-- Dropdown Perfumes -->
          <div
            class="relative"
            @mouseenter="perfumesOpen = true"
            @mouseleave="perfumesOpen = false"
          >
            <button
              class="flex items-center gap-1 text-xs tracking-widest uppercase transition-colors"
              :class="perfumesOpen ? 'text-gold' : 'text-aroma-muted hover:text-aroma-text'"
            >
              Perfumes
              <svg
                class="w-3 h-3 transition-transform duration-200"
                :class="perfumesOpen ? 'rotate-180' : ''"
                fill="none" stroke="currentColor" viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
              </svg>
            </button>

            <transition
              enter-active-class="transition-all duration-200 ease-out"
              enter-from-class="opacity-0 translate-y-1"
              enter-to-class="opacity-100 translate-y-0"
              leave-active-class="transition-all duration-150 ease-in"
              leave-from-class="opacity-100 translate-y-0"
              leave-to-class="opacity-0 translate-y-1"
            >
              <div v-show="perfumesOpen" class="absolute top-full left-1/2 -translate-x-1/2 pt-4 z-50">
                <div class="bg-aroma-dark border border-white/10 shadow-2xl min-w-[160px] overflow-hidden">
                  <router-link
                    v-for="item in perfumesMenu"
                    :key="item.label"
                    :to="item.to"
                    @click="perfumesOpen = false"
                    class="flex items-center gap-3 px-5 py-3.5 text-xs tracking-widest uppercase
                           text-aroma-muted hover:text-gold hover:bg-white/5 transition-colors
                           border-b border-white/5 last:border-0 group"
                  >
                    <span class="w-1.5 h-1.5 rounded-full bg-gold/40 group-hover:bg-gold transition-colors shrink-0"></span>
                    {{ item.label }}
                  </router-link>
                </div>
              </div>
            </transition>
          </div>

          <!-- Contacto -->
          <router-link
            to="/contact"
            class="text-xs tracking-widest uppercase text-aroma-muted hover:text-aroma-text transition-colors"
            active-class="text-gold border-b border-gold pb-0.5"
          >
            Contacto
          </router-link>

        </nav>

        <!-- Separador -->
        <div class="hidden md:block h-5 w-px bg-white/15"></div>

        <!-- Iconos -->
        <div class="flex items-center gap-5">
          <router-link
            :to="auth.isAuthenticated ? '/account' : '/login'"
            class="text-aroma-muted hover:text-gold transition-colors"
            :title="auth.isAuthenticated ? 'Mi Cuenta' : 'Iniciar Sesión'"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
            </svg>
          </router-link>

          <router-link to="/cart" class="relative text-aroma-muted hover:text-gold transition-colors" title="Carrito">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/>
            </svg>
            <span
              v-if="cart.count > 0"
              class="absolute -top-2 -right-2 bg-gold text-aroma-dark text-[10px] w-4 h-4 rounded-full flex items-center justify-center font-bold"
            >
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
const perfumesOpen = ref(false)

// El dropdown usa el campo gender del producto (no categoría)
const perfumesMenu = [
  { label: 'Hombre', to: '/shop?gender=hombre' },
  { label: 'Mujer',  to: '/shop?gender=mujer'  },
  { label: 'Unisex', to: '/shop?gender=unisex' },
]

function onScroll() {
  scrolled.value = window.scrollY > 20
}

onMounted(() => window.addEventListener('scroll', onScroll))

onUnmounted(() => window.removeEventListener('scroll', onScroll))
</script>
