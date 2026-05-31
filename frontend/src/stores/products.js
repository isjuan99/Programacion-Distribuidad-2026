import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../router/api'

export const useProductsStore = defineStore('products', () => {
  const products = ref([])
  const currentProduct = ref(null)
  const total = ref(0)
  const page = ref(1)
  const pages = ref(1)
  const loading = ref(false)
  const categories = ref([])
  const brands = ref([])

  async function fetchProducts(params = {}) {
    loading.value = true
    try {
      const { data } = await api.get('/products', { params })
      products.value = data.items
      total.value = data.total
      page.value = data.page
      pages.value = data.pages
    } finally {
      loading.value = false
    }
  }

  async function fetchProduct(id) {
    loading.value = true
    try {
      const { data } = await api.get(`/products/${id}`)
      currentProduct.value = data
      return data
    } finally {
      loading.value = false
    }
  }

  async function fetchCategories() {
    const { data } = await api.get('/categories')
    categories.value = data
    return data
  }

  async function fetchBrands() {
    const { data } = await api.get('/brands')
    brands.value = data
    return data
  }

  return {
    products, currentProduct, total, page, pages, loading,
    categories, brands,
    fetchProducts, fetchProduct, fetchCategories, fetchBrands,
  }
})
