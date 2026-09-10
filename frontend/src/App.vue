<template>
  <!-- 着色器门户世界：两页均自带头部导航，App 不再套壳 -->
  <router-view />
</template>

<script setup lang="ts">
</script>

<style>
:root { color-scheme: light; }
html {
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue",
    "PingFang SC", "Microsoft YaHei", sans-serif;
  scrollbar-color: rgba(0,0,0,.28) #f5f5f7;
}
::selection { background: rgba(0,122,255,.22); color: #1d1d1f; }
</style>
