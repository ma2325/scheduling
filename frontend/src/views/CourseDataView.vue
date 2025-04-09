<template>
  <div class="space-y-6">
    <!-- 加载状态和错误提示 -->
    <div v-if="isLoading || loadError" class="bg-white rounded-lg shadow p-4 mb-4">
      <div v-if="isLoading" class="flex items-center text-gray-600">
        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        正在加载课程数据...
      </div>
      <div v-if="loadError" class="text-red-500">
        <div class="font-medium">加载数据失败</div>
        <div class="text-sm">{{ loadError }}</div>
        <button 
          @click="fetchCoursesFromAPI" 
          class="mt-2 px-3 py-1 text-sm rounded-md bg-primary text-white hover:bg-primary-dark"
        >
          重试
        </button>
      </div>
    </div>

    <!-- 数据来源信息 -->
    <div class="bg-white rounded-lg shadow p-4 mb-4">
      <div class="flex justify-between items-center">
        <div>
          <span class="text-sm font-medium">数据来源: </span>
          <span class="text-sm">API数据 ({{ courses.length }}条)</span>
        </div>
        <button 
          @click="fetchCoursesFromAPI" 
          class="px-3 py-1 text-sm rounded-md border border-input bg-background shadow-sm hover:bg-gray-50"
        >
          <RefreshCw class="w-4 h-4 inline-block mr-1" />
          刷新API数据
        </button>
      </div>
    </div>
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <h2 class="text-xl font-bold">排课数据展示</h2>
      <div class="flex flex-wrap gap-2">
        <!-- View toggle -->
        <div class="flex rounded-md shadow-sm">
          <button 
            @click="viewMode = 'detailed'" 
            class="px-3 py-1 text-sm rounded-l-md border border-input shadow-sm"
            :class="viewMode === 'detailed' ? 'bg-primary text-white' : 'bg-background'"
          >
            <LayoutGrid class="w-4 h-4 inline-block mr-1" />
            详细视图
          </button>
          <button 
            @click="viewMode = 'thumbnail'" 
            class="px-3 py-1 text-sm rounded-r-md border border-input shadow-sm"
            :class="viewMode === 'thumbnail' ? 'bg-primary text-white' : 'bg-background'"
          >
            <Grid class="w-4 h-4 inline-block mr-1" />
            缩略视图
          </button>
        </div>
        
        <!-- Week selector -->
        <div class="flex items-center space-x-2">
          <label for="week-select" class="text-sm font-medium">周次:</label>
          <select 
            id="week-select" 
            v-model="selectedWeek" 
            class="h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm"
          >
            <option v-for="week in availableWeeks" :key="week" :value="week">第{{ week }}周</option>
          </select>
        </div>
        
        <!-- Day selector -->
        <div class="flex items-center space-x-2">
          <label for="day-select" class="text-sm font-medium">星期:</label>
          <select 
            id="day-select" 
            v-model="selectedDay" 
            class="h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm"
          >
            <option value="">全部</option>
            <option v-for="day in weekdays" :key="day.value" :value="day.value">{{ day.label }}</option>
          </select>
        </div>
        
        <!-- Color customization -->
        <div class="flex items-center space-x-2">
          <label for="color-select" class="text-sm font-medium">卡片颜色:</label>
          <div class="relative">
            <input 
              type="color" 
              v-model="cardColor" 
              class="w-9 h-9 rounded-md border border-input cursor-pointer"
            />
          </div>
        </div>
        
        <!-- Export button -->
        <button 
          @click="exportData" 
          class="px-3 py-1 text-sm rounded-md border border-input bg-background shadow-sm hover:bg-gray-50"
        >
          <Download class="w-4 h-4 inline-block mr-1" />
          导出数据
        </button>
      </div>
    </div>

    <!-- Search filters -->
    <div class="bg-white rounded-lg shadow p-4">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Classroom search -->
        <div>
          <label class="block text-sm font-medium mb-1">教室搜索</label>
          <div class="relative">
            <input 
              v-model="classroomSearch" 
              type="text" 
              placeholder="搜索教室" 
              class="w-full h-9 rounded-md border border-input bg-background pl-9 pr-3 py-1 text-sm shadow-sm"
            />
            <Search class="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
          </div>
        </div>
        
        <!-- Course name search -->
        <div>
          <label class="block text-sm font-medium mb-1">课程名称</label>
          <div class="relative">
            <input 
              v-model="courseNameSearch" 
              type="text" 
              placeholder="搜索课程名称" 
              class="w-full h-9 rounded-md border border-input bg-background pl-9 pr-3 py-1 text-sm shadow-sm"
            />
            <Search class="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
          </div>
        </div>
        
        <!-- Class search -->
        <div>
          <label class="block text-sm font-medium mb-1">班级</label>
          <div class="relative">
            <input 
              v-model="classSearch" 
              type="text" 
              placeholder="搜索班级" 
              class="w-full h-9 rounded-md border border-input bg-background pl-9 pr-3 py-1 text-sm shadow-sm"
            />
            <Search class="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
          </div>
        </div>
      </div>
    </div>

    <!-- Detailed view timetable -->
    <div v-if="viewMode === 'detailed'" class="bg-white rounded-lg shadow overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full border-collapse">
          <thead>
            <tr class="bg-gray-50">
              <th class="border p-2 w-40">教室 / 时间</th>
              <th 
                v-for="day in displayedDays" 
                :key="`day-${day.value}`" 
                :colspan="availablePeriods.length" 
                class="border p-2 text-center"
                :class="{'bg-yellow-50': day.value === currentDayOfWeek}"
              >
                {{ day.label }}
              </th>
            </tr>
            <tr class="bg-gray-50">
              <th class="border p-2"></th>
              <template v-for="day in displayedDays" >
                <th 
                  v-for="period in availablePeriods" 
                  :key="`${day.value}-${period}`" 
                  class="border p-2 min-w-[100px]"
                  :class="{'bg-yellow-50': day.value === currentDayOfWeek}"
                >
                  第{{ period }}节
                  <div class="text-xs text-gray-500">{{ getPeriodTimeLabel(period) }}</div>
                </th>
              </template>
            </tr>
          </thead>
          <tbody>
            <tr v-for="classroom in filteredClassrooms" :key="classroom">
              <td class="border p-2 font-medium bg-gray-50">{{ classroom }}</td>
              <template v-for="day in displayedDays" >
                <td 
                  v-for="period in availablePeriods" 
                  :key="`${classroom}-${day.value}-${period}`" 
                  class="border p-2 align-top relative overflow-hidden"
                  :class="{'bg-yellow-50': day.value === currentDayOfWeek}"
                  style="width: 100px; height: 80px;"
                >
                  <div 
                    v-for="course in getCoursesForClassroomDayAndPeriod(classroom, day.value, period)" 
                    :key="`${course.scid}-${day.value}-${period}`"
                    class="mb-1 p-2 rounded-md shadow-sm cursor-pointer hover:shadow-md transition-shadow overflow-hidden"
                    :style="`background-color: ${cardColor}20;`"
                    @click="viewCourseDetails(course)"
                  >
                    <div class="font-medium text-sm truncate" :title="course.sctask">{{ course.sctask }}</div>
                    <div class="text-xs truncate" :title="course.composition">{{ course.composition }}</div>
                    <div class="text-xs text-gray-500 truncate">
                      教师ID: {{ course.scteacherid }}
                    </div>
                    <div class="text-xs bg-blue-100 text-blue-800 px-1 py-0.5 rounded-sm inline-block mt-1">
                      {{ course.scbegin_week }}~{{ course.scend_week }}周
                    </div>
                  </div>
                  <div 
                    v-if="!getCoursesForClassroomDayAndPeriod(classroom, day.value, period).length" 
                    class="text-xs text-gray-400 h-full flex items-center justify-center"
                  >
                    空闲
                  </div>
                </td>
              </template>
            </tr>
            <tr v-if="filteredClassrooms.length === 0">
              <td :colspan="displayedDays.length * availablePeriods.length + 1" class="border p-4 text-center text-gray-500">
                没有找到匹配的教室
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Thumbnail view -->
    <div v-if="viewMode === 'thumbnail'" class="bg-white rounded-lg shadow p-4">
      <div class="overflow-x-auto">
        <table class="min-w-full border-collapse">
          <thead>
            <tr class="bg-gray-50">
              <th class="border p-2 w-28">教室 / 时间</th>
              <th 
                v-for="day in displayedDays" 
                :key="`thumb-day-${day.value}`" 
                :colspan="availablePeriods.length" 
                class="border p-2 text-center"
                :class="{'bg-yellow-50': day.value === currentDayOfWeek}"
              >
                {{ day.label }}
              </th>
            </tr>
            <tr class="bg-gray-50">
              <th class="border p-2"></th>
              <template v-for="day in displayedDays" >
                <th 
                  v-for="period in availablePeriods" 
                  :key="`thumb-${day.value}-${period}`" 
                  class="border p-1 w-8"
                  :class="{'bg-yellow-50': day.value === currentDayOfWeek}"
                >
                  {{ period }}
                </th>
              </template>
            </tr>
          </thead>
          <tbody>
            <tr v-for="classroom in filteredClassrooms" :key="`thumb-${classroom}`">
              <td class="border p-2 font-medium bg-gray-50">{{ classroom }}</td>
              <template v-for="day in displayedDays" >
                <td 
                  v-for="period in availablePeriods" 
                  :key="`thumb-${classroom}-${day.value}-${period}`" 
                  class="border p-0 align-middle text-center h-8 w-8"
                  :class="{'bg-yellow-50': day.value === currentDayOfWeek}"
                >
                  <div 
                    v-if="hasCourseForDay(classroom, day.value, period)" 
                    class="w-full h-full cursor-pointer relative"
                    :style="`background-color: ${cardColor};`"
                    @click="viewThumbnailCourseDetails(classroom, day.value, period)"
                  >
                    <div class="absolute bottom-0 right-0 text-[8px] text-white bg-black bg-opacity-50 px-0.5">
                      {{ getCourseWeeks(classroom, day.value, period) }}
                    </div>
                  </div>
                </td>
              </template>
            </tr>
            <tr v-if="filteredClassrooms.length === 0">
              <td :colspan="displayedDays.length * availablePeriods.length + 1" class="border p-4 text-center text-gray-500">
                没有找到匹配的教室
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- Legend for thumbnail view -->
      <div class="mt-4 flex items-center text-sm">
        <div class="w-4 h-4 mr-2" :style="`background-color: ${cardColor};`"></div>
        <span>有课</span>
      </div>
    </div>

    <!-- Course details dialog -->
    <div v-if="selectedCourse" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <div class="flex justify-between items-start mb-4">
          <h3 class="text-lg font-medium">课程详情</h3>
          <button @click="selectedCourse = null" class="text-gray-500 hover:text-gray-700">
            <X class="w-5 h-5" />
          </button>
        </div>
        <div class="space-y-3">
          <div>
            <div class="text-sm font-medium text-gray-500">课程ID</div>
            <div>{{ selectedCourse.sctask }}</div>
          </div>
          <div>
            <div class="text-sm font-medium text-gray-500">班级</div>
            <div class="text-sm">{{ selectedCourse.composition }}</div>
          </div>
          <div>
            <div class="text-sm font-medium text-gray-500">教室</div>
            <div>{{ selectedCourse.scroom }}</div>
          </div>
          <div>
            <div class="text-sm font-medium text-gray-500">教师ID</div>
            <div>{{ selectedCourse.scteacherid }}</div>
          </div>
          <div>
            <div class="text-sm font-medium text-gray-500">开课学院</div>
            <div>{{ selectedCourse.scteacherdepartment }}</div>
          </div>
          <div>
            <div class="text-sm font-medium text-gray-500">时间</div>
            <div>第{{ selectedCourse.time }}节 ({{ selectedCourse.scbegin_time }} - {{ selectedCourse.scend_time }})</div>
          </div>
          <div>
            <div class="text-sm font-medium text-gray-500">周次</div>
            <div>第{{ selectedCourse.scbegin_week }}~{{ selectedCourse.scend_week }}周</div>
          </div>
          <div>
            <div class="text-sm font-medium text-gray-500">定位信息</div>
            <div class="text-sm bg-gray-100 p-2 rounded">
              教室: {{ selectedCourse.scroom }} | 
              日期: 第{{ selectedCourse.scbegin_week }}~{{ selectedCourse.scend_week }}周{{ getWeekdayName(parseInt(selectedCourse.scday_of_week)) }} | 
              节次: 第{{ selectedCourse.time }}节
            </div>
          </div>
        </div>
        <div class="mt-6 flex justify-end space-x-2">
          <button 
            @click="selectedCourse = null" 
            class="px-4 py-2 border rounded-md hover:bg-gray-50"
          >
            关闭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { Search, Download, X, LayoutGrid, Grid, RefreshCw } from 'lucide-vue-next';

// View mode
const viewMode = ref('detailed');

// Card color customization
const cardColor = ref('#4f46e5');

// Days of the week
const weekdays = [
  { label: '周一', value: 1 },
  { label: '周二', value: 2 },
  { label: '周三', value: 3 },
  { label: '周四', value: 4 },
  { label: '周五', value: 5 },
  { label: '周六', value: 6 },
  { label: '周日', value: 7 }
];

// Current day of week (1-7, where 1 is Monday)
const currentDayOfWeek = ref(1);

// State variables
const selectedWeek = ref(1);
const selectedDay = ref('');
const selectedCourse = ref(null);
const classroomSearch = ref('');
const courseNameSearch = ref('');
const classSearch = ref('');

// Available options
const availableWeeks = ref([...Array(20)].map((_, i) => i + 1)); // Weeks 1-20
const availablePeriods = ref([1, 2, 3, 4, 5, 6, 7, 8]); // Periods 1-8

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

// 课程数据
const courses = ref([]);

// 添加API数据加载状态
const isLoading = ref(false);
const loadError = ref(null);

// Filtered courses
const filteredCourses = computed(() => {
  let result = [...courses.value];
  
  // Filter by week
  result = result.filter(course => 
    course.scbegin_week <= selectedWeek.value && 
    course.scend_week >= selectedWeek.value
  );
  
  // Filter by day (if a specific day is selected)
  if (selectedDay.value) {
    result = result.filter(course => parseInt(course.scday_of_week) === parseInt(selectedDay.value));
  }
  
  // Filter by course name
  if (courseNameSearch.value) {
    result = result.filter(course => 
      course.sctask.toLowerCase().includes(courseNameSearch.value.toLowerCase())
    );
  }
  
  // Filter by class
  if (classSearch.value) {
    result = result.filter(course => 
      course.composition.toLowerCase().includes(classSearch.value.toLowerCase())
    );
  }
  
  return result;
});

// Get all classrooms
const allClassrooms = computed(() => {
  const classrooms = new Set();
  courses.value.forEach(course => {
    classrooms.add(course.scroom);
  });
  return [...classrooms].sort();
});

// Filtered classrooms
const filteredClassrooms = computed(() => {
  let result = [...allClassrooms.value];
  
  // Filter by classroom name
  if (classroomSearch.value) {
    result = result.filter(classroom => 
      classroom.toLowerCase().includes(classroomSearch.value.toLowerCase())
    );
  }
  
  // If there's a course name or class filter, only show classrooms with matching courses
  if (courseNameSearch.value || classSearch.value) {
    const matchedClassrooms = new Set();
    filteredCourses.value.forEach(course => {
      matchedClassrooms.add(course.scroom);
    });
    result = result.filter(classroom => matchedClassrooms.has(classroom));
  }
  
  return result;
});

// Displayed days based on selection
const displayedDays = computed(() => {
  if (selectedDay.value) {
    return weekdays.filter(day => day.value === parseInt(selectedDay.value));
  }
  return weekdays;
});

// Get courses for a specific classroom, day, and period
const getCoursesForClassroomDayAndPeriod = (classroom, day, period) => {
  return filteredCourses.value.filter(course => 
    course.scroom === classroom && 
    parseInt(course.scday_of_week) === day &&
    parseInt(course.time) === period
  );
};

// Check if a classroom has a course for a specific day and period
const hasCourseForDay = (classroom, day, period) => {
  return getCoursesForClassroomDayAndPeriod(classroom, day, period).length > 0;
};

// Get course weeks display for thumbnail
const getCourseWeeks = (classroom, day, period) => {
  const cellCourses = getCoursesForClassroomDayAndPeriod(classroom, day, period);
  if (cellCourses.length === 0) return '';
  
  const course = cellCourses[0];
  return `${course.scbegin_week }~${course.scend_week}`;
};

// Get period time label
const getPeriodTimeLabel = (period) => {
  if (period <= periodTimes.length) {
    const time = periodTimes[period - 1];
    return `${time.start}-${time.end}`;
  }
  return '';
};

// Get day name
const getWeekdayName = (day) => {
  const dayObj = weekdays.find(d => d.value === day);
  return dayObj ? dayObj.label : '';
};

// View course details
const viewCourseDetails = (course) => {
  selectedCourse.value = course;
};

// View course details from thumbnail
const viewThumbnailCourseDetails = (classroom, day, period) => {
  const courses = getCoursesForClassroomDayAndPeriod(classroom, day, period);
  if (courses.length > 0) {
    selectedCourse.value = courses[0];
  }
};

// Export data
const exportData = () => {
  alert('导出功能将在未来版本中实现');
};

// Get current day of week
const getCurrentDayOfWeek = () => {
  const today = new Date();
  // getDay() returns 0 for Sunday, 1 for Monday, etc.
  // Convert to our format where 1 is Monday, 7 is Sunday
  let day = today.getDay();
  return day === 0 ? 7 : day;
};

// 从API获取数据的函数
const fetchCoursesFromAPI = async () => {
  isLoading.value = true;
  loadError.value = null;
  
  try {
    // 模拟API请求
    // 实际使用时替换为真实的API请求
    // const response = await fetch('http://localhost:8080/classroom');
    
    // 模拟API响应
    const mockResponse = {
      code: 200,
      rows: [
        {
          scid: 1,
          sctask: "570102KBOB032024202511017",
          scday_of_week: "2",
          scroom: "JXL517",
          scbegin_week: 1,
          scend_week: 16,
          scbegin_time: "08:00:00",
          scend_time: "09:40:00",
          time: 1,
          scteacherid: "130",
          scteacherdepartment: "教育艺术学院",
          composition: "23学前教育5班"
        },
        {
          scid: 2,
          sctask: "570102KBOB032024202511018",
          scday_of_week: "3",
          scroom: "JXL101",
          scbegin_week: 1,
          scend_week: 8,
          scbegin_time: "10:00:00",
          scend_time: "11:40:00",
          time: 3,
          scteacherid: "131",
          scteacherdepartment: "计算机科学学院",
          composition: "23计算机科学1班,23计算机科学2班"
        },
        {
          scid: 3,
          sctask: "570102KBOB032024202511019",
          scday_of_week: "4",
          scroom: "JXL201",
          scbegin_week: 9,
          scend_week: 16,
          scbegin_time: "14:00:00",
          scend_time: "15:40:00",
          time: 5,
          scteacherid: "132",
          scteacherdepartment: "外国语学院",
          composition: "23英语1班"
        },
        {
          scid: 4,
          sctask: "570102KBOB032024202511020",
          scday_of_week: "1",
          scroom: "JXL301",
          scbegin_week: 1,
          scend_week: 16,
          scbegin_time: "08:00:00",
          scend_time: "09:40:00",
          time: 1,
          scteacherid: "133",
          scteacherdepartment: "数学学院",
          composition: "23数学1班,23数学2班,23数学3班"
        },
        {
          scid: 5,
          sctask: "570102KBOB032024202511021",
          scday_of_week: "5",
          scroom: "JXL401",
          scbegin_week: 1,
          scend_week: 16,
          scbegin_time: "16:00:00",
          scend_time: "17:40:00",
          time: 7,
          scteacherid: "134",
          scteacherdepartment: "物理学院",
          composition: "23物理1班"
        },
        {
          scid: 6,
          sctask: "570102KBOB032024202511022",
          scday_of_week: "1",
          scroom: "JXL301",
          scbegin_week: 1,
          scend_week: 16,
          scbegin_time: "10:00:00",
          scend_time: "11:40:00",
          time: 3,
          scteacherid: "135",
          scteacherdepartment: "化学学院",
          composition: "23化学1班,23化学2班"
        },
        {
          scid: 7,
          sctask: "570102KBOB032024202511023",
          scday_of_week: "2",
          scroom: "JXL517",
          scbegin_week: 1,
          scend_week: 8,
          scbegin_time: "14:00:00",
          scend_time: "15:40:00",
          time: 5,
          scteacherid: "136",
          scteacherdepartment: "生物学院",
          composition: "23生物1班"
        },
        {
          scid: 8,
          sctask: "570102KBOB032024202511024",
          scday_of_week: "3",
          scroom: "JXL101",
          scbegin_week: 9,
          scend_week: 16,
          scbegin_time: "08:00:00",
          scend_time: "09:40:00",
          time: 1,
          scteacherid: "137",
          scteacherdepartment: "历史学院",
          composition: "23历史1班,23历史2班"
        }
      ]
    };
    
    // 如果使用真实API，解析响应
    // if (!response.ok) {
    //   throw new Error(`API请求失败: ${response.status}`);
    // }
    // const data = await response.json();
    
    // 使用模拟数据
    const data = mockResponse;
    
    if (data.code === 200) {
      courses.value = data.rows;
      console.log('从API加载了', data.rows.length, '条课程数据');
    } else {
      throw new Error(`API返回错误: ${data.code}`);
    }
  } catch (error) {
    console.error('获取课程数据失败:', error);
    loadError.value = error.message;
  } finally {
    isLoading.value = false;
  }
};

// Lifecycle hooks
onMounted(() => {
  // Set current day of week
  currentDayOfWeek.value = getCurrentDayOfWeek();
  
  // Automatically select current day
  selectedDay.value = currentDayOfWeek.value.toString();
  
  // 从API获取数据
  fetchCoursesFromAPI();
  
  console.log('Component mounted');
});
</script>

<style scoped>
.bg-primary {
  background-color: #4f46e5;
}

.bg-primary-dark {
  background-color: #4338ca;
}

.text-primary {
  color: #4f46e5;
}

.border-primary {
  border-color: #4f46e5;
}
</style>
