<template>
    <div class="space-y-6">
      <div class="flex justify-between items-center">
        <h2 class="text-xl font-bold">智能排课</h2>
        <div class="flex space-x-2">
          <button 
            @click="startScheduling" 
            class="px-6 py-3 bg-primary text-white rounded-md hover:bg-primary-dark flex items-center"
            :disabled="isScheduling"
          >
            <Loader2 v-if="isScheduling" class="w-5 h-5 mr-2 animate-spin" />
            <Play v-else class="w-5 h-5 mr-2" />
            {{ isScheduling ? '排课中...' : '开始排课' }}
          </button>
        </div>
      </div>
  
      <!-- 约束条件区域 -->
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-medium mb-4">约束条件设置</h3>
        
        <div class="max-h-[70vh] overflow-y-auto pr-2">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- 约束条件卡片 -->
            <div 
              v-for="constraint in constraintsList" 
              :key="constraint.id" 
              class="bg-gray-50 rounded-lg p-4 border border-gray-200"
            >
              <div class="flex justify-between items-start mb-2">
                <div>
                  <h4 class="font-medium text-gray-900">{{ constraint.name }}</h4>
                  <p class="text-sm text-gray-600">{{ constraint.detail }}</p>
                </div>
                <div class="flex items-center">
                  <input 
                    type="checkbox" 
                    :id="constraint.id" 
                    v-model="constraint.enabled"
                    class="rounded text-primary focus:ring-primary"
                  />
                </div>
              </div>
              <div v-if="constraint.enabled" class="mt-3">
                <label class="block text-sm font-medium text-gray-700 mb-1">优先级</label>
                <div class="flex items-center">
                  <input 
                    type="range" 
                    v-model="constraint.priority" 
                    min="1" 
                    max="10" 
                    class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                  <span class="ml-2 text-sm font-medium">{{ constraint.priority }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
  
      <!-- 排课结果弹窗 -->
      <div v-if="showResultModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div class="bg-white rounded-lg p-6 w-full max-w-2xl">
          <div class="flex justify-between items-start mb-4">
            <h3 class="text-lg font-medium text-gray-900">排课完成</h3>
            <button @click="showResultModal = false" class="text-gray-400 hover:text-gray-500">
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <div class="mb-4">
            <p class="text-green-600 font-medium mb-2">排课已成功完成！</p>
            <p class="text-gray-600">系统已根据您设置的约束条件生成最优排课方案。</p>
          </div>
          
          <div class="grid grid-cols-2 gap-4 mb-6">
            <div class="bg-gray-50 p-3 rounded-md">
              <p class="text-sm text-gray-500">总课程数</p>
              <p class="text-xl font-medium">{{ schedulingResult.totalCourses || 0 }}</p>
            </div>
            <div class="bg-gray-50 p-3 rounded-md">
              <p class="text-sm text-gray-500">已排课程</p>
              <p class="text-xl font-medium">{{ schedulingResult.scheduledCourses || 0 }}</p>
            </div>
            <div class="bg-gray-50 p-3 rounded-md">
              <p class="text-sm text-gray-500">算法运行时间</p>
              <p class="text-xl font-medium">{{ schedulingResult.executionTime || '0s' }}</p>
            </div>
          </div>
          
          <div class="flex justify-end space-x-3">
            <button 
              @click="showResultModal = false" 
              class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              关闭
            </button>
            <button 
              @click="viewStatistics" 
              class="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary-dark"
            >
              查看详细统计
            </button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive } from 'vue';
  import { useRouter } from 'vue-router';
  import { Play, Loader2 } from 'lucide-vue-next';
  import {runScheduling} from '@/api/schedule'
  import { useSchedulingStore } from '@/stores/schedulingStore';
  
  const router = useRouter();
  const isScheduling = ref(false);
  const showResultModal = ref(false);
  const schedulingStore = useSchedulingStore();

  // 约束条件列表
  const constraintsList = reactive([
    {
      id: 1,
      name: '同一课程教室相同',
      detail: '减少师生找教室的混乱，便于教学设备布置和使用',
      enabled: true,
      priority: 5
    },
    {
      id: 2,
      name: '班级排课集中',
      detail: '尽可能把一个班级的一天课程集中安排在较短时间段内，避免“早来一节、晚走一节”这种低效时段浪费',
      enabled: true,
      priority: 5
    },
    {
      id: 3,
      name: '教师排课集中',
      detail: '老师一天的课程尽量排在连续的时间段内，以便提高教师授课效率',
      enabled: true,
      priority: 5
    },
    {
      id: 4,
      name: '体育课安排在下午',
      detail: '体育活动更适合在下午进行，避免早晨天气寒冷或刚起床身体僵硬的情况，更符合学生体能活动规律',
      enabled: true,
      priority: 5
    },
    {
      id: 5,
      name: '体育课后是否上课',
      detail: '体育课后学生容易疲惫，若紧接着安排文化课，可能影响学习效率',
      enabled: true,
      priority: 5
    },
    {
      id: 6,
      name: '晚上是否上课',
      detail: '是否利用晚自习时间段排文化课，一般根据学校教学计划或年级特点决定',
      enabled: true,
      priority: 5
    }
  ]);
  
  // 排课结果
  const schedulingResult = ref({
    totalCourses: 0,
    scheduledCourses: 0,
    executionTime: '0s'
  });
  
  // 开始排课
  const startScheduling = async () => {
    
    isScheduling.value = true;
    
    try {
      //筛选需传给后端的数据(即被选中的约束)
      const soft_constraints = constraintsList
      .filter(constraint => constraint.enabled)
      .map(constraint => ({
        constraintItem: constraint.id,  // 对应后端要求的字段
        priority: constraint.priority,
      }));
      
      const startTime = Date.now();
      //发送 PUT 请求
      const response = await runScheduling(soft_constraints);
      if (response.data.code === 200) {
        alert("智能调课完成！");


        const endTime = Date.now();
        const duration = (endTime - startTime)/1000; // 算法执行耗时（毫秒）

        // const summary = {
        //         totalClasses,
        //         scheduledClasses,
        //         unscheduledClasses,
        //         totalRooms,
        //         usedRooms,
        //         roomRate,
        //         totalTeachers,
        //         totalScheduledTeachers
        //     };

        // 获取后端返回的统计数据
        const summary = response.data.data.summary;
        
        // 保存到 store 中
        schedulingStore.setSummary(summary);

        // 结果数据
        schedulingResult.value = {
          totalCourses: summary.totalClasses,
          scheduledCourses: summary.scheduledClasses,
          executionTime: `${duration}s`
        };
        
        // 显示结果弹窗
        showResultModal.value = true;

        console.log("调课统计数据：", response.data.data.summary);
      } else {
        alert(response.data.msg || "调课失败");
      }
      

    } catch (error) {
      console.error('排课请求失败:', error);
      alert('排课过程中发生错误，请重试');
    } finally {
      isScheduling.value = false;
    }
  };
  
  // 查看统计数据
  const viewStatistics = () => {
    showResultModal.value = false;
    router.push('/statistics');
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
  .focus\:ring-primary:focus {
    --tw-ring-color: #4f46e5;
  }
  </style>
  
  