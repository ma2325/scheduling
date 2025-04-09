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
      <!-- 左侧课程导航栏 -->
      <div 
        :class="[sidebarCollapsed ? 'w-10' : `w-${sidebarWidth}/12`]" 
        class="bg-white rounded-lg shadow overflow-hidden flex flex-col transition-all duration-300 ease-in-out"
        :style="sidebarCollapsed ? '' : `min-width: ${sidebarMinWidth}px`"
      >
        <!-- 侧边栏标题栏 -->
        <div class="p-2 border-b flex justify-between items-center">
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
        
        <!-- 侧边栏内容 -->
        <transition 
          name="sidebar-content" 
          mode="out-in"
        >
          <div v-if="!sidebarCollapsed" class="flex flex-col flex-1 overflow-hidden">
            <div class="p-2 border-b">
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
            <div class="flex-1 overflow-y-auto p-2">
              <div 
                v-for="course in filteredCourses" 
                :key="course.scid"
                class="p-3 mb-2 rounded-md cursor-pointer transition-all duration-200"
                :class="selectedCourse && selectedCourse.scid === course.scid ? 'bg-primary-light border-l-4 border-primary' : 'bg-gray-50 hover:bg-gray-100 border-l-4 border-transparent'"
                @click="selectCourse(course)"
                draggable="true"
                @dragstart="onDragStart($event, course)"
              >
                <div class="font-medium">{{ course.sctask }}</div>
                <div class="text-sm text-gray-600">{{ course.composition }}</div>
                <div class="text-sm text-gray-600">{{ course.scteacherdepartment }}</div>
                <div v-if="isScheduled(course)" class="mt-1 text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded-full inline-block">
                  {{ getWeekdayName(parseInt(course.scday_of_week)) }} 第{{ course.time }}节<span v-if="course.slot_end && course.slot_end !== course.time">-{{ course.slot_end }}节</span> {{ course.scroom }}
                </div>
                <div v-if="isScheduled(course)" class="mt-1 text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full inline-block">
                  {{ course.scbegin_week }}~{{ course.scend_week }}周
                </div>
              </div>
              <div v-if="filteredCourses.length === 0" class="p-4 text-center text-gray-500">
                没有找到匹配的课程
              </div>
            </div>
          </div>
        </transition>
      </div>

      <!-- 调整大小的拖动条 -->
      <transition name="fade">
        <div 
          v-if="!sidebarCollapsed"
          class="w-1 bg-gray-200 hover:bg-primary hover:w-1.5 cursor-col-resize transition-all"
          @mousedown="startResize"
        ></div>
      </transition>

      <!-- 右侧排课区域 -->
      <div class="flex-1 flex flex-col gap-3 overflow-hidden">
        <!-- 课程详情卡片 (只在选中课程时显示) -->
        <div v-if="selectedCourse" class="bg-white rounded-lg shadow p-3">
          <div class="flex justify-between items-start">
            <div class="flex-1 grid grid-cols-3 gap-3">
              <div class="col-span-2">
                <h3 class="text-base font-medium">{{ selectedCourse.sctask }}</h3>
                <div class="text-sm text-gray-600">{{ selectedCourse.composition }}</div>
                <div class="text-xs text-gray-600">教师ID: {{ selectedCourse.scteacherid }} | 学院: {{ selectedCourse.scteacherdepartment }}</div>
              </div>
              
              <div class="flex gap-2 justify-end">
                <button 
                  v-if="isScheduled(selectedCourse)"
                  @click="unschedule(selectedCourse)" 
                  class="px-3 py-1 text-sm bg-red-50 text-red-600 rounded-md hover:bg-red-100"
                >
                  取消排课
                </button>
              </div>
            </div>
          </div>
          
          <!-- 排课表单 -->
          <div class="mt-3 grid grid-cols-6 gap-3">
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
                      class="border p-1 w-8"
                    >
                      {{ period }}
                    </th>
                  </template>
                </tr>
              </thead>
              <tbody>
                <tr v-for="classroom in classrooms" :key="`thumb-${classroom}`">
                  <td class="border p-2 font-medium bg-gray-50 sticky left-0 z-10">{{ classroom }}</td>
                  <template v-for="day in weekdays" >
                    <td 
                      v-for="period in availablePeriods" 
                      :key="`thumb-${classroom}-${day.value}-${period}`" 
                      class="border p-0 align-middle text-center h-8 w-8"
                      @dragover.prevent
                      @drop="onDrop($event, classroom, day.value, period)"
                    >
                      <div 
                        v-if="hasCourse(classroom, day.value, period)" 
                        class="w-full h-full cursor-pointer relative"
                        :class="{'bg-yellow-400': isHighlighted(classroom, day.value, period)}"
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
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { Search, Save, X, ChevronLeft, ChevronRight } from 'lucide-vue-next';
import axios from 'axios';

// 侧边栏状态变量
const sidebarCollapsed = ref(false);
const sidebarWidth = ref(4); // 默认宽度为4/12
const sidebarMinWidth = ref(300); // 最小宽度

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
const classrooms = [
  'JXL101',
  'JXL102',
  'JXL201',
  'JXL202',
  'JXL301',
  'JXL302',
  'JXL401',
  'JXL402',
  'JXL501',
  'JXL517'
];

// 添加API数据加载状态
const isLoading = ref(false);
const loadError = ref(null);

// 课程数据 - 重新添加声明
const courses = ref([]);

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
      courses.value = processCourseData(response.data.rows);
      console.log('从API加载了', courses.value.length, '条课程数据');
    } else {
      throw new Error(`API返回错误: ${response.data.code || response.status}`);
    }
  } catch (error) {
    console.error('获取课程数据失败:', error);
    console.log('使用测试数据替代');
    
    // 使用测试数据
    courses.value = processCourseData(mockCourses);
  } finally {
    isLoading.value = false;
  }
};

// 筛选课程
const filteredCourses = computed(() => {
  let result = [...courses.value];
  
  // 按搜索关键词筛选
  if (courseSearch.value) {
    const searchLower = courseSearch.value.toLowerCase();
    result = result.filter(course => 
      course.sctask.toLowerCase().includes(searchLower) ||
      course.composition.toLowerCase().includes(searchLower) ||
      course.scteacherdepartment.toLowerCase().includes(searchLower)
    );
  }
  
  // 按排课状态筛选
  if (filterType.value === 'scheduled') {
    result = result.filter(course => isScheduled(course));
  } else if (filterType.value === 'unscheduled') {
    result = result.filter(course => !isScheduled(course));
  }
  
  return result;
});

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
  selectedCourse.value = { ...course };
  
  // 确保数值类型正确
  selectedCourse.value.scbegin_week = parseInt(selectedCourse.value.scbegin_week);
  selectedCourse.value.scend_week = parseInt(selectedCourse.value.scend_week);
  selectedCourse.value.time = parseInt(selectedCourse.value.time);
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
  
  // 更新课程数据
  const index = courses.value.findIndex(c => c.scid === selectedCourse.value.scid);
  if (index !== -1) {
    courses.value[index] = { ...selectedCourse.value };
  }
  
  alert('排课成功');
};

// 取消排课
const unschedule = (course) => {
  if (!confirm(`确定要取消 ${course.sctask} 的排课吗?`)) return;
  
  const index = courses.value.findIndex(c => c.scid === course.scid);
  if (index !== -1) {
    courses.value[index] = {
      ...courses.value[index],
      scday_of_week: "",
      scroom: "",
      time: 0
    };
    
    // 更新选中的课程
    if (selectedCourse.value && selectedCourse.value.scid === course.scid) {
      selectedCourse.value = { ...courses.value[index] };
    }
  }
};

// 检查是否有课程
const hasCourse = (classroom, day, period) => {
  return getCoursesByCell(classroom, day, period).length > 0;
};

// 获取单元格中的课程
const getCoursesByCell = (classroom, day, period) => {
  return courses.value.filter(course => 
    course.scroom === classroom && 
    parseInt(course.scday_of_week) === day &&
    course.time === period &&
    course.scbegin_week <= selectedWeek.value &&
    course.scend_week >= selectedWeek.value
  );
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

// 检查是否是高亮的单元格
const isHighlighted = (classroom, day, period) => {
  if (!selectedCourse.value) return false;
  
  return courses.value.some(course => 
    course.scid === selectedCourse.value.scid &&
    course.scroom === classroom && 
    parseInt(course.scday_of_week) === day &&
    course.time === period
  );
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
  // 获取当前单元格中的所有课程（不限于当前周）
  const cellCourses = courses.value.filter(course => 
    course.scroom === classroom && 
    parseInt(course.scday_of_week) === day &&
    course.time === period
  );
  
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
  
  // 更新课程数据
  const index = courses.value.findIndex(c => c.scid === courseId);
  if (index !== -1) {
    courses.value[index] = updatedCourse;
    
    // 更新选中的课程
    if (selectedCourse.value && selectedCourse.value.scid === courseId) {
      selectedCourse.value = { ...updatedCourse };
    }
  }
};

// 检查冲突
const checkConflicts = (classroom, day, period, excludeCourseId) => {
  // 查找在同一教室、同一时间有课的其他课程
  return courses.value.filter(course => 
    course.scid !== excludeCourseId &&
    course.scroom === classroom && 
    parseInt(course.scday_of_week) === day &&
    course.time === period &&
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
const saveSchedule = () => {
  // 这里可以添加保存到后端的逻辑
  alert('排课已保存');
};

// 切换侧边栏
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value;
};

// 侧边栏大小调整
let isResizing = false;

const startResize = (e) => {
  isResizing = true;
  document.addEventListener('mousemove', resize);
  document.addEventListener('mouseup', stopResize);
};

const resize = (e) => {
  if (!isResizing) return;
  
  // 计算宽度百分比
  const containerWidth = document.querySelector('.flex.flex-1.gap-4').offsetWidth;
  let newWidth = e.clientX / containerWidth * 12;
  
  // 限制最小和最大宽度
  newWidth = Math.max(2, Math.min(6, newWidth));
  
  sidebarWidth.value = newWidth;
};

const stopResize = () => {
  isResizing = false;
  document.removeEventListener('mousemove', resize);
  document.removeEventListener('mouseup', stopResize);
};

// 清理事件监听器
onBeforeUnmount(() => {
  document.removeEventListener('mousemove', resize);
  document.removeEventListener('mouseup', stopResize);
});

// 生命周期钩子
onMounted(() => {
  // 从API获取数据
  fetchCoursesFromAPI();
  
  console.log('手动排课组件已挂载');
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
</style>

