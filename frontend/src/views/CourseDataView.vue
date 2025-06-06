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
          <thead class="sticky top-0 bg-white z-10">
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
                  class="border p-1 w-[60px]"
                  :class="{'bg-yellow-50': day.value === currentDayOfWeek}"
                >
                  第{{ period }}节
                  <div class="text-[9px] text-gray-500">{{ getPeriodTimeLabel(period) }}</div>
                </th>
              </template>
            </tr>
          </thead>
          <tbody>
            <tr v-for="classroom in filteredClassrooms" :key="classroom">
              <td class="border p-2 font-medium bg-gray-50 sticky left-0 z-10">{{ classroom }}</td>
              <template v-for="day in displayedDays" >
                <td 
                  v-for="period in availablePeriods" 
                  :key="`${classroom}-${day.value}-${period}`" 
                  class="border p-0.5 align-top relative"
                  :class="{'bg-yellow-50': day.value === currentDayOfWeek}"
                  style="width: 60px; height: 60px; overflow: hidden;"
                >
                  <!-- Apply mini-card style if course exists -->
                  <div 
                    v-if="getCoursesForClassroomDayAndPeriod(classroom, day.value, period).length > 0"
                    class="h-full w-full p-1 rounded-[3px] bg-primary/10 hover:bg-primary/20 cursor-pointer flex flex-col justify-center text-[9px] leading-tight"
                    @click="viewCourseDetails(getCoursesForClassroomDayAndPeriod(classroom, day.value, period)[0])"
                  >
                    <div class="font-medium text-primary/90 truncate" :title="getCoursesForClassroomDayAndPeriod(classroom, day.value, period)[0].sctask">
                      {{ getCoursesForClassroomDayAndPeriod(classroom, day.value, period)[0].sctask }}
                    </div>
                    <div class="truncate text-gray-600 text-[8px]" :title="getCoursesForClassroomDayAndPeriod(classroom, day.value, period)[0].composition">
                      {{ getCoursesForClassroomDayAndPeriod(classroom, day.value, period)[0].composition }}
                    </div>
                    <div class="text-[8px] text-blue-700">{{ getCoursesForClassroomDayAndPeriod(classroom, day.value, period)[0].scbegin_week }}~{{ getCoursesForClassroomDayAndPeriod(classroom, day.value, period)[0].scend_week }}周</div>
                  </div>
                  <!-- Empty cell style -->
                  <div 
                    v-else
                    class="text-[9px] text-gray-400 h-full flex items-center justify-center"
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
          <thead class="sticky top-0 bg-white z-10">
            <tr class="bg-gray-50">
              <th class="border p-2 w-28 sticky left-0 z-20">教室 / 时间</th>
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
              <th class="border p-2 sticky left-0 z-20"></th>
              <template v-for="day in displayedDays" >
                <th 
                  v-for="period in availablePeriods" 
                  :key="`thumb-${day.value}-${period}`" 
                  class="border p-0 align-middle text-center h-6 w-6"
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
                </th>
              </template>
            </tr>
          </thead>
          <tbody>
            <tr v-for="classroom in filteredClassrooms" :key="`thumb-${classroom}`">
              <td class="border p-2 font-medium bg-gray-50 sticky left-0 z-10">{{ classroom }}</td>
              <template v-for="day in displayedDays" >
                <td 
                  v-for="period in availablePeriods" 
                  :key="`thumb-${classroom}-${day.value}-${period}`" 
                  class="border p-0 align-middle text-center h-6 w-6"
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
            <div>第{{ selectedCourse.time }}节 <span v-if="selectedCourse.slot_end && selectedCourse.slot_end !== selectedCourse.time">至{{ selectedCourse.slot_end }}节</span> 
              <span v-if="selectedCourse.scbegin_time">({{ selectedCourse.scbegin_time }} - {{ selectedCourse.scend_time }})</span>
            </div>
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
              节次: 第{{ selectedCourse.time }}节<span v-if="selectedCourse.slot_end && selectedCourse.slot_end !== selectedCourse.time">至{{ selectedCourse.slot_end }}节</span>
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
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import { Search, Download, X, LayoutGrid, Grid, RefreshCw } from 'lucide-vue-next';
import axios from 'axios';

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

// 优化：将所有课程数据缓存在内存中
const allCourses = ref([]);
// 显示给用户看的课程数据
const courses = ref([]);

// 添加API数据加载状态
const isLoading = ref(false);
const loadError = ref(null);

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

// 解析课程槽位
const parseSlot = (slotStr) => {
  if (!slotStr) return { start: 0, end: 0 };
  
  const parts = slotStr.split('-');
  const start = parseInt(parts[0]);
  const end = parts.length > 1 ? parseInt(parts[1]) : start;
  
  return { start, end };
};

// 处理API返回的课程数据
const processCourseData = (apiCourses) => {
  return apiCourses.map(course => {
    // 解析课程槽位
    const slot = parseSlot(course.scslot);
    
    // 设置开始和结束时间
    let beginTime = '';
    let endTime = '';
    if (slot.start > 0 && slot.start <= periodTimes.length) {
      beginTime = periodTimes[slot.start - 1].start;
    }
    if (slot.end > 0 && slot.end <= periodTimes.length) {
      endTime = periodTimes[slot.end - 1].end;
    }
    
    // 转换数据类型确保一致性
    return {
      ...course,
      scday_of_week: course.scday_of_week.toString(),
      scbegin_week: parseInt(course.scbegin_week),
      scend_week: parseInt(course.scend_week),
      time: slot.start, // 使用开始槽位作为时间
      slot_end: slot.end, // 添加结束槽位
      scbegin_time: beginTime,
      scend_time: endTime
    };
  });
};

// 优化：根据筛选条件从主数据集中过滤数据，而不是每次都重新计算
const applyFilters = () => {
  // 创建一个新的筛选后的数据集
  let result = [...allCourses.value];
  
  // 筛选周次
  result = result.filter(course => 
    course.scbegin_week <= selectedWeek.value && 
    course.scend_week >= selectedWeek.value
  );
  
  // 筛选星期
  if (selectedDay.value) {
    result = result.filter(course => parseInt(course.scday_of_week) === parseInt(selectedDay.value));
  }
  
  // 筛选课程名称
  if (courseNameSearch.value) {
    const searchTerm = courseNameSearch.value.toLowerCase();
    result = result.filter(course => 
      course.sctask.toLowerCase().includes(searchTerm)
    );
  }
  
  // 筛选班级
  if (classSearch.value) {
    const searchTerm = classSearch.value.toLowerCase();
    result = result.filter(course => 
      course.composition.toLowerCase().includes(searchTerm)
    );
  }
  
  // 更新筛选后的课程数据
  courses.value = result;
};

// 添加监听器，当筛选条件变化时，更新数据
watch([selectedWeek, selectedDay, courseNameSearch, classSearch], () => {
  nextTick(() => {
    applyFilters();
  });
}, { deep: true });

// 计算所有教室
const allClassrooms = computed(() => {
  const classrooms = new Set();
  courses.value.forEach(course => {
    if (course.scroom) {
      classrooms.add(course.scroom);
    }
  });
  return [...classrooms].sort();
});

// 根据搜索条件筛选教室
const filteredClassrooms = computed(() => {
  if (!classroomSearch.value) return allClassrooms.value;
  
  const searchTerm = classroomSearch.value.toLowerCase();
  return allClassrooms.value.filter(classroom => 
    classroom.toLowerCase().includes(searchTerm)
  );
});

// 根据选择的天数显示
const displayedDays = computed(() => {
  if (selectedDay.value) {
    return weekdays.filter(day => day.value === parseInt(selectedDay.value));
  }
  return weekdays;
});

// 优化：使用索引加速查找课程
const courseIndexes = ref(new Map()); // 教室-日期-节次 索引

// 优化：创建查找索引以加快数据检索
const createCourseIndexes = () => {
  const indexMap = new Map();
  
  courses.value.forEach(course => {
    const classroom = course.scroom;
    const day = parseInt(course.scday_of_week);
    const startSlot = course.time;
    const endSlot = course.slot_end || course.time;
    
    for (let slot = startSlot; slot <= endSlot; slot++) {
      const key = `${classroom}-${day}-${slot}`;
      if (!indexMap.has(key)) {
        indexMap.set(key, []);
      }
      indexMap.get(key).push(course);
    }
  });
  
  courseIndexes.value = indexMap;
};

// 监听课程数据变化，重建索引
watch(courses, () => {
  createCourseIndexes();
}, { deep: true });

// 优化：使用索引获取课程
const getCoursesForClassroomDayAndPeriod = (classroom, day, period) => {
  const key = `${classroom}-${day}-${period}`;
  return courseIndexes.value.get(key) || [];
};

// 检查教室在特定日期和节次是否有课
const hasCourseForDay = (classroom, day, period) => {
  const key = `${classroom}-${day}-${period}`;
  return courseIndexes.value.has(key) && courseIndexes.value.get(key).length > 0;
};

// 获取课程周次显示
const getCourseWeeks = (classroom, day, period) => {
  const cellCourses = getCoursesForClassroomDayAndPeriod(classroom, day, period);
  if (cellCourses.length === 0) return '';
  
  const course = cellCourses[0];
  return `${course.scbegin_week}~${course.scend_week}`;
};

// 获取时间段标签
const getPeriodTimeLabel = (period) => {
  if (period <= periodTimes.length) {
    const time = periodTimes[period - 1];
    return `${time.start}-${time.end}`;
  }
  return '';
};

// 获取星期名称
const getWeekdayName = (day) => {
  const dayObj = weekdays.find(d => d.value === day);
  return dayObj ? dayObj.label : '';
};

// 查看课程详情
const viewCourseDetails = (course) => {
  selectedCourse.value = course;
};

// 从缩略图查看课程详情
const viewThumbnailCourseDetails = (classroom, day, period) => {
  const courses = getCoursesForClassroomDayAndPeriod(classroom, day, period);
  if (courses.length > 0) {
    selectedCourse.value = courses[0];
  }
};

// 导出数据
const exportData = () => {
  alert('导出功能将在未来版本中实现');
};

// 获取当前星期几
const getCurrentDayOfWeek = () => {
  const today = new Date();
  // getDay() returns 0 for Sunday, 1 for Monday, etc.
  // Convert to our format where 1 is Monday, 7 is Sunday
  let day = today.getDay();
  return day === 0 ? 7 : day;
};

// 测试数据
const mockCourses = [
  {
    scid: 1,
    sctask: "570102KBOB032024202511017",
    scday_of_week: "2",
    scroom: "JXL517",
    scbegin_week: 1,
    scend_week: 16,
    scslot: "1-2",
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
    scslot: "3-4",
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
    scslot: "5-6",
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
    scslot: "1-2",
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
    scslot: "7-8",
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
    scslot: "3-4",
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
    scslot: "5-6",
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
    scslot: "1-2",
    scteacherid: "137",
    scteacherdepartment: "历史学院",
    composition: "23历史1班,23历史2班"
  }
];

// 从API获取数据的函数
const fetchCoursesFromAPI = async () => {
  isLoading.value = true;
  loadError.value = null;
  
  try {
    // 尝试从实际API获取数据
    const response = await axios.get('http://localhost:8080/manual/all');
    
    if (response.status === 200 && response.data.code === 200) {
      // 处理API返回的数据
      const processedData = processCourseData(response.data.rows);
      allCourses.value = processedData; // 存储完整数据集
      applyFilters(); // 应用筛选条件
      console.log('从API加载了', allCourses.value.length, '条课程数据');
    } else {
      throw new Error(`API返回错误: ${response.data.code || response.status}`);
    }
  } catch (error) {
    console.error('获取课程数据失败:', error);
    loadError.value = `无法从API获取数据: ${error.message}。使用测试数据代替。`;
    
    // 使用测试数据
    allCourses.value = processCourseData(mockCourses);
    applyFilters();
    console.log('使用测试数据', allCourses.value.length, '条');
  } finally {
    isLoading.value = false;
  }
};

// 生命周期钩子
onMounted(() => {
  // 设置当前星期几
  currentDayOfWeek.value = getCurrentDayOfWeek();
  
  // 自动选择当前日期
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

/* Add specific style for the mini-card appearance */
.bg-primary\/10 {
  background-color: rgba(79, 70, 229, 0.1);
}
.hover\:bg-primary\/20:hover {
  background-color: rgba(79, 70, 229, 0.2);
}
.text-primary\/90 {
  color: rgba(79, 70, 229, 0.9);
}
</style>
