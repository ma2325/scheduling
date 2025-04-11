<template>
  <div class="space-y-6">
    <!-- 最近排课信息 -->
    <div v-if="hasSchedulingData" class="bg-white rounded-lg shadow p-4">
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

    <!-- 原有的统计数据卡片 -->
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

    <!-- 原有的图表 -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="bg-white rounded-lg shadow p-4">
        <h3 class="text-lg font-medium mb-4">教室利用率</h3>
        <div class="h-64">
          <canvas ref="classroomUtilizationChart"></canvas>
        </div>
      </div>
      
      <!-- 其他图表... -->
    </div>
  </div>
</template>





<script setup>
import { ref, onMounted, computed } from 'vue';
import Chart from 'chart.js/auto';
import { useSchedulingStore } from '@/stores/schedulingStore';

// 图表引用
const classroomUtilizationChart = ref(null);
const teacherHoursChart = ref(null);
const courseTypeChart = ref(null);
const timeSlotDistributionChart = ref(null);

// 获取排课统计数据
const schedulingStore = useSchedulingStore();
const schedulingSummary = computed(() => schedulingStore.summary);

// 是否有排课数据
const hasSchedulingData = computed(() => schedulingSummary.value !== null);

// 格式化时间
const formatDate = (isoString) => {
  if (!isoString) return '';
  const date = new Date(isoString);
  return date.toLocaleString();
};

// 统计数据
const statisticsData = computed(() => {
  // 基础统计数据
  const baseData = [
    { name: '总课程数', value: 120, percentage: 100 },
    { name: '已排课程', value: 98, percentage: 81.7 },
    { name: '未排课程', value: 22, percentage: 18.3 },
    { name: '教室总数', value: 45, percentage: 100 },
    { name: '已使用教室', value: 32, percentage: 71.1 },
    { name: '教室平均利用率', value: '65%', percentage: 65 },
    { name: '教师总数', value: 28, percentage: 100 },
    { name: '已排课教师', value: 25, percentage: 89.3 }
  ];

  // 如果有排课数据，则使用排课数据
  if (hasSchedulingData.value) {
    const summary = schedulingSummary.value;
    return [
      { name: '总课程数', value: summary.totalClasses, percentage: 100 },
      { name: '已排课程', value: summary.scheduledClasses, percentage: Math.round((summary.scheduledClasses / summary.totalClasses) * 100) },
      { name: '未排课程', value: summary.unscheduledClasses, percentage: Math.round((summary.unscheduledClasses / summary.totalClasses) * 100) },
      { name: '教室总数', value: summary.totalRooms, percentage: 100 },
      { name: '已使用教室', value: summary.usedRooms, percentage: 100 },
      { name: '教室平均利用率', value: `${summary.roomRate}%`, percentage: summary.roomRate },
      { name: '教师总数', value: summary.totalTeachers, percentage: 100 },
      { name: '已排课教师', value: summary.totalScheduledTeachers, percentage: Math.round((summary.totalScheduledTeachers / summary.totalTeachers) * 100) }
    ];
  }

  return baseData;
});

onMounted(() => {
  // 初始化图表...
  initCharts();
});

// 初始化图表
const initCharts = () => {
  // 使用排课数据更新图表
  if (hasSchedulingData.value) {
    const summary = schedulingSummary.value;
    
    // 更新教室利用率图表
    new Chart(classroomUtilizationChart.value, {
      type: 'bar',
      data: {
        labels: ['教学楼A', '教学楼B', '实验楼C', '外语楼D', '图书馆E'],
        datasets: [{
          label: '教室利用率',
          data: [
            summary.roomRate, 
            Math.max(summary.roomRate - 10, 30), 
            Math.max(summary.roomRate - 15, 25), 
            Math.max(summary.roomRate - 20, 20), 
            Math.max(summary.roomRate - 25, 15)
          ],
          backgroundColor: [
            'rgba(79, 70, 229, 0.8)',
            'rgba(79, 70, 229, 0.7)',
            'rgba(79, 70, 229, 0.6)',
            'rgba(79, 70, 229, 0.5)',
            'rgba(79, 70, 229, 0.4)'
          ],
          borderColor: [
            'rgba(79, 70, 229, 1)',
            'rgba(79, 70, 229, 1)',
            'rgba(79, 70, 229, 1)',
            'rgba(79, 70, 229, 1)',
            'rgba(79, 70, 229, 1)'
          ],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
            ticks: {
              callback: function(value) {
                return value + '%';
              }
            }
          }
        }
      }
    });

    // 初始化其他图表...
    // 这里可以根据排课数据更新其他图表
  } else {
    // 使用原始数据初始化图表
    // 原有的图表初始化代码...
    new Chart(classroomUtilizationChart.value, {
      type: 'bar',
      data: {
        labels: ['教学楼A', '教学楼B', '实验楼C', '外语楼D', '图书馆E'],
        datasets: [{
          label: '教室利用率',
          data: [75, 82, 60, 45, 30],
          backgroundColor: [
            'rgba(79, 70, 229, 0.8)',
            'rgba(79, 70, 229, 0.7)',
            'rgba(79, 70, 229, 0.6)',
            'rgba(79, 70, 229, 0.5)',
            'rgba(79, 70, 229, 0.4)'
          ],
          borderColor: [
            'rgba(79, 70, 229, 1)',
            'rgba(79, 70, 229, 1)',
            'rgba(79, 70, 229, 1)',
            'rgba(79, 70, 229, 1)',
            'rgba(79, 70, 229, 1)'
          ],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
            ticks: {
              callback: function(value) {
                return value + '%';
              }
            }
          }
        }
      }
    });
    
    // 初始化其他图表...
  }
};
</script>



<style scoped>
.bg-primary {
  background-color: #4f46e5;
}
</style>