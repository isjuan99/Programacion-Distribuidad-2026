<template>
  <div class="min-h-screen bg-white">
    <Header />
    <div class="pt-36 max-w-3xl mx-auto px-6 pb-24">
      <h1 class="font-display text-5xl text-[#1a1a1a] mb-12">Términos de Servicio</h1>
      <div class="max-w-none text-gray-600 leading-relaxed space-y-6">
        <p>Al utilizar Aroma-Distribuido, aceptas los siguientes términos y condiciones. Todos los productos son auténticos y provienen de distribuidores autorizados. Los precios están sujetos a cambios sin previo aviso.</p>
        <p>Las devoluciones se aceptan dentro de los 30 días posteriores a la recepción del producto, siempre que se encuentre en su estado original y sin abrir. Los costos de envío de devolución son responsabilidad del cliente.</p>
        <p>Aroma-Distribuido se reserva el derecho de cancelar pedidos en casos de error en el precio o disponibilidad. En tales casos, se realizará un reembolso completo.</p>
      </div>
    </div>
    <Footer />
  </div>
</template>
<script setup>
import Header from '../components/layout/Header.vue'
import Footer from '../components/layout/Footer.vue'
</script>
