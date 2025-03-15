<template>
  <div class="overflow-x-auto">
    <table class="min-w-full divide-y divide-gray-200">
      <thead class="bg-gray-50">
        <tr>
          <th class="w-20 px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">时间</th>
          <th v-for="day in weekdays" :key="day.value" class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
            {{ day.label }}
          </th>
        </tr>
      </thead>
      <tbody class="bg-white divide-y divide-gray-200">
        <tr v-for="timeSlot in timeSlots" :key="timeSlot.value">
          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
            {{ timeSlot.label }}
          </td>
          <td v-for="day in weekdays" :key="day.value" class="px-6 py-4 whitespace-nowrap">
            <div v-for="course in getCoursesForTimeAndDay(timeSlot.value, day.value)" :key="course.id" 
                 class="p-2 rounded-md bg-primary-light text-primary-dark text-sm">
              <div class="font-medium">{{ course.name }}</div>
              <div class="text-xs">{{ course.teacher }}</div>
              <div class="text-xs">{{ course.classroom }}</div>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { defineProps } from 'vue';

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
  { label: '08:00-09:40', value: '08:00-09:40' },
  { label: '10:00-11:40', value: '10:00-11:40' },
  { label: '14:00-15:40', value: '14:00-15:40' },
  { label: '16:00-17:40', value: '16:00-17:40' },
  { label: '19:00-20:40', value: '19:00-20:40' }
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
</script>

<style scoped>
.bg-primary-light {
  background-color: #ede9fe;
}
.text-primary-dark {
  color: #4f46e5;
}
</style>