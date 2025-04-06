import random
from typing import List, Dict, Tuple, Set, Any
from collections import defaultdict
import time
#排课率约:80%
#用时约：10s
#这里是好滴
class CSPScheduler:
    """支持教学周连续性的CSP排课求解器"""

    def __init__(self, courses: List, rooms: List):
        """
        初始化
        :param courses: 课程列表，每个课程需包含:
            - uid: 课程唯一ID
            - time_slots: [(start_week, end_week, lessons_per_week)]
            - continuous (可选): 连排节数
            - 其他属性: fixedroom, fixedroomtype, teacherid等
        :param rooms: 教室列表，每个教室需包含:
            - rid: 教室ID
            - rtype: 教室类型
            - rcapacity: 教室容量
        """
        self.courses = sorted(courses, key=self.calculate_priority, reverse=True)
        self.rooms = rooms
        self.log = []
        self.room_pools = self._build_room_pools()

    def solve(self) -> Tuple[List[Tuple], List[Any]]:
        """主求解入口"""
        self._log("=== CSP求解开始 ===")
        self._log(f"课程总数: {len(self.courses)} | 教室总数: {len(self.rooms)}")

        solution = []
        unscheduled = []

        for idx, course in enumerate(self.courses):
            course_weeks = self._get_course_weeks(course)
            self._log(
                f"\n处理课程 [{idx+1}/{len(self.courses)}] {course.uid} "
                f"(周数: {course_weeks} 优先级: {self.calculate_priority(course):.1f})"
            )

            domains = self._generate_domains(course)
            assigned = False

            for pattern in domains:
                room = self._find_compatible_room(course, pattern, solution)
                if room:
                    self._assign_course(solution, course, pattern, room)
                    assigned = True
                    break

            if not assigned:
                unscheduled.append(course)
                self._log(f"⚠️ 无法安排课程 {course.uid}", "WARNING")

        self._report_stats(solution, unscheduled)
        return solution, unscheduled

    # ------------------- 核心算法方法 -------------------
    def _generate_domains(self, course) -> List[List[Tuple[int, int, int]]]:
        """
        生成课程的有效时间模式候选域
        返回: [ [(day, start_slot, length)], ... ]
        """
        patterns = []
        continuous = getattr(course, 'continuous', 1)
        total_lessons = course.total_hours
        total_weeks = sum(end - start + 1 for start, end, _ in course.time_slots)
        lessons_per_week = total_lessons / total_weeks

        # 验证连排设置
        if continuous > 1 and lessons_per_week % continuous != 0:
            self._log(f"课程 {course.uid} 的周课时数 {lessons_per_week} 不匹配连排设置 {continuous}", "ERROR")
            return []

        # 连排课程模式生成
        if continuous > 1:
            allowed_starts = CONTINUOUS_SLOT_RULES.get(continuous, [])
            groups_per_week = int(lessons_per_week / continuous)
            days = random.sample(range(1, DAYS_PER_WEEK + 1), groups_per_week)
            for day in random.sample(range(1, DAYS_PER_WEEK + 1), groups_per_week):
                for start in allowed_starts:
                    if start + continuous - 1 <= SLOTS_PER_DAY:
                        patterns.append([(day, start, continuous)])
        # 非连排课程模式生成
        else:
            days = random.sample(range(1, DAYS_PER_WEEK + 1), int(lessons_per_week))
            patterns.append([(day, 1, 1) for day in days])

        self._log(f"生成 {len(patterns)} 种时间模式: {patterns}", "DEBUG")
        return patterns

    def _find_compatible_room(self, course, pattern, solution) -> Any:
        # 策略0: 如果已安排过该课程，必须使用原教室
        existing_room = next((e[1] for e in solution if e[0] == course.uid), None)
        if existing_room:
            room = next((r for r in self.rooms if r.rid == existing_room), None)
            if room and self._check_availability(room, course, pattern, solution):
                return room
            return None
        """三级教室匹配策略"""
        # 策略1: 固定教室优先
        if getattr(course, 'fixedroom', None):
            fixed_room = next((r for r in self.rooms if r.rname == course.fixedroom), None)
            if fixed_room and self._check_availability(fixed_room, course, pattern, solution):
                return fixed_room

        # 策略2: 按类型匹配
        room_type = getattr(course, 'fixedroomtype', '教室')
        candidates = [r for r in self.room_pools.get(room_type, [])
                      if r.rcapacity >= getattr(course, 'popularity', 0)]

        # 策略3: 若无匹配类型，选择容量足够的任意教室
        if not candidates:
            candidates = [r for r in self.rooms
                          if r.rcapacity >= getattr(course, 'popularity', 0)]

        candidates.sort(key=lambda r: abs(r.rcapacity - getattr(course, 'popularity', 0)))

        for room in candidates[:10]:  # 限制检查数量
            if self._check_availability(room, course, pattern, solution):
                return room
        return None

    def _check_availability(self, room, course, pattern, solution) -> bool:
        existing_slots = {e[3:6] for e in solution if e[0] == course.uid}
        new_slots = set(self._expand_pattern(course, pattern))
        if existing_slots & new_slots:
            return False  # 该课程已占用该教室的其他时间段
        """检查教室和教师在课程教学周内的可用性"""
        required_slots = set(self._expand_pattern(course, pattern))
        course_weeks = self._get_course_weeks(course)

        for entry in solution:
            # 教室冲突检查 (同一教室+同周次+同时间段)
            if entry[1] == room.rid and entry[3] in course_weeks:
                if (entry[4], entry[5]) in {(p[0], p[1]) for p in pattern}:
                    return False

            # 教师冲突检查
            if (hasattr(course, 'teacherid') and (entry[2] == course.teacherid)):
                if (entry[3] in course_weeks) and (entry[4], entry[5]) in {(p[0], p[1]) for p in pattern}:
                    return False

        return True

    # ------------------- 工具方法 -------------------
    def _expand_pattern(self, course, pattern) -> List[Tuple[int, int, int]]:
        """将周模式扩展到具体的(周, 天, 节)时间点"""
        slots = []
        try:
            for start_week, end_week, _ in getattr(course, 'time_slots', [(1, WEEKS_IN_SEMESTER, 1)]):
                for week in range(start_week, end_week + 1):
                    for item in pattern:
                        day, start, length = item[:3]
                        slots.extend((week, day, start + offset) for offset in range(length))
        except Exception as e:
            print("Error in _expand_pattern with pattern:", pattern)
            raise e
        return slots


    def _get_course_weeks(self, course) -> Set[int]:
        """获取课程的所有教学周"""
        weeks = set()
        for start, end, _ in getattr(course, 'time_slots', [(1, WEEKS_IN_SEMESTER, 1)]):
            weeks.update(range(start, end + 1))
        return weeks

    def _assign_course(self, solution, course, pattern, room):
        """将课程安排添加到解决方案"""
        slots = self._expand_pattern(course, pattern)
        solution.extend(
            (course.uid, room.rid, getattr(course, 'teacherid', ''),
             week, day, slot
             ) for week, day, slot in slots
        )
        self._log(
            f"✅ 安排课程 {course.uid} -> 教室 {room.rid} "
            f"时间: {self._format_slots(slots)}",
            "SUCCESS"
        )

    def _report_stats(self, solution, unscheduled):
        """输出统计报告"""
        scheduled_courses = len({e[0] for e in solution})
        total_courses = len(self.courses)

        self._log("\n=== 求解结果 ===")
        self._log(f"已安排课程: {scheduled_courses}/{total_courses}")
        self._log(f"未安排课程: {len(unscheduled)}")

        if unscheduled:
            self._log("未安排课程列表:", "WARNING")
            for course in unscheduled:
                self._log(f"  - {course.uid} (周数: {self._get_course_weeks(course)})", "WARNING")

    def _format_slots(self, slots) -> str:
        """格式化时间点输出"""
        return ", ".join(
            f"第{week}周 周{day} 第{slot}节"
            for week, day, slot in slots[:3]  # 只显示前3个时间点
        ) + ("" if len(slots) <= 3 else f" 等{len(slots)}个时间点")

    # ------------------- 辅助方法 -------------------
    @staticmethod
    def calculate_priority(course) -> float:
        """课程优先级计算"""
        score = getattr(course, 'total_hours', 0)
        score += getattr(course, 'popularity', 0) * 0.5
        if getattr(course, 'fixedroom', None):
            score += 50
        return score

    def _build_room_pools(self) -> Dict[str, List]:
        """按教室类型分类资源池"""
        pools = defaultdict(list)
        for room in self.rooms:
            pools[room.rtype].append(room)
        self._log(f"教室资源池构建完成: { {k: len(v) for k, v in pools.items()} }")
        return pools

    def _log(self, message: str, level: str = "INFO"):
        """分级日志记录"""
        log_entry = f"[{level}] {message}"
        self.log.append(log_entry)

        # 控制台彩色输出
        if level == "ERROR":
            print(f"\033[91m{log_entry}\033[0m")  # 红色
        elif level == "WARNING":
            print(f"\033[93m{log_entry}\033[0m")  # 黄色
        elif level == "SUCCESS":
            print(f"\033[92m{log_entry}\033[0m")  # 绿色
        elif level == "DEBUG":
            pass  # 调试日志默认不显示
        else:
            print(log_entry)

# ------------------- 常量定义 -------------------
CONTINUOUS_SLOT_RULES = {
    2: [1, 3, 5, 7],  # 两节连排允许的开始节次
    4: [1, 3, 5],     # 四节连排允许的开始节次
}
WEEKS_IN_SEMESTER = 20
DAYS_PER_WEEK = 5
SLOTS_PER_DAY = 8


