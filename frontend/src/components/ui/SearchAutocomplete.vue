<template>
  <div class="relative" ref="containerRef">
    <div class="flex items-center border-b border-gray-700 focus-within:border-[#c9a84c] transition-colors">
      <svg class="w-4 h-4 text-gray-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
      </svg>
      <input
        ref="inputRef"
        v-model="query"
        type="text"
        :placeholder="$t('nav.search')"
        class="w-full bg-transparent text-white text-sm px-3 py-2 focus:outline-none placeholder-gray-600"
        @keydown.down.prevent="moveCursor(1)"
        @keydown.up.prevent="moveCursor(-1)"
        @keydown.enter.prevent="selectCurrent"
        @keydown.escape="close"
        @input="onInput"
      />
      <button v-if="query" @click="query = ''; suggestions = []" class="text-gray-500 hover:text-white shrink-0 px-1">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
    </div>

    <div
      v-if="showDropdown"
      class="absolute top-full left-0 right-0 mt-1 bg-[#111] border border-gray-800 shadow-2xl z-50 max-h-80 overflow-y-auto"
    >
      <div v-if="loading" class="p-4 flex justify-center">
        <div class="w-4 h-4 border border-[#c9a84c] border-t-transparent rounded-full animate-spin"></div>
      </div>

      <template v-else-if="suggestions.length > 0">
        <RouterLink
          v-for="(s, i) in suggestions"
          :key="s.id"
          :to="`/product/${s.id}`"
          @click="close"
          class="flex items-center gap-3 px-4 py-3 hover:bg-white/5 transition-colors border-b border-gray-800/50 last:border-0"
          :class="{ 'bg-white/5': cursor === i }"
        >
          <img
            v-if="s.primary_image"
            :src="s.primary_image"
            :alt="s.name"
            class="w-10 h-10 object-cover shrink-0 bg-gray-800"
          />
          <div v-else class="w-10 h-10 bg-gray-800 shrink-0 flex items-center justify-center">
            <svg class="w-4 h-4 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-white text-sm truncate">{{ s.name }}</p>
            <p class="text-gray-500 text-xs">{{ s.brand }}</p>
          </div>
          <span v-if="s.price" class="text-[#c9a84c] text-sm shrink-0">${{ s.price }}</span>
        </RouterLink>

        <RouterLink
          :to="`/shop?q=${encodeURIComponent(query)}`"
          @click="close"
          class="flex items-center justify-between px-4 py-3 text-sm text-[#c9a84c] hover:bg-white/5 transition-colors"
        >
          <span>{{ $t('search.view_all_results', { q: query }) }}</span>
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
          </svg>
        </RouterLink>
      </template>

      <div v-else class="px-4 py-4 text-sm text-gray-500 text-center">
        {{ $t('search.no_suggestions', { q: query }) }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../router/api'

const router = useRouter()
const query = ref('')
const suggestions = ref([])
const loading = ref(false)
const cursor = ref(-1)
const containerRef = ref(null)
let debounceTimer = null

const showDropdown = computed(() =>
  query.value.length >= 2 && (loading.value || suggestions.value.length > 0 || (!loading.value && query.value.length >= 2))
)

function onInput() {
  cursor.value = -1
  clearTimeout(debounceTimer)
  if (query.value.length < 2) {
    suggestions.value = []
    return
  }
  loading.value = true
  debounceTimer = setTimeout(async () => {
    try {
      const { data } = await api.get(`/products/suggestions?q=${encodeURIComponent(query.value)}`)
      suggestions.value = data
    } catch {
      suggestions.value = []
    } finally {
      loading.value = false
    }
  }, 300)
}

function moveCursor(dir) {
  const max = suggestions.value.length
  cursor.value = Math.max(-1, Math.min(max - 1, cursor.value + dir))
}

function selectCurrent() {
  if (cursor.value >= 0 && suggestions.value[cursor.value]) {
    router.push(`/product/${suggestions.value[cursor.value].id}`)
    close()
  } else if (query.value) {
    router.push(`/shop?q=${encodeURIComponent(query.value)}`)
    close()
  }
}

function close() {
  suggestions.value = []
  query.value = ''
  cursor.value = -1
}

function handleOutsideClick(e) {
  if (containerRef.value && !containerRef.value.contains(e.target)) {
    suggestions.value = []
  }
}

onMounted(() => document.addEventListener('click', handleOutsideClick))
onUnmounted(() => document.removeEventListener('click', handleOutsideClick))
</script>
