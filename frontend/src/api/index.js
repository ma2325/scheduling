// API 服务封装
import axios from 'axios';

// 创建 axios 实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data;
  },
  error => {
    if (error.response && error.response.status === 401) {
      // 未授权，跳转到登录页
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// 课程相关 API
export const courseApi = {
  // 获取课程列表
  getCourses() {
    return api.get('/courses');
  },
  
  // 获取未排课程
  getUnscheduledCourses() {
    return api.get('/courses/unscheduled');
  },
  
  // 保存课程安排
  saveCourseArrangement(data) {
    return api.post('/courses/arrangement', data);
  }
};

// 教室相关 API
export const classroomApi = {
  // 获取教室列表
  getClassrooms() {
    return api.get('/classrooms');
  },
  
  // 获取可用教室
  getAvailableClassrooms(params) {
    return api.get('/classrooms/available', { params });
  }
};

// 统计分析相关 API
export const statisticsApi = {
  // 获取教室利用率
  getClassroomUtilization() {
    return api.get('/statistics/classroom-utilization');
  },
  
  // 获取教师课时分布
  getTeacherHours() {
    return api.get('/statistics/teacher-hours');
  },
  
  // 获取课程类型分布
  getCourseTypeDistribution() {
    return api.get('/statistics/course-type');
  },
  
  // 获取时间段课程分布
  getTimeSlotDistribution() {
    return api.get('/statistics/time-slot');
  }
};

// 智能调课相关 API
export const adjustmentApi = {
  // 生成调课建议
  generateSuggestions(params) {
    return api.post('/adjustment/suggestions', params);
  },
  
  // 应用调课建议
  applySuggestion(data) {
    return api.post('/adjustment/apply', data);
  }
};

// 认证相关 API
export const authApi = {
  // 登录
  login(data) {
    return api.post('/auth/login', data);
  },
  
  // 注册
  register(data) {
    return api.post('/auth/register', data);
  },
  
  // 退出登录
  logout() {
    return api.post('/auth/logout');
  }
};

export default {
  course: courseApi,
  classroom: classroomApi,
  statistics: statisticsApi,
  adjustment: adjustmentApi,
  auth: authApi
};