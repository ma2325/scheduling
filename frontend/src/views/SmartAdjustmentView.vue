<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h2 class="text-xl font-bold">智能调课</h2>
      <div class="flex space-x-2">
        <button @click="generateSuggestions" class="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary-dark">
          生成调课建议
        </button>
      </div>
    </div>

    <!-- 调课条件设置 -->
    <div class="bg-white rounded-lg shadow p-6">
      <h3 class="text-lg font-medium mb-4">调课条件</h3>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">优化目标</label>
          <select v-model="adjustmentSettings.optimizationGoal" class="w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50">
            <option value="teacherLoad">平衡教师课时负担</option>
            <option value="classroomUtilization">提高教室利用率</option>
            <option value="timeDistribution">优化时间分布</option>
            <option value="studentExperience">改善学生体验</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">调整范围</label>
          <select v-model="adjustmentSettings.adjustmentScope" class="w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50">
            <option value="all">所有课程</option>
            <option value="department">按院系</option>
            <option value="teacher">按教师</option>
            <option value="courseType">按课程类型</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">约束条件</label>
          <div class="space-y-2">
            <div class="flex items-center">
              <input type="checkbox" v-model="adjustmentSettings.constraints.keepTeacher" id="keepTeacher" class="rounded text-primary focus:ring-primary" />
              <label for="keepTeacher" class="ml-2 text-sm text-gray-700">保持原教师不变</label>
            </div>
            <div class="flex items-center">
              <input type="checkbox" v-model="adjustmentSettings.constraints.keepTimeSlot" id="keepTimeSlot" class="rounded text-primary focus:ring-primary" />
              <label for="keepTimeSlot" class="ml-2 text-sm text-gray-700">尽量保持原时间段</label>
            </div>
            <div class="flex items-center">
              <input type="checkbox" v-model="adjustmentSettings.constraints.avoidConflicts" id="avoidConflicts" class="rounded text-primary focus:ring-primary" />
              <label for="avoidConflicts" class="ml-2 text-sm text-gray-700">避免师生冲突</label>
            </div>
          </div>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">调整力度</label>
          <input type="range" v-model="adjustmentSettings.adjustmentIntensity" min="1" max="10" class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer" />
          <div class="flex justify-between text-xs text-gray-500">
            <span>轻微调整</span>
            <span>中等调整</span>
            <span>大幅调整</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 调课建议列表 -->
    <div v-if="suggestions.length > 0" class="bg-white rounded-lg shadow p-6">
      <h3 class="text-lg font-medium mb-4">调课建议</h3>
      
      <div class="space-y-4">
        <div v-for="(suggestion, index) in suggestions" :key="index" 
             class="border rounded-lg p-4 hover:bg-gray-50">
          <div class="flex justify-between items-start">
            <div>
              <h4 class="font-medium">建议 #{{ index + 1 }}: {{ suggestion.title }}</h4>
              <p class="text-sm text-gray-600 mt-1">{{ suggestion.description }}</p>
              
              <div class="mt-3 grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
                <div>
                  <span class="font-medium">原课程:</span> {{ suggestion.originalCourse.name }}
                </div>
                <div>
                  <span class="font-medium">调整后:</span> {{ suggestion.newCourse.name }}
                </div>
                <div>
                  <span class="font-medium">原时间:</span> 周{{ getWeekdayName(suggestion.originalCourse.weekday) }} {{ suggestion.originalCourse.timeSlot }}
                </div>
                <div>
                  <span class="font-medium">新时间:</span> 周{{ getWeekdayName(suggestion.newCourse.weekday) }} {{ suggestion.newCourse.timeSlot }}
                </div>
                <div>
                  <span class="font-medium">原教室:</span> {{ suggestion.originalCourse.classroom }}
                </div>
                <div>
                  <span class="font-medium">新教室:</span> {{ suggestion.newCourse.classroom }}
                </div>
              </div>
              
              <div class="mt-3">
                <span class="text-sm font-medium">优化效果:</span>
                <div class="flex items-center mt-1">
                  <div class="w-full bg-gray-200 rounded-full h-2.5">
                    <div class="bg-primary h-2.5 rounded-full" :style="{ width: suggestion.improvementPercentage + '%' }"></div>
                  </div>
                  <span class="ml-2 text-sm text-gray-600">{{ suggestion.improvementPercentage }}%</span>
                </div>
              </div>
            </div>
            
            <div class="flex space-x-2">
              <button @click="applySuggestion(suggestion)" class="px-3 py-1 bg-primary text-white text-sm rounded-md hover:bg-primary-dark">
                应用
              </button>
              <button @click="ignoreSuggestion(index)" class="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-md hover:bg-gray-200">
                忽略
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 无建议提示 -->
    <div v-else-if="showNoSuggestions" class="bg-white rounded-lg shadow p-6 text-center">
      <div class="text-gray-500 my-8">
        <div class="mb-4">
          <svg class="w-16 h-16 mx-auto text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        </div>
        <p class="text-lg">当前没有调课建议</p>
        <p class="text-sm mt-2">您可以调整条件后重新生成建议</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';

// 调课设置
const adjustmentSettings = reactive({
  optimizationGoal: 'teacherLoad',
  adjustmentScope: 'all',
  constraints: {
    keepTeacher: true,
    keepTimeSlot: false,
    avoidConflicts: true
  },
  adjustmentIntensity: 5
});

// 调课建议
const suggestions = ref([]);
const showNoSuggestions = ref(false);

// 生成调课建议
const generateSuggestions = () => {
  // 这里应该调用API获取调课建议
  // 模拟API调用
  setTimeout(() => {
    suggestions.value = [
      {
        title: '交换两门课程时间',
        description: '建议交换高等数学和大学物理的上课时间，以平衡教师工作负担并提高教室利用率。',
        originalCourse: {
          name: '高等数学',
          weekday: 1,
          timeSlot: '08:00-09:40',
          classroom: '教学楼A-101'
        },
        newCourse: {
          name: '高等数学',
          weekday: 2,
          timeSlot: '10:00-11:40',
          classroom: '教学楼B-202'
        },
        improvementPercentage: 85
      },
      {
        title: '更换教室',
        description: '建议将程序设计课程从实验楼C-303调整到教学楼B-201，以便更好地利用教室资源。',
        originalCourse: {
          name: '程序设计',
          weekday: 3,
          timeSlot: '14:00-15:40',
          classroom: '实验楼C-303'
        },
        newCourse: {
          name: '程序设计',
          weekday: 3,
          timeSlot: '14:00-15:40',
          classroom: '教学楼B-201'
        },
        improvementPercentage: 65
      },
      {
        title: '调整上课时间',
        description: '建议将数据结构课程从周四下午调整到周五上午，以优化学生的学习体验。',
        originalCourse: {
          name: '数据结构',
          weekday: 4,
          timeSlot: '16:00-17:40',
          classroom: '教学楼A-201'
        },
        newCourse: {
          name: '数据结构',
          weekday: 5,
          timeSlot: '10:00-11:40',
          classroom: '教学楼A-201'
        },
        improvementPercentage: 75
      }
    ];
    
    showNoSuggestions.value = suggestions.value.length === 0;
  }, 1000);
};

// 应用调课建议
const applySuggestion = (suggestion) => {
  // 这里应该调用API应用调课建议
  console.log('应用调课建议:', suggestion);
  alert(`已应用调课建议: ${suggestion.title}`);
  
  // 从建议列表中移除
  suggestions.value = suggestions.value.filter(s => s !== suggestion);
  showNoSuggestions.value = suggestions.value.length === 0;
};

// 忽略调课建议
const ignoreSuggestion = (index) => {
  suggestions.value.splice(index, 1);
  showNoSuggestions.value = suggestions.value.length === 0;
};

// 获取星期几的名称
const getWeekdayName = (weekday) => {
  const weekdays = ['日', '一', '二', '三', '四', '五', '六', '日'];
  return weekdays[weekday];
};
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
.focus\:border-primary:focus {
  border-color: #4f46e5;
}
.focus\:ring-primary:focus {
  --tw-ring-color: #4f46e5;
}
.text-primary-dark {
  color: #4338ca;
}
</style>