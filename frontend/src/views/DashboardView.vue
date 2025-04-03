<template>
  <div class="space-y-6">
    <!-- 用户信息选择区域 -->
    <div class="bg-white rounded-lg shadow p-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">用户类型</label>
          <div class="flex space-x-2">
            <button 
              @click="userType = 'teacher'"
              class="px-4 py-2 rounded-md text-sm font-medium flex-1"
              :class="userType === 'teacher' ? 'bg-primary text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
            >
              教师
            </button>
            <button 
              @click="userType = 'student'"
              class="px-4 py-2 rounded-md text-sm font-medium flex-1"
              :class="userType === 'student' ? 'bg-primary text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
            >
              学生
            </button>
          </div>
        </div>
        <div>
          <label for="userId" class="block text-sm font-medium text-gray-700 mb-1">
            {{ userType === 'teacher' ? '教师编号' : '教学班级' }}
          </label>
          <div class="flex">
            <input 
              type="text" 
              id="userId" 
              v-model="user" 
              class="flex-1 rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50"
              :placeholder="userType === 'teacher' ? '请输入教师编号 (例如: 304)' : '请输入教学班级 (例如: 24教学7班)'"
            />
            <button 
              @click="fetchCourses()" 
              class="ml-2 px-4 py-2 bg-primary text-white rounded-md hover:bg-primary-dark"
            >
              查询
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="flex justify-between items-center">
      <!--视图切换按钮-->
      <div class="flex space-x-4">
        <button 
          v-for="view in viewOptions" 
          :key="view.value"
          @click="currentView = view.value; fetchCourses()"
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
      <!-- 学期视图 -->
      <SemesterView v-else :courses="courses" :current-semester="currentSemester" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { getWeekView, getTermView} from '@/api/schedule';
import { ChevronLeft, ChevronRight } from 'lucide-vue-next';
import WeekView from '@/components/schedule/WeekView.vue';
import SemesterView from '@/components/schedule/SemesterView.vue';

// 视图选项
const viewOptions = [
  { label: '周视图', value: 'week' },
  { label: '学期视图', value: 'term' }
];

// 用户信息
const user = ref('304');
const userType = ref('teacher');

// 当用户类型改变时，设置默认示例值
watch(userType, (newType) => {
  if (newType === 'teacher') {
    user.value = '304';
  } else {
    user.value = '24教学7班';
  }
});

const currentView = ref('week');
const currentWeek = ref(1);
const currentSemester = ref('2024-2025-1');

// 课程数据
const courses = ref([]);

// **请求 API 获取课程数据**
const fetchCourses = async () => {
  try {
    let response;
    if(currentView.value === 'week') {
      response = await getWeekView(user.value, userType.value, currentWeek.value); // 发送请求
    } else if (currentView.value === 'term') {
      response = await getTermView(user.value, userType.value, currentWeek.value);
    }
    
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

// 监听周次或学期变化，重新获取数据
watch([currentWeek, currentSemester], () => {
  fetchCourses();
});

// 展示课程
const filteredCourses = computed(() => {
  return courses.value;
});

// 当前周期标签
const currentPeriodLabel = computed(() => {
  if (currentView.value === 'week') {
    return `第${currentWeek.value}周`;
  } else if (currentView.value === 'term') {
    return currentSemester.value;
  }
});

// 上一周期
const prevPeriod = () => {
  if (currentView.value === 'week' && currentWeek.value > 1) {
    currentWeek.value--;
    // fetchCourses() 会通过 watch 自动触发
  } else if (currentView.value === 'term') {
    // 切换上一学期，这里简化处理(目前没有其他学期的数据)
    currentSemester.value = '2024-2025-1';
    // fetchCourses() 会通过 watch 自动触发
  }
};

// 下一周期
const nextPeriod = () => {
  if (currentView.value === 'week' && currentWeek.value < 20) {
    currentWeek.value++;
    // fetchCourses() 会通过 watch 自动触发
  } else if (currentView.value === 'term') {
    // 切换下一学期，这里简化处理(目前没有其他学期的数据)
    currentSemester.value = '2024-2025-1';
    // fetchCourses() 会通过 watch 自动触发
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
.bg-primary-dark {
  background-color: #4338ca;
}
.focus\:border-primary:focus {
  border-color: #4f46e5;
}
.focus\:ring-primary:focus {
  --tw-ring-color: #4f46e5;
}
</style>

