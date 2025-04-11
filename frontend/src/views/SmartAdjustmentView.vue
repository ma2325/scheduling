<template>
  <div class="space-y-6">
    <!-- 头部标题和按钮 -->
    <div class="flex justify-between items-center">
      <h2 class="text-xl font-bold">智能调课</h2>
      <div class="flex space-x-2">
        <button 
          @click="clearAllData" 
          class="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
          v-if="hasSavedData"
        >
          清除数据
        </button>
        <button 
          @click="fetchCoursesAndGenerateSuggestions" 
          class="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary-dark"
          :disabled="isLoading"
        >
          <span v-if="isLoading" class="flex items-center">
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            分析中...
          </span>
          <span v-else>生成调课建议</span>
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

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">分析课程数量</label>
          <input 
            type="number" 
            v-model="coursesLimit" 
            min="3" 
            max="10" 
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50"
          />
          <div class="text-xs text-gray-500 mt-1">
            建议选择 3-10 门课程进行分析，数量过多可能影响分析质量
          </div>
        </div>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="errorMessage" class="bg-red-50 border border-red-200 text-red-800 rounded-lg p-4">
      <div class="flex">
        <svg class="h-5 w-5 text-red-600 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <div>
          <p class="font-medium">分析出错</p>
          <p class="text-sm">{{ errorMessage }}</p>
        </div>
      </div>
    </div>

    <!-- 原始课程数据 -->
    <div v-if="courses.length > 0" class="bg-white rounded-lg shadow p-6">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-medium">当前课程安排</h3>
        <div class="text-sm text-gray-500">
          共 {{ courses.length }} 门课程，显示前 {{ displayedCourses.length }} 门
        </div>
      </div>
      
      <div class="overflow-x-auto">
        <table class="w-full text-sm text-left">
          <thead class="text-xs text-gray-700 uppercase bg-gray-50">
            <tr>
              <th class="px-4 py-2">课程任务</th>
              <th class="px-4 py-2">教师</th>
              <th class="px-4 py-2">教室</th>
              <th class="px-4 py-2">时间</th>
              <th class="px-4 py-2">周次</th>
              <th class="px-4 py-2">班级</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="course in displayedCourses" :key="course.scid" class="border-b hover:bg-gray-50">
              <td class="px-4 py-2 font-medium">{{ course.sctask }}</td>
              <td class="px-4 py-2">{{ course.scteacherid }}</td>
              <td class="px-4 py-2">{{ course.scroom }}</td>
              <td class="px-4 py-2">周{{ getWeekdayName(parseInt(course.scday_of_week)) }} {{ course.scslot }}</td>
              <td class="px-4 py-2">{{ course.scbegin_week }}-{{ course.scend_week }}周</td>
              <td class="px-4 py-2">{{ course.composition }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 调课建议列表 -->
    <div v-if="suggestions.length > 0" class="bg-white rounded-lg shadow p-6">
      <h3 class="text-lg font-medium mb-4">调课建议</h3>
      
      <div class="space-y-4">
        <div v-for="(suggestion, index) in suggestions" :key="index" 
             class="border rounded-lg p-4 hover:bg-gray-50">
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <h4 class="font-medium">建议 #{{ index + 1 }}: {{ suggestion.title }}</h4>
              <p class="text-sm text-gray-600 mt-1">{{ suggestion.description }}</p>
              
              <div class="mt-3 grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
                <div>
                  <span class="font-medium">课程ID:</span> {{ suggestion.courseId }}
                </div>
                <div>
                  <span class="font-medium">课程名称:</span> {{ suggestion.courseName }}
                </div>
                <div v-if="suggestion.originalRoom !== suggestion.newRoom">
                  <span class="font-medium">原教室:</span> {{ suggestion.originalRoom }}
                </div>
                <div v-if="suggestion.originalRoom !== suggestion.newRoom">
                  <span class="font-medium">新教室:</span> {{ suggestion.newRoom }}
                </div>
                <div v-if="suggestion.originalDay !== suggestion.newDay || suggestion.originalSlot !== suggestion.newSlot">
                  <span class="font-medium">原时间:</span> 周{{ getWeekdayName(suggestion.originalDay) }} {{ suggestion.originalSlot }}
                </div>
                <div v-if="suggestion.originalDay !== suggestion.newDay || suggestion.originalSlot !== suggestion.newSlot">
                  <span class="font-medium">新时间:</span> 周{{ getWeekdayName(suggestion.newDay) }} {{ suggestion.newSlot }}
                </div>
                <div v-if="suggestion.originalWeeks !== suggestion.newWeeks">
                  <span class="font-medium">原周次:</span> {{ suggestion.originalWeeks }}
                </div>
                <div v-if="suggestion.originalWeeks !== suggestion.newWeeks">
                  <span class="font-medium">新周次:</span> {{ suggestion.newWeeks }}
                </div>
              </div>
              
              <div class="mt-3">
                <span class="text-sm font-medium">优化理由:</span>
                <p class="text-sm text-gray-600 mt-1">{{ suggestion.reason }}</p>
              </div>
            </div>
            
            <div class="flex space-x-2 ml-4">
              <button 
                @click="applySuggestion(suggestion)" 
                class="px-3 py-1 bg-primary text-white text-sm rounded-md hover:bg-primary-dark"
                :disabled="isApplying"
              >
                <span v-if="isApplying && applyingIndex === index" class="flex items-center">
                  <svg class="animate-spin -ml-1 mr-1 h-3 w-3 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  应用中
                </span>
                <span v-else>应用</span>
              </button>
              <button 
                @click="ignoreSuggestion(index)" 
                class="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-md hover:bg-gray-200"
                :disabled="isApplying"
              >
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

    <!-- AI 分析结果对话框 -->
    <div v-if="showAnalysisDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-3xl">
        <div class="flex justify-between items-start mb-4">
          <h3 class="text-lg font-medium">AI 分析详情</h3>
          <button @click="showAnalysisDialog = false" class="text-gray-500 hover:text-gray-700">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="max-h-[60vh] overflow-y-auto prose">
          <pre class="whitespace-pre-wrap text-sm bg-gray-50 p-4 rounded">{{ rawAnalysisResult }}</pre>
        </div>
        <div class="mt-4 flex justify-end">
          <button 
            @click="showAnalysisDialog = false" 
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
import { ref, reactive, computed, onMounted } from 'vue';
import axios from 'axios';

// 状态变量
const isLoading = ref(false);
const isApplying = ref(false);
const applyingIndex = ref(-1);
const courses = ref([]);
const coursesLimit = ref(5);
const suggestions = ref([]);
const showNoSuggestions = ref(false);
const errorMessage = ref('');
const rawAnalysisResult = ref('');
const showAnalysisDialog = ref(false);
const hasSavedData = ref(false);

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

// 显示的课程数据
const displayedCourses = computed(() => {
  return courses.value.slice(0, parseInt(coursesLimit.value));
});

// 星期几名称映射
const weekdayNames = ['日', '一', '二', '三', '四', '五', '六', '日'];

// 获取星期几的名称
const getWeekdayName = (weekday) => {
  return weekdayNames[weekday] || '';
};

// 从后端获取课程数据
const fetchCourses = async () => {
  try {
    const response = await axios.get('http://localhost:8080/manual/all');
    if (response.status === 200 && response.data.code === 200) {
      // 随机选择指定数量的课程
      const allCourses = response.data.rows || [];
      const shuffled = [...allCourses].sort(() => 0.5 - Math.random());
      courses.value = shuffled.slice(0, parseInt(coursesLimit.value));
      return courses.value;
    } else {
      throw new Error('获取课程数据失败');
    }
  } catch (error) {
    console.error('获取课程数据出错:', error);
    errorMessage.value = '获取课程数据失败，请稍后重试';
    // 使用模拟数据
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
      }
    ];
    courses.value = mockCourses;
    return mockCourses;
  }
};

/**
 * 调用 DeepSeek API 进行对话生成
 * @param {string} apiKey - DeepSeek API 密钥
 * @param {Array} messages - 对话历史
 * @param {string} model - 使用的模型
 * @returns {Promise<string>} - 返回 AI 生成的回复内容
 */
async function callDeepSeekAPI(apiKey, messages, model = "deepseek-chat") {
  const API_ENDPOINT = "https://api.deepseek.com/v1/chat/completions";
  
  try {
    const response = await fetch(API_ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: model,
        messages: messages,
        temperature: 0.7,
        max_tokens: 2000
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error?.message || "API 请求失败");
    }

    const data = await response.json();
    return data.choices[0].message.content;
    
  } catch (error) {
    console.error("调用 DeepSeek API 出错:", error);
    throw error;
  }
}

// 生成调课建议
const fetchCoursesAndGenerateSuggestions = async () => {
  isLoading.value = true;
  errorMessage.value = '';
  suggestions.value = [];
  showNoSuggestions.value = false;
  
  try {
    // 获取课程数据
    const coursesData = await fetchCourses();
    
    if (!coursesData || coursesData.length === 0) {
      throw new Error('没有获取到课程数据');
    }
    
    // 准备提示语
    const prompt = generateAIPrompt(coursesData);
    
    // 调用 DeepSeek API
    const apiKey = "sk-6b3de816799d4f0386bc2fbe014797b0";
    const messages = [
      { role: "user", content: prompt }
    ];
    
    const analysisResult = await callDeepSeekAPI(apiKey, messages);
    
    // 保存原始分析结果
    rawAnalysisResult.value = analysisResult;
    
    // 解析 AI 返回的建议
    const parsedSuggestions = parseAIResponse(analysisResult);
    suggestions.value = parsedSuggestions;
    
    // 保存数据到本地存储
    saveDataToStorage();
    
    // 显示分析对话框
    showAnalysisDialog.value = true;
    
    // 如果没有建议，显示提示
    showNoSuggestions.value = parsedSuggestions.length === 0;
    
  } catch (error) {
    console.error('生成调课建议出错:', error);
    errorMessage.value = error.message || '生成调课建议失败，请稍后重试';
    showNoSuggestions.value = true;
  } finally {
    isLoading.value = false;
  }
};

// 生成给 AI 的提示语
const generateAIPrompt = (coursesData) => {
  // 根据调课设置生成适当的提示语
  const goalMap = {
    'teacherLoad': '平衡教师课时负担',
    'classroomUtilization': '提高教室利用率',
    'timeDistribution': '优化时间分布',
    'studentExperience': '改善学生体验'
  };
  
  const scopeMap = {
    'all': '所有课程',
    'department': '按院系',
    'teacher': '按教师',
    'courseType': '按课程类型'
  };
  
  // 将课程数据转为易读的格式
  const formattedCourses = coursesData.map(course => {
    return `
课程ID: ${course.scid}
课程任务: ${course.sctask}
教室: ${course.scroom}
周次: ${course.scbegin_week}-${course.scend_week}周
星期: ${course.scday_of_week}
节次: ${course.scslot}
教师ID: ${course.scteacherid}
学院: ${course.scteacherdepartment || '未知'}
班级: ${course.composition || '未知'}
    `;
  }).join('\n---\n');
  
  // 构建提示语
  return `
你是一个大学课程排课系统的专家助手。我需要你分析以下${coursesData.length}门课程的排课情况，并给出调课建议。

【优化目标】: ${goalMap[adjustmentSettings.optimizationGoal]}
【调整范围】: ${scopeMap[adjustmentSettings.adjustmentScope]}
【约束条件】: 
- ${adjustmentSettings.constraints.keepTeacher ? '需要' : '不需要'}保持原教师不变
- ${adjustmentSettings.constraints.keepTimeSlot ? '尽量' : '不需要'}保持原时间段
- ${adjustmentSettings.constraints.avoidConflicts ? '需要' : '不需要'}避免师生冲突
【调整力度】: ${adjustmentSettings.adjustmentIntensity}/10 (数值越大调整越大)

【课程数据】:
${formattedCourses}

请分析这些课程的排课情况，并根据优化目标给出2-3条具体的调课建议。你的建议应该考虑到约束条件和调整力度。

对于每条建议，请提供以下信息，并使用JSON格式输出：
1. 建议标题
2. 建议描述
3. 需要调整的课程ID
4. 课程名称
5. 原始教室和建议的新教室（如需调整）
6. 原始星期几和建议的新星期几（如需调整）
7. 原始节次和建议的新节次（如需调整）
8. 原始周次和建议的新周次（如需调整）
9. 优化理由

请使用以下JSON格式回复，只需要JSON数据，不要附加任何其他文字：
[
  {
    "title": "建议标题",
    "description": "建议描述",
    "courseId": 课程ID,
    "courseName": "课程名称",
    "originalRoom": "原教室",
    "newRoom": "新教室",
    "originalDay": 原星期几数字(1-7),
    "newDay": 新星期几数字(1-7),
    "originalSlot": "原节次",
    "newSlot": "新节次",
    "originalWeeks": "原周次",
    "newWeeks": "新周次",
    "reason": "详细的优化理由"
  },
  {...}
]
`;
};

// 解析 AI 回复
const parseAIResponse = (response) => {
  try {
    // 尝试提取JSON部分
    const jsonMatch = response.match(/\[[\s\S]*\]/);
    const jsonString = jsonMatch ? jsonMatch[0] : response;
    
    // 解析JSON
    const suggestions = JSON.parse(jsonString);
    
    // 验证格式是否正确
    if (!Array.isArray(suggestions)) {
      throw new Error('无效的回复格式');
    }
    
    return suggestions;
  } catch (error) {
    console.error('解析AI回复出错:', error);
    errorMessage.value = '解析AI回复失败，请重试';
    return [];
  }
};

// 应用调课建议
const applySuggestion = async (suggestion) => {
  if (!suggestion || !suggestion.courseId) {
    return;
  }
  
  isApplying.value = true;
  applyingIndex.value = suggestions.value.indexOf(suggestion);
  
  try {
    // 根据建议准备更新数据
    const updateData = {
      scid: suggestion.courseId
    };
    
    // 只添加需要更新的字段
    if (suggestion.newRoom && suggestion.newRoom !== suggestion.originalRoom) {
      updateData.scroom = suggestion.newRoom;
    }
    
    if (suggestion.newDay && suggestion.newDay !== suggestion.originalDay) {
      updateData.scday_of_week = suggestion.newDay.toString();
    }
    
    if (suggestion.newSlot && suggestion.newSlot !== suggestion.originalSlot) {
      updateData.scslot = suggestion.newSlot;
    }
    
    if (suggestion.newWeeks && suggestion.newWeeks !== suggestion.originalWeeks) {
      // 处理周次，假设格式为 "1-16"
      const weeks = suggestion.newWeeks.split('-');
      if (weeks.length === 2) {
        updateData.scbegin_week = parseInt(weeks[0]);
        updateData.scend_week = parseInt(weeks[1]);
      }
    }
    
    console.log('更新数据:', updateData);
    
    // 调用后端API更新课程
    const response = await axios.post('http://localhost:8080/manual/change', updateData);
    
    if (response.status === 200 && response.data.code === 200) {
      // 更新成功，从建议列表中移除
      suggestions.value = suggestions.value.filter(s => s !== suggestion);
      showNoSuggestions.value = suggestions.value.length === 0;
      
      // 更新本地课程数据
      const courseIndex = courses.value.findIndex(c => c.scid === suggestion.courseId);
      if (courseIndex !== -1) {
        if (updateData.scroom) courses.value[courseIndex].scroom = updateData.scroom;
        if (updateData.scday_of_week) courses.value[courseIndex].scday_of_week = updateData.scday_of_week;
        if (updateData.scslot) courses.value[courseIndex].scslot = updateData.scslot;
        if (updateData.scbegin_week) courses.value[courseIndex].scbegin_week = updateData.scbegin_week;
        if (updateData.scend_week) courses.value[courseIndex].scend_week = updateData.scend_week;
      }
      
      // 保存更新后的数据
      saveDataToStorage();
      
      // 显示成功消息
      alert(`应用调课建议成功: ${suggestion.title}`);
    } else {
      throw new Error(response.data.msg || '应用调课建议失败');
    }
  } catch (error) {
    console.error('应用调课建议出错:', error);
    errorMessage.value = error.message || '应用调课建议失败，请稍后重试';
  } finally {
    isApplying.value = false;
    applyingIndex.value = -1;
  }
};

// 忽略调课建议
const ignoreSuggestion = (index) => {
  suggestions.value.splice(index, 1);
  showNoSuggestions.value = suggestions.value.length === 0;
  
  // 保存更新后的数据
  saveDataToStorage();
};

// 清除所有数据
const clearAllData = () => {
  if (confirm('确定要清除所有数据吗？此操作不可恢复。')) {
    localStorage.removeItem('smart-adjustment-courses');
    localStorage.removeItem('smart-adjustment-suggestions');
    localStorage.removeItem('smart-adjustment-analysis');
    
    courses.value = [];
    suggestions.value = [];
    rawAnalysisResult.value = '';
    showNoSuggestions.value = false;
    hasSavedData.value = false;
  }
};

// 保存数据到本地存储
const saveDataToStorage = () => {
  try {
    // 保存课程数据、建议和分析结果到localStorage
    localStorage.setItem('smart-adjustment-courses', JSON.stringify(courses.value));
    localStorage.setItem('smart-adjustment-suggestions', JSON.stringify(suggestions.value));
    localStorage.setItem('smart-adjustment-analysis', rawAnalysisResult.value);
    
    // 更新数据状态标志
    hasSavedData.value = true;
  } catch (error) {
    console.error('保存数据到本地存储出错:', error);
  }
};

// 从本地存储加载数据
const loadDataFromStorage = () => {
  try {
    const savedCourses = localStorage.getItem('smart-adjustment-courses');
    const savedSuggestions = localStorage.getItem('smart-adjustment-suggestions');
    const savedAnalysis = localStorage.getItem('smart-adjustment-analysis');
    
    if (savedCourses) {
      courses.value = JSON.parse(savedCourses);
    }
    
    if (savedSuggestions) {
      suggestions.value = JSON.parse(savedSuggestions);
      showNoSuggestions.value = suggestions.value.length === 0;
    }
    
    if (savedAnalysis) {
      rawAnalysisResult.value = savedAnalysis;
    }
    
    // 更新数据状态标志
    hasSavedData.value = Boolean(savedCourses || savedSuggestions || savedAnalysis);
    
    return hasSavedData.value;
  } catch (error) {
    console.error('从本地存储加载数据出错:', error);
    return false;
  }
};

// 组件挂载时检查本地存储的数据
onMounted(() => {
  loadDataFromStorage();
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
.focus\:border-primary:focus {
  border-color: #4f46e5;
}
.focus\:ring-primary:focus {
  --tw-ring-color: #4f46e5;
}
.text-primary-dark {
  color: #4338ca;
}

/* 禁用按钮样式 */
button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* 加载动画 */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
.animate-spin {
  animation: spin 1s linear infinite;
}
</style>