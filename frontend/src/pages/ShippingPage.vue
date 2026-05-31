<template>
  <div class="min-h-screen bg-white">
    <Header />
    <div class="pt-36 max-w-3xl mx-auto px-6 pb-24">
      <h1 class="font-display text-5xl text-[#1a1a1a] mb-12">Envíos y Devoluciones</h1>
      <div class="space-y-10">
        <div>
          <h2 class="text-[10px] tracking-widest uppercase text-[#c9a84c] mb-4">Envío Estándar</h2>
          <p class="text-gray-600 text-sm leading-relaxed">3-5 días hábiles. Gratis en pedidos superiores a $250. Incluye número de rastreo y firma requerida.</p>
        </div>
        <div>
          <h2 class="text-[10px] tracking-widest uppercase text-[#c9a84c] mb-4">Envío Express</h2>
          <p class="text-gray-600 text-sm leading-relaxed">1-2 días hábiles. Costo: $25. Disponible para pedidos realizados antes de las 2pm (hora Colombia).</p>
        </div>
        <div>
          <h2 class="text-[10px] tracking-widest uppercase text-[#c9a84c] mb-4">Devoluciones</h2>
          <p class="text-gray-600 text-sm leading-relaxed">Aceptamos devoluciones dentro de los 30 días posteriores a la recepción. El producto debe estar sellado y en su estado original. Los costos de envío de vuelta son responsabilidad del cliente.</p>
        </div>
      </div>
    </div>
    <Footer />
  </div>
</template>
<script setup>
import Header from '../components/layout/Header.vue'
import Footer from '../components/layout/Footer.vue'
</script>
