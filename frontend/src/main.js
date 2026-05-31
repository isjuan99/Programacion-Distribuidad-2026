import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import router from './router/index.js'
import App from './App.vue'
import './assets/main.css'

import es from './locales/es.json'
import en from './locales/en.json'

const i18n = createI18n({
  legacy: false,
  locale: localStorage.getItem('aroma_locale') || 'es',
  fallbackLocale: 'en',
  messages: { es, en },
})

const pinia = createPinia()

createApp(App)
  .use(pinia)
  .use(router)
  .use(i18n)
  .mount('#app')
