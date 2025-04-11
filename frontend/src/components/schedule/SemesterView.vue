<template>
  <div>
    <h3 class="text-lg font-medium mb-4">{{ currentSemester }} 学期课程安排</h3>
    
    <div class="space-y-4">
      <div v-for="course in courses" :key="course.id" class="bg-white border rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow">
        <div class="flex justify-between items-start">
          <div>
            <h4 class="text-lg font-medium text-primary">{{ course.name }}</h4>
            <p class="text-sm text-gray-600">教师: {{ course.teacher }}</p>
            <p class="text-sm text-gray-600">教室: {{ course.classroom }}</p>
            <p class="text-sm text-gray-600">
              时间: 周{{ getWeekdayName(course.weekday) }} {{ getSlotTimeRange(course.slot) }}
            </p>
          </div>
          <div class="text-sm bg-gray-100 px-3 py-1 rounded-full">
            第{{ course.weeks.join(',') }}周
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue';

const props = defineProps({
  courses: {
    type: Array,
    required: true
  },
  currentSemester: {
    type: String,
    required: true
  }
});

// 获取星期几的名称
const getWeekdayName = (weekday) => {
  const weekdays = ['日', '一', '二', '三', '四', '五', '六', '日'];
  return weekdays[weekday];
};


// Period time settings
const periodTimes = [
  { start: '08:00', end: '08:45' },
  { start: '08:55', end: '09:40' },
  { start: '10:00', end: '10:45' },
  { start: '10:55', end: '11:40' },
  { start: '14:00', end: '14:45' },
  { start: '14:55', end: '15:40' },
  { start: '16:00', end: '16:45' },
  { start: '16:55', end: '17:40' },
  { start: '19:00', end: '19:45' },
  { start: '19:55', end: '20:40' },
  { start: '20:50', end: '21:35' },
  { start: '21:45', end: '22:30' },
];


// 检查特定节次是否在课程的 slot 范围内
const isPeriodInSlot = (period, courseSlot) => {
  if (!courseSlot) return false;
  
  // 解析课程的 slot 范围
  const [start, end] = courseSlot.split('-').map(Number);
  
  // 检查当前节次是否在课程的 slot 范围内
  return period >= start && period <= end;
};

// 获取时间段的显示文本
const getSlotTimeRange = (slot) => {
  if (!slot) return '';
  
  const [start, end] = slot.split('-').map(Number);
  if (start <= periodTimes.length && end <= periodTimes.length) {
    return `${periodTimes[start-1].start}-${periodTimes[end-1].end}`;
  }
  return slot; // 如果无法解析，则返回原始 slot 值
};


</script>

<style scoped>
.text-primary {
  color: #4f46e5;
}
</style>