<template>
  <div class="grid grid-cols-7 gap-2">
    <div v-for="day in weekdays" :key="day" class="text-center font-medium text-gray-500 p-2">
      {{ day }}
    </div>
    
    <div v-for="(day, index) in daysInMonth" :key="index" 
         class="border rounded-md p-2 min-h-[100px] relative"
         :class="{ 'bg-gray-50': !day.inMonth }">
      <div class="text-right text-sm text-gray-500 mb-2">{{ day.date }}</div>
      
      <div v-for="course in getCoursesForDay(day)" :key="course.id" 
           class="p-1 mb-1 rounded text-xs bg-primary-light text-primary-dark truncate">
        {{ course.name }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, computed } from 'vue';

const props = defineProps({
  courses: {
    type: Array,
    required: true
  },
  currentMonth: {
    type: Number,
    required: true
  }
});

// 星期几标题
const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];

// 生成当月的日期数据
const daysInMonth = computed(() => {
  const year = new Date().getFullYear();
  const month = props.currentMonth - 1; // JavaScript月份从0开始
  
  // 当月第一天
  const firstDay = new Date(year, month, 1);
  // 当月最后一天
  const lastDay = new Date(year, month + 1, 0);
  
  const days = [];
  
  // 填充当月第一天之前的日期
  const firstDayOfWeek = firstDay.getDay();
  for (let i = 0; i < firstDayOfWeek; i++) {
    const prevDate = new Date(year, month, -i);
    days.unshift({
      date: prevDate.getDate(),
      fullDate: prevDate,
      inMonth: false,
      weekday: prevDate.getDay()
    });
  }
  
  // 填充当月的日期
  for (let i = 1; i <= lastDay.getDate(); i++) {
    const currentDate = new Date(year, month, i);
    days.push({
      date: i,
      fullDate: currentDate,
      inMonth: true,
      weekday: currentDate.getDay()
    });
  }
  
  // 填充当月最后一天之后的日期，确保总共显示42个日期（6周）
  const remainingDays = 42 - days.length;
  for (let i = 1; i <= remainingDays; i++) {
    const nextDate = new Date(year, month + 1, i);
    days.push({
      date: i,
      fullDate: nextDate,
      inMonth: false,
      weekday: nextDate.getDay()
    });
  }
  
  return days;
});

// 获取特定日期的课程
const getCoursesForDay = (day) => {
  if (!day.inMonth) return [];
  
  // 计算这一天是第几周
  const year = new Date().getFullYear();
  const firstDayOfYear = new Date(year, 0, 1);
  const dayOfYear = Math.floor((day.fullDate - firstDayOfYear) / (24 * 60 * 60 * 1000));
  const weekNumber = Math.ceil((dayOfYear + firstDayOfYear.getDay() + 1) / 7);
  
  return props.courses.filter(course => {
    return course.weekday === (day.weekday === 0 ? 7 : day.weekday) && // 将周日(0)转换为7
           course.weeks.includes(weekNumber);
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