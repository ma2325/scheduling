<template>
  <div class="space-y-8">
    <!-- 上层：排课算法运行后的数据 - 只在有数据时显示 -->
    <section v-if="hasSchedulingData">
      <h2 class="text-xl font-bold mb-4">排课算法统计</h2>
      
      <!-- 最近排课信息 -->
      <div class="bg-white rounded-lg shadow p-4 mb-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium">最近排课结果</h3>
          <span class="text-sm text-gray-500">{{ formatDate(schedulingStore.lastSchedulingTime) }}</span>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="bg-gray-50 p-3 rounded-md">
            <p class="text-sm text-gray-500">总课程数</p>
            <p class="text-xl font-medium">{{ schedulingSummary.totalClasses }}</p>
          </div>
          <div class="bg-gray-50 p-3 rounded-md">
            <p class="text-sm text-gray-500">已排课程</p>
            <p class="text-xl font-medium">{{ schedulingSummary.scheduledClasses }}</p>
          </div>
          <div class="bg-gray-50 p-3 rounded-md">
            <p class="text-sm text-gray-500">教室利用率</p>
            <p class="text-xl font-medium">{{ schedulingSummary.roomRate }}%</p>
          </div>
          <div class="bg-gray-50 p-3 rounded-md">
            <p class="text-sm text-gray-500">已排教师</p>
            <p class="text-xl font-medium">{{ schedulingSummary.totalScheduledTeachers }}</p>
          </div>
        </div>
      </div>

      <!-- 统计数据卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div v-for="(stat, index) in statisticsData" :key="index" class="bg-white rounded-lg shadow p-4">
          <h3 class="text-lg font-medium mb-2">{{ stat.name }}</h3>
          <div class="flex items-end justify-between">
            <span class="text-3xl font-bold">{{ stat.value }}</span>
            <span class="text-sm text-gray-500">{{ stat.percentage }}%</span>
          </div>
          <div class="mt-2 bg-gray-200 rounded-full h-2">
            <div class="bg-primary h-2 rounded-full" :style="{ width: `${stat.percentage}%` }"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- 下层：特定周次的数据 - 始终显示 -->
    <section>
      <h2 class="text-xl font-bold mb-4">周次统计数据</h2>
      
      <!-- 周次选择器 -->
      <div class="mb-6">
        <label for="week-select" class="block text-sm font-medium text-gray-700 mb-2">选择周次</label>
        <div class="flex items-center">
          <select 
            id="week-select" 
            v-model="selectedWeek" 
            class="block w-full max-w-xs rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50"
          >
            <option v-for="week in 20" :key="week" :value="week">第 {{ week }} 周</option>
          </select>
          <button 
            @click="fetchWeekData" 
            class="ml-2 px-4 py-2 bg-primary text-white rounded-md hover:bg-primary-dark"
            :disabled="isLoading"
          >
            <span v-if="!isLoading">查询</span>
            <span v-else class="flex items-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              加载中...
            </span>
          </button>
        </div>
      </div>
      
      <!-- 错误提示 -->
      <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
        <div class="flex">
          <div class="py-1">
            <svg class="h-6 w-6 text-red-500 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <p class="font-medium">获取数据失败</p>
            <p class="text-sm">{{ error }}</p>
          </div>
        </div>
        <div class="mt-2 text-right">
          <button @click="fetchWeekData" class="text-sm text-red-600 hover:text-red-800">重试</button>
        </div>
      </div>
      
      <!-- 图表区域 -->
      <div v-if="weekData" class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- 教室利用率图表 -->
        <div class="bg-white rounded-lg shadow p-4">
          <h3 class="text-lg font-medium mb-4">教室利用率 (第{{ selectedWeek }}周)</h3>
          <div class="h-64">
            <canvas ref="classroomUtilizationChart"></canvas>
          </div>
        </div>
        
        <!-- 课程类型分布图表 -->
        <div class="bg-white rounded-lg shadow p-4">
          <h3 class="text-lg font-medium mb-4">课程类型分布 (第{{ selectedWeek }}周)</h3>
          <div class="h-64">
            <canvas ref="courseTypeChart"></canvas>
          </div>
        </div>
      </div>
      
      <!-- 加载中状态 -->
      <div v-else-if="isLoading" class="bg-white rounded-lg shadow p-8 text-center">
        <div class="flex justify-center mb-4">
          <svg class="animate-spin h-10 w-10 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
        <p class="text-gray-600">正在加载第{{ selectedWeek }}周数据...</p>
      </div>
      
      <!-- 无数据状态 -->
      <div v-else-if="!error" class="bg-white rounded-lg shadow p-8 text-center">
        <div class="flex justify-center mb-4">
          <svg class="h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <p class="text-gray-600 mb-2">暂无数据</p>
        <p class="text-gray-500 text-sm">请选择周次并点击查询按钮</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, nextTick } from "vue"
import Chart from "chart.js/auto"
import { useSchedulingStore } from "@/stores/schedulingStore"
import { getWeekStatistics } from "@/api/statistics"

// 图表引用
const classroomUtilizationChart = ref(null)
const courseTypeChart = ref(null)

// 获取排课统计数据
const schedulingStore = useSchedulingStore()
const schedulingSummary = computed(() => schedulingStore.summary)

// 是否有排课数据
const hasSchedulingData = computed(() => schedulingSummary.value !== null)

// 周次选择和数据
const selectedWeek = ref(1)
const weekData = ref(null)
const isLoading = ref(false)
const error = ref(null)

// 图表实例
let classroomChartInstance = null
let courseTypeChartInstance = null

// 格式化时间
const formatDate = (isoString) => {
  if (!isoString) return ""
  const date = new Date(isoString)
  return date.toLocaleString()
}

const baseData = ref([
  { name: "总课程数", value: 120, percentage: 100.0 },
  { name: "已排课程", value: 98, percentage: 81.7 },
  { name: "未排课程", value: 22, percentage: 18.3 },
  { name: "教室总数", value: 45, percentage: 100.0 },
  { name: "已使用教室", value: 32, percentage: 71.1 },
  { name: "教室平均利用率", value: "65%", percentage: 65.0 },
  { name: "教师总数", value: 28, percentage: 100.0 },
  { name: "已排课教师", value: 25, percentage: 89.3 },
])

// 统计数据
const statisticsData = computed(() => {
  if (!hasSchedulingData.value) {
    return baseData.value
  }

  const summary = schedulingSummary.value
  return [
    { name: "总课程数", value: summary.totalClasses, percentage: 100.0 },
    {
      name: "已排课程",
      value: summary.scheduledClasses,
      percentage: ((summary.scheduledClasses / summary.totalClasses) * 100).toFixed(2),
    },
    {
      name: "未排课程",
      value: summary.unscheduledClasses,
      percentage: ((summary.unscheduledClasses / summary.totalClasses) * 100).toFixed(2),
    },
    { name: "教室总数", value: summary.totalRooms, percentage: 100.0 },
    { name: "已使用教室", value: summary.usedRooms, percentage: 100.0 },
    {
      name: "教室平均利用率",
      value: `${summary.roomRate.toFixed(2)}%`,
      percentage: summary.roomRate.toFixed(2),
    },
    { name: "教师总数", value: summary.totalTeachers, percentage: 100.0 },
    {
      name: "已排课教师",
      value: summary.totalScheduledTeachers,
      percentage: ((summary.totalScheduledTeachers / summary.totalTeachers) * 100).toFixed(2),
    },
  ]
})

// 获取特定周次的数据
const fetchWeekData = async () => {
  isLoading.value = true
  error.value = null

  try {
    const response = await getWeekStatistics(selectedWeek.value)

    if (response.data.code === 200) {
      weekData.value = response.data.data
      // 等待DOM更新后再更新图表
      await nextTick()
      updateWeekCharts()
    } else {
      error.value = response.data.msg || "获取数据失败"
    }
  } catch (err) {
    console.error("获取周次数据失败:", err)
    error.value = err.response?.data?.msg || "服务器异常，请稍后重试"
  } finally {
    isLoading.value = false
  }
}

// 更新周次相关图表
const updateWeekCharts = () => {
  if (!weekData.value) return

  // 清除旧图表
  if (classroomChartInstance) {
    classroomChartInstance.destroy()
  }
  
  if (courseTypeChartInstance) {
    courseTypeChartInstance.destroy()
  }

  // 教室利用率图表数据
  const buildingData = weekData.value[0]
  const buildingLabels = buildingData.map((item) => item.building)
  const buildingRates = buildingData.map((item) => item.rate)

  // 课程类型分布图表数据
  const courseTypeData = weekData.value[1]
  const courseTypeLabels = courseTypeData.map((item) => item.type)
  const courseTypeCounts = courseTypeData.map((item) => item.count)

  // 创建教室利用率图表
  if (classroomUtilizationChart.value) {
    // const adjustedRates = buildingRates.map(rate => rate);
    classroomChartInstance = new Chart(classroomUtilizationChart.value, {
      type: "bar",
      data: {
        labels: buildingLabels,
        datasets: [
          {
            label: "教室利用率",
            data: buildingRates,
            backgroundColor: buildingLabels.map((_, index) => {
              const opacity = 0.8 - index * 0.1
              return `rgba(79, 70, 229, ${opacity > 0.3 ? opacity : 0.3})`
            }),
            borderColor: buildingLabels.map(() => "rgba(79, 70, 229, 1)"),
            borderWidth: 1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
            ticks: {
              callback: function (value) {
                return value + "%"
              },
            },
          },
        },
      },
    })
  }

  // 创建课程类型分布图表
  if (courseTypeChart.value) {
    courseTypeChartInstance = new Chart(courseTypeChart.value, {
      type: "pie",
      data: {
        labels: courseTypeLabels,
        datasets: [
          {
            data: courseTypeCounts,
            backgroundColor: [
              "rgba(79, 70, 229, 0.8)",
              "rgba(79, 70, 229, 0.7)",
              "rgba(79, 70, 229, 0.6)",
              "rgba(79, 70, 229, 0.5)",
              "rgba(79, 70, 229, 0.4)",
              "rgba(79, 70, 229, 0.3)",
            ],
            borderColor: courseTypeLabels.map(() => "rgba(79, 70, 229, 1)"),
            borderWidth: 1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "right",
          },
        },
      },
    })
  }
}

// 组件挂载时初始化
onMounted(() => {
  // 默认获取第一周数据
  fetchWeekData()
})

// 监听周次变化
watch(selectedWeek, () => {
  fetchWeekData()
})
</script>

<style scoped>
.bg-primary {
  background-color: #4f46e5;
}
.hover\:bg-primary-dark:hover {
  background-color: #4338ca;
}
.focus\:border-primary:focus {
  border-color: #4f46e5;
}
.focus\:ring-primary:focus {
  --tw-ring-color: #4f46e5;
}
</style>