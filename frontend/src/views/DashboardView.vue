<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <!--视图切换按钮-->
      <div class="flex space-x-4">
        <button 
          v-for="view in viewOptions" 
          :key="view.value"
          @click="currentView = view.value"
          class="px-4 py-2 rounded-md text-sm font-medium"
          :class="currentView === view.value ? 'bg-primary text-white' : 'bg-white text-gray-700 hover:bg-gray-50'"
        >
          {{ view.label }}
        </button>
      </div>
      
      <!--时间周期选择按钮-->
      <div class="flex space-x-2">
        <!--左切换箭头-->
        <button @click="prevPeriod" class="p-2 rounded-md bg-white text-gray-700 hover:bg-gray-50">
          <ChevronLeft class="w-5 h-5" />
        </button>
        <span class="p-2 font-medium">{{ currentPeriodLabel }}</span>
        <!--右切换箭头-->
        <button @click="nextPeriod" class="p-2 rounded-md bg-white text-gray-700 hover:bg-gray-50">
          <ChevronRight class="w-5 h-5" />
        </button>
      </div>
    </div>

    <!--当前选择视图-->
    <div class="bg-white rounded-lg shadow p-6">
      <!-- 周视图 -->
      <WeekView v-if="currentView === 'week'" :courses="filteredCourses" :current-week="currentWeek" />
      
      <!-- 月视图 -->
      <MonthView v-else-if="currentView === 'month'" :courses="filteredCourses" :current-month="currentMonth" />
      
      <!-- 学期视图 -->
      <SemesterView v-else :courses="courses" :current-semester="currentSemester" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import { ChevronLeft, ChevronRight } from 'lucide-vue-next';
import WeekView from '@/components/schedule/WeekView.vue';
import MonthView from '@/components/schedule/MonthView.vue';
import SemesterView from '@/components/schedule/SemesterView.vue';

// 视图选项
const viewOptions = [
  { label: '周视图', value: 'week' },
  { label: '月视图', value: 'month' },
  { label: '学期视图', value: 'semester' }
];

//TO DO


const currentView = ref('week');
const currentWeek = ref(2);
const currentMonth = ref(4); // 3月
const currentSemester = ref('2024-2025-1');

// 课程数据
const courses = ref([]);

// **请求 API 获取课程数据**
const fetchCourses = async () => {
  try {
    const response = await axios.get('/dashboard'); // 发送请求
    if (response.data.code === 200) {
      courses.value = response.data.data; // API 返回的课程数据
    } else {
      console.error('获取课程数据失败:', response.data.msg);
    }
  } catch (error) {
    console.error('API 请求错误:', error);
  }
};

// 组件挂载时获取数据
onMounted(fetchCourses);


// 根据当前视图过滤课程
const filteredCourses = computed(() => {
  if (currentView.value === 'week') {
    return courses.value.filter(course => course.weeks.includes(currentWeek.value));
  } else if (currentView.value === 'month') {
    // 简化处理，实际应该根据月份和周数的对应关系过滤
    return courses.value;
  } else {
    return courses.value;
  }
});

// 当前周期标签
const currentPeriodLabel = computed(() => {
  if (currentView.value === 'week') {
    return `第${currentWeek.value}周`;
  } else if (currentView.value === 'month') {
    return `${currentMonth.value}月`;
  } else {
    return currentSemester.value;
  }
});

// 上一周期
const prevPeriod = () => {
  if (currentView.value === 'week' && currentWeek.value > 1) {
    currentWeek.value--;
  } else if (currentView.value === 'month' && currentMonth.value > 1) {
    currentMonth.value--;
  } else if (currentView.value === 'semester') {
    // 切换上一学期，这里简化处理
    currentSemester.value = '2023-2024-1';
  }
};

// 下一周期
const nextPeriod = () => {
  if (currentView.value === 'week' && currentWeek.value < 20) {
    currentWeek.value++;
  } else if (currentView.value === 'month' && currentMonth.value < 12) {
    currentMonth.value++;
  } else if (currentView.value === 'semester') {
    // 切换下一学期，这里简化处理
    currentSemester.value = '2024-2025-2';
  }
};
</script>

<style scoped>
.bg-primary {
  background-color: #4f46e5;
}
.text-primary {
  color: #4f46e5;
}
</style>