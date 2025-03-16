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
              时间: 周{{ getWeekdayName(course.weekday) }} {{ course.startTime }}-{{ course.endTime }}
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
</script>

<style scoped>
.text-primary {
  color: #4f46e5;
}
</style>