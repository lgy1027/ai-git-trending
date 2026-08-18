<template>
  <div class="contact-nav-wrap">
    <router-link
      :to="to"
      :class="['terminal-nav', active ? 'active' : '']"
    >
      {{ label }}
    </router-link>
    <div v-if="showQr" class="contact-qr-popup">
      <img
        src="/images/wechat.png"
        alt="WeChat QR Code"
        width="240"
        height="253"
        class="block h-auto w-60"
        loading="lazy"
      />
      <p class="mt-2 text-center text-xs text-slate-400">
        扫码加微信，备注「GitTrend」
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    to?: string
    label?: string
    active?: boolean
    showQr?: boolean
  }>(),
  {
    to: '/contact',
    label: '联系我们',
    active: false,
    showQr: true,
  },
)
</script>

<style scoped>
.contact-nav-wrap {
  position: relative;
}

.contact-qr-popup {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  padding: 0.75rem;
  background: #0f172a;
  border: 1px solid rgba(34, 211, 238, 0.4);
  border-radius: 0.5rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  opacity: 0;
  transform: translateY(-4px);
  pointer-events: none;
  transition: opacity 0.2s ease, transform 0.2s ease;
  z-index: 50;
}

.contact-nav-wrap:hover .contact-qr-popup,
.contact-nav-wrap:focus-within .contact-qr-popup {
  opacity: 1;
  transform: translateY(0);
}
</style>
