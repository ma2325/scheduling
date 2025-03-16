<template>
  <div class="space-y-6">
    <!-- 标题 -->
    <div class="flex justify-between items-center">
      <h2 class="text-xl font-bold">手动排课</h2>
      <div class="flex space-x-2">
        <button @click="saveCourseArrangement" class="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary-dark">
          保存排课
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- 左侧：课程列表 -->
      <div class="bg-white rounded-lg shadow p-4">
        <h3 class="text-lg font-medium mb-4">待排课程</h3>
        <div class="space-y-2">
          <div v-for="course in unscheduledCourses" :key="course.id" 
               class="p-3 bg-gray-50 rounded-md cursor-move"
               draggable="true"
               @dragstart="onDragStart($event, course)">
            <div class="font-medium">{{ course.name }}</div>
            <div class="text-sm text-gray-600">{{ course.teacher }}</div>
            <div class="text-sm text-gray-600">学时: {{ course.hours }}</div>
          </div>
        </div>
      </div>

      <!-- 中间：课表 -->
      <div class="md:col-span-2 bg-white rounded-lg shadow p-4">
        <h3 class="text-lg font-medium mb-4">课表安排</h3>
        <div class="overflow-x-auto">
          <table class="min-w-full border-collapse">
            <!--头行显示-->
            <thead>
              <tr>
                <th class="border p-2 bg-gray-50">时间/日期</th>
                <th v-for="day in weekdays" :key="day.value" class="border p-2 bg-gray-50">
                  {{ day.label }}
                </th>
              </tr>
            </thead>
            <tbody>
            <!--双层循环建构课表-->
              <!--时间段-->
              <tr v-for="timeSlot in timeSlots" :key="timeSlot.value">
                <td class="border p-2 text-sm">{{ timeSlot.label }}</td>
                <!--每个时间段的每天-->
                <td v-for="day in weekdays" :key="day.value" 
                    class="border p-2 h-24 align-top"
                    @dragover.prevent
                    @drop="onDrop($event, day.value, timeSlot.value)">
                  <!--渲染已排的课程-->
                  <div v-for="course in getScheduledCourse(day.value, timeSlot.value)" 
                       :key="course.id"
                       class="p-2 mb-1 bg-primary-light text-primary-dark rounded-md text-sm"
                       draggable="true"
                       @dragstart="onDragStart($event, course, true)">
                    <div class="font-medium">{{ course.name }}</div>
                    <div class="text-xs">{{ course.teacher }}</div>
                    <div class="text-xs">{{ course.classroom || '未分配' }}</div>
                    <button @click="removeCourse(course)" class="text-xs text-red-500 mt-1">
                      移除
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 教室选择对话框 -->
    <div v-if="showClassroomDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-96">
        <h3 class="text-lg font-medium mb-4">选择教室</h3>
        <div class="space-y-4">
          <div v-for="classroom in availableClassrooms" :key="classroom.id" 
               class="p-3 border rounded-md cursor-pointer hover:bg-gray-50"
               @click="selectClassroom(classroom)">
            <div class="font-medium">{{ classroom.name }}</div>
            <div class="text-sm text-gray-600">容量: {{ classroom.capacity }}人</div>
            <div class="text-sm text-gray-600">设备: {{ classroom.equipment }}</div>
          </div>
        </div>
        <div class="mt-4 flex justify-end">
          <button @click="CancelClassroom" class="px-4 py-2 text-gray-600 hover:text-gray-800">
            取消
          </button>
          <button @click="confirmClassroom" class="ml-2 px-4 py-2 bg-primary text-white rounded-md hover:bg-primary-dark">
            确认
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';

//TO DO

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
  { label: '08:00-09:50', value: '08:00-09:50' },
  { label: '10:10-12:00', value: '10:10-12:00' },
  { label: '14:10-16:00', value: '14:10-16:00' },
  { label: '16:20-18:10', value: '16:20-18:10' },
  { label: '19:00-20:50', value: '19:00-20:50' },
  { label: '21:00-21:50', value: '21:00-21:50' }
];

// 未排课程
const unscheduledCourses = ref([
  { id: 101, name: '计算机网络', teacher: '张教授', hours: 32 },
  { id: 102, name: '操作系统', teacher: '李教授', hours: 48 },
  { id: 103, name: '软件工程', teacher: '王教授', hours: 32 },
  { id: 104, name: '数据库系统', teacher: '刘教授', hours: 48 },
  { id: 105, name: '人工智能', teacher: '陈教授', hours: 32 }
]);

// 已排课程
const scheduledCourses = ref([]);

// 可用教室
const availableClassrooms = [
  { id: 1, name: '教学楼A-101', capacity: 60, equipment: '多媒体' },
  { id: 2, name: '教学楼A-102', capacity: 80, equipment: '多媒体' },
  { id: 3, name: '教学楼B-201', capacity: 100, equipment: '多媒体、实验设备' },
  { id: 4, name: '教学楼B-202', capacity: 120, equipment: '多媒体、实验设备' },
  { id: 5, name: '实验楼C-301', capacity: 40, equipment: '计算机' }
];

// 拖拽相关
const draggedCourse = ref(null);
const draggedFromScheduled = ref(false);
const showClassroomDialog = ref(false);
const selectedTimeSlot = reactive({
  weekday: null,
  timeSlot: null
});

// 开始拖拽
const onDragStart = (event, course, fromScheduled = false) => {
  draggedCourse.value = course;
  draggedFromScheduled.value = fromScheduled;
  event.dataTransfer.effectAllowed = 'move';
};

// 放置课程
const onDrop = (event, weekday, timeSlot) => {
  event.preventDefault();
  
  if (!draggedCourse.value) return;
  

  // 如果是从已排课程拖拽，先移除原来的
  if (draggedFromScheduled.value) {
    scheduledCourses.value = scheduledCourses.value.filter(c => c.id !== draggedCourse.value.id);
  } else {
    // 从未排课程拖拽，从未排课程中移除
    unscheduledCourses.value = unscheduledCourses.value.filter(c => c.id !== draggedCourse.value.id);
  }
  
  // 保存当前选择的时间槽
  selectedTimeSlot.weekday = weekday;
  selectedTimeSlot.timeSlot = timeSlot;
  
  // 显示教室选择对话框
  showClassroomDialog.value = true;
};

// 选择教室
const selectClassroom = (classroom) => {
  // 保存选中的教室
  draggedCourse.value.classroom = classroom.name;
};

// 取消教室选择
const CancelClassroom = () => {
  //返回拖拽课程
  // const { weekday, timeSlot, classroom, weeks, ...restCourse } = draggedCourse.value;
  // unscheduledCourses.value.push(draggedCourse.value);
  // // unscheduledCourses.value.push(draggedFromScheduled);
  
  // // 关闭对话框
  // showClassroomDialog.value = false;
  // draggedCourse.value = null;
  if (draggedCourse.value) {
    unscheduledCourses.value.push({ ...draggedCourse.value });
  }

  showClassroomDialog.value = false;
  draggedCourse.value = null;
};

// 确认教室选择
const confirmClassroom = () => {
  // 添加到已排课程
  scheduledCourses.value.push({
    ...draggedCourse.value,
    weekday: selectedTimeSlot.weekday,
    timeSlot: selectedTimeSlot.timeSlot,
    weeks: [1, 2, 3, 4, 5, 6, 7, 8] // 默认排在前8周
  });
  
  // 关闭对话框
  showClassroomDialog.value = false;
  draggedCourse.value = null;
};

// 获取已排课程
const getScheduledCourse = (weekday, timeSlot) => {
  return scheduledCourses.value.filter(course => 
    course.weekday === weekday && course.timeSlot === timeSlot
  );
};

// 移除课程
const removeCourse = (course) => {
  // 从已排课程中移除
  scheduledCourses.value = scheduledCourses.value.filter(c => c.id !== course.id);
  
  // 添加回未排课程
  const { weekday, timeSlot, classroom, weeks, ...restCourse } = course;
  unscheduledCourses.value.push(restCourse);
};

//TO DO
// 保存排课
const saveCourseArrangement = () => {
  // 这里应该调用API保存排课结果
  console.log('保存排课结果:', scheduledCourses.value);
  alert('排课结果已保存');
};
</script>

<style scoped>
.bg-primary {
  background-color: #4f46e5;
}
.bg-primary-dark {
  background-color: #4338ca;
}
.bg-primary-light {
  background-color: #ede9fe;
}
.text-primary {
  color: #4f46e5;
}
.text-primary-dark {
  color: #4338ca;
}
</style>