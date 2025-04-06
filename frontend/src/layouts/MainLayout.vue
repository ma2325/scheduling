<template>
  <div class="flex h-screen bg-gray-100">
    <!-- Sidebar -->
    <aside 
      class="bg-white shadow-md transition-all duration-300 ease-in-out"
      :class="isSidebarCollapsed ? 'w-16' : 'w-64'"
    >
      <div class="p-4 border-b flex justify-between items-center">
        <h1 class="text-xl font-bold text-gray-800" :class="isSidebarCollapsed ? 'hidden' : ''">排课系统</h1>
        <button @click="toggleSidebar" class="text-gray-500 hover:text-gray-700">
          <ChevronRight v-if="isSidebarCollapsed" class="w-5 h-5" />
          <ChevronLeft v-else class="w-5 h-5" />
        </button>
      </div>
      <nav class="mt-6">
        <router-link 
          v-for="item in menuItems" 
          :key="item.path" 
          :to="item.path"
          class="flex items-center py-3 text-gray-600 hover:bg-gray-100 hover:text-gray-900"
          :class="{ 
            'bg-gray-100 text-gray-900': isActive(item.path),
            'px-6': !isSidebarCollapsed,
            'px-4 justify-center': isSidebarCollapsed
          }"
        >
          <component :is="item.icon" class="w-5 h-5" :class="isSidebarCollapsed ? '' : 'mr-3'" />
          <span :class="isSidebarCollapsed ? 'hidden' : ''">{{ item.name }}</span>
        </router-link>
      </nav>
    </aside>

    <!-- Main content area -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Top navigation bar -->
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

      <!-- Page content -->
      <main class="flex-1 overflow-auto p-6 bg-gray-100">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { Calendar, Grid, BarChart2, RefreshCw, Database, ChevronLeft, ChevronRight, Cpu } from 'lucide-vue-next';

const router = useRouter();
const route = useRoute();

// User information
const username = ref('管理员');

// Sidebar state
const isSidebarCollapsed = ref(false);

// Toggle sidebar
const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value;
};

// Menu items
const menuItems = [
  { name: '课表展示', path: '/dashboard', icon: Calendar },
  { name: '手动排课', path: '/manual-scheduling', icon: Grid },
  { name: '智能排课', path: '/smart-scheduling', icon: Cpu },
  { name: '统计分析', path: '/statistics', icon: BarChart2 },
  { name: '智能调课', path: '/smart-adjustment', icon: RefreshCw },
  { name: '排课数据', path: '/course-data', icon: Database },
];

// Current page title
const currentPageTitle = computed(() => {
  const currentPath = route.path;
  const currentItem = menuItems.find(item => item.path === currentPath);
  return currentItem ? currentItem.name : '排课系统';
});

// Check if route is active
const isActive = (path) => {
  return route.path === path;
};

// Logout
const logout = () => {
  localStorage.removeItem('user');
  router.push('/login');
};
</script>