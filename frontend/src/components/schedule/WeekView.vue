<template>
  <div class="overflow-x-auto">
    <div class="max-h-[70vh] overflow-y-auto">
      <table class="w-full divide-y divide-gray-200">
        <thead class="bg-gray-50 sticky top-0 z-10">
          <tr>
            <th class="w-[15%] px-2 sm:px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">时间</th>
            <th v-for="day in weekdays" :key="day.value" class="w-[12%] px-1 sm:px-2 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
              {{ day.label }}
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="timeSlot in timeSlots" :key="timeSlot.value">
            <td class="px-2 sm:px-4 py-2 whitespace-nowrap text-xs sm:text-sm text-gray-500">
              {{ timeSlot.label }}
            </td>
            <td v-for="day in weekdays" :key="day.value" class="px-1 sm:px-2 py-2 h-24 sm:h-28 align-top relative">
              <div v-for="course in getCoursesForTimeAndDay(timeSlot.value, day.value)" :key="course.id" 
                  class="p-1 sm:p-2 rounded-md bg-primary-light text-primary-dark text-xs sm:text-sm cursor-pointer hover:bg-primary-lighter w-full h-full overflow-y-auto"
                  @click="openCourseDetails(course)">
                <div class="font-medium mb-1">{{ course.name }}</div>
                <div class="text-xs">{{ course.teacher }}</div>
                <div class="text-xs">{{ course.classroom }}</div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- 课程详情弹窗 -->
    <div v-if="showCourseDetails" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg p-4 sm:p-6 w-full max-w-md">
        <div class="flex justify-between items-start">
          <h3 class="text-lg font-medium text-gray-900">课程详情</h3>
          <button @click="showCourseDetails = false" class="text-gray-400 hover:text-gray-500">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="mt-4 space-y-3" v-if="selectedCourse">
          <div>
            <span class="font-medium">课程名称:</span> {{ selectedCourse.name }}
          </div>
          <div>
            <span class="font-medium">授课教师:</span> {{ selectedCourse.teacher }}
          </div>
          <div>
            <span class="font-medium">教室:</span> {{ selectedCourse.classroom }}
          </div>
          <div>
            <span class="font-medium">时间:</span> 周{{ getWeekdayName(selectedCourse.weekday) }} {{ formatTime(selectedCourse.startTime) }}-{{ formatTime(selectedCourse.endTime) }}
          </div>
          <div>
            <span class="font-medium">周次:</span> 第{{ selectedCourse.weeks.join(', ') }}周
          </div>
        </div>
        <div class="mt-6 flex justify-end">
          <button @click="showCourseDetails = false" class="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary-dark">
            关闭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, ref } from 'vue';

const props = defineProps({
  courses: {
    type: Array,
    required: true
  },
  currentWeek: {
    type: Number,
    required: true
  }
});

// 星期几
const weekdays = [
  { label: '周一', value: 1 },
  { label: '周二', value: 2 },
  { label: '周三', value: 3 },
  { label: '周四', value: 4 },
  { label: '周五', value: 5 },
  { label: '周六', value: 6 },
  { label: '周日', value: 7 }
];

// 时间段
const timeSlots = [
  { label: '08:00-09:40', value: '08:00:00-09:40:00' },
  { label: '10:00-11:40', value: '10:00:00-11:40:00' },
  { label: '14:00-15:40', value: '14:00:00-15:40:00' },
  { label: '16:00-17:40', value: '16:00:00-17:40:00' },
  { label: '19:00-20:40', value: '19:00:00-20:40:00' }
];

// 获取特定时间和星期的课程
const getCoursesForTimeAndDay = (timeSlot, weekday) => {
  const [startTime, endTime] = timeSlot.split('-');
  return props.courses.filter(course => {
    return course.weekday === weekday && 
           course.startTime === startTime && 
           course.endTime === endTime &&
           course.weeks.includes(props.currentWeek);
  });
};

// 课程详情弹窗
const showCourseDetails = ref(false);
const selectedCourse = ref(null);

// 打开课程详情
const openCourseDetails = (course) => {
  selectedCourse.value = course;
  showCourseDetails.value = true;
};

// 获取星期几的名称
const getWeekdayName = (weekday) => {
  const weekdays = ['日', '一', '二', '三', '四', '五', '六', '日'];
  return weekdays[weekday];
};

// 格式化时间（去掉秒）
const formatTime = (time) => {
  if (!time) return '';
  return time.split(':').slice(0, 2).join(':');
};
</script>

<style scoped>
.bg-primary-light {
  background-color: #ede9fe;
}
.bg-primary-lighter {
  background-color: #ddd6fe;
}
.text-primary-dark {
  color: #4f46e5;
}
.bg-primary {
  background-color: #4f46e5;
}
.bg-primary-dark {
  background-color: #4338ca;
}

/* 响应式表格样式 */
@media (max-width: 640px) {
  table {
    font-size: 0.75rem;
  }
}

/* 确保表格在各种屏幕尺寸下都能保持合适的比例 */
table {
  table-layout: fixed;
}

/* 表头固定 */
thead {
  background-color: #f9fafb;
}

/* 课程块样式 */
td > div {
  word-break: break-word;
  line-height: 1.3;
}
</style>

