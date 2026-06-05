<template>
  <div class="min-h-screen bg-white">
    <Header />
    <div class="pt-36 max-w-7xl mx-auto px-6 py-16">
      <div v-if="loading" class="grid grid-cols-2 gap-16">
        <div class="aspect-square bg-gray-200 animate-pulse" />
        <div class="space-y-4">
          <div class="h-6 bg-gray-200 animate-pulse w-1/2" />
          <div class="h-10 bg-gray-200 animate-pulse" />
        </div>
      </div>

      <div v-else-if="product" class="grid grid-cols-1 md:grid-cols-2 gap-16">
        <!-- Images -->
        <div>
          <div class="aspect-square bg-gray-100 overflow-hidden mb-4">
            <img v-if="product.images?.[selectedImage]"
              :src="product.images[selectedImage]"
              :alt="product.name"
              class="w-full h-full object-cover" />
            <div v-else class="w-full h-full flex items-center justify-center">
              <span class="text-gray-500 text-xs tracking-widest uppercase">Imagen pendiente</span>
            </div>
          </div>
          <div v-if="product.images?.length > 1" class="flex gap-3">
            <div v-for="(img, i) in product.images" :key="i"
              @click="selectedImage = i"
              class="w-20 h-20 bg-gray-100 cursor-pointer border-2 transition-colors overflow-hidden"
              :class="i === selectedImage ? 'border-gold' : 'border-transparent hover:border-gray-300'">
              <img :src="img" :alt="`${product.name} ${i+1}`" class="w-full h-full object-cover" />
            </div>
          </div>
        </div>

        <!-- Info -->
        <div>
          <div class="mb-2">
            <router-link :to="`/shop?brand=${product.brand_id}`"
              class="text-[10px] tracking-widest uppercase text-gold hover:underline">
              {{ product.brand_name }}
            </router-link>
          </div>
          <h1 class="font-display text-5xl text-gray-900 mb-2">{{ product.name }}</h1>

          <!-- Bundle badge -->
          <div v-if="product?.is_bundle" class="border border-[#c9a84c]/30 bg-[#c9a84c]/5 p-4 my-4">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-xs bg-[#c9a84c] text-black px-2 py-0.5 tracking-widest font-bold uppercase">GIFT SET</span>
              <span class="text-sm text-[#c9a84c]">{{ $t('product.bundle_label') }}</span>
            </div>
            <p class="text-sm text-gray-700">{{ $t('product.bundle_includes') }}</p>
          </div>

          <!-- Rating -->
          <div v-if="product.review_count > 0" class="flex items-center gap-2 mb-6">
            <div class="flex gap-0.5">
              <svg v-for="i in 5" :key="i" class="w-4 h-4"
                :class="i <= Math.round(product.average_rating) ? 'fill-gold text-gold' : 'fill-gray-200 text-gray-200'"
                viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
              </svg>
            </div>
            <span class="text-gray-700 text-xs">{{ product.average_rating }} ({{ product.review_count }} reseñas)</span>
          </div>

          <!-- Price -->
          <p class="font-display text-4xl text-gray-900 mb-8">
            {{ selectedVariant?.price != null ? formatCOP(selectedVariant.price) : '—' }}
          </p>

          <!-- Olfactory notes -->
          <div v-if="product.olfactory_notes?.length" class="mb-8">
            <p class="text-[10px] tracking-widest uppercase text-gray-700 mb-3">{{ $t('product.olfactory_notes') }}</p>
            <div class="flex gap-2 flex-wrap">
              <span v-for="note in product.olfactory_notes" :key="note"
                class="border border-gray-300 text-gray-700 text-[10px] tracking-widest uppercase px-3 py-1">
                {{ note }}
              </span>
            </div>
          </div>

          <!-- Size selector -->
          <div class="mb-6">
            <p class="text-[10px] tracking-widest uppercase text-gray-700 mb-3">{{ $t('product.size') }}</p>
            <div class="flex gap-3">
              <button v-for="v in product.variants" :key="v.id"
                @click="selectedVariantId = v.id"
                class="px-4 py-2 text-sm border transition-colors"
                :class="v.id === selectedVariantId
                  ? 'border-gold bg-gold text-white'
                  : v.stock === 0
                    ? 'border-gray-300 text-gray-400 opacity-40 cursor-not-allowed'
                    : 'border-gray-300 text-gray-700 hover:border-gold hover:text-gold'"
                :disabled="v.stock === 0">
                {{ v.size_ml }}ml
              </button>
            </div>
          </div>

          <!-- Quantity -->
          <div class="flex items-center gap-4 mb-8">
            <p class="text-[10px] tracking-widest uppercase text-gray-700">{{ $t('product.quantity') }}</p>
            <div class="flex items-center border border-gray-300">
              <button @click="qty = Math.max(1, qty - 1)"
                class="w-10 h-10 flex items-center justify-center text-gray-500 hover:text-gray-900 transition-colors">
                −
              </button>
              <span class="w-10 text-center text-gray-900 text-sm">{{ qty }}</span>
              <button @click="qty++"
                class="w-10 h-10 flex items-center justify-center text-gray-500 hover:text-gray-900 transition-colors">
                +
              </button>
            </div>
          </div>

          <!-- Add to cart -->
          <button @click="handleAddToCart"
            :disabled="!selectedVariant || selectedVariant.stock === 0"
            class="btn-gold w-full py-4 disabled:opacity-40">
            {{ selectedVariant?.stock === 0 ? $t('shop.out_of_stock') : $t('product.add_to_cart') }}
          </button>

          <!-- Description -->
          <div v-if="product.description" class="mt-10 pt-8 border-t border-gray-200">
            <p class="text-[10px] tracking-widest uppercase text-gray-700 mb-4">{{ $t('product.description') }}</p>
            <p class="text-gray-700 leading-relaxed text-sm">{{ product.description }}</p>
          </div>
        </div>
      </div>

      <!-- Reviews section -->
      <div v-if="product" class="mt-20 border-t border-gray-200 pt-16">

        <!-- Header con resumen de rating -->
        <div class="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 mb-12">
          <div>
            <p class="text-[10px] tracking-[4px] uppercase text-gold mb-2">Opiniones</p>
            <h2 class="font-display text-3xl text-gray-900">{{ $t('product.reviews') }}</h2>
          </div>
          <div v-if="reviews.length > 0" class="flex items-center gap-4">
            <div class="text-right">
              <p class="font-display text-4xl text-gray-900 leading-none">
                {{ (reviews.reduce((s, r) => s + r.rating, 0) / reviews.length).toFixed(1) }}
              </p>
              <p class="text-xs text-gray-400 mt-1">de 5 · {{ reviews.length }} {{ reviews.length === 1 ? 'reseña' : 'reseñas' }}</p>
            </div>
            <div class="flex flex-row gap-0.5">
              <svg v-for="i in 5" :key="i" class="w-5 h-5"
                :class="i <= Math.round(reviews.reduce((s, r) => s + r.rating, 0) / reviews.length) ? 'fill-gold text-gold' : 'fill-gray-200 text-gray-200'"
                viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
              </svg>
            </div>
          </div>
        </div>

        <!-- Grid de tarjetas de reseñas -->
        <div class="mb-16">
          <!-- Sin reseñas -->
          <div v-if="reviews.length === 0" class="text-center py-16 border border-dashed border-gray-200">
            <svg class="w-10 h-10 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
            </svg>
            <p class="text-gray-400 text-sm">{{ $t('product.no_reviews') }}</p>
            <p class="text-gray-300 text-xs mt-1">Sé el primero en compartir tu experiencia</p>
          </div>

          <!-- Cards grid -->
          <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div
              v-for="review in reviews"
              :key="review.id"
              class="bg-white border border-gray-100 rounded-sm shadow-sm hover:shadow-md transition-shadow duration-300 overflow-hidden"
            >
              <!-- Franja dorada superior -->
              <div class="h-0.5 bg-gradient-to-r from-gold via-gold-light to-transparent"></div>

              <div class="p-6">
                <!-- Cabecera: avatar + info + estrellas -->
                <div class="flex items-start justify-between gap-3 mb-5">
                  <div class="flex items-center gap-3">
                    <!-- Avatar con inicial -->
                    <div class="w-10 h-10 rounded-full bg-gradient-to-br from-gold/20 to-gold/5 border border-gold/20 flex items-center justify-center shrink-0">
                      <span class="font-display text-gold text-base font-semibold">
                        {{ review.user_name?.[0]?.toUpperCase() || '?' }}
                      </span>
                    </div>
                    <div>
                      <p class="text-sm font-semibold text-gray-900 leading-tight">{{ review.user_name }}</p>
                      <p v-if="review.created_at" class="text-[10px] text-gray-400 mt-0.5 tracking-wide">
                        {{ new Date(review.created_at).toLocaleDateString('es-CO', { day: '2-digit', month: 'long', year: 'numeric' }) }}
                      </p>
                    </div>
                  </div>
                  <!-- Estrellas -->
                  <div class="flex gap-0.5 shrink-0 mt-0.5">
                    <svg v-for="i in 5" :key="i" class="w-3.5 h-3.5"
                      :class="i <= review.rating ? 'fill-gold text-gold' : 'fill-gray-200 text-gray-200'"
                      viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                    </svg>
                  </div>
                </div>

                <!-- Separador con acento -->
                <div class="flex items-center gap-3 mb-4">
                  <div class="w-6 h-px bg-gold"></div>
                  <div class="flex-1 h-px bg-gray-100"></div>
                </div>

                <!-- Título de la reseña -->
                <p v-if="review.title" class="text-gray-900 font-semibold text-sm mb-2 leading-snug">
                  "{{ review.title }}"
                </p>

                <!-- Cuerpo -->
                <p class="text-gray-600 text-sm leading-relaxed">{{ review.body }}</p>

                <!-- Imágenes -->
                <div v-if="review.images?.length" class="flex gap-2 mt-4 flex-wrap">
                  <img
                    v-for="(imgUrl, i) in review.images"
                    :key="i"
                    :src="imgUrl"
                    :alt="`Foto de reseña ${i+1}`"
                    class="w-16 h-16 object-cover rounded-sm border border-gray-200 cursor-pointer hover:border-gold hover:scale-105 transition-all duration-200"
                    @click="lightboxImage = imgUrl"
                  />
                </div>

                <!-- Footer: verificado -->
                <div class="mt-5 pt-4 border-t border-gray-50 flex items-center gap-1.5">
                  <svg class="w-3.5 h-3.5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
                  </svg>
                  <span class="text-[10px] text-emerald-600 tracking-widest uppercase font-medium">Compra verificada</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Formulario de reseña -->
        <div class="border border-gray-200 rounded-sm overflow-hidden">
          <!-- Header del form -->
          <div class="bg-gray-50 border-b border-gray-200 px-8 py-5 flex items-center gap-3">
            <div class="w-1 h-6 bg-gold"></div>
            <h3 class="font-display text-xl text-gray-900">{{ $t('product.write_review') }}</h3>
          </div>

          <form @submit.prevent="submitReview" class="p-8 space-y-6 bg-white">

            <!-- Rating con etiqueta descriptiva -->
            <div>
              <p class="text-[10px] tracking-widest text-gray-500 uppercase mb-3">Tu calificación</p>
              <div class="flex items-center gap-2">
                <div class="flex gap-1">
                  <button
                    v-for="i in 5"
                    :key="i"
                    type="button"
                    @click="reviewForm.rating = i"
                    class="w-9 h-9 transition-all duration-150 hover:scale-110"
                    :class="i <= reviewForm.rating ? 'text-gold' : 'text-gray-300 hover:text-gold'"
                  >
                    <svg class="w-full h-full" :class="i <= reviewForm.rating ? 'fill-gold' : 'fill-gray-200'" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                    </svg>
                  </button>
                </div>
                <span class="text-xs text-gray-400 ml-1">
                  {{ ['', 'Muy malo', 'Malo', 'Regular', 'Bueno', 'Excelente'][reviewForm.rating] }}
                </span>
              </div>
            </div>

            <div class="grid grid-cols-1 gap-5">
              <!-- Título -->
              <div>
                <label class="block text-[10px] tracking-widest text-gray-500 uppercase mb-2">Título de tu reseña</label>
                <input
                  v-model="reviewForm.title"
                  type="text"
                  class="w-full bg-white border border-gray-200 text-gray-900 text-sm px-4 py-3 focus:outline-none focus:border-gold transition-colors rounded-sm placeholder-gray-300"
                  placeholder="Resume tu experiencia en una línea"
                />
              </div>

              <!-- Comentario -->
              <div>
                <label class="block text-[10px] tracking-widest text-gray-500 uppercase mb-2">Tu comentario</label>
                <textarea
                  v-model="reviewForm.body"
                  rows="4"
                  class="w-full bg-white border border-gray-200 text-gray-900 text-sm px-4 py-3 focus:outline-none focus:border-gold transition-colors resize-none rounded-sm placeholder-gray-300"
                  placeholder="Cuéntanos cómo es la fragancia, su durabilidad, proyección..."
                ></textarea>
              </div>
            </div>

            <!-- Fotos -->
            <div>
              <label class="block text-[10px] tracking-widest text-gray-500 uppercase mb-3">{{ $t('product.add_review_photos') }}</label>
              <div class="flex gap-3 flex-wrap">
                <div
                  v-for="(img, i) in reviewImages"
                  :key="i"
                  class="relative w-20 h-20 group shrink-0"
                >
                  <img :src="img.preview" class="w-full h-full object-cover rounded-sm border border-gray-200"/>
                  <button
                    type="button"
                    @click="removeReviewImage(i)"
                    class="absolute -top-1.5 -right-1.5 w-5 h-5 bg-red-500 text-white rounded-full text-xs flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity shadow-sm leading-none"
                  >×</button>
                </div>
                <label
                  v-if="reviewImages.length < 3"
                  class="w-20 h-20 border border-dashed border-gray-300 hover:border-gold bg-gray-50 hover:bg-gold/5 flex flex-col items-center justify-center text-gray-400 hover:text-gold cursor-pointer transition-all rounded-sm shrink-0"
                >
                  <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4v16m8-8H4"/>
                  </svg>
                  <span class="text-[10px] mt-1 tracking-wide">{{ $t('product.add_photo') }}</span>
                  <input type="file" accept="image/jpeg,image/png,image/webp" multiple class="hidden" @change="handleReviewImageUpload"/>
                </label>
              </div>
              <p class="text-[10px] text-gray-400 mt-2">{{ $t('product.review_photo_hint') }}</p>
            </div>

            <!-- Submit -->
            <div class="flex items-center justify-between pt-2 border-t border-gray-100">
              <p class="text-xs text-gray-400">Tu reseña aparecerá de inmediato</p>
              <button type="submit" :disabled="reviewSubmitting || !reviewForm.body" class="btn-gold px-8 py-3 disabled:opacity-40 flex items-center gap-2">
                <svg v-if="reviewSubmitting" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
                {{ reviewSubmitting ? 'Publicando...' : $t('product.write_review') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Related Products -->
    <div class="max-w-7xl mx-auto px-6 pb-16">
      <section v-if="relatedProducts.length > 0" class="mt-16 border-t border-gray-200 pt-12">
        <h2 class="text-xl tracking-widest text-gray-900 uppercase mb-8">{{ $t('product.related_products') }}</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div
            v-for="p in relatedProducts.slice(0, 4)"
            :key="p.id"
            class="group"
          >
            <RouterLink :to="`/product/${p.id}`">
              <div class="aspect-square overflow-hidden bg-gray-100 mb-3">
                <img
                  v-if="p.images && p.images[0]"
                  :src="p.images[0]"
                  :alt="p.name"
                  class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                  <svg class="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                  </svg>
                </div>
              </div>
              <p class="text-xs text-gray-600 mb-1">{{ p.brand_name }}</p>
              <p class="text-sm text-gray-900 group-hover:text-[#c9a84c] transition-colors">{{ p.name }}</p>
              <p v-if="p.variants && p.variants[0]" class="text-[#c9a84c] text-sm mt-1">{{ formatCOP(p.variants[0].price) }}</p>
            </RouterLink>
          </div>
        </div>
      </section>

      <!-- Fragrance Profile Recommendations -->
      <section v-if="fragranceProfile.length > 0" class="mt-12 border-t border-gray-200 pt-12">
        <h2 class="text-xl tracking-widest text-gray-900 uppercase mb-2">{{ $t('product.if_you_like') }}</h2>
        <p class="text-sm text-gray-600 mb-8">{{ $t('product.fragrance_match_subtitle', { name: product?.name }) }}</p>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div
            v-for="p in fragranceProfile"
            :key="p.id"
            class="group relative"
          >
            <RouterLink :to="`/product/${p.id}`">
              <div class="absolute top-2 left-2 z-10 bg-[#c9a84c] text-black text-xs px-2 py-0.5 font-bold">
                {{ p.match_pct }}% match
              </div>
              <div class="aspect-square overflow-hidden bg-gray-100 mb-3">
                <img
                  v-if="p.primary_image"
                  :src="p.primary_image"
                  :alt="p.name"
                  class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <div v-else class="w-full h-full bg-gray-200"></div>
              </div>
              <p class="text-xs text-gray-600 mb-1">{{ p.brand }}</p>
              <p class="text-sm text-gray-900 group-hover:text-[#c9a84c] transition-colors">{{ p.name }}</p>
              <p v-if="p.price" class="text-[#c9a84c] text-sm mt-1">{{ formatCOP(p.price) }}</p>
              <p v-if="p.common_notes?.length" class="text-xs text-gray-500 mt-1 capitalize">
                {{ p.common_notes.slice(0, 2).join(' · ') }}
              </p>
            </RouterLink>
          </div>
        </div>
      </section>
    </div>

    <Footer />

    <!-- Lightbox -->
    <div
      v-if="lightboxImage"
      class="fixed inset-0 bg-black/90 flex items-center justify-center z-50"
      @click="lightboxImage = null"
    >
      <img
        :src="lightboxImage"
        class="max-w-full max-h-[90vh] object-contain"
        @click.stop
      />
      <button
        @click="lightboxImage = null"
        class="absolute top-4 right-4 text-white hover:text-[#c9a84c] transition-colors"
      >
        <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Header from '../components/layout/Header.vue'
import Footer from '../components/layout/Footer.vue'
import { useCartStore } from '../stores/cart'
import { formatCOP } from '../utils/currency'
import api from '../router/api'

const route = useRoute()
const cart = useCartStore()
const { t } = useI18n()

const product = ref(null)
const loading = ref(true)
const selectedImage = ref(0)
const selectedVariantId = ref(null)
const qty = ref(1)
const relatedProducts = ref([])
const fragranceProfile = ref([])

// Reviews state
const reviews = ref([])
const reviewSubmitting = ref(false)
const reviewForm = ref({ rating: 5, title: '', body: '' })

// Review photo upload state
const reviewImages = ref([])  // array of { preview: string, url: string }
const lightboxImage = ref(null)

const selectedVariant = computed(() =>
  product.value?.variants?.find(v => v.id === selectedVariantId.value)
)

function handleAddToCart() {
  if (product.value && selectedVariant.value) {
    cart.addItem(product.value, selectedVariant.value, qty.value)
  }
}

async function loadRelated(productId) {
  try {
    const { data } = await api.get(`/products/${productId}/related`)
    relatedProducts.value = data.items || []
  } catch {
    relatedProducts.value = []
  }
}

async function loadFragranceProfile(productId) {
  try {
    const { data } = await api.get(`/products/${productId}/fragrance-profile`)
    fragranceProfile.value = data || []
  } catch {
    fragranceProfile.value = []
  }
}

async function loadReviews(productId) {
  try {
    const { data } = await api.get(`/reviews/product/${productId}`)
    reviews.value = data.items || data || []
  } catch {
    reviews.value = []
  }
}

async function handleReviewImageUpload(event) {
  const files = Array.from(event.target.files || [])
  for (const file of files) {
    if (reviewImages.value.length >= 3) break
    if (file.size > 2 * 1024 * 1024) {
      alert(t('product.review_image_too_large'))
      continue
    }
    const formData = new FormData()
    formData.append('file', file)
    try {
      const { data } = await api.post('/upload/review-image', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      const preview = URL.createObjectURL(file)
      reviewImages.value.push({ preview, url: data.url })
    } catch {
      alert(t('product.review_image_upload_error'))
    }
  }
  // Reset the input so the same file can be selected again
  event.target.value = ''
}

function removeReviewImage(index) {
  URL.revokeObjectURL(reviewImages.value[index].preview)
  reviewImages.value.splice(index, 1)
}

async function submitReview() {
  if (!reviewForm.value.rating || !reviewForm.value.body) return
  reviewSubmitting.value = true
  try {
    await api.post('/reviews', {
      product_id: product.value.id,
      rating: reviewForm.value.rating,
      title: reviewForm.value.title,
      body: reviewForm.value.body,
      images: reviewImages.value.map(i => i.url)
    })
    reviewForm.value = { rating: 5, title: '', body: '' }
    reviewImages.value = []
    await loadReviews(product.value.id)
  } catch {
    // silently fail; backend returns validation errors
  } finally {
    reviewSubmitting.value = false
  }
}

onMounted(async () => {
  try {
    const id = route.params.id
    const { data } = await api.get(`/products/${id}`)
    product.value = data
    if (data.variants?.length) {
      selectedVariantId.value = data.variants[0].id
    }
    await Promise.all([loadRelated(id), loadFragranceProfile(id), loadReviews(id)])
  } finally {
    loading.value = false
  }
})
</script>
