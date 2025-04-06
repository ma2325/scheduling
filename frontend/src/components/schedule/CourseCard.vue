<template>
  <div 
    class="p-2 mb-1 bg-primary-light text-primary-dark rounded-md text-sm cursor-pointer hover:shadow-md transition-shadow"
    :class="{'border-2 border-dashed border-primary': isEditMode}"
    draggable="isEditMode"
    @dragstart="onDragStart"
    @click="$emit('click')"
  >
    <div class="font-medium truncate" :title="course.name">{{ course.name }}</div>
    <div class="text-xs truncate" :title="formatClasses(course.classes)">
      {{ formatClasses(course.classes) }}
    </div>
    <div class="text-xs truncate" :title="course.classroom">{{ course.classroom }}</div>
    <div class="text-xs">教师ID: {{ course.teacherId }}</div>
    
    <div v-if="isEditMode" class="mt-1 flex justify-end">
      <button 
        @click.stop="$emit('remove')" 
        class="text-xs text-red-500 hover:text-red-700 p-1"
        title="移除课程"
      >
        <Trash2 class="w-3 h-3" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';
import { Trash2 } from 'lucide-vue-next';

const props = defineProps({
  course: {
    type: Object,
    required: true
  },
  isEditMode: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['click', 'drag-start', 'remove']);

// 格式化班级显示
const formatClasses = (classes) => {
  if (!classes) return '';
  const classList = classes.split(',');
  if (classList.length <= 2) return classes;
  return `${classList[0]}等${classList.length}个班级`;
};

// 拖拽开始
const onDragStart = (event) => {
  if (!props.isEditMode) {
    event.preventDefault();
    return;
  }
  
  emit('drag-start', event);
};
</script>

<style scoped>
.bg-primary-light {
  background-color: #ede9fe;
}

.text-primary-dark {
  color: #4338ca;
}

.border-primary {
  border-color: #4f46e5;
}
</style>

