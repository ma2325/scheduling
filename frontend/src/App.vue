<template>
  <router-view />
</template>

<script setup>
// App.vue 是应用的根组件
</script>

<style>
/* 新的 Tailwind CSS v4 导入方式 */
@import 'tailwindcss';

html, body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background-color: #f3f4f6;
  color: #1f2937;
}
</style>

