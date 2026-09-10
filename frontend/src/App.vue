<template>
  <!-- 着色器门户世界：两页均自带头部导航，App 不再套壳 -->
  <router-view />
</template>

<script setup lang="ts">
</script>

<style>
#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    'Noto Sans', sans-serif;
}

/* 浏览器原生部件也属于这个设计世界：选中/焦点/滚动条主题化 */
::selection {
  background: #ff7a45;
  color: #0a0e1a;
}
html {
  scrollbar-color: rgba(232, 236, 244, 0.3) #0a0e1a;
}
</style>
