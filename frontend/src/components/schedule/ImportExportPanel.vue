<template>
  <div class="bg-white rounded-lg shadow p-4">
    <h3 class="text-lg font-medium mb-4">数据导入导出</h3>
    
    <div class="space-y-4">
      <!-- 导入区域 -->
      <div class="border-2 border-dashed border-gray-300 rounded-md p-6 text-center">
        <input
          type="file"
          ref="fileInput"
          class="hidden"
          accept=".csv,.xlsx,.json"
          @change="handleFileUpload"
        />
        <div class="space-y-2">
          <Upload class="w-10 h-10 mx-auto text-gray-400" />
          <p class="text-sm text-gray-500">
            拖拽文件到此处或
            <button 
              @click="$refs.fileInput.click()" 
              class="text-primary hover:text-primary-dark"
            >
              浏览文件
            </button>
          </p>
          <p class="text-xs text-gray-400">
            支持 .csv, .xlsx, .json 格式
          </p>
        </div>
      </div>
      
      <!-- 导入历史 -->
      <div v-if="importHistory.length > 0">
        <h4 class="text-sm font-medium mb-2">导入历史</h4>
        <div class="space-y-2">
          <div 
            v-for="(item, index) in importHistory" 
            :key="index"
            class="flex justify-between items-center p-2 bg-gray-50 rounded-md text-sm"
          >
            <div>
              <span class="font-medium">{{ item.filename }}</span>
              <span class="text-xs text-gray-500 ml-2">{{ item.date }}</span>
            </div>
            <div class="flex items-center space-x-2">
              <span class="text-xs px-2 py-1 rounded-full" :class="getStatusClass(item.status)">
                {{ item.status }}
              </span>
              <button v-if="item.status === '成功'" class="text-gray-500 hover:text-gray-700">
                <RefreshCw class="w-4 h-4" />
              </button>
              <button class="text-gray-500 hover:text-gray-700">
                <Trash2 class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 导出选项 -->
      <div>
        <h4 class="text-sm font-medium mb-2">导出选项</h4>
        <div class="space-y-2">
          <div class="flex items-center space-x-2">
            <select 
              v-model="exportFormat" 
              class="h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm flex-1"
            >
              <option value="csv">CSV 格式</option>
              <option value="xlsx">Excel 格式</option>
              <option value="json">JSON 格式</option>
              <option value="pdf">PDF 格式</option>
            </select>
            <button 
              @click="exportData" 
              class="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary-dark"
            >
              导出数据
            </button>
          </div>
          
          <div class="flex flex-wrap gap-2 mt-2">
            <label class="flex items-center space-x-2">
              <input type="checkbox" v-model="exportOptions.includeConflicts" class="rounded text-primary" />
              <span class="text-sm">包含冲突信息</span>
            </label>
            <label class="flex items-center space-x-2">
              <input type="checkbox" v-model="exportOptions.includeStatistics" class="rounded text-primary" />
              <span class="text-sm">包含统计数据</span>
            </label>
            <label class="flex items-center space-x-2">
              <input type="checkbox" v-model="exportOptions.currentWeekOnly" class="rounded text-primary" />
              <span class="text-sm">仅当前周次</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { Upload, RefreshCw, Trash2 } from 'lucide-vue-next';

// 状态变量
const fileInput = ref(null);
const exportFormat = ref('xlsx');
const exportOptions = reactive({
  includeConflicts: true,
  includeStatistics: false,
  currentWeekOnly: false
});

// 导入历史
const importHistory = ref([
  { 
    filename: '2023-2024-2学期课表.xlsx', 
    date: '2024-03-15 14:30', 
    status: '成功', 
    records: 120 
  },
  { 
    filename: '教师课表.csv', 
    date: '2024-03-10 09:15', 
    status: '部分成功', 
    records: 85 
  },
  { 
    filename: '实验室排课.json', 
    date: '2024-03-05 16:45', 
    status: '失败', 
    records: 0 
  }
]);

// 获取状态样式类
const getStatusClass = (status) => {
  switch (status) {
    case '成功':
      return 'bg-green-100 text-green-800';
    case '部分成功':
      return 'bg-yellow-100 text-yellow-800';
    case '失败':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

// 处理文件上传
const handleFileUpload = (event) => {
  const file = event.target.files[0];
  if (!file) return;
  
  // 这里可以添加文件处理逻辑
  console.log('上传文件:', file.name);
  
  // 模拟添加到导入历史
  importHistory.value.unshift({
    filename: file.name,
    date: new Date().toLocaleString(),
    status: '处理中',
    records: 0
  });
  
  // 模拟处理完成
  setTimeout(() => {
    importHistory.value[0].status = '成功';
    importHistory.value[0].records = Math.floor(Math.random() * 100) + 50;
  }, 2000);
  
  // 清除文件输入
  event.target.value = '';
};

// 导出数据
const exportData = () => {
  console.log('导出格式:', exportFormat.value);
  console.log('导出选项:', exportOptions);
  
  // 这里可以添加导出逻辑
  alert(`数据将以 ${exportFormat.value.toUpperCase()} 格式导出`);
};
</script>

<style scoped>
.bg-primary {
  background-color: #4f46e5;
}
.text-primary {
  color: #4f46e5;
}
.text-primary-dark {
  color: #4338ca;
}
</style>

