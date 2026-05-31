<template>
  <div class="min-h-screen bg-white">
    <Header />
    <div class="pt-24 min-h-screen">
      <div class="max-w-5xl mx-auto px-6 py-10 grid grid-cols-1 md:grid-cols-[240px_1fr] gap-8">

        <!-- Sidebar -->
        <aside class="bg-white border border-gray-200 rounded-sm p-5 self-start sticky top-24 shadow-sm">
          <div class="mb-5 pb-4 border-b border-gray-100">
            <div class="w-12 h-12 rounded-full bg-gold/10 border-2 border-gold flex items-center justify-center mx-auto mb-3">
              <span class="text-gold font-bold text-lg">{{ auth.user?.first_name?.[0]?.toUpperCase() }}</span>
            </div>
            <p class="text-center text-sm font-medium text-[#111010]">{{ auth.user?.first_name }} {{ auth.user?.last_name }}</p>
            <p class="text-center text-xs text-gray-400 mt-0.5">{{ auth.user?.email }}</p>
          </div>
          <nav class="space-y-0.5">
            <button v-for="item in menuItems" :key="item.tab"
              @click="activeTab = item.tab"
              class="w-full flex items-center gap-2.5 px-3 py-2.5 text-sm text-left transition-colors rounded-sm"
              :class="activeTab === item.tab
                ? 'bg-gold/10 text-gold font-medium border-l-2 border-gold'
                : 'text-gray-600 hover:text-[#111010] hover:bg-gray-50'">
              <span class="text-base">{{ item.icon }}</span>
              {{ $t(item.i18n) }}
            </button>
          </nav>
          <button @click="handleLogout"
            class="mt-5 w-full border border-gray-300 text-gray-600 py-2 text-xs tracking-widest uppercase hover:border-red-400 hover:text-red-500 transition-colors rounded-sm">
            Cerrar Sesión
          </button>
        </aside>

        <!-- Contenido principal -->
        <main>

          <!-- ── TAB: PERFIL ────────────────────────────────────── -->
          <div v-if="activeTab === 'profile'">
            <h1 class="font-display text-3xl text-[#111010] mb-1">
              Hola, <span class="text-gold">{{ auth.user?.first_name }}</span>
            </h1>
            <p class="text-gray-500 text-sm mb-8">{{ $t('account.profile_subtitle') }}</p>

            <!-- Último pedido -->
            <div class="bg-white border border-gray-200 rounded-sm p-6 mb-6 shadow-sm">
              <div class="flex items-center justify-between mb-4">
                <h2 class="text-[10px] tracking-widest uppercase text-gray-400">Último Pedido</h2>
                <button v-if="lastOrder" @click="activeTab = 'orders'" class="text-xs text-gold hover:underline">Ver todos →</button>
              </div>

              <!-- Sin pedidos -->
              <div v-if="!lastOrder" class="text-center py-8">
                <p class="text-gray-400 text-sm mb-4">Aún no has realizado ningún pedido.</p>
                <router-link to="/shop" class="btn-gold text-xs">Ir a la tienda</router-link>
              </div>

              <!-- Con pedido -->
              <div v-else>
                <div class="flex items-start justify-between gap-4 mb-4">
                  <div>
                    <p class="font-display text-xl text-gold">#AROMA-{{ lastOrder.order_number }}</p>
                    <p class="text-xs text-gray-400 mt-0.5">{{ formatDate(lastOrder.created_at) }}</p>
                  </div>
                  <span class="px-3 py-1 rounded-full text-xs font-medium" :class="statusBadgeClass(lastOrder.status)">
                    {{ statusLabel(lastOrder.status) }}
                  </span>
                </div>

                <!-- Miniaturas -->
                <div v-if="lastOrder.items?.length" class="flex gap-2 mb-4">
                  <div v-for="item in lastOrder.items.slice(0, 4)" :key="item.id"
                    class="w-10 h-10 bg-gray-100 border border-gray-200 rounded overflow-hidden shrink-0">
                    <img v-if="item.image" :src="item.image" :alt="item.product_name" class="w-full h-full object-cover" />
                    <div v-else class="w-full h-full flex items-center justify-center text-gray-300 text-xs">🧴</div>
                  </div>
                  <div v-if="lastOrder.items.length > 4"
                    class="w-10 h-10 bg-gray-100 border border-gray-200 rounded flex items-center justify-center text-xs text-gray-400 font-medium">
                    +{{ lastOrder.items.length - 4 }}
                  </div>
                </div>

                <!-- Tracking -->
                <div v-if="lastOrder.tracking_number" class="bg-blue-50 border border-blue-200 rounded p-3 mb-4 text-xs">
                  <p class="text-blue-600 font-medium mb-0.5">En tránsito</p>
                  <p class="text-blue-500">{{ lastOrder.tracking_company }} · <span class="font-mono">{{ lastOrder.tracking_number }}</span></p>
                </div>

                <div class="flex items-center justify-between">
                  <p class="text-lg font-bold text-[#111010]">{{ formatCOP(lastOrder.total) }}</p>
                  <div class="flex gap-2">
                    <button @click="activeTab = 'orders'" class="text-xs border border-gold text-gold px-3 py-1.5 hover:bg-gold/10 transition-colors rounded-sm">
                      Ver detalle
                    </button>
                    <router-link v-if="lastOrder.status === 'delivered'" to="/shop"
                      class="text-xs bg-gold text-white px-3 py-1.5 hover:bg-gold-dark transition-colors rounded-sm">
                      Comprar de nuevo
                    </router-link>
                  </div>
                </div>
              </div>
            </div>

            <!-- Stats row -->
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
              <!-- Puntos -->
              <div class="bg-white border border-gray-200 rounded-sm p-5 text-center shadow-sm cursor-pointer hover:border-gold transition-colors" @click="activeTab = 'loyalty'">
                <div class="text-2xl mb-1">⭐</div>
                <p class="font-display text-2xl text-[#111010]">{{ (auth.user?.loyalty_points || 0).toLocaleString() }}</p>
                <p class="text-[10px] tracking-widest uppercase text-gray-400 mt-1">Puntos</p>
              </div>

              <!-- Total pedidos -->
              <div class="bg-white border border-gray-200 rounded-sm p-5 text-center shadow-sm cursor-pointer hover:border-gold transition-colors" @click="activeTab = 'orders'">
                <div class="text-2xl mb-1">📦</div>
                <p class="font-display text-2xl text-[#111010]">{{ orders.length }}</p>
                <p class="text-[10px] tracking-widest uppercase text-gray-400 mt-1">Pedidos</p>
              </div>

              <!-- Wishlist -->
              <div class="bg-white border border-gray-200 rounded-sm p-5 text-center shadow-sm cursor-pointer hover:border-gold transition-colors" @click="activeTab = 'wishlist'">
                <div class="text-2xl mb-1">❤️</div>
                <p class="font-display text-2xl text-[#111010]">{{ wishlistItems.length }}</p>
                <p class="text-[10px] tracking-widest uppercase text-gray-400 mt-1">Favoritos</p>
              </div>
            </div>

            <!-- Dirección predeterminada -->
            <div class="bg-white border border-gray-200 rounded-sm p-6 shadow-sm">
              <div class="flex items-center justify-between mb-4">
                <h2 class="text-[10px] tracking-widest uppercase text-gray-400">Dirección Predeterminada</h2>
                <button @click="activeTab = 'addresses'" class="text-xs text-gold hover:underline">Gestionar →</button>
              </div>
              <div v-if="defaultAddress" class="border border-gold/30 bg-gold/5 rounded-sm p-4">
                <div class="flex items-center gap-2 mb-2">
                  <span class="text-xs bg-gold text-white px-2 py-0.5 rounded-full">★ Predeterminada</span>
                  <span class="text-xs text-gray-500 uppercase tracking-widest">{{ defaultAddress.label }}</span>
                </div>
                <p class="text-sm text-[#111010] font-medium">{{ defaultAddress.first_name }} {{ defaultAddress.last_name }}</p>
                <p class="text-sm text-gray-500 leading-relaxed mt-1">
                  {{ defaultAddress.address }}<br>
                  {{ defaultAddress.city }}<span v-if="defaultAddress.state">, {{ defaultAddress.state }}</span> {{ defaultAddress.postal_code }}<br>
                  {{ defaultAddress.country }}
                </p>
                <p v-if="defaultAddress.phone" class="text-xs text-gray-400 mt-1">📱 {{ defaultAddress.phone }}</p>
              </div>
              <div v-else class="text-center py-6 text-gray-400">
                <p class="text-sm mb-3">No tienes dirección predeterminada.</p>
                <button @click="activeTab = 'addresses'; openNewAddress()"
                  class="text-xs text-gold border border-gold/30 px-4 py-2 hover:bg-gold/10 transition-colors rounded-sm">
                  + Agregar dirección
                </button>
              </div>
            </div>
          </div>

          <!-- ── TAB: PEDIDOS ───────────────────────────────────── -->
          <div v-if="activeTab === 'orders'">
            <h2 class="font-display text-2xl text-[#111010] mb-6">Mis Pedidos</h2>
            <div v-if="loadingOrders" class="space-y-3">
              <div v-for="i in 3" :key="i" class="h-20 bg-gray-100 animate-pulse rounded-sm" />
            </div>
            <div v-else-if="orders.length === 0" class="text-center py-16 text-gray-400">
              <p class="text-4xl mb-4">📦</p>
              <p class="text-sm mb-6">Aún no has realizado ningún pedido. ¡Descubre nuestras fragancias!</p>
              <router-link to="/shop" class="btn-gold text-xs">Ir a la tienda</router-link>
            </div>
            <div v-else class="space-y-4">
              <div v-for="order in orders" :key="order.id"
                class="bg-white border border-gray-200 rounded-sm p-5 shadow-sm hover:border-gray-300 transition-colors">
                <div class="flex items-center justify-between gap-4 mb-3">
                  <div>
                    <p class="font-medium text-[#111010]">#AROMA-{{ order.order_number }}</p>
                    <p class="text-xs text-gray-400 mt-0.5">{{ formatDate(order.created_at) }}</p>
                  </div>
                  <div class="flex items-center gap-3">
                    <span class="text-sm font-bold text-[#111010]">{{ formatCOP(order.total) }}</span>
                    <span class="px-2.5 py-1 rounded-full text-xs font-medium" :class="statusBadgeClass(order.status)">
                      {{ statusLabel(order.status) }}
                    </span>
                  </div>
                </div>
                <div v-if="order.tracking_number" class="bg-blue-50 border border-blue-200 rounded p-3 mt-3 text-xs">
                  <p class="text-blue-600 font-medium">🚚 {{ order.tracking_company }} · <span class="font-mono">{{ order.tracking_number }}</span></p>
                  <a v-if="order.tracking_url" :href="order.tracking_url" target="_blank"
                    class="text-blue-500 underline mt-1 inline-block">Rastrear paquete →</a>
                </div>
                <button v-if="order.status === 'delivered'" @click="openReturnForm(order.id)"
                  class="text-xs text-gray-400 border border-gray-200 px-3 py-1.5 hover:border-gray-400 hover:text-gray-600 transition-colors mt-3 rounded-sm">
                  Solicitar devolución
                </button>
              </div>
            </div>
          </div>

          <!-- ── TAB: DIRECCIONES ───────────────────────────────── -->
          <div v-if="activeTab === 'addresses'">
            <div class="flex items-center justify-between mb-6">
              <h2 class="font-display text-2xl text-[#111010]">Mis Direcciones</h2>
              <button @click="openNewAddress"
                class="text-xs text-gold border border-gold/40 px-4 py-2 hover:bg-gold/10 transition-colors rounded-sm">
                + Agregar dirección
              </button>
            </div>
            <div v-if="addressLoading" class="text-center py-8 text-gray-400 text-sm">Cargando...</div>
            <div v-else-if="addresses.length === 0" class="text-center py-12 text-gray-400 text-sm">
              No tienes direcciones guardadas.
            </div>
            <div v-else class="grid gap-4 sm:grid-cols-2">
              <div v-for="addr in addresses" :key="addr.id"
                class="border rounded-sm p-5"
                :class="addr.is_default ? 'border-gold/50 bg-gold/5' : 'border-gray-200 bg-white'">
                <div class="flex items-start justify-between gap-2 mb-3">
                  <div class="flex items-center gap-2">
                    <span class="text-xs text-gray-400 uppercase tracking-widest">{{ addr.label }}</span>
                    <span v-if="addr.is_default" class="text-xs bg-gold text-white px-2 py-0.5 rounded-full">★ Principal</span>
                  </div>
                  <div class="flex gap-2">
                    <button @click="openEditAddress(addr)" class="text-xs text-gray-400 hover:text-[#111010] transition-colors">Editar</button>
                    <button @click="deleteAddress(addr.id)" class="text-xs text-red-400 hover:text-red-600 transition-colors">Eliminar</button>
                  </div>
                </div>
                <p v-if="addr.first_name" class="text-sm text-[#111010] font-medium">{{ addr.first_name }} {{ addr.last_name }}</p>
                <p class="text-sm text-gray-500 leading-relaxed mt-1">
                  {{ addr.address }}<br>{{ addr.city }}<span v-if="addr.state">, {{ addr.state }}</span> {{ addr.postal_code }}<br>{{ addr.country }}
                </p>
                <p v-if="addr.phone" class="text-xs text-gray-400 mt-1">{{ addr.phone }}</p>
                <button v-if="!addr.is_default" @click="setDefaultAddress(addr.id)"
                  class="text-xs text-gold hover:underline mt-3 block">
                  Establecer como principal
                </button>
              </div>
            </div>

            <!-- Modal dirección -->
            <div v-if="showAddressForm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 px-4" @click.self="showAddressForm = false">
              <div class="bg-white rounded-sm p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto shadow-xl">
                <h3 class="font-display text-xl text-[#111010] mb-5">
                  {{ editingAddress ? 'Editar dirección' : 'Nueva dirección' }}
                </h3>
                <form @submit.prevent="saveAddress" class="space-y-3">
                  <div>
                    <label class="block text-xs tracking-widest text-gray-500 mb-1 uppercase">Etiqueta</label>
                    <input v-model="addressForm.label" type="text" required
                      class="w-full border border-gray-300 text-[#111010] px-3 py-2.5 text-sm focus:border-gold focus:outline-none rounded-sm"/>
                  </div>
                  <div class="grid grid-cols-2 gap-3">
                    <div>
                      <label class="block text-xs tracking-widest text-gray-500 mb-1 uppercase">Nombre</label>
                      <input v-model="addressForm.first_name" type="text"
                        class="w-full border border-gray-300 text-[#111010] px-3 py-2.5 text-sm focus:border-gold focus:outline-none rounded-sm"/>
                    </div>
                    <div>
                      <label class="block text-xs tracking-widest text-gray-500 mb-1 uppercase">Apellido</label>
                      <input v-model="addressForm.last_name" type="text"
                        class="w-full border border-gray-300 text-[#111010] px-3 py-2.5 text-sm focus:border-gold focus:outline-none rounded-sm"/>
                    </div>
                  </div>
                  <div>
                    <label class="block text-xs tracking-widest text-gray-500 mb-1 uppercase">Dirección</label>
                    <input v-model="addressForm.address" type="text" required
                      class="w-full border border-gray-300 text-[#111010] px-3 py-2.5 text-sm focus:border-gold focus:outline-none rounded-sm"/>
                  </div>
                  <div class="grid grid-cols-2 gap-3">
                    <div>
                      <label class="block text-xs tracking-widest text-gray-500 mb-1 uppercase">Ciudad</label>
                      <input v-model="addressForm.city" type="text" required
                        class="w-full border border-gray-300 text-[#111010] px-3 py-2.5 text-sm focus:border-gold focus:outline-none rounded-sm"/>
                    </div>
                    <div>
                      <label class="block text-xs tracking-widest text-gray-500 mb-1 uppercase">Departamento</label>
                      <input v-model="addressForm.state" type="text"
                        class="w-full border border-gray-300 text-[#111010] px-3 py-2.5 text-sm focus:border-gold focus:outline-none rounded-sm"/>
                    </div>
                  </div>
                  <div class="grid grid-cols-2 gap-3">
                    <div>
                      <label class="block text-xs tracking-widest text-gray-500 mb-1 uppercase">Código Postal</label>
                      <input v-model="addressForm.postal_code" type="text" required
                        class="w-full border border-gray-300 text-[#111010] px-3 py-2.5 text-sm focus:border-gold focus:outline-none rounded-sm"/>
                    </div>
                    <div>
                      <label class="block text-xs tracking-widest text-gray-500 mb-1 uppercase">País</label>
                      <input v-model="addressForm.country" type="text" required
                        class="w-full border border-gray-300 text-[#111010] px-3 py-2.5 text-sm focus:border-gold focus:outline-none rounded-sm"/>
                    </div>
                  </div>
                  <div>
                    <label class="block text-xs tracking-widest text-gray-500 mb-1 uppercase">Teléfono</label>
                    <input v-model="addressForm.phone" type="text"
                      class="w-full border border-gray-300 text-[#111010] px-3 py-2.5 text-sm focus:border-gold focus:outline-none rounded-sm"/>
                  </div>
                  <label class="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
                    <input v-model="addressForm.is_default" type="checkbox" class="accent-gold"/>
                    Establecer como dirección principal
                  </label>
                  <div class="flex gap-3 pt-2">
                    <button type="submit" class="flex-1 bg-gold text-white py-3 text-sm tracking-widest hover:bg-gold-dark transition-colors rounded-sm">
                      Guardar
                    </button>
                    <button type="button" @click="showAddressForm = false"
                      class="px-6 border border-gray-300 text-gray-600 text-sm hover:border-gray-400 transition-colors rounded-sm">
                      Cancelar
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>

          <!-- ── TAB: MÉTODOS DE PAGO ───────────────────────────── -->
          <div v-if="activeTab === 'payment'">
            <div class="flex items-center justify-between mb-6">
              <h2 class="font-display text-2xl text-[#111010]">Métodos de Pago</h2>
              <button @click="showAddCardForm = true"
                class="text-xs text-gold border border-gold/40 px-4 py-2 hover:bg-gold/10 transition-colors rounded-sm">
                + Agregar tarjeta
              </button>
            </div>
            <div v-if="paymentMethods.length === 0" class="text-center py-16 text-gray-400">
              <p class="text-4xl mb-4">💳</p>
              <p class="text-sm mb-2">No tienes métodos de pago guardados.</p>
              <p class="text-xs text-gray-300 mb-6">Agrega uno para pagos más rápidos.</p>
              <button @click="showAddCardForm = true" class="btn-gold text-xs">Agregar método de pago</button>
            </div>
            <div v-else class="space-y-3">
              <div v-for="pm in paymentMethods" :key="pm.id"
                class="flex items-center justify-between border rounded-sm p-4 bg-white shadow-sm"
                :class="pm.is_default ? 'border-gold/50' : 'border-gray-200'">
                <div class="flex items-center gap-4">
                  <!-- Brand icon -->
                  <div class="w-12 h-8 rounded flex items-center justify-center text-white text-xs font-bold"
                    :class="pm.brand === 'visa' ? 'bg-blue-600' : pm.brand === 'mastercard' ? 'bg-orange-500' : 'bg-gray-600'">
                    {{ pm.brand?.toUpperCase().slice(0, 4) }}
                  </div>
                  <div>
                    <p class="text-sm font-medium text-[#111010]">•••• •••• •••• {{ pm.last4 }}</p>
                    <p class="text-xs text-gray-400">Vence {{ pm.exp_month.toString().padStart(2, '0') }}/{{ pm.exp_year }}</p>
                  </div>
                  <span v-if="pm.is_default" class="text-xs bg-gold text-white px-2 py-0.5 rounded-full">Principal</span>
                </div>
                <div class="flex gap-2">
                  <button v-if="!pm.is_default" @click="setDefaultPM(pm.id)"
                    class="text-xs text-gray-400 hover:text-gold transition-colors border border-gray-200 px-3 py-1.5 rounded-sm hover:border-gold">
                    Principal
                  </button>
                  <button @click="deletePM(pm.id)"
                    class="text-xs text-red-400 hover:text-red-600 transition-colors border border-gray-200 px-3 py-1.5 rounded-sm hover:border-red-400">
                    Eliminar
                  </button>
                </div>
              </div>
            </div>

            <!-- Modal agregar tarjeta (demo sin Stripe Elements) -->
            <div v-if="showAddCardForm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 px-4" @click.self="showAddCardForm = false">
              <div class="bg-white rounded-sm p-6 w-full max-w-md shadow-xl">
                <h3 class="font-display text-xl text-[#111010] mb-5">Agregar Tarjeta</h3>
                <div class="bg-yellow-50 border border-yellow-200 rounded p-3 mb-4 text-xs text-yellow-700">
                  🔒 Los datos de tu tarjeta se procesan de forma segura a través de Stripe. No almacenamos tu información completa.
                </div>
                <form @submit.prevent="addCard" class="space-y-3">
                  <div>
                    <label class="block text-xs text-gray-500 mb-1 uppercase tracking-widest">Número de tarjeta</label>
                    <input v-model="cardForm.number" type="text" placeholder="•••• •••• •••• ••••" maxlength="19" required
                      class="w-full border border-gray-300 text-[#111010] px-3 py-2.5 text-sm focus:border-gold focus:outline-none rounded-sm"/>
                  </div>
                  <div class="grid grid-cols-2 gap-3">
                    <div>
                      <label class="block text-xs text-gray-500 mb-1 uppercase tracking-widest">Vencimiento</label>
                      <input v-model="cardForm.expiry" type="text" placeholder="MM/AA" maxlength="5" required
                        class="w-full border border-gray-300 text-[#111010] px-3 py-2.5 text-sm focus:border-gold focus:outline-none rounded-sm"/>
                    </div>
                    <div>
                      <label class="block text-xs text-gray-500 mb-1 uppercase tracking-widest">CVC</label>
                      <input v-model="cardForm.cvc" type="text" placeholder="123" maxlength="4" required
                        class="w-full border border-gray-300 text-[#111010] px-3 py-2.5 text-sm focus:border-gold focus:outline-none rounded-sm"/>
                    </div>
                  </div>
                  <label class="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
                    <input v-model="cardForm.setDefault" type="checkbox" class="accent-gold"/>
                    Establecer como tarjeta principal
                  </label>
                  <div class="flex gap-3 pt-2">
                    <button type="submit" class="flex-1 bg-gold text-white py-3 text-sm tracking-widest hover:bg-gold-dark transition-colors rounded-sm">
                      Guardar tarjeta
                    </button>
                    <button type="button" @click="showAddCardForm = false"
                      class="px-5 border border-gray-300 text-gray-600 text-sm hover:border-gray-400 transition-colors rounded-sm">
                      Cancelar
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>

          <!-- ── TAB: LISTA DE DESEOS ──────────────────────────── -->
          <div v-if="activeTab === 'wishlist'">
            <h2 class="font-display text-2xl text-[#111010] mb-6">Lista de Deseos</h2>
            <div v-if="loadingWishlist" class="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div v-for="i in 6" :key="i" class="bg-gray-100 animate-pulse aspect-[3/4] rounded-sm" />
            </div>
            <div v-else-if="wishlistItems.length === 0" class="text-center py-16 text-gray-400">
              <p class="text-4xl mb-4">❤️</p>
              <p class="text-sm mb-2">Aún no tienes productos en tu lista de deseos.</p>
              <p class="text-xs text-gray-300 mb-6">¡Explora nuestra tienda y guarda tus favoritos!</p>
              <router-link to="/shop" class="btn-gold text-xs">Ir a la tienda</router-link>
            </div>
            <div v-else class="grid grid-cols-2 md:grid-cols-3 gap-5">
              <div v-for="item in wishlistItems" :key="item.id"
                class="bg-white border border-gray-200 rounded-sm shadow-sm hover:shadow-md transition-shadow group">
                <!-- Imagen -->
                <div class="relative aspect-[3/4] bg-gray-50 overflow-hidden">
                  <router-link :to="`/product/${item.product_id}`">
                    <img v-if="item.product_image" :src="item.product_image" :alt="item.product_name"
                      class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                    <div v-else class="w-full h-full flex items-center justify-center text-gray-200 text-4xl">🧴</div>
                  </router-link>
                  <!-- Quitar de favoritos -->
                  <button @click="removeWishlistItem(item.product_id)"
                    class="absolute top-2 right-2 w-8 h-8 bg-white rounded-full shadow flex items-center justify-center hover:scale-110 transition-transform">
                    <svg class="w-4 h-4 text-red-500 fill-red-500" viewBox="0 0 24 24">
                      <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                    </svg>
                  </button>
                  <!-- Badge oferta -->
                  <div v-if="item.product_compare_price" class="absolute top-2 left-2 bg-[#e85d04] text-white text-[10px] font-bold px-2 py-0.5 rounded-full">
                    -{{ Math.round((1 - item.product_price / item.product_compare_price) * 100) }}%
                  </div>
                </div>
                <!-- Info -->
                <div class="p-3">
                  <p class="text-[10px] tracking-widest uppercase text-gray-400 mb-0.5">{{ item.product_brand }}</p>
                  <router-link :to="`/product/${item.product_id}`" class="text-sm font-medium text-[#111010] hover:text-gold transition-colors line-clamp-2">
                    {{ item.product_name }}
                  </router-link>
                  <div class="flex items-center gap-2 mt-2">
                    <span v-if="item.product_compare_price" class="text-xs text-gray-400 line-through">{{ formatCOP(item.product_compare_price) }}</span>
                    <span class="text-sm font-bold text-gold">{{ item.product_price ? formatCOP(item.product_price) : 'Consultar' }}</span>
                  </div>
                  <button @click="addWishlistToCart(item)"
                    class="mt-3 w-full bg-gold text-white text-xs py-2 tracking-widest uppercase hover:bg-gold-dark transition-colors rounded-sm">
                    Agregar al carrito
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- ── TAB: PUNTOS DE LEALTAD ─────────────────────────── -->
          <div v-if="activeTab === 'loyalty'">
            <h2 class="font-display text-2xl text-[#111010] mb-6">Puntos de Lealtad</h2>

            <!-- Tarjeta de saldo -->
            <div class="bg-gradient-to-br from-[#C8963E] to-[#A8762E] rounded-sm p-8 text-white mb-6 shadow-lg">
              <p class="text-[10px] tracking-[4px] uppercase opacity-80 mb-2">Saldo actual</p>
              <p class="font-display text-6xl mb-1">{{ (auth.user?.loyalty_points || 0).toLocaleString() }}</p>
              <p class="text-sm opacity-80">puntos</p>
              <div class="mt-4 pt-4 border-t border-white/20">
                <p class="text-xs opacity-70">Equivalente a aprox. {{ formatCOP((auth.user?.loyalty_points || 0) * 10) }} en descuentos</p>
              </div>
            </div>

            <!-- Barra de progreso al siguiente nivel -->
            <div class="bg-white border border-gray-200 rounded-sm p-5 mb-6 shadow-sm">
              <div class="flex justify-between text-xs text-gray-500 mb-2">
                <span>Progreso al siguiente nivel</span>
                <span>{{ auth.user?.loyalty_points || 0 }} / 1000 pts</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="bg-gold h-2 rounded-full transition-all duration-500"
                  :style="`width: ${Math.min(((auth.user?.loyalty_points || 0) / 1000) * 100, 100)}%`" />
              </div>
              <p class="text-xs text-gray-400 mt-2">
                {{ Math.max(0, 1000 - (auth.user?.loyalty_points || 0)) }} puntos para alcanzar el nivel Oro ⭐
              </p>
            </div>

            <!-- Cómo ganar puntos -->
            <div class="bg-gray-50 border border-gray-200 rounded-sm p-5 mb-6">
              <h3 class="text-sm font-semibold text-[#111010] mb-4">¿Cómo ganar puntos?</h3>
              <div class="space-y-2.5">
                <div v-for="tip in loyaltyTips" :key="tip.text" class="flex items-center gap-3">
                  <span class="text-lg shrink-0">{{ tip.icon }}</span>
                  <p class="text-sm text-gray-600">{{ tip.text }}</p>
                </div>
              </div>
            </div>

            <!-- Historial de transacciones -->
            <div>
              <h3 class="text-sm font-semibold text-[#111010] mb-4">Historial de Puntos</h3>
              <div v-if="loyaltyLoading" class="space-y-2">
                <div v-for="i in 4" :key="i" class="h-12 bg-gray-100 animate-pulse rounded-sm" />
              </div>
              <div v-else-if="loyaltyTransactions.length === 0" class="text-center py-8 text-gray-400 text-sm">
                Aún no tienes transacciones de puntos.
              </div>
              <div v-else class="border border-gray-200 rounded-sm overflow-hidden">
                <table class="w-full text-sm">
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="text-left p-3 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Fecha</th>
                      <th class="text-left p-3 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Descripción</th>
                      <th class="text-right p-3 text-[10px] tracking-widest uppercase text-gray-400 font-normal">Puntos</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="tx in loyaltyTransactions" :key="tx.id" class="border-t border-gray-100">
                      <td class="p-3 text-gray-400 text-xs">{{ formatDate(tx.created_at) }}</td>
                      <td class="p-3 text-gray-600">{{ tx.description }}</td>
                      <td class="p-3 text-right font-medium"
                        :class="tx.type === 'earned' ? 'text-green-600' : 'text-red-500'">
                        {{ tx.type === 'earned' ? '+' : '-' }}{{ Math.abs(tx.points) }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- ── TAB: DEVOLUCIONES ──────────────────────────────── -->
          <div v-if="activeTab === 'returns'">
            <h2 class="font-display text-2xl text-[#111010] mb-6">Mis Devoluciones</h2>
            <div v-if="returns.length === 0" class="text-center py-12 text-gray-400 text-sm">
              No tienes solicitudes de devolución.
            </div>
            <div v-else class="space-y-3">
              <div v-for="ret in returns" :key="ret.id"
                class="bg-white border border-gray-200 rounded-sm p-4 flex items-center justify-between gap-4 shadow-sm">
                <div>
                  <p class="text-sm text-[#111010]">Pedido #{{ ret.order_id }} · {{ ret.reason }}</p>
                  <p class="text-xs text-gray-400 mt-0.5">{{ formatDate(ret.created_at) }}</p>
                </div>
                <span class="text-xs px-2.5 py-1 rounded-full font-medium"
                  :class="{
                    'bg-yellow-100 text-yellow-700': ret.status === 'pending',
                    'bg-green-100 text-green-700': ret.status === 'approved' || ret.status === 'refunded',
                    'bg-red-100 text-red-700': ret.status === 'rejected',
                    'bg-blue-100 text-blue-700': ret.status === 'shipped',
                  }">
                  {{ returnStatusLabel(ret.status) }}
                </span>
              </div>
            </div>
          </div>

        </main>
      </div>
    </div>

    <!-- Modal devolución -->
    <div v-if="showReturnForm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 px-4" @click.self="showReturnForm = false">
      <div class="bg-white rounded-sm p-6 w-full max-w-md shadow-xl">
        <h3 class="font-display text-xl text-[#111010] mb-5">Solicitar Devolución</h3>
        <form @submit.prevent="submitReturn" class="space-y-4">
          <div>
            <label class="block text-xs text-gray-500 mb-1 uppercase tracking-widest">Motivo</label>
            <select v-model="returnForm.reason" required
              class="w-full border border-gray-300 text-[#111010] px-3 py-2.5 text-sm focus:border-gold focus:outline-none rounded-sm bg-white">
              <option value="" disabled>Selecciona un motivo</option>
              <option v-for="r in returnReasons" :key="r" :value="r">{{ r }}</option>
            </select>
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1 uppercase tracking-widest">Comentarios (opcional)</label>
            <textarea v-model="returnForm.comments" rows="3"
              class="w-full border border-gray-300 text-[#111010] px-3 py-2.5 text-sm focus:border-gold focus:outline-none rounded-sm resize-none"/>
          </div>
          <div class="flex gap-3">
            <button type="submit" class="flex-1 bg-gold text-white py-3 text-sm hover:bg-gold-dark transition-colors rounded-sm">
              Enviar solicitud
            </button>
            <button type="button" @click="showReturnForm = false"
              class="px-5 border border-gray-300 text-gray-600 text-sm hover:border-gray-400 transition-colors rounded-sm">
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>

    <Footer />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Header from '../components/layout/Header.vue'
import Footer from '../components/layout/Footer.vue'
import { useAuthStore } from '../stores/auth'
import { useCartStore } from '../stores/cart'
import { formatCOP } from '../utils/currency'
import api from '../router/api'

const router = useRouter()
const auth = useAuthStore()
const cart = useCartStore()
const { t } = useI18n()

const activeTab = ref('profile')

// Pedidos
const orders = ref([])
const loadingOrders = ref(false)
const lastOrder = computed(() => orders.value[0] || null)

// Direcciones
const addresses = ref([])
const addressLoading = ref(false)
const showAddressForm = ref(false)
const editingAddress = ref(null)
const addressForm = ref({ label: 'Casa', first_name: '', last_name: '', phone: '', address: '', city: '', state: '', postal_code: '', country: '', is_default: false })
const defaultAddress = computed(() => addresses.value.find(a => a.is_default) || null)

// Wishlist
const wishlistItems = ref([])
const loadingWishlist = ref(false)

// Loyalty
const loyaltyTransactions = ref([])
const loyaltyLoading = ref(false)
const loyaltyTips = [
  { icon: '🛍️', text: 'Cada $1.000 COP gastados = 1 punto' },
  { icon: '📸', text: 'Deja una reseña con foto = 50 puntos extra' },
  { icon: '👥', text: 'Refiere a un amigo = 200 puntos' },
  { icon: '🎂', text: 'Compra en tu cumpleaños = puntos x2' },
]

// Métodos de pago
const paymentMethods = ref([])
const showAddCardForm = ref(false)
const cardForm = ref({ number: '', expiry: '', cvc: '', setDefault: false })

// Devoluciones
const returns = ref([])
const showReturnForm = ref(false)
const returnOrderId = ref(null)
const returnForm = ref({ reason: '', comments: '' })
const returnReasons = ['Producto dañado', 'No coincide con la descripción', 'Cambio de opinión', 'Producto incorrecto recibido', 'Calidad insatisfactoria']

const menuItems = [
  { tab: 'profile',  i18n: 'account.profile',     icon: '👤' },
  { tab: 'orders',   i18n: 'account.orders',       icon: '📦' },
  { tab: 'addresses',i18n: 'account.addresses',    icon: '📍' },
  { tab: 'payment',  i18n: 'account.payment',      icon: '💳' },
  { tab: 'wishlist', i18n: 'account.wishlist',     icon: '❤️' },
  { tab: 'loyalty',  i18n: 'account.loyalty',      icon: '⭐' },
  { tab: 'returns',  i18n: 'account.my_returns',   icon: '↩️' },
]

// ── Helpers ─────────────────────────────────────────────────────
function formatDate(d) {
  return new Date(d).toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' })
}

function statusLabel(s) {
  return { pending: 'Pendiente', processing: 'Procesando', shipped: 'Enviado', delivered: 'Entregado', cancelled: 'Cancelado' }[s] || s
}

function statusBadgeClass(s) {
  return {
    pending:    'bg-yellow-100 text-yellow-700',
    processing: 'bg-blue-100 text-blue-700',
    shipped:    'bg-orange-100 text-orange-700',
    delivered:  'bg-green-100 text-green-700',
    cancelled:  'bg-red-100 text-red-700',
  }[s] || 'bg-gray-100 text-gray-500'
}

function returnStatusLabel(s) {
  return { pending: 'Pendiente', approved: 'Aprobada', rejected: 'Rechazada', shipped: 'En camino', refunded: 'Reembolsada' }[s] || s
}

// ── Direcciones ──────────────────────────────────────────────────
async function loadAddresses() {
  addressLoading.value = true
  try {
    const { data } = await api.get('/users/me/addresses')
    addresses.value = data
  } catch { addresses.value = [] } finally { addressLoading.value = false }
}

function openNewAddress() {
  editingAddress.value = null
  addressForm.value = { label: 'Casa', first_name: '', last_name: '', phone: '', address: '', city: '', state: '', postal_code: '', country: '', is_default: false }
  showAddressForm.value = true
}

function openEditAddress(addr) {
  editingAddress.value = addr
  addressForm.value = { ...addr }
  showAddressForm.value = true
}

async function saveAddress() {
  try {
    if (editingAddress.value) {
      await api.put(`/users/me/addresses/${editingAddress.value.id}`, addressForm.value)
    } else {
      await api.post('/users/me/addresses', addressForm.value)
    }
    showAddressForm.value = false
    await loadAddresses()
  } catch (e) { alert(e.response?.data?.detail || 'Error guardando dirección') }
}

async function deleteAddress(id) {
  if (!confirm('¿Eliminar esta dirección?')) return
  try { await api.delete(`/users/me/addresses/${id}`); await loadAddresses() } catch {}
}

async function setDefaultAddress(id) {
  try { await api.put(`/users/me/addresses/${id}/default`); await loadAddresses() } catch {}
}

// ── Wishlist ─────────────────────────────────────────────────────
async function loadWishlist() {
  loadingWishlist.value = true
  try {
    const { data } = await api.get('/users/me/wishlist')
    wishlistItems.value = data
  } catch { wishlistItems.value = [] } finally { loadingWishlist.value = false }
}

async function removeWishlistItem(productId) {
  try {
    await api.delete(`/users/me/wishlist/${productId}`)
    wishlistItems.value = wishlistItems.value.filter(i => i.product_id !== productId)
  } catch {}
}

function addWishlistToCart(item) {
  if (item.product_price) {
    cart.addItem(
      { id: item.product_id, name: item.product_name, images: [item.product_image], brand_name: item.product_brand },
      { id: null, price: item.product_price },
      1
    )
  }
}

// ── Loyalty ──────────────────────────────────────────────────────
async function loadLoyalty() {
  loyaltyLoading.value = true
  try {
    const { data } = await api.get('/users/me/loyalty')
    loyaltyTransactions.value = data.transactions || []
  } catch { loyaltyTransactions.value = [] } finally { loyaltyLoading.value = false }
}

// ── Métodos de pago ──────────────────────────────────────────────
async function loadPaymentMethods() {
  try {
    const { data } = await api.get('/users/me/payment-methods')
    paymentMethods.value = data
  } catch { paymentMethods.value = [] }
}

async function addCard() {
  try {
    const parts = cardForm.value.expiry.split('/')
    const month = parseInt(parts[0])
    const year = parseInt('20' + (parts[1] || '').trim())
    const last4 = cardForm.value.number.replace(/\s/g, '').slice(-4)
    const num = cardForm.value.number.replace(/\s/g, '')
    const brand = num.startsWith('4') ? 'visa' : num.startsWith('5') ? 'mastercard' : 'card'
    await api.post('/users/me/payment-methods', {
      stripe_payment_method_id: `pm_demo_${Date.now()}`,
      last4, brand, exp_month: month, exp_year: year,
      set_default: cardForm.value.setDefault,
    })
    showAddCardForm.value = false
    cardForm.value = { number: '', expiry: '', cvc: '', setDefault: false }
    await loadPaymentMethods()
  } catch (e) { alert(e.response?.data?.detail || 'Error al agregar tarjeta') }
}

async function deletePM(id) {
  if (!confirm('¿Eliminar este método de pago?')) return
  try { await api.delete(`/users/me/payment-methods/${id}`); await loadPaymentMethods() } catch {}
}

async function setDefaultPM(id) {
  try { await api.put(`/users/me/payment-methods/${id}/default`); await loadPaymentMethods() } catch {}
}

// ── Devoluciones ─────────────────────────────────────────────────
async function loadReturns() {
  try {
    const { data } = await api.get('/returns/my-returns')
    returns.value = data
  } catch { returns.value = [] }
}

function openReturnForm(orderId) {
  returnOrderId.value = orderId
  returnForm.value = { reason: '', comments: '' }
  showReturnForm.value = true
}

async function submitReturn() {
  try {
    await api.post('/returns', { order_id: returnOrderId.value, ...returnForm.value })
    showReturnForm.value = false
    await loadReturns()
  } catch (e) { alert(e.response?.data?.detail || 'Error') }
}

async function handleLogout() {
  await auth.logout()
  router.push('/')
}

onMounted(async () => {
  loadingOrders.value = true
  try {
    const { data } = await api.get('/orders/my-orders', { params: { per_page: 10 } })
    orders.value = data.items
  } catch {} finally { loadingOrders.value = false }

  await Promise.all([loadAddresses(), loadWishlist(), loadReturns(), loadPaymentMethods(), loadLoyalty()])
})
</script>
