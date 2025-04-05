<template>
  <div class="space-y-6">
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
              <template v-for="day in displayedDays">
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
                  class="border p-2 align-top relative h-24"
                  :class="{'bg-yellow-50': day.value === currentDayOfWeek}"
                >
                  <div 
                    v-for="course in getCoursesForClassroomDayAndPeriod(classroom, day.value, period)" 
                    :key="`${course.id}-${day.value}-${period}`"
                    class="mb-1 p-2 rounded-md shadow-sm cursor-pointer hover:shadow-md transition-shadow"
                    :style="`background-color: ${cardColor}20;`"
                    @click="viewCourseDetails(course)"
                  >
                    <div class="font-medium text-sm truncate" :title="course.name">{{ course.name }}</div>
                    <div class="text-xs truncate" :title="formatClasses(course.classes)">
                      {{ formatClasses(course.classes) }}
                    </div>
                    <div class="text-xs text-gray-500">
                      教师ID: {{ course.teacherId }}
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
              <th class="border p-2 w-40">教室 / 时间</th>
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
              <template v-for="day in displayedDays">
                <td 
                  v-for="period in availablePeriods" 
                  :key="`thumb-${classroom}-${day.value}-${period}`" 
                  class="border p-0 align-middle text-center h-8 w-8"
                  :class="{'bg-yellow-50': day.value === currentDayOfWeek}"
                >
                  <div 
                    v-if="hasCourseForDay(classroom, day.value, period)" 
                    class="w-full h-full cursor-pointer"
                    :style="`background-color: ${cardColor};`"
                    @click="viewThumbnailCourseDetails(classroom, day.value, period)"
                  ></div>
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
            <div class="text-sm font-medium text-gray-500">课程名称</div>
            <div>{{ selectedCourse.name }}</div>
          </div>
          <div>
            <div class="text-sm font-medium text-gray-500">班级</div>
            <div class="text-sm">{{ selectedCourse.classes }}</div>
          </div>
          <div>
            <div class="text-sm font-medium text-gray-500">教室</div>
            <div>{{ selectedCourse.classroom }}</div>
          </div>
          <div>
            <div class="text-sm font-medium text-gray-500">教师ID</div>
            <div>{{ selectedCourse.teacherId }}</div>
          </div>
          <div>
            <div class="text-sm font-medium text-gray-500">时间</div>
            <div>第{{ selectedCourse.week }}周 {{ getWeekdayName(selectedCourse.day) }} 第{{ selectedCourse.period }}节</div>
          </div>
          <div>
            <div class="text-sm font-medium text-gray-500">定位信息</div>
            <div class="text-sm bg-gray-100 p-2 rounded">
              教室: {{ selectedCourse.classroom }} | 
              日期: 第{{ selectedCourse.week }}周{{ getWeekdayName(selectedCourse.day) }} | 
              节次: 第{{ selectedCourse.period }}节
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
          <button 
            @click="editCourse(selectedCourse)" 
            class="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary-dark"
          >
            编辑
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { Search, Download, X, LayoutGrid, Grid } from 'lucide-vue-next';

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
const selectedWeek = ref(6);
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

// Sample course data
const courses = ref([
  {
    id: 1,
    name: '710201ZXB01',
    classes: '24数字媒体技术1班（五年制）,24数字媒体技术2班（五年制）,24计算机应用1班,24计算机应用2班',
    classroom: 'JNL2#205-网络实训室',
    teacherId: 439,
    week: 6,
    day: 4,
    period: 1
  },
  {
    id: 2,
    name: '710201ZXB01',
    classes: '24数字媒体技术1班（五年制）,24数字媒体技术2班（五年制）,24计算机应用1班,24计算机应用2班',
    classroom: 'JNL2#205-网络实训室',
    teacherId: 439,
    week: 6,
    day: 4,
    period: 2
  },
  {
    id: 3,
    name: '710201ZXB01',
    classes: '24数字媒体技术1班（五年制）,24数字媒体技术2班（五年制）,24计算机应用1班,24计算机应用2班',
    classroom: 'JNL2#205-网络实训室',
    teacherId: 439,
    week: 7,
    day: 4,
    period: 1
  },
  {
    id: 4,
    name: '710201ZXB01',
    classes: '24数字媒体技术1班（五年制）,24数字媒体技术2班（五年制）,24计算机应用1班,24计算机应用2班',
    classroom: 'JNL2#205-网络实训室',
    teacherId: 439,
    week: 7,
    day: 4,
    period: 2
  },
  // More sample data
  {
    id: 5,
    name: '710202ZXB02',
    classes: '24数字媒体技术1班（五年制）',
    classroom: 'JNL2#206-多媒体实训室',
    teacherId: 440,
    week: 6,
    day: 1,
    period: 3
  },
  {
    id: 6,
    name: '710203ZXB03',
    classes: '24计算机应用1班',
    classroom: 'JNL2#207-程序设计实训室',
    teacherId: 441,
    week: 6,
    day: 2,
    period: 4
  },
  {
    id: 7,
    name: '710204ZXB04',
    classes: '24计算机应用2班',
    classroom: 'JNL2#208-数据库实训室',
    teacherId: 442,
    week: 6,
    day: 3,
    period: 5
  },
  {
    id: 8,
    name: '710205ZXB05',
    classes: '24数字媒体技术1班（五年制）,24数字媒体技术2班（五年制）',
    classroom: 'JNL1#101-普通教室',
    teacherId: 443,
    week: 6,
    day: 1,
    period: 1
  },
  {
    id: 9,
    name: '710206ZXB06',
    classes: '24计算机应用1班,24计算机应用2班',
    classroom: 'JNL1#102-普通教室',
    teacherId: 444,
    week: 6,
    day: 2,
    period: 2
  },
  {
    id: 10,
    name: '710207ZXB07',
    classes: '24数字媒体技术1班（五年制）',
    classroom: 'JNL1#201-普通教室',
    teacherId: 445,
    week: 6,
    day: 3,
    period: 3
  },
  // Courses for the same classroom on different days
  {
    id: 11,
    name: '710208ZXB08',
    classes: '24计算机应用1班',
    classroom: 'JNL2#206-多媒体实训室',
    teacherId: 446,
    week: 6,
    day: 2,
    period: 3
  },
  {
    id: 12,
    name: '710209ZXB09',
    classes: '24计算机应用2班',
    classroom: 'JNL2#206-多媒体实训室',
    teacherId: 447,
    week: 6,
    day: 3,
    period: 3
  },
  // Courses for the same classroom and period in different weeks
  {
    id: 13,
    name: '710210ZXB10',
    classes: '24数字媒体技术1班（五年制）',
    classroom: 'JNL1#202-普通教室',
    teacherId: 448,
    week: 6,
    day: 4,
    period: 4
  },
  {
    id: 14,
    name: '710210ZXB10',
    classes: '24数字媒体技术1班（五年制）',
    classroom: 'JNL1#202-普通教室',
    teacherId: 448,
    week: 7,
    day: 4,
    period: 4
  },
  // Add more courses for different days
  {
    id: 15,
    name: '710211ZXB11',
    classes: '24数字媒体技术2班（五年制）',
    classroom: 'JNL1#201-普通教室',
    teacherId: 449,
    week: 6,
    day: 5,
    period: 2
  },
  {
    id: 16,
    name: '710212ZXB12',
    classes: '24计算机应用1班',
    classroom: 'JNL2#207-程序设计实训室',
    teacherId: 450,
    week: 6,
    day: 6,
    period: 1
  },
  {
    id: 17,
    name: '710213ZXB13',
    classes: '24计算机应用2班',
    classroom: 'JNL2#208-数据库实训室',
    teacherId: 451,
    week: 6,
    day: 7,
    period: 3
  }
]);

// Filtered courses
const filteredCourses = computed(() => {
  let result = [...courses.value];
  
  // Filter by week
  result = result.filter(course => course.week === selectedWeek.value);
  
  // Filter by day (if a specific day is selected)
  if (selectedDay.value) {
    result = result.filter(course => course.day === parseInt(selectedDay.value));
  }
  
  // Filter by course name
  if (courseNameSearch.value) {
    result = result.filter(course => 
      course.name.toLowerCase().includes(courseNameSearch.value.toLowerCase())
    );
  }
  
  // Filter by class
  if (classSearch.value) {
    result = result.filter(course => 
      course.classes.toLowerCase().includes(classSearch.value.toLowerCase())
    );
  }
  
  return result;
});

// Get all classrooms
const allClassrooms = computed(() => {
  const classrooms = new Set();
  courses.value.forEach(course => {
    classrooms.add(course.classroom);
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
      matchedClassrooms.add(course.classroom);
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
    course.classroom === classroom && 
    course.day === day &&
    course.period === period
  );
};

// Check if a classroom has a course for a specific day and period
const hasCourseForDay = (classroom, day, period) => {
  return getCoursesForClassroomDayAndPeriod(classroom, day, period).length > 0;
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

// Format class display
const formatClasses = (classes) => {
  if (!classes) return '';
  const classList = classes.split(',');
  if (classList.length <= 2) return classes;
  return `${classList[0]}等${classList.length}个班级`;
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

// Edit course
const editCourse = (course) => {
  // Add logic for editing a course
  alert(`编辑课程: ${course.name}`);
  selectedCourse.value = null;
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

// Lifecycle hooks
onMounted(() => {
  // Set current day of week
  currentDayOfWeek.value = getCurrentDayOfWeek();
  
  // Automatically select current day
  selectedDay.value = currentDayOfWeek.value.toString();
  
  // Here you can add logic to fetch data from backend
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

