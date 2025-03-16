<template>
  <div class="space-y-6">
    <h2 class="text-xl font-bold">统计分析</h2>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- 教室利用率 -->
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-medium mb-4">教室利用率</h3>
        <div class="h-80">
          <canvas ref="classroomUtilizationChart"></canvas>
        </div>
      </div>

      <!-- 教师课时分布 -->
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-medium mb-4">教师课时分布</h3>
        <div class="h-80">
          <canvas ref="teacherHoursChart"></canvas>
        </div>
      </div>

      <!-- 课程类型分布 -->
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-medium mb-4">课程类型分布</h3>
        <div class="h-80">
          <canvas ref="courseTypeChart"></canvas>
        </div>
      </div>

      <!-- 时间段课程分布 -->
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-medium mb-4">时间段课程分布</h3>
        <div class="h-80">
          <canvas ref="timeSlotDistributionChart"></canvas>
        </div>
      </div>
    </div>

    <!-- 详细统计数据 -->
    <div class="bg-white rounded-lg shadow p-6">
      <h3 class="text-lg font-medium mb-4">详细统计数据</h3>
      
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">指标</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">数值</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">比例</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="(stat, index) in statisticsData" :key="index">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ stat.name }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ stat.value }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ stat.percentage }}%</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Chart from 'chart.js/auto';

// 图表引用
const classroomUtilizationChart = ref(null);
const teacherHoursChart = ref(null);
const courseTypeChart = ref(null);
const timeSlotDistributionChart = ref(null);

// 统计数据
const statisticsData = [
  { name: '总课程数', value: 120, percentage: 100 },
  { name: '已排课程', value: 98, percentage: 81.7 },
  { name: '未排课程', value: 22, percentage: 18.3 },
  { name: '教室总数', value: 45, percentage: 100 },
  { name: '已使用教室', value: 32, percentage: 71.1 },
  { name: '教室平均利用率', value: '65%', percentage: 65 },
  { name: '教师总数', value: 28, percentage: 100 },
  { name: '已排课教师', value: 25, percentage: 89.3 }
];

onMounted(() => {
  // 初始化教室利用率图表
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

  // 初始化教师课时分布图表
  new Chart(teacherHoursChart.value, {
    type: 'bar',
    data: {
      labels: ['张教授', '李教授', '王教授', '刘教授', '陈教授'],
      datasets: [{
        label: '课时数',
        data: [32, 48, 24, 36, 40],
        backgroundColor: 'rgba(79, 70, 229, 0.6)',
        borderColor: 'rgba(79, 70, 229, 1)',
        borderWidth: 1
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          beginAtZero: true
        }
      }
    }
  });

  // 初始化课程类型分布图表
  new Chart(courseTypeChart.value, {
    type: 'pie',
    data: {
      labels: ['理论课', '实验课', '实践课', '讨论课', '其他'],
      datasets: [{
        data: [45, 25, 15, 10, 5],
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
      plugins: {
        legend: {
          position: 'right'
        }
      }
    }
  });

  // 初始化时间段课程分布图表
  new Chart(timeSlotDistributionChart.value, {
    type: 'line',
    data: {
      labels: ['8:00-9:50', '10:10-12:00', '14:10-16:00', '16:20-18:10', '19:00-20:50','21:00-21:50'],
      datasets: [{
        label: '课程数量',
        data: [25, 30, 28, 22, 15, 10, 5],
        fill: false,
        borderColor: 'rgba(79, 70, 229, 1)',
        tension: 0.1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
});
</script>