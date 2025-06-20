<template>
  <div class="flex flex-col h-full space-y-4">
    <!-- 加载状态提示 -->
    <div v-if="isLoading" class="bg-white rounded-lg shadow p-3 text-center">
      <div class="flex items-center justify-center text-gray-600">
        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        正在加载课程数据...
      </div>
    </div>
    
    <!-- 顶部控制栏 -->
    <div class="bg-white rounded-lg shadow p-3">
      <div class="flex flex-wrap justify-between items-center gap-4">
        <h2 class="text-xl font-bold">手动排课</h2>
        <div class="flex flex-wrap gap-2">
          <!-- 周次选择器 -->
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
          
          <!-- 保存按钮 -->
          <button 
            @click="saveSchedule" 
            class="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary-dark"
          >
            <Save class="w-4 h-4 inline-block mr-1" />
            保存排课
          </button>
        </div>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="flex flex-1 gap-4 overflow-hidden">
      <!-- 左侧课程导航栏 - 修改宽度绑定 -->
      <div 
        :style="sidebarStyle" 
        class="bg-white rounded-lg shadow overflow-hidden flex flex-col transition-all duration-300 ease-in-out"
      >
        <!-- 侧边栏标题栏 -->
        <div class="p-2 border-b flex justify-between items-center flex-shrink-0">
          <transition name="fade" mode="out-in">
            <h3 v-if="!sidebarCollapsed" class="text-lg font-medium">课程列表</h3>
          </transition>
          <button 
            @click="toggleSidebar" 
            class="p-1 rounded-full hover:bg-gray-100 transition-transform duration-300"
            :class="{'rotate-180': sidebarCollapsed}"
          >
            <ChevronLeft class="w-5 h-5" />
          </button>
        </div>
        
        <!-- 侧边栏内容 - 确保flex布局正确 -->
        <transition 
          name="sidebar-content" 
          mode="out-in"
        >
          <div v-if="!sidebarCollapsed" class="flex flex-col flex-1 overflow-hidden">
            <!-- 搜索和过滤 - 保持flex-shrink: 0 -->
            <div class="p-2 border-b flex-shrink-0">
              <div class="relative">
                <input 
                  v-model="courseSearch" 
                  type="text" 
                  placeholder="搜索课程" 
                  class="w-full h-9 rounded-md border border-input bg-background pl-9 pr-3 py-1 text-sm shadow-sm"
                />
                <Search class="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
              </div>
              <div class="mt-2 flex flex-wrap gap-2">
                <button 
                  @click="filterType = 'all'" 
                  class="px-2 py-1 text-xs rounded-md transition-colors duration-200"
                  :class="filterType === 'all' ? 'bg-primary text-white' : 'bg-gray-100 text-gray-700'"
                >
                  全部
                </button>
                <button 
                  @click="filterType = 'unscheduled'" 
                  class="px-2 py-1 text-xs rounded-md transition-colors duration-200"
                  :class="filterType === 'unscheduled' ? 'bg-primary text-white' : 'bg-gray-100 text-gray-700'"
                >
                  未排课
                </button>
                <button 
                  @click="filterType = 'scheduled'" 
                  class="px-2 py-1 text-xs rounded-md transition-colors duration-200"
                  :class="filterType === 'scheduled' ? 'bg-primary text-white' : 'bg-gray-100 text-gray-700'"
                >
                  已排课
                </button>
              </div>
            </div>
            
            <!-- 课程列表容器 - 保持 overflow-y-auto -->
            <div class="flex-1 overflow-y-auto p-1 space-y-1">
              <div 
                v-for="course in paginatedCourses" 
                :key="course.scid" 
                class="border rounded-md cursor-pointer transition-all duration-150 overflow-hidden"
                :class="[
                  selectedCourse && selectedCourse.scid === course.scid ? 'bg-primary-light border-primary' : 'bg-white border-gray-200 hover:border-gray-300',
                  isCourseExpanded(course.scid) ? 'shadow-sm' : ''
                ]"
                @click="toggleAndSelectCourse(course)"
                draggable="true"
                @dragstart="onDragStart($event, course)"
              >
                <!-- 基础信息 (始终显示) -->
                <div class="p-2 flex justify-between items-center">
                  <div>
                    <div class="font-medium text-sm truncate" :title="course.sctask">{{ course.sctask }}</div>
                    <div class="text-xs text-gray-600 truncate" :title="course.composition">{{ course.composition }}</div>
                  </div>
                  <button 
                    class="p-1 rounded hover:bg-gray-100"
                    @click.stop="toggleExpand(course.scid)" 
                  >
                    <ChevronDown 
                      class="w-4 h-4 text-gray-500 transition-transform duration-200"
                      :class="{'rotate-180': isCourseExpanded(course.scid)}"
                    />
                  </button>
                </div>
                
                <!-- 详细信息 (可折叠) -->
                <div v-if="isCourseExpanded(course.scid)" class="p-2 border-t border-gray-200 bg-gray-50">
                  <div class="text-xs text-gray-600 truncate mb-1">教师ID: {{ course.scteacherid }}</div>
                  <div class="text-xs text-gray-600 truncate mb-1">学院: {{ course.scteacherdepartment }}</div>
                  <div v-if="isScheduled(course)" class="flex flex-wrap gap-1">
                    <span class="text-[10px] bg-green-100 text-green-800 px-1 py-0.5 rounded-sm inline-block">
                      {{ getWeekdayName(parseInt(course.scday_of_week)) }} {{ course.time }}<span v-if="course.slot_end && course.slot_end !== course.time">-{{ course.slot_end }}</span>
                    </span>
                    <span class="text-[10px] bg-blue-100 text-blue-800 px-1 py-0.5 rounded-sm inline-block">
                      {{ course.scbegin_week }}~{{ course.scend_week }}
                    </span>
                    <span class="text-[10px] bg-gray-200 text-gray-800 px-1 py-0.5 rounded-sm inline-block truncate">
                      {{ course.scroom }}
                    </span>
                  </div>
                  <div v-else class="text-xs text-gray-400 italic">
                    未排课
                  </div>
                </div>
              </div>
              <div v-if="courses.length === 0" class="p-4 text-center text-gray-500">
                没有找到匹配的课程
              </div>
              
              <!-- 分页控制 -->
              <div v-if="totalPages > 1" class="pt-2 flex justify-between items-center text-xs border-t mt-2">
                <span>
                  显示 {{ (courseListPage - 1) * courseListPageSize + 1 }}-{{ Math.min(courseListPage * courseListPageSize, courses.length) }} / {{ courses.length }}
                </span>
                <div class="flex gap-1 items-center">
                  <button 
                    @click="courseListPage = 1" 
                    class="px-2 py-1 bg-gray-100 rounded hover:bg-gray-200 disabled:opacity-50"
                    :disabled="courseListPage === 1"
                    title="首页"
                  >
                    &laquo;
                  </button>
                  <button 
                    @click="prevPage" 
                    class="px-2 py-1 bg-gray-100 rounded hover:bg-gray-200 disabled:opacity-50"
                    :disabled="courseListPage === 1"
                  >
                    &lsaquo;
                  </button>
                  
                  <!-- 页码快速索引 -->
                  <div class="flex items-center gap-1 mx-1">
                    <div v-for="(page, index) in pageNumbers" :key="`page-${index}-${page}`" class="flex">
                      <button 
                        v-if="page !== '...'"
                        @click="courseListPage = page" 
                        class="w-6 h-6 text-center rounded text-xs"
                        :class="page === courseListPage ? 'bg-primary text-white' : 'bg-gray-100 hover:bg-gray-200'"
                      >
                        {{ page }}
                      </button>
                      <span v-else class="text-gray-500">...</span>
                    </div>
                  </div>
                  
                  <!-- 页码输入框 -->
                  <div class="relative mx-1 hidden sm:block">
                    <input 
                      v-model="tempCoursePageInput"
                      @keyup.enter="jumpToCoursePage"
                      type="text" 
                      class="w-10 h-6 text-center text-xs border rounded"
                      placeholder="#"
                    />
                  </div>
                  
                  <button 
                    @click="nextPage" 
                    class="px-2 py-1 bg-gray-100 rounded hover:bg-gray-200 disabled:opacity-50"
                    :disabled="courseListPage === totalPages"
                  >
                    &rsaquo;
                  </button>
                  <button 
                    @click="courseListPage = totalPages" 
                    class="px-2 py-1 bg-gray-100 rounded hover:bg-gray-200 disabled:opacity-50"
                    :disabled="courseListPage === totalPages"
                    title="末页"
                  >
                    &raquo;
                  </button>
                </div>
              </div>
            </div>
          </div>
        </transition>
      </div>

      <!-- 调整大小的拖动条 - 保持不变 -->
      <transition name="fade">
        <div 
          v-if="!sidebarCollapsed"
          class="w-1 bg-gray-200 hover:bg-primary hover:w-1.5 cursor-col-resize transition-all"
          @mousedown="startResize"
        ></div>
      </transition>

      <!-- 右侧排课区域 - 确保 flex-1 生效 -->
      <div class="flex-1 flex flex-col gap-3 overflow-hidden">
        <!-- 课程详情卡片 (只在选中课程时显示) -->
        <div v-if="selectedCourse" class="bg-white rounded-lg shadow p-3">
          <!-- 课程基本信息 -->
          <div class="mb-3 bg-gray-50 p-2 rounded-md">
            <div class="text-sm font-medium text-primary truncate" :title="selectedCourse.sctask">{{ selectedCourse.sctask }}</div>
            <div class="text-xs text-gray-600 truncate" :title="selectedCourse.composition">{{ selectedCourse.composition }}</div>
            <div class="text-xs text-gray-500 flex gap-2 mt-1">
              <span>教师ID: {{ selectedCourse.scteacherid }}</span>
              <span>学院: {{ selectedCourse.scteacherdepartment }}</span>
            </div>
          </div>
          
          <!-- 排课表单 -->
          <div class="grid grid-cols-6 gap-3">
            <div>
              <label class="block text-xs font-medium mb-1">教室</label>
              <input 
                v-model="selectedCourse.scroom" 
                type="text" 
                class="w-full h-8 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm"
              />
            </div>
            <div>
              <label class="block text-xs font-medium mb-1">星期</label>
              <select 
                v-model="selectedCourse.scday_of_week" 
                class="w-full h-8 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm"
              >
                <option v-for="day in weekdays" :key="day.value" :value="day.value.toString()">{{ day.label }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-medium mb-1">节次</label>
              <select 
                v-model="selectedCourse.time" 
                class="w-full h-8 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm"
              >
                <option v-for="period in availablePeriods" :key="period" :value="period">第{{ period }}节</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-medium mb-1">开始周</label>
              <select 
                v-model="selectedCourse.scbegin_week" 
                class="w-full h-8 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm"
              >
                <option v-for="week in availableWeeks" :key="week" :value="week">第{{ week }}周</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-medium mb-1">结束周</label>
              <select 
                v-model="selectedCourse.scend_week" 
                class="w-full h-8 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm"
              >
                <option v-for="week in availableWeeks" :key="week" :value="week">第{{ week }}周</option>
              </select>
            </div>
            <div class="flex items-end">
              <button 
                @click="applySchedule" 
                class="px-4 py-1.5 bg-primary text-white rounded-md hover:bg-primary-dark"
              >
                应用排课
              </button>
            </div>
          </div>
        </div>

        <!-- 缩略图视图 -->
        <div class="flex-1 bg-white rounded-lg shadow overflow-hidden">
          <div class="overflow-auto h-full">
            <table class="w-full border-collapse">
              <thead class="sticky top-0 bg-white z-10">
                <tr class="bg-gray-50">
                  <th class="border p-2 w-20">教室 / 时间</th>
                  <th 
                    v-for="day in weekdays" 
                    :key="`thumb-day-${day.value}`" 
                    :colspan="availablePeriods.length" 
                    class="border p-2 text-center"
                  >
                    {{ day.label }}
                  </th>
                </tr>
                <tr class="bg-gray-50">
                  <th class="border p-2"></th>
                  <template v-for="day in weekdays" >
                    <th 
                      v-for="period in availablePeriods" 
                      :key="`thumb-${day.value}-${period}`" 
                      class="border p-0 w-6 text-[9px]"
                    >
                      {{ period }}
                    </th>
                  </template>
                </tr>
              </thead>
              <tbody>
                <tr v-for="classroom in paginatedClassrooms" :key="`thumb-${classroom}`">
                  <td class="border p-2 font-medium bg-gray-50 sticky left-0 z-10">{{ classroom }}</td>
                  <template v-for="day in weekdays" >
                    <td 
                      v-for="period in availablePeriods" 
                      :key="`thumb-${classroom}-${day.value}-${period}`" 
                      class="border p-0 align-middle text-center h-6 w-6"
                      @dragover.prevent
                      @drop="onDrop($event, classroom, day.value, period)"
                    >
                      <div 
                        v-if="hasCourse(classroom, day.value, period)" 
                        class="w-full h-full cursor-pointer relative"
                        :style="getCellStyle(classroom, day.value, period)"
                        @click="viewCellDetails(classroom, day.value, period)"
                      >
                        <div class="absolute bottom-0 right-0 text-[8px] text-white bg-black bg-opacity-50 px-0.5">
                          {{ getCourseWeeks(classroom, day.value, period) }}
                        </div>
                      </div>
                      <div 
                        v-else
                        class="w-full h-full"
                        :class="{'bg-green-100': isValidDropTarget(classroom, day.value, period)}"
                      ></div>
                    </td>
                  </template>
                </tr>
              </tbody>
            </table>
            
            <!-- 表格分页控制 -->
            <div v-if="totalTablePages > 1" class="p-2 flex justify-between items-center border-t">
              <span class="text-sm">
                显示教室 {{ (tablePage - 1) * tablePageSize + 1 }}-{{ Math.min(tablePage * tablePageSize, classrooms.length) }} / {{ classrooms.length }}
              </span>
              <div class="flex gap-2">
                <button 
                  @click="tablePage = 1" 
                  class="px-2 py-1 bg-gray-100 text-sm rounded hover:bg-gray-200 disabled:opacity-50"
                  :disabled="tablePage === 1"
                  title="首页"
                >
                  &laquo;
                </button>
                <button 
                  @click="prevTablePage" 
                  class="px-2 py-1 bg-gray-100 text-sm rounded hover:bg-gray-200 disabled:opacity-50"
                  :disabled="tablePage === 1"
                >
                  &lsaquo;
                </button>
                
                <!-- 页码快速索引 -->
                <div class="flex items-center gap-1 mx-1">
                  <div v-for="(page, index) in tablePageNumbers" :key="`page-${index}-${page}`" class="flex">
                    <button 
                      v-if="page !== '...'"
                      @click="tablePage = page" 
                      class="w-6 h-6 text-center rounded text-xs"
                      :class="page === tablePage ? 'bg-primary text-white' : 'bg-gray-100 hover:bg-gray-200'"
                    >
                      {{ page }}
                    </button>
                    <span v-else class="text-gray-500">...</span>
                  </div>
                </div>
                
                <!-- 页码输入框 -->
                <div class="relative mx-1 hidden sm:block">
                  <input 
                    v-model="tempTablePageInput"
                    @keyup.enter="jumpToTablePage"
                    type="text" 
                    class="w-10 h-6 text-center text-xs border rounded"
                    placeholder="#"
                  />
                </div>
                
                <button 
                  @click="nextTablePage" 
                  class="px-3 py-1 bg-gray-100 text-sm rounded hover:bg-gray-200 disabled:opacity-50"
                  :disabled="tablePage === totalTablePages"
                >
                  &rsaquo;
                </button>
                <button 
                  @click="tablePage = totalTablePages" 
                  class="px-2 py-1 bg-gray-100 text-sm rounded hover:bg-gray-200 disabled:opacity-50"
                  :disabled="tablePage === totalTablePages"
                  title="末页"
                >
                  &raquo;
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 单元格详情对话框 -->
    <div v-if="cellDetails.visible" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <div class="flex justify-between items-start mb-4">
          <h3 class="text-lg font-medium">课程详情</h3>
          <button @click="closeCellDetails" class="text-gray-500 hover:text-gray-700">
            <X class="w-5 h-5" />
          </button>
        </div>
        <div v-if="cellDetails.courses.length > 0" class="space-y-4">
          <div v-for="course in cellDetails.courses" :key="course.scid" class="p-3 border rounded-md">
            <div class="font-medium">{{ course.sctask }}</div>
            <div class="text-sm">{{ course.composition }}</div>
            <div class="text-sm text-gray-600">教室: {{ course.scroom }}</div>
            <div class="text-sm text-gray-600">教师ID: {{ course.scteacherid }}</div>
            <div class="text-sm text-gray-600">学院: {{ course.scteacherdepartment }}</div>
            <div class="text-sm text-gray-600">时间: {{ getWeekdayName(parseInt(course.scday_of_week)) }} 第{{ course.time }}节</div>
            <div class="text-sm text-gray-600">周次: {{ course.scbegin_week }}~{{ course.scend_week }}周</div>
            <div class="mt-2 flex justify-end">
              <button 
                @click="selectCourse(course); closeCellDetails();" 
                class="px-3 py-1 text-sm bg-primary text-white rounded-md hover:bg-primary-dark"
              >
                编辑
              </button>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-4 text-gray-500">
          没有找到课程信息
        </div>
        <div class="mt-4 flex justify-end">
          <button 
            @click="closeCellDetails" 
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
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue';
import { Search, Save, X, ChevronLeft, ChevronDown } from 'lucide-vue-next';
import axios from 'axios';

// 侧边栏状态变量
const sidebarCollapsed = ref(false);
const sidebarWidth = ref(4); // Default width 4/12 - Represents fraction

// 状态变量
const selectedWeek = ref(1);
const courseSearch = ref('');
const filterType = ref('all');
const selectedCourse = ref(null);
const cellDetails = ref({
  visible: false,
  classroom: '',
  day: 0,
  period: 0,
  courses: []
});

// 可用选项
const availableWeeks = ref([...Array(20)].map((_, i) => i + 1)); // 1-20周
const availablePeriods = ref([1, 2, 3, 4, 5, 6, 7, 8]); // 1-8节

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

// 示例教室列表
// const classrooms = [
//   'JXL101',
//   'JXL102',
//   'JXL201',
//   'JXL202',
//   'JXL301',
//   'JXL302',
//   'JXL401',
//   'JXL402',
//   'JXL501',
//   'JXL517'
// ];
const classrooms = ref([]);

// 添加API数据加载状态
const isLoading = ref(false);
const loadError = ref(null);

// 课程数据
const allCourses = ref([]); // 所有课程数据
const courses = ref([]); // 当前过滤后的课程数据
const courseIndexes = ref(new Map()); // 课程索引：教室-日期-节次 -> 课程数组

// 添加课程列表可视化控制变量
const courseListPageSize = 20; // 每页显示的课程数量
const courseListPage = ref(1); // 当前页码

// 分页显示课程
const paginatedCourses = computed(() => {
  const startIndex = (courseListPage.value - 1) * courseListPageSize;
  return courses.value.slice(startIndex, startIndex + courseListPageSize);
});

// 课程总页数
const totalPages = computed(() => {
  return Math.ceil(courses.value.length / courseListPageSize);
});

// 切换到下一页
const nextPage = () => {
  if (courseListPage.value < totalPages.value) {
    courseListPage.value++;
  }
};

// 切换到上一页
const prevPage = () => {
  if (courseListPage.value > 1) {
    courseListPage.value--;
  }
};

// 创建课程索引，用于快速查找
const createCourseIndexes = () => {
  const indexMap = new Map();
  
  courses.value.forEach(course => {
    if (!course.scroom || !course.scday_of_week || !course.time) return;
    
    const classroom = course.scroom;
    const day = parseInt(course.scday_of_week);
    const period = course.time;
    
    // 创建教室-日期-节次 索引
    const key = `${classroom}-${day}-${period}`;
    if (!indexMap.has(key)) {
      indexMap.set(key, []);
    }
    indexMap.get(key).push(course);
    
    // 创建课程ID索引
    indexMap.set(`course-${course.scid}`, course);
  });
  
  courseIndexes.value = indexMap;
};

// 应用筛选条件
const applyFilters = () => {
  let result = [...allCourses.value];
  
  // 按搜索关键词筛选
  if (courseSearch.value) {
    const searchLower = courseSearch.value.toLowerCase();
    result = result.filter(course => {
      // Check against multiple fields, ensuring they exist and can be searched
      const taskMatch = (course.sctask?.toLowerCase() || '').includes(searchLower);
      const compositionMatch = (course.composition?.toLowerCase() || '').includes(searchLower);
      const departmentMatch = (course.scteacherdepartment?.toLowerCase() || '').includes(searchLower);
      const teacherIdMatch = (course.scteacherid?.toString() || '').includes(searchLower);
      
      return taskMatch || compositionMatch || departmentMatch || teacherIdMatch;
    });
  }

  // 按排课状态筛选
  if (filterType.value === 'scheduled') {
    result = result.filter(course => isScheduled(course));
  } else if (filterType.value === 'unscheduled') {
    result = result.filter(course => !isScheduled(course));
  }

  courses.value = result;
  createCourseIndexes(); // 重建索引
};

// 监听筛选条件变化
watch([courseSearch, filterType], () => {
  applyFilters();
});

// 新增：管理展开课程的状态
const expandedCourses = ref(new Set());

// 检查课程是否展开
const isCourseExpanded = (courseId) => {
  return expandedCourses.value.has(courseId);
};

// 切换课程展开/折叠状态
const toggleExpand = (courseId) => {
  if (expandedCourses.value.has(courseId)) {
    expandedCourses.value.delete(courseId);
  } else {
    expandedCourses.value.add(courseId);
  }
};

// 新函数：点击课程项时，切换展开状态并选中课程
const toggleAndSelectCourse = (course) => {
  selectCourse(course); // 保留选中逻辑
  // 可以选择是否在这里也切换展开状态，或者只通过小箭头切换
  // toggleExpand(course.scid); // 如果希望点击整个卡片也切换展开
};

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
    if (slot.start > 0 && slot.start <= 8) {
      beginTime = `08:00:00`;
    }
    if (slot.end > 0 && slot.end <= 8) {
      endTime = `09:40:00`;
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
      allCourses.value = processCourseData(response.data.rows);
      console.log('从API加载了', allCourses.value.length, '条课程数据');
      
      // 从加载的数据中提取教室列表
      const uniqueClassrooms = [...new Set(allCourses.value.map(course => course.scroom).filter(Boolean))];
      classrooms.value = uniqueClassrooms.sort();
      
      // 应用筛选条件
      applyFilters();

    } else {
      throw new Error(`API返回错误: ${response.data.code || response.status}`);
    }
  } catch (error) {
    console.error('获取课程数据失败:', error);
    console.log('使用测试数据替代');
    
    // 使用测试数据
    allCourses.value = processCourseData(mockCourses);
    // 从模拟数据中提取教室列表
    const uniqueMockClassrooms = [...new Set(allCourses.value.map(course => course.scroom).filter(Boolean))];
    classrooms.value = uniqueMockClassrooms.sort();
    
    // 应用筛选条件
    applyFilters();

  } finally {
    isLoading.value = false;
  }
};

// 使用引用代替计算属性，提高性能
const filteredCourses = computed(() => courses.value);

// 检查课程是否已排课
const isScheduled = (course) => {
  return course.scday_of_week && course.scroom && course.time > 0;
};

// 获取星期几的名称
const getWeekdayName = (day) => {
  const dayObj = weekdays.find(d => d.value === day);
  return dayObj ? dayObj.label : '';
};

// 选择课程
const selectCourse = (course) => {
  // 尝试使用浅拷贝（直接赋值）来解决高亮问题
  selectedCourse.value = course; 
  
  // --- Previous deep copy logic ---
  // if (window.structuredClone) {
  //   selectedCourse.value = structuredClone(course);
  // } else {
  //   selectedCourse.value = JSON.parse(JSON.stringify(course));
  // }
  
  // // 确保数值类型正确 (浅拷贝时可能不需要，因为是同一对象)
  // if (selectedCourse.value) {
  //   selectedCourse.value.scbegin_week = parseInt(selectedCourse.value.scbegin_week);
  //   selectedCourse.value.scend_week = parseInt(selectedCourse.value.scend_week);
  //   if (selectedCourse.value.time) {
  //     selectedCourse.value.time = parseInt(selectedCourse.value.time);
  //   }
  // }
};

// 应用排课
const applySchedule = () => {
  if (!selectedCourse.value) return;
  
  // 验证必填字段
  if (!selectedCourse.value.scroom || !selectedCourse.value.scday_of_week || !selectedCourse.value.time) {
    alert('请填写完整的排课信息');
    return;
  }
  
  // 验证周次
  if (selectedCourse.value.scbegin_week > selectedCourse.value.scend_week) {
    alert('开始周不能大于结束周');
    return;
  }
  
  // 检查冲突
  const conflicts = checkConflicts(
    selectedCourse.value.scroom,
    parseInt(selectedCourse.value.scday_of_week),
    selectedCourse.value.time,
    selectedCourse.value.scid
  );
  
  if (conflicts.length > 0) {
    const confirmMsg = `检测到以下冲突:\n${conflicts.map(c => `- ${c.sctask} (${c.composition})`).join('\n')}\n\n是否继续排课?`;
    if (!confirm(confirmMsg)) {
      return;
    }
  }
  
  // 更新课程数据 - 在allCourses和courses中同时更新
  const indexInAll = allCourses.value.findIndex(c => c.scid === selectedCourse.value.scid);
  const indexInFiltered = courses.value.findIndex(c => c.scid === selectedCourse.value.scid);
  
  if (indexInAll !== -1) {
    allCourses.value[indexInAll] = { ...selectedCourse.value };
  }
  
  if (indexInFiltered !== -1) {
    courses.value[indexInFiltered] = { ...selectedCourse.value };
  }
  
  // 重建索引
  createCourseIndexes();
  
  alert('排课成功');
};

// 取消排课
const unschedule = (course) => {
  if (!confirm(`确定要取消 ${course.sctask} 的排课吗?`)) return;
  
  // 在allCourses和courses中同时更新
  const indexInAll = allCourses.value.findIndex(c => c.scid === course.scid);
  const indexInFiltered = courses.value.findIndex(c => c.scid === course.scid);
  
  const updatedCourse = {
    ...course,
    scday_of_week: "",
    scroom: "",
    time: 0
  };
  
  if (indexInAll !== -1) {
    allCourses.value[indexInAll] = updatedCourse;
  }
  
  if (indexInFiltered !== -1) {
    courses.value[indexInFiltered] = updatedCourse;
  }
  
  // 重建索引
  createCourseIndexes();
  
  // 更新选中的课程
  if (selectedCourse.value && selectedCourse.value.scid === course.scid) {
    selectedCourse.value = { ...updatedCourse };
  }
};

// 检查是否有课程
const hasCourse = (classroom, day, period) => {
  return getCoursesByCell(classroom, day, period).length > 0;
};

// 获取单元格中的课程 - 优化使用索引
const getCoursesByCell = (classroom, day, period) => {
  const key = `${classroom}-${day}-${period}`;
  
  // 首先从索引中查找
  if (courseIndexes.value.has(key)) {
    // 在所有缓存的课程中找出符合当前周次的课程
    return courseIndexes.value.get(key).filter(course => 
      course.scbegin_week <= selectedWeek.value &&
      course.scend_week >= selectedWeek.value
    );
  }
  
  // 如果索引中没有，返回空数组
  return [];
};

// 获取单元格样式
const getCellStyle = (classroom, day, period) => {
  const cellCourses = getCoursesByCell(classroom, day, period);
  if (cellCourses.length === 0) return {};
  
  // 如果是高亮的课程，返回黄色
  if (isHighlighted(classroom, day, period)) {
    return { backgroundColor: '#FBBF24' };
  }
  
  // 所有未选中的课程使用统一颜色
  return { backgroundColor: '#4f46e5' };
};

// 检查是否是高亮的单元格 - 优化使用索引
const isHighlighted = (classroom, day, period) => {
  if (!selectedCourse.value || !selectedCourse.value.scid) return false;

  // 仅当选中的课程本身有排课信息时，才进行高亮判断
  if (!selectedCourse.value.scroom || !selectedCourse.value.scday_of_week || !selectedCourse.value.time) {
    return false; // 如果选中的课程未排课，则不高亮任何单元格
  }

  // 直接比较单元格坐标和选中课程的排课信息
  return (
    selectedCourse.value.scroom === classroom &&
    parseInt(selectedCourse.value.scday_of_week) === day &&
    selectedCourse.value.time === period
  );
  
  // --- Previous logic using index (removed for clarity in highlighting the specific selected course) ---
  // const key = `${classroom}-${day}-${period}`;
  // if (!courseIndexes.value.has(key)) return false;
  
  // return courseIndexes.value.get(key).some(course => 
  //   course.scid === selectedCourse.value.scid
  // );
};

// 获取课程周次显示
const getCourseWeeks = (classroom, day, period) => {
  const cellCourses = getCoursesByCell(classroom, day, period);
  if (cellCourses.length === 0) return '';
  
  const course = cellCourses[0];
  return `${course.scbegin_week}~${course.scend_week}`;
};

// 查看单元格详情
const viewCellDetails = (classroom, day, period) => {
  // 使用索引获取课程数据 - 不再筛选周次，显示该单元格所有课程
  const key = `${classroom}-${day}-${period}`;
  const cellCourses = courseIndexes.value.has(key) ? courseIndexes.value.get(key) : [];
  
  cellDetails.value = {
    visible: true,
    classroom,
    day,
    period,
    courses: cellCourses
  };
};

// 关闭单元格详情
const closeCellDetails = () => {
  cellDetails.value.visible = false;
};

// 拖拽开始
const onDragStart = (event, course) => {
  event.dataTransfer.setData('courseId', course.scid);
  selectCourse(course);
};

// 拖拽放置
const onDrop = (event, classroom, day, period) => {
  const courseId = parseInt(event.dataTransfer.getData('courseId'));
  const course = courses.value.find(c => c.scid === courseId);
  
  if (!course) return;
  
  // 更新课程信息
  const updatedCourse = {
    ...course,
    scroom: classroom,
    scday_of_week: day.toString(),
    time: period
  };
  
  // 检查冲突
  const conflicts = checkConflicts(classroom, day, period, courseId);
  
  if (conflicts.length > 0) {
    const confirmMsg = `检测到以下冲突:\n${conflicts.map(c => `- ${c.sctask} (${c.composition})`).join('\n')}\n\n是否继续排课?`;
    if (!confirm(confirmMsg)) {
      return;
    }
  }
  
  // 更新课程数据 - 在allCourses和courses中同时更新
  const indexInAll = allCourses.value.findIndex(c => c.scid === courseId);
  const indexInFiltered = courses.value.findIndex(c => c.scid === courseId);
  
  if (indexInAll !== -1) {
    allCourses.value[indexInAll] = updatedCourse;
  }
  
  if (indexInFiltered !== -1) {
    courses.value[indexInFiltered] = updatedCourse;
  }
  
  // 重建索引
  createCourseIndexes();
  
  // 更新选中的课程
  if (selectedCourse.value && selectedCourse.value.scid === courseId) {
    selectedCourse.value = { ...updatedCourse };
  }
};

// 检查冲突 - 优化使用索引
const checkConflicts = (classroom, day, period, excludeCourseId) => {
  // 使用索引快速查找可能冲突的课程
  const key = `${classroom}-${day}-${period}`;
  if (!courseIndexes.value.has(key)) return [];
  
  // 从索引中获取课程，并检查周次重叠
  return courseIndexes.value.get(key).filter(course => 
    course.scid !== excludeCourseId &&
    // 检查周次是否有重叠
    ((course.scbegin_week <= selectedCourse.value.scbegin_week && course.scend_week >= selectedCourse.value.scbegin_week) ||
     (course.scbegin_week <= selectedCourse.value.scend_week && course.scend_week >= selectedCourse.value.scend_week) ||
     (course.scbegin_week >= selectedCourse.value.scbegin_week && course.scend_week <= selectedCourse.value.scend_week))
  );
};

// 检查是否是有效的放置目标
const isValidDropTarget = (classroom, day, period) => {
  if (!selectedCourse.value) return false;
  
  // 这里可以添加更多的限制条件
  // 例如：特定课程只能放在特定类型的教室
  // 或者：某些时间段不允许排课
  
  // 示例：周末不允许排课
  if (day > 5) return false;
  
  return true;
};

// 保存排课
const saveSchedule = async () => {
  try {
    // 找出所有修改过的课程数据
    const scheduledCourses = courses.value.filter(isScheduled);
    
    if (scheduledCourses.length === 0) {
      alert('没有课程被安排，无需保存');
      return;
    }
    
    // 显示保存中提示
    isLoading.value = true;
    
    // 先提取需要的字段并转换格式，然后批量提交
    const updatePromises = scheduledCourses.map(course => {
      // 构建更新数据
      const updateData = {
        scid: course.scid,
        scroom: course.scroom,
        scday_of_week: course.scday_of_week,
        scbegin_week: course.scbegin_week,
        scend_week: course.scend_week
      };
      
      // 处理节次数据
      if (course.time && course.slot_end) {
        if (course.time === course.slot_end) {
          updateData.scslot = `${course.time}`;
        } else {
          updateData.scslot = `${course.time}-${course.slot_end}`;
        }
      } else if (course.time) {
        updateData.scslot = `${course.time}`;
      }
      
      // 调用API
      return axios.post('http://localhost:8080/manual/change', updateData);
    });
    
    // 等待所有请求完成
    const results = await Promise.allSettled(updatePromises);
    
    // 统计成功和失败数量
    const successful = results.filter(r => r.status === 'fulfilled' && r.value?.data?.code === 200).length;
    const failed = results.filter(r => r.status === 'rejected' || r.value?.data?.code !== 200).length;
    
    // 根据结果显示不同的提示
    if (failed === 0) {
      alert(`排课保存成功，共更新了 ${successful} 门课程。`);
    } else {
      alert(`排课部分保存成功，成功 ${successful} 门课程，失败 ${failed} 门课程。`);
    }
  } catch (error) {
    console.error('保存排课失败:', error);
    alert(`保存排课失败: ${error.message || '未知错误'}`);
  } finally {
    isLoading.value = false;
  }
};

// 切换侧边栏
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value;
};

// 修改：计算侧边栏样式
const sidebarStyle = computed(() => {
  if (sidebarCollapsed.value) {
    return {
      width: '2.5rem', // w-10
      minWidth: '2.5rem',
      flexBasis: '2.5rem',
      flexGrow: 0,
      flexShrink: 0,
      overflow: 'hidden',
    };
  } else {
    const percentage = (sidebarWidth.value / 12) * 100;
    return {
      flexBasis: `${percentage}%`,
      width: `${percentage}%`, // Keep for clarity/fallback
      minWidth: '200px', // Use a FIXED minimum width
      flexGrow: 0,
      flexShrink: 0,
      overflow: 'hidden',
    };
  }
});

// 侧边栏大小调整逻辑
let resizing = false;
let startX = 0;
let initialWidthFraction = 0; // Store initial width as fraction (2-6)

const startResize = (e) => {
  e.preventDefault();
  e.stopPropagation();
  resizing = true;
  startX = e.clientX;
  initialWidthFraction = sidebarWidth.value; // Store the initial fraction (2-6)
  window.addEventListener('mousemove', handleResize);
  window.addEventListener('mouseup', stopResize);
  document.body.style.cursor = 'col-resize';
  document.body.classList.add('select-none');
};

const handleResize = (e) => {
  if (!resizing) return;
  const container = document.querySelector('.flex.flex-1.gap-4');
  if (!container) {
    console.error("Resize container not found!");
    return;
  }
  const containerWidth = container.clientWidth;
  if (containerWidth <= 0) return;

  const deltaX = e.clientX - startX;
  const widthChangeFraction = (deltaX / containerWidth) * 12;
  
  // Calculate the new width fraction
  let newWidthFraction = initialWidthFraction + widthChangeFraction;

  // Apply limits (e.g., 2/12 to 6/12)
  newWidthFraction = Math.max(2, Math.min(6, newWidthFraction));
  
  // ONLY update the sidebarWidth ref (the fraction)
  sidebarWidth.value = newWidthFraction;
  
  // REMOVED the logic that updated sidebarMinWidth.value here
};

const stopResize = () => {
  if (!resizing) return;
  resizing = false;
  window.removeEventListener('mousemove', handleResize);
  window.removeEventListener('mouseup', stopResize);
  document.body.style.cursor = '';
  document.body.classList.remove('select-none');
};

onBeforeUnmount(() => {
  window.removeEventListener('mousemove', handleResize);
  window.removeEventListener('mouseup', stopResize);
  document.body.style.cursor = '';
  document.body.classList.remove('select-none');
});

// 生命周期钩子
onMounted(() => {
  // 从API获取数据
  fetchCoursesFromAPI();
  
  console.log('手动排课组件已挂载');
});

// 监听周次选择器变化
watch(selectedWeek, () => {
  // 不需要重新加载数据，只需要更新视图
  // 这样在切换周次时不会导致浏览器卡顿
});

// 表格分页变量
const tablePageSize = 10; // 每页显示的教室数量
const tablePage = ref(1); // 当前页码

// 分页显示教室
const paginatedClassrooms = computed(() => {
  const startIndex = (tablePage.value - 1) * tablePageSize;
  return classrooms.value.slice(startIndex, startIndex + tablePageSize);
});

// 教室总页数
const totalTablePages = computed(() => {
  return Math.ceil(classrooms.value.length / tablePageSize);
});

// 切换表格页面
const nextTablePage = () => {
  if (tablePage.value < totalTablePages.value) {
    tablePage.value++;
  }
};

const prevTablePage = () => {
  if (tablePage.value > 1) {
    tablePage.value--;
  }
};

// 添加页码导航相关变量
const tempCoursePageInput = ref('');
const tempTablePageInput = ref('');

// 跳转到指定课程页
const jumpToCoursePage = () => {
  const pageNum = parseInt(tempCoursePageInput.value);
  if (pageNum && pageNum > 0 && pageNum <= totalPages.value) {
    courseListPage.value = pageNum;
  }
  tempCoursePageInput.value = '';
};

// 跳转到指定表格页
const jumpToTablePage = () => {
  const pageNum = parseInt(tempTablePageInput.value);
  if (pageNum && pageNum > 0 && pageNum <= totalTablePages.value) {
    tablePage.value = pageNum;
  }
  tempTablePageInput.value = '';
};

// 生成课程列表分页页码
const pageNumbers = computed(() => {
  const total = totalPages.value;
  const current = courseListPage.value;
  
  // 总页数小于10，显示所有页码
  if (total <= 10) {
    return Array.from({ length: total }, (_, i) => i + 1);
  }
  
  // 总页数大于10，显示首页、末页和当前页附近的页码
  const pages = [];
  
  // 当前页附近的页码
  const nearbyPages = [];
  for (let i = Math.max(2, current - 2); i <= Math.min(total - 1, current + 2); i++) {
    nearbyPages.push(i);
  }
  
  // 添加首页
  pages.push(1);
  
  // 如果首页和当前页区域之间有间隔，添加省略号
  if (nearbyPages[0] > 2) {
    pages.push('...');
  }
  
  // 添加当前页附近的页码
  pages.push(...nearbyPages);
  
  // 如果当前页区域和末页之间有间隔，添加省略号
  if (nearbyPages[nearbyPages.length - 1] < total - 1) {
    pages.push('...');
  }
  
  // 添加末页
  pages.push(total);
  
  return pages;
});

// 生成表格分页页码
const tablePageNumbers = computed(() => {
  const total = totalTablePages.value;
  const current = tablePage.value;
  
  // 总页数小于10，显示所有页码
  if (total <= 10) {
    return Array.from({ length: total }, (_, i) => i + 1);
  }
  
  // 总页数大于10，显示首页、末页和当前页附近的页码
  const pages = [];
  
  // 当前页附近的页码
  const nearbyPages = [];
  for (let i = Math.max(2, current - 2); i <= Math.min(total - 1, current + 2); i++) {
    nearbyPages.push(i);
  }
  
  // 添加首页
  pages.push(1);
  
  // 如果首页和当前页区域之间有间隔，添加省略号
  if (nearbyPages[0] > 2) {
    pages.push('...');
  }
  
  // 添加当前页附近的页码
  pages.push(...nearbyPages);
  
  // 如果当前页区域和末页之间有间隔，添加省略号
  if (nearbyPages[nearbyPages.length - 1] < total - 1) {
    pages.push('...');
  }
  
  // 添加末页
  pages.push(total);
  
  return pages;
});
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

.border-primary {
  border-color: #4f46e5;
}

/* 添加过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.sidebar-content-enter-active,
.sidebar-content-leave-active {
  transition: opacity 0.3s, transform 0.3s;
  transform-origin: left;
}

.sidebar-content-enter-from,
.sidebar-content-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

/* 显著增强拖拽条的可见性和交互体验 */
.w-1.bg-gray-200.hover\:bg-primary.hover\:w-1\.5.cursor-col-resize {
  width: 4px !important;
  background-color: #e5e7eb;
  cursor: col-resize;
  transition: background-color 0.2s;
  position: relative;
  z-index: 10;
  margin: 0 -2px;
}

.w-1.bg-gray-200.hover\:bg-primary.hover\:w-1\.5.cursor-col-resize:hover,
.w-1.bg-gray-200.hover\:bg-primary.hover\:w-1\.5.cursor-col-resize:active {
  background-color: #4f46e5 !important;
}

.w-1.bg-gray-200.hover\:bg-primary.hover\:w-1\.5.cursor-col-resize::before {
  content: "";
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  cursor: col-resize;
}

.w-1.bg-gray-200.hover\:bg-primary.hover\:w-1\.5.cursor-col-resize::after {
  content: "⋮";
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #6b7280;
  font-size: 16px;
  pointer-events: none;
}

.w-1.bg-gray-200.hover\:bg-primary.hover\:w-1\.5.cursor-col-resize:hover::after {
  color: white;
}

/* 简化侧栏列表样式 */
.border-b.border-gray-200 {
  transition: background-color 0.15s;
}

.border-b.border-gray-200:last-child {
  border-bottom: none;
}

/* 侧栏列表项过渡 */
.border.rounded-md {
  transition: border-color 0.2s, background-color 0.2s, box-shadow 0.2s;
}

/* Ensure flex items behave correctly */
.flex-shrink-0 {
  flex-shrink: 0;
}

.flex-1 {
  flex: 1 1 0%; /* Common definition for flex-1 */
}

/* Optional: Add transition to flex-basis for smoother resize */
.transition-all {
  /* Check if transition property includes flex-basis or width */
  transition-property: all;
  /* If not, add it: */
  /* transition-property: width, min-width, flex-basis, background-color, border-color, color, fill, stroke, opacity, box-shadow, transform, filter, backdrop-filter; */
}
</style>

