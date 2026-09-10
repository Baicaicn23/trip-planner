<template>
  <!-- Home 首屏是全屏沉浸的着色器门户：不套旧壳；Result 页暂用旧壳（阶段一第二步统一） -->
  <router-view v-if="isHome" />

  <div v-else id="app">
    <a-layout style="min-height: 100vh">
      <a-layout-header style="background: #001529; padding: 0 50px">
        <div style="color: white; font-size: 24px; font-weight: bold">
          HelloAgents智能旅行助手
        </div>
      </a-layout-header>
      <a-layout-content style="padding: 24px">
        <router-view />
      </a-layout-content>
      <a-layout-footer style="text-align: center">
        HelloAgents智能旅行助手 ©2025 基于HelloAgents框架
      </a-layout-footer>
    </a-layout>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const isHome = computed(() => route.name === 'Home')
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
