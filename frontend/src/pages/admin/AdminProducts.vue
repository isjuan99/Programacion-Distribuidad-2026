<template>
  <AdminSidebar>
    <div class="p-8">
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="font-display text-3xl text-aroma-dark">{{ $t('admin.product_portfolio') }}</h1>
          <p class="text-gray-400 text-sm mt-1">{{ $t('admin.manage_products') }}</p>
        </div>
        <button @click="showCreate = true"
          class="bg-gold text-aroma-dark px-6 py-2.5 text-xs tracking-widest uppercase font-medium hover:bg-gold-light transition-colors">
          {{ $t('admin.new_fragrance') }}
        </button>
      </div>

      <!-- Products table -->
      <div class="bg-white border border-gray-100 rounded-sm overflow-hidden">
        <div class="p-4 border-b border-gray-100 flex gap-3">
          <input v-model="search" type="text" placeholder="Buscar fragancia..."
            class="border border-gray-200 text-sm px-3 py-2 text-aroma-dark w-64 focus:outline-none focus:border-gold-dark" />
        </div>

        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-gray-100 bg-gray-50">
              <th class="text-left p-4 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Producto</th>
              <th class="text-left p-4 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Marca</th>
              <th class="text-left p-4 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Categoría</th>
              <th class="text-left p-4 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Precio base</th>
              <th class="text-left p-4 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Estado</th>
              <th class="p-4" />
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="6" class="p-8 text-center text-gray-400 text-sm">Cargando...</td>
            </tr>
            <tr v-else v-for="p in products" :key="p.id"
              class="border-b border-gray-50 transition-colors"
              :class="hasLowStock(p) ? 'bg-red-50 hover:bg-red-100' : 'hover:bg-gray-50'">
              <td class="p-4">
                <div class="flex items-center gap-3">
                  <div class="w-12 h-12 bg-gray-100 overflow-hidden shrink-0">
                    <img v-if="p.images?.[0]" :src="p.images[0]" class="w-full h-full object-cover" />
                  </div>
                  <div>
                    <p class="font-medium text-aroma-dark">{{ p.name }}</p>
                    <p class="text-xs text-gray-400">{{ p.slug }}</p>
                  </div>
                </div>
              </td>
              <td class="p-4 text-gray-600">{{ p.brand_name }}</td>
              <td class="p-4 text-gray-600">{{ p.category_name }}</td>
              <td class="p-4">
                <span class="text-aroma-dark">${{ p.variants?.[0]?.price?.toFixed(2) || '—' }}</span>
                <span v-if="hasLowStock(p)"
                  class="ml-2 inline-flex items-center px-1.5 py-0.5 text-[10px] font-medium
                         bg-red-100 text-red-700 border border-red-200 rounded-full">
                  Stock bajo
                </span>
              </td>
              <td class="p-4">
                <span class="text-[10px] px-2 py-1 rounded-full"
                  :class="p.status === 'active' ? 'bg-green-50 text-green-700' : 'bg-gray-100 text-gray-500'">
                  {{ p.status }}
                </span>
              </td>
              <td class="p-4">
                <div class="flex gap-2">
                  <button @click="editProduct(p)" title="Editar producto" aria-label="Editar producto"
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded
                           bg-[#f9edd8] border border-gold text-gold-dark
                           hover:bg-[#f0d9a8] transition-colors">
                    <svg class="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                    </svg>
                    <span class="hidden sm:inline">Editar</span>
                  </button>
                  <button @click="deleteProduct(p.id)" title="Eliminar producto" aria-label="Eliminar producto"
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded
                           bg-red-50 border border-red-300 text-red-700
                           hover:bg-red-100 transition-colors">
                    <svg class="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                    </svg>
                    <span class="hidden sm:inline">Eliminar</span>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Pagination -->
        <div class="p-4 border-t border-gray-100 flex justify-between items-center text-xs text-gray-400">
          <span>{{ total }} productos en total</span>
          <div class="flex gap-1">
            <button v-for="p in pages" :key="p" @click="page = p"
              class="w-7 h-7 border text-xs"
              :class="p === page ? 'border-gold bg-gold text-aroma-dark' : 'border-gray-200 hover:border-gray-400'">
              {{ p }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create / Edit panel -->
    <transition name="slide">
      <div v-if="showCreate || editingProduct"
        class="fixed inset-y-0 right-0 w-[440px] bg-white border-l border-gray-200 z-50 overflow-y-auto shadow-2xl"
        @click.stop>
        <div class="p-8">
          <div class="flex justify-between items-start mb-6">
            <div>
              <h2 class="font-display text-2xl text-aroma-dark">
                {{ editingProduct ? 'Editar fragancia' : $t('admin.create_product') }}
              </h2>
              <p class="text-gray-400 text-xs mt-1">{{ $t('admin.add_fragrance') }}</p>
            </div>
            <button @click="closePanel" class="text-gray-400 hover:text-aroma-dark">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>

          <form @submit.prevent="handleSubmit" class="space-y-5">

            <!-- Images -->
            <div>
              <p class="text-[10px] tracking-widest uppercase text-gold mb-3">Fotos del Producto</p>
              <div class="flex flex-wrap gap-2 mb-3">
                <div v-for="(url, i) in form.images" :key="i"
                  class="relative w-20 h-20 border border-gray-200 overflow-hidden group">
                  <img :src="url" class="w-full h-full object-cover" />
                  <button type="button" @click="removeImage(i)"
                    class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 flex items-center justify-center text-white text-xs transition-opacity">
                    ✕
                  </button>
                </div>
              </div>

              <input id="product-image-input" type="file"
                accept="image/jpeg,image/png,image/webp"
                style="position:absolute;width:1px;height:1px;opacity:0;overflow:hidden;"
                :disabled="uploadingImage" @change="uploadImage" />

              <label for="product-image-input"
                class="flex items-center gap-2 border border-dashed border-gray-300 px-4 py-2.5 text-xs
                       cursor-pointer hover:border-gold-dark hover:text-gold-dark transition-colors w-full justify-center"
                :class="uploadingImage ? 'opacity-50 cursor-not-allowed pointer-events-none' : 'text-gray-500'">
                <svg v-if="!uploadingImage" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                </svg>
                <span>{{ uploadingImage ? 'Subiendo imagen...' : 'Seleccionar imagen del perfume' }}</span>
              </label>

              <p class="text-[10px] text-gray-400 mt-1">JPG, PNG o WebP · máx 5MB · primera imagen = portada</p>
              <div v-if="uploadError" class="mt-2 bg-red-50 border border-red-200 text-red-600 text-xs px-3 py-2">
                {{ uploadError }}
              </div>
            </div>

            <hr class="border-gray-100" />

            <div>
              <p class="text-[10px] tracking-widest uppercase text-gold mb-3">{{ $t('admin.identity') }}</p>
              <div class="space-y-3">
                <div>
                  <label class="text-xs text-gray-500 block mb-1">{{ $t('admin.fragrance_name') }}</label>
                  <input v-model="form.name" required
                    class="w-full border border-gray-200 text-aroma-dark px-3 py-2.5 text-sm focus:outline-none focus:border-gold-dark" />
                </div>
                <div class="grid grid-cols-2 gap-3">
                  <div>
                    <label class="text-xs text-gray-500 block mb-1">{{ $t('admin.brand_house') }}</label>
                    <div v-if="brands.length === 0" class="text-xs text-amber-600 bg-amber-50 border border-amber-200 px-3 py-2">
                      Sin marcas —
                      <router-link to="/admin/brands" class="underline font-medium">créalas aquí</router-link>
                    </div>
                    <select v-else v-model="form.brand_id" required
                      class="w-full border border-gray-200 text-aroma-dark px-3 py-2.5 text-sm focus:outline-none focus:border-gold-dark bg-white">
                      <option :value="null" disabled>Seleccionar marca</option>
                      <option v-for="b in brands" :key="b.id" :value="b.id">{{ b.name }}</option>
                    </select>
                  </div>
                  <div>
                    <label class="text-xs text-gray-500 block mb-1">{{ $t('admin.category') }}</label>
                    <div v-if="categories.length === 0" class="text-xs text-amber-600 bg-amber-50 border border-amber-200 px-3 py-2">
                      Sin categorías —
                      <router-link to="/admin/categories" class="underline font-medium">créalas aquí</router-link>
                    </div>
                    <select v-else v-model="form.category_id" required
                      class="w-full border border-gray-200 text-aroma-dark px-3 py-2.5 text-sm focus:outline-none focus:border-gold-dark bg-white">
                      <option :value="null" disabled>Seleccionar categoría</option>
                      <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            <hr class="border-gray-100" />

            <!-- Variante única -->
            <div>
              <p class="text-[10px] tracking-widest uppercase text-gold mb-4">Precio y Stock</p>

              <!-- Tamaño -->
              <div class="mb-3">
                <label class="text-xs text-gray-500 block mb-1">Tamaño</label>
                <select v-model="mainVariant.size_ml"
                  class="w-full border border-gray-200 text-aroma-dark px-3 py-2.5 text-sm focus:outline-none focus:border-gold-dark bg-white">
                  <option :value="30">30 ml</option>
                  <option :value="50">50 ml</option>
                  <option :value="100">100 ml</option>
                  <option :value="150">150 ml</option>
                  <option :value="200">200 ml</option>
                </select>
              </div>

              <!-- Precio -->
              <div class="grid grid-cols-2 gap-3 mb-3">
                <div>
                  <label class="text-xs text-gray-500 block mb-1">
                    Precio <span class="text-red-400">*</span>
                  </label>
                  <input
                    :value="mainVariant.price ?? ''"
                    @input="mainVariant.price = $event.target.value === '' ? 0 : Number($event.target.value)"
                    type="number" step="1" placeholder="Ej: 150000"
                    class="w-full border border-gray-200 text-aroma-dark px-3 py-2.5 text-sm focus:outline-none focus:border-gold-dark" />
                </div>
                <div>
                  <label class="text-xs text-gray-500 block mb-1">Stock</label>
                  <input
                    :value="mainVariant.stock ?? ''"
                    @input="mainVariant.stock = $event.target.value === '' ? 0 : Number($event.target.value)"
                    type="number" placeholder="Ej: 25"
                    class="w-full border border-gray-200 text-aroma-dark px-3 py-2.5 text-sm focus:outline-none focus:border-gold-dark" />
                </div>
              </div>

              <!-- Precio de oferta -->
              <div class="bg-orange-50 border border-orange-200 rounded p-3">
                <label class="text-xs text-orange-700 block mb-1 font-medium">
                  Precio original (opcional — activa el badge de oferta)
                </label>
                <input
                  :value="mainVariant.compare_at_price ?? ''"
                  @input="mainVariant.compare_at_price = $event.target.value === '' ? null : Number($event.target.value)"
                  type="number" step="1" placeholder="Ej: 180000 — dejar vacío si no hay oferta"
                  class="w-full border border-orange-300 text-aroma-dark px-3 py-2 text-sm focus:outline-none focus:border-orange-400 bg-white placeholder-orange-300" />
                <p v-if="mainVariant.compare_at_price && mainVariant.price" class="text-orange-600 text-xs mt-1.5">
                  Descuento: {{ Math.round((1 - mainVariant.price / mainVariant.compare_at_price) * 100) }}% off
                </p>
              </div>
            </div>

            <hr class="border-gray-100" />

            <!-- Composition -->
            <div>
              <p class="text-[10px] tracking-widest uppercase text-gold mb-3">{{ $t('admin.composition') }}</p>
              <div>
                <label class="text-xs text-gray-500 block mb-1">{{ $t('admin.olfactory_notes') }}</label>
                <input v-model="notesInput" type="text" placeholder="bergamota, sándalo, ambar (separados por coma)"
                  class="w-full border border-gray-200 text-aroma-dark px-3 py-2.5 text-sm focus:outline-none focus:border-gold-dark" />
              </div>
            </div>

            <!-- Description -->
            <div>
              <label class="text-xs text-gray-500 block mb-1">{{ $t('admin.story') }}</label>
              <textarea v-model="form.description" rows="4"
                class="w-full border border-gray-200 text-aroma-dark px-3 py-2.5 text-sm focus:outline-none focus:border-gold-dark resize-none"
                placeholder="Historia y descripción de la fragancia..." />
            </div>

            <!-- Género -->
            <div>
              <p class="text-[10px] tracking-widest uppercase text-gold mb-3">Género</p>
              <div class="grid grid-cols-3 gap-2">
                <label v-for="g in genderOptions" :key="g.value"
                  class="flex items-center gap-2 border px-3 py-2.5 cursor-pointer transition-colors text-xs"
                  :class="form.gender === g.value
                    ? 'border-gold bg-gold/10 text-gold font-medium'
                    : 'border-gray-200 text-gray-500 hover:border-gray-400'">
                  <input type="radio" :value="g.value" v-model="form.gender" class="sr-only" />
                  {{ g.label }}
                </label>
              </div>
            </div>

            <!-- Status -->
            <div class="flex items-center gap-6">
              <label class="flex items-center gap-2 text-xs text-gray-600 cursor-pointer">
                <input type="checkbox" v-model="form.is_featured" class="accent-gold-dark" />
                Destacado
              </label>
              <label class="flex items-center gap-2 text-xs text-gray-600 cursor-pointer">
                <input type="checkbox" v-model="form.is_new" class="accent-gold-dark" />
                Nuevo
              </label>
              <select v-model="form.status"
                class="border border-gray-200 text-aroma-dark px-3 py-2 text-xs focus:outline-none focus:border-gold-dark bg-white">
                <option value="draft">Borrador</option>
                <option value="active">Activo</option>
              </select>
            </div>

            <!-- Bundle toggle -->
            <div class="flex items-center gap-3 py-2">
              <label class="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" v-model="form.is_bundle" class="accent-[#c9a84c] w-4 h-4"/>
                <span class="text-sm text-gray-300">{{ $t('admin.is_bundle') }}</span>
              </label>
              <span class="text-xs text-gray-500">{{ $t('admin.bundle_hint') }}</span>
            </div>

            <p v-if="formError" class="text-red-500 text-xs">{{ formError }}</p>

            <div class="flex gap-3 pt-2">
              <button type="submit" :disabled="formLoading"
                class="flex-1 bg-gold text-aroma-dark py-3 text-xs tracking-widest uppercase font-medium hover:bg-gold-light disabled:opacity-50">
                {{ formLoading ? 'Guardando...' : $t('admin.publish') }}
              </button>
              <button type="button" @click="closePanel"
                class="flex-1 border border-gray-200 text-gray-600 py-3 text-xs tracking-widest uppercase hover:border-gray-400">
                {{ $t('admin.cancel') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </transition>
    <div v-if="showCreate || editingProduct"
      @click="closePanel"
      class="fixed inset-0 bg-black/30 z-40" />
  </AdminSidebar>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import AdminSidebar from '../../components/layout/AdminSidebar.vue'
import api from '../../router/api'

const products = ref([])
const total = ref(0)
const pages = ref(1)
const page = ref(1)
const loading = ref(false)
const search = ref('')
const brands = ref([])
const categories = ref([])
const showCreate = ref(false)
const editingProduct = ref(null)
const notesInput = ref('')
const formLoading = ref(false)
const formError = ref('')
const uploadingImage = ref(false)
const uploadError = ref('')

const genderOptions = [
  { value: null,     label: 'Sin especificar' },
  { value: 'hombre', label: '♂ Hombre' },
  { value: 'mujer',  label: '♀ Mujer' },
  { value: 'unisex', label: '⚧ Unisex' },
]

function emptyVariant() {
  return { id: undefined, size_ml: 50, price: 0, compare_at_price: null, stock: 0 }
}

function emptyForm() {
  return {
    name: '', brand_id: null, category_id: null, description: '',
    status: 'draft', is_featured: false, is_new: false, is_bundle: false,
    gender: null, images: [],
    variants: [emptyVariant()],
  }
}

const form = ref(emptyForm())

// Referencia directa a la única variante editable
const mainVariant = computed(() => form.value.variants[0])

async function uploadImage(event) {
  const file = event.target.files[0]
  if (!file) return
  uploadingImage.value = true
  uploadError.value = ''
  try {
    const fd = new FormData()
    fd.append('file', file)
    const { data } = await api.post('/upload/image', fd, { headers: { 'Content-Type': undefined } })
    form.value.images.push(data.url)
  } catch (e) {
    uploadError.value = e.response?.data?.detail || 'Error al subir imagen'
  } finally {
    uploadingImage.value = false
    event.target.value = ''
  }
}

function removeImage(index) {
  form.value.images.splice(index, 1)
}

function editProduct(p) {
  editingProduct.value = p
  // Toma solo la primera variante para editar
  const v = p.variants?.[0] ? { ...p.variants[0] } : emptyVariant()
  form.value = { ...p, variants: [v] }
  notesInput.value = p.olfactory_notes?.join(', ') || ''
  showCreate.value = false
}

function closePanel() {
  showCreate.value = false
  editingProduct.value = null
  formError.value = ''
  form.value = emptyForm()
  notesInput.value = ''
}

function hasLowStock(product) {
  return product.variants?.some(v => v.stock < 5) ?? false
}

async function handleSubmit() {
  formLoading.value = true
  formError.value = ''
  try {
    const v = mainVariant.value
    const cleanVariant = {
      id: v.id || undefined,
      size_ml: Number(v.size_ml) || 50,
      price: Number(v.price) || 0,
      compare_at_price: v.compare_at_price != null && v.compare_at_price !== ''
        ? Number(v.compare_at_price) : null,
      stock: Number(v.stock) || 0,
      sku: v.sku || undefined,
    }
    const payload = {
      ...form.value,
      variants: [cleanVariant],
      olfactory_notes: notesInput.value.split(',').map(n => n.trim()).filter(Boolean),
    }
    if (editingProduct.value) {
      await api.put(`/products/${editingProduct.value.id}`, payload)
    } else {
      await api.post('/products', payload)
    }
    closePanel()
    await load()
  } catch (e) {
    const detail = e.response?.data?.detail
    formError.value = Array.isArray(detail)
      ? detail.map(d => d.msg).join(', ')
      : (detail || 'Error al guardar el producto')
  } finally {
    formLoading.value = false
  }
}

async function deleteProduct(id) {
  if (!confirm('¿Eliminar este producto?')) return
  try {
    await api.delete(`/products/${id}`)
    await load()
  } catch (e) {
    alert(e.response?.data?.detail || 'Error al eliminar el producto')
  }
}

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/products', {
      params: { page: page.value, per_page: 15, search: search.value || undefined, status: undefined },
    })
    products.value = data.items
    total.value = data.total
    pages.value = data.pages
  } finally {
    loading.value = false
  }
}

watch([page, search], () => load())

onMounted(async () => {
  const [b, c] = await Promise.all([api.get('/brands'), api.get('/categories')])
  brands.value = b.data
  categories.value = c.data
  await load()
})
</script>

<style scoped>
.slide-enter-active, .slide-leave-active { transition: transform 0.3s ease; }
.slide-enter-from, .slide-leave-to { transform: translateX(100%); }
</style>
