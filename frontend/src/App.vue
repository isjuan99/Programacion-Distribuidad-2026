<template>
  <router-view />
  <AuthModal />
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import { useWishlistStore } from './stores/wishlist'
import AuthModal from './components/auth/AuthModal.vue'

const auth = useAuthStore()
const wishlist = useWishlistStore()

onMounted(async () => {
  if (auth.isAuthenticated) {
    try {
      await auth.fetchMe()
    } catch {
      // Token expired — interceptor handles refresh
    }
    await wishlist.loadFromApi()
  }
})
</script>
