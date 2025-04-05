import axios from 'axios'


// 获取周视图
export function getWeekView(user, userType, week) {

  return axios.get(`/dashboard/weekView?user=${user}&userType=${userType}&week=${week}`);
}

//获取学期视图
export function getTermView(user, userType) {

  return axios.get(`/dashboard/termView?user=${user}&userType=${userType}`);
}


// 基础API配置
const api = axios.create({
  baseURL: "/dashboard",
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
})

// // 获取周视图数据
// export const getWeekView = (user, userType, week) => {
//   return api.get("/weekView", {
//     params: {
//       user,
//       userType,
//       week,
//     },
//   })
// }

// // 获取学期视图数据
// export const getTermView = (user, userType, term) => {
//   return api.get("/termView", {
//     params: {
//       user,
//       userType,
//     },
//   })
// }


//TO DO


// 智能排课API
export const startSmartScheduling = (constraints) => {
  return api.post("/schedule/smart", constraints)
}

// 获取排课统计数据
export const getSchedulingStatistics = () => {
  return api.get("/schedule/statistics")
}



export default {
  getWeekView,
  getTermView,
  startSmartScheduling,
  getSchedulingStatistics,
}