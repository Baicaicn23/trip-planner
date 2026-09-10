<template>
  <router-view />
</template>

<script setup lang="ts">
</script>

<style>
/* Maple Mono NF CN：全局主字体（圆润等宽，中英文等宽混排） */
@font-face {
  font-family: 'Maple Mono NF CN';
  src: url('/fonts/MapleMono-NF-CN-Regular.ttf') format('truetype');
  font-weight: 400; font-display: swap;
}
@font-face {
  font-family: 'Maple Mono NF CN';
  src: url('/fonts/MapleMono-NF-CN-SemiBold.ttf') format('truetype');
  font-weight: 600; font-display: swap;
}
@font-face {
  font-family: 'Maple Mono NF CN';
  src: url('/fonts/MapleMono-NF-CN-Bold.ttf') format('truetype');
  font-weight: 700; font-display: swap;
}

:root { color-scheme: light; }
html {
  font-family: 'Maple Mono NF CN', -apple-system, BlinkMacSystemFont, "SF Pro Text",
    "PingFang SC", "Microsoft YaHei", sans-serif;
  scrollbar-color: rgba(0,0,0,.28) #f5f5f7;
}
::selection { background: rgba(0,122,255,.22); color: #1d1d1f; }
</style>
