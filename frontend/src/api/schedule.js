import axios from 'axios'

// 获取周视图
export function getWeekView(user, userType, week) {

  return axios.get(`/dashboard/weekView?user=${user}&userType=${userType}&week=${week}`);
}

//获取学期视图
export function getTermView(user, userType) {

  return axios.get(`/dashboard/termView?user=${user}&userType=${userType}`);
}