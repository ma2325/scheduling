import axios from 'axios'

// 获取课表数据
export function getSchedule() {
  return axios.get('/dashboard')
}