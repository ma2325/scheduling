import { createRouter, createWebHistory } from "vue-router"
import LoginView from "../views/LoginView.vue"
import MainLayout from "../layouts/MainLayout.vue"
import DashboardView from "../views/DashboardView.vue"
import ManualSchedulingView from "../views/ManualSchedulingView.vue"
import StatisticsView from "../views/StatisticsView.vue"
import SmartAdjustmentView from "../views/SmartAdjustmentView.vue"
import CourseDataView from "../views/CourseDataView.vue"

const routes = [
  {
    path: "/login",
    name: "Login",
    component: LoginView,
    meta: { requiresAuth: false },
  },
  {
    path: "/",
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: "",
        redirect: "/dashboard",
      },
      {
        path: "/dashboard",
        name: "Dashboard",
        component: DashboardView,
      },
      {
        path: "/manual-scheduling",
        name: "ManualScheduling",
        component: ManualSchedulingView,
      },
      {
        path: "/statistics",
        name: "Statistics",
        component: StatisticsView,
      },
      {
        path: "/smart-adjustment",
        name: "SmartAdjustment",
        component: SmartAdjustmentView,
      },
      {
        path: "/course-data",
        name: "CourseData",
        component: CourseDataView,
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem("user") !== null

  if (to.meta.requiresAuth && !isAuthenticated) {
    next("/login")
  } else if (to.path === "/login" && isAuthenticated) {
    next("/dashboard")
  } else {
    next()
  }
})

export default router

