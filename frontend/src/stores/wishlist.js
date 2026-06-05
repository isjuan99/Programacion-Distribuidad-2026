import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../router/api'
import { useAuthStore } from './auth'

export const useWishlistStore = defineStore('wishlist', () => {
  const KEY = 'aroma_wishlist'
  const items = ref(JSON.parse(localStorage.getItem(KEY) || '[]'))

  const count = computed(() => items.value.length)
  const ids = computed(() => items.value.map(i => i.id))

  function persist() {
    localStorage.setItem(KEY, JSON.stringify(items.value))
  }

  function isWished(productId) {
    return ids.value.includes(productId)
  }

  async function toggle(product) {
    const auth = useAuthStore()
    const idx = items.value.findIndex(i => i.id === product.id)
    if (idx === -1) {
      items.value.push(product)
      if (auth.isAuthenticated) {
        try { await api.post(`/users/me/wishlist/${product.id}`) } catch {}
      }
    } else {
      items.value.splice(idx, 1)
      if (auth.isAuthenticated) {
        try { await api.delete(`/users/me/wishlist/${product.id}`) } catch {}
      }
    }
    persist()
  }

  async function loadFromApi() {
    const auth = useAuthStore()
    if (!auth.isAuthenticated) return
    try {
      const { data } = await api.get('/users/me/wishlist')
      items.value = data.map(i => ({
        id: i.product_id,
        name: i.product_name,
        brand_name: i.product_brand,
        images: i.product_image ? [i.product_image] : [],
        variants: [{ price: i.product_price }],
      }))
      persist()
    } catch {}
  }

  function add(product) {
    if (!isWished(product.id)) {
      items.value.push(product)
      persist()
    }
  }

  function remove(productId) {
    items.value = items.value.filter(i => i.id !== productId)
    persist()
  }

  function clear() {
    items.value = []
    persist()
  }

  return { items, count, ids, isWished, toggle, add, remove, clear, loadFromApi }
})
