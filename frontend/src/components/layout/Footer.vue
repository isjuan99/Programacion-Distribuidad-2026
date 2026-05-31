<template>
  <footer class="bg-aroma-darker border-t border-aroma-border mt-24">
    <div class="max-w-7xl mx-auto px-6 py-16">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-12">
        <!-- Brand -->
        <div>
          <h3 class="font-display text-2xl text-aroma-text mb-4">Aroma-Distribuido</h3>
          <p class="text-aroma-muted text-sm leading-relaxed max-w-xs">{{ $t('footer.tagline') }}</p>
        </div>

        <!-- Explore -->
        <div>
          <h4 class="text-xs tracking-widest uppercase text-gold mb-6">{{ $t('footer.explore') }}</h4>
          <ul class="space-y-3">
            <li v-for="link in exploreLinks" :key="link.to">
              <router-link :to="link.to"
                class="text-aroma-muted text-sm hover:text-aroma-text transition-colors">
                {{ $t(link.i18n) }}
              </router-link>
            </li>
          </ul>
        </div>

        <!-- Customer Care -->
        <div>
          <h4 class="text-xs tracking-widest uppercase text-gold mb-6">{{ $t('footer.customer_care') }}</h4>
          <ul class="space-y-3">
            <li v-for="link in careLinks" :key="link.to">
              <router-link :to="link.to"
                class="text-aroma-muted text-sm hover:text-aroma-text transition-colors">
                {{ $t(link.i18n) }}
              </router-link>
            </li>
          </ul>
        </div>
      </div>

      <div class="border-t border-aroma-border mt-12 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
        <p class="text-aroma-muted text-xs tracking-wider uppercase">{{ $t('footer.copyright') }}</p>
        <div class="flex gap-6">
          <!-- Language toggle -->
          <button @click="toggleLocale"
            class="text-xs tracking-widest uppercase text-aroma-muted hover:text-gold transition-colors">
            {{ locale === 'es' ? 'EN' : 'ES' }}
          </button>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()

function toggleLocale() {
  locale.value = locale.value === 'es' ? 'en' : 'es'
  localStorage.setItem('aroma_locale', locale.value)
}

const exploreLinks = [
  { to: '/shop', i18n: 'nav.catalog' },
  { to: '/shop?collections=1', i18n: 'nav.collections' },
  { to: '/contact', i18n: 'nav.contact' },
]

const careLinks = [
  { to: '/privacy', i18n: 'footer.privacy' },
  { to: '/terms', i18n: 'footer.terms' },
  { to: '/shipping', i18n: 'footer.shipping' },
]
</script>
