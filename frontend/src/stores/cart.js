import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useCartStore = defineStore('cart', () => {
  const items = ref(JSON.parse(localStorage.getItem('aroma_cart') || '[]'))

  const count = computed(() => items.value.reduce((sum, i) => sum + i.quantity, 0))

  const subtotal = computed(() =>
    items.value.reduce((sum, i) => sum + i.price * i.quantity, 0)
  )

  function _persist() {
    localStorage.setItem('aroma_cart', JSON.stringify(items.value))
  }

  function addItem(product, variant, quantity = 1) {
    const existing = items.value.find(
      i => i.variant_id === variant.id
    )
    if (existing) {
      existing.quantity += quantity
    } else {
      items.value.push({
        variant_id: variant.id,
        product_id: product.id,
        name: product.name,
        brand: product.brand_name,
        size_ml: variant.size_ml,
        price: variant.price,
        image: product.images?.[0] || null,
        quantity,
      })
    }
    _persist()
  }

  function removeItem(variantId) {
    items.value = items.value.filter(i => i.variant_id !== variantId)
    _persist()
  }

  function updateQuantity(variantId, quantity) {
    const item = items.value.find(i => i.variant_id === variantId)
    if (item) {
      if (quantity <= 0) {
        removeItem(variantId)
      } else {
        item.quantity = quantity
        _persist()
      }
    }
  }

  function clearCart() {
    items.value = []
    localStorage.removeItem('aroma_cart')
  }

  return { items, count, subtotal, addItem, removeItem, updateQuantity, clearCart }
})
