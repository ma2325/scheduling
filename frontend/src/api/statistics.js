import axios from "axios"

// 获取特定周次的统计数据
export const getWeekStatistics = (week) => {
  return axios.get("/statistics", {
    params: { week },
  })
}

export default {
  getWeekStatistics,
}
