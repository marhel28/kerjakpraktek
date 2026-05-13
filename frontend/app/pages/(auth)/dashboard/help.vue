<script setup lang="ts">
definePageMeta({
  layout: 'dashboard'
})
</script>

<template>
  <div class="p-6">
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-gray-900">Pusat Bantuan</h1>
      <p class="text-gray-500">Temukan jawaban atas pertanyaan Anda seputar layanan kami.</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- FAQ Section -->
      <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
        <div class="flex items-center gap-3 mb-4">
          <div class="p-2 bg-indigo-100 rounded-lg">
            <UIcon name="i-heroicons-question-mark-circle" class="w-6 h-6 text-indigo-600" />
          </div>
          <h2 class="text-lg font-bold text-gray-900">Pertanyaan Umum (FAQ)</h2>
        </div>
        <ul class="space-y-4">
          <li class="p-3 bg-gray-50 rounded-xl hover:bg-gray-100 cursor-pointer transition-colors">
            <div class="font-medium text-gray-800">Bagaimana cara memesan jasa pemasangan?</div>
          </li>
          <li class="p-3 bg-gray-50 rounded-xl hover:bg-gray-100 cursor-pointer transition-colors">
            <div class="font-medium text-gray-800">Berapa lama garansi pemasangan?</div>
          </li>
          <li class="p-3 bg-gray-50 rounded-xl hover:bg-gray-100 cursor-pointer transition-colors">
            <div class="font-medium text-gray-800">Metode pembayaran apa saja yang tersedia?</div>
          </li>
        </ul>
      </div>

      <!-- Contact Support -->
      <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
        <div class="flex items-center gap-3 mb-4">
          <div class="p-2 bg-green-100 rounded-lg">
            <UIcon name="i-heroicons-chat-bubble-left-right" class="w-6 h-6 text-green-600" />
          </div>
          <h2 class="text-lg font-bold text-gray-900">Hubungi Kami</h2>
        </div>
        <p class="text-gray-600 mb-6">Butuh bantuan lebih lanjut? Tim support kami siap melayani Anda.</p>
        <div class="space-y-3">
          <UButton
            block
            color="green"
            variant="solid"
            icon="i-heroicons-phone"
            to="https://wa.me/628123456789"
            target="_blank"
          >
            WhatsApp Support
          </UButton>
          <UButton
            block
            color="white"
            variant="outline"
            icon="i-heroicons-envelope"
          >
            Email Support
          </UButton>
        </div>
      </div>
    </div>
  </div>
</template>
