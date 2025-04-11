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
  baseURL: "/automatic",
  timeout: 10000,
  // headers: {
  //   "Content-Type": "application/json",
  // },
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


/**
 * 启动智能调课
 * @param {Array} soft_constraints - 一个数组，每项对象格式为 { constraintItem, priority }，
 *                                  对应后端要求形如 [(id, priority), ...]
 * @returns {Promise} - 返回后端调课结果的 Promise 对象
 */
export const runScheduling = (soft_constraints) => {
  // 参数校验：确保传入的是一个数组
  if (!Array.isArray(soft_constraints)) {
    return Promise.reject(new Error("softConstraints 参数必须为数组"));
  }
  
  // 发送 PUT 请求，传递 soft_constraints 到后端
  return axios.put("/automatic", {soft_constraints: soft_constraints});
}



export default {
  getWeekView,
  getTermView,
  runScheduling,
};