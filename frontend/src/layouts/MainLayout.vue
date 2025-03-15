<template>
  <div class="flex h-screen bg-gray-100">
    <!-- 侧边栏 -->
    <aside class="w-64 bg-white shadow-md">
      <div class="p-4 border-b">
        <h1 class="text-xl font-bold text-gray-800">排课系统</h1>
      </div>
      <nav class="mt-6">
        <!--点击切换跳转-->
        <router-link v-for="item in menuItems" :key="item.path" :to="item.path"
                    class="flex items-center px-6 py-3 text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                    :class="{ 'bg-gray-100 text-gray-900': isActive(item.path) }">
          <component :is="item.icon" class="w-5 h-5 mr-3" />
          <span>{{ item.name }}</span>
        </router-link>
      </nav>
    </aside>

    <!-- 主内容区 -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- 顶部导航栏 -->
      <header class="bg-white shadow-sm z-10">
        <div class="flex items-center justify-between p-4">
          <div>
            <h2 class="text-lg font-medium text-gray-800">{{ currentPageTitle }}</h2>
          </div>
          <div class="flex items-center">
            <span class="mr-2 text-sm text-gray-600">{{ username }}</span>
            <button @click="logout" class="text-sm text-red-500 hover:text-red-700">退出</button>
          </div>
        </div>
      </header>

      <!-- 页面内容 -->
      <main class="flex-1 overflow-auto p-6 bg-gray-100">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { Calendar, Grid, BarChart2, RefreshCw } from 'lucide-vue-next';

//用于跳转
const router = useRouter();
//用于判断当前路径
const route = useRoute();

//TO DO
// 用户信息
const username = ref('管理员');

// 菜单项
const menuItems = [
  { name: '课表展示', path: '/dashboard', icon: Calendar },
  { name: '手动排课', path: '/manual-scheduling', icon: Grid },
  { name: '统计分析', path: '/statistics', icon: BarChart2 },
  { name: '智能调课', path: '/smart-adjustment', icon: RefreshCw },
];

// 当前页面标题
const currentPageTitle = computed(() => {
  const currentPath = route.path;
  const currentItem = menuItems.find(item => item.path === currentPath);
  return currentItem ? currentItem.name : '排课系统';
});


// 判断当前路由是否激活
const isActive = (path) => {
  return route.path === path;
};

// 退出登录
const logout = () => {
  localStorage.removeItem('user');
  router.push('/login');
};
</script>