import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useWishlistStore = defineStore('wishlist', () => {
  const KEY = 'aroma_wishlist'

  // State — array of product objects { id, name, brand, price, image, slug }
  const items = ref(JSON.parse(localStorage.getItem(KEY) || '[]'))

  // Computed
  const count = computed(() => items.value.length)
  const ids = computed(() => items.value.map(i => i.id))

  function persist() {
    localStorage.setItem(KEY, JSON.stringify(items.value))
  }

  function isWished(productId) {
    return ids.value.includes(productId)
  }

  function toggle(product) {
    const idx = items.value.findIndex(i => i.id === product.id)
    if (idx === -1) {
      items.value.push(product)
    } else {
      items.value.splice(idx, 1)
    }
    persist()
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

  return { items, count, ids, isWished, toggle, add, remove, clear }
})
