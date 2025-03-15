import { createRouter, createWebHistory } from 'vue-router';
import LoginView from '../views/LoginView.vue';
import MainLayout from '../layouts/MainLayout.vue';
import DashboardView from '../views/DashboardView.vue';
import ManualSchedulingView from '../views/ManualSchedulingView.vue';
import StatisticsView from '../views/StatisticsView.vue';
import SmartAdjustmentView from '../views/SmartAdjustmentView.vue';

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: DashboardView
      },
      {
        path: '/manual-scheduling',
        name: 'ManualScheduling',
        component: ManualSchedulingView
      },
      {
        path: '/statistics',
        name: 'Statistics',
        component: StatisticsView
      },
      {
        path: '/smart-adjustment',
        name: 'SmartAdjustment',
        component: SmartAdjustmentView
      }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 路由守卫(每次页面跳转前进行判断)
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('user') !== null;
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    //如果to的页面需要验证且未认证则转到登入界面
    next('/login');
  } else if (to.path === '/login' && isAuthenticated) {
    //如果登入了还想访问登入页面直接将其跳转至dashboard
    next('/dashboard');
  } else {
    //若无问题则正常访问
    next();
  }
});

export default router;