import random
from typing import List, Dict, Tuple, Set, Any
from collections import defaultdict

#排课率约:85%
#用时约：1min
#进行伟大实验
class CSPScheduler:
    """支持教学周连续性的CSP排课求解器"""

    def __init__(self, courses: List, rooms: List,soft_constraints=None):
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
        self.soft_constraints = soft_constraints or []
        self.log = []
        self.room_pools = self._build_room_pools()
    def _get_constraint_weight(self, constraint_id):
        """根据前端参数获取约束权重"""
        for c in self.soft_constraints:
            if c[0] == constraint_id:
                return c[1] / 10.0  # 归一化到0-1范围
        return 0

    def _get_constraint_param(self, constraint_id):
        """获取约束参数（如是否允许晚上）"""
        for c in self.soft_constraints:
            if c[0] == constraint_id:
                return c[1]  # 参数直接为传入的int值
        return 0

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

            domains = self._generate_domains(course,solution)
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
    def _generate_domains(self, course,solution) -> List[List[Tuple[int, int, int]]]:
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
        #软约束相关
        scored_patterns = []
        for pattern in patterns:
            # 初始化评分
            pattern_score = 0

            # 约束2: 班级排课集中（同班级课程尽量相邻）
            # 约束2: 班级排课集中（同班级课程尽量相邻）
            if any(c[0] == 2 for c in self.soft_constraints):
                # 假设同班级课程已被安排的时间段（需从solution获取）
                same_class_slots = [s for s in solution if s[0].formclass == course.formclass]
                if same_class_slots:
                    avg_day = sum(s[4] for s in same_class_slots) / len(same_class_slots)
                    pattern_score += (5 - abs(avg_day - pattern[0][0])) * self._get_constraint_weight(2)

            # 约束4: 体育课安排在下午（开始节次>=5）
            if course.is_pe and any(c[0] == 4 for c in self.soft_constraints):
                if pattern[0][1] >= 5:  # 下午时间段（假设1-4为上午，5-8为下午）
                    pattern_score += 10 * self._get_constraint_weight(4)

            # 约束6: 晚上是否上课（优先级控制）
            if any(c[0] == 6 for c in self.soft_constraints):
                is_evening = (pattern[0][1] >= 7)  # 晚上时间段
                if self._get_constraint_param(6) > 0:  # 允许晚上
                    pattern_score += 5 * abs(self._get_constraint_param(6))
                else:  # 禁止晚上
                    pattern_score -= 10 * abs(self._get_constraint_param(6))

            scored_patterns.append((pattern, pattern_score))

        # 按评分降序排序，优先选择高评分模式
        scored_patterns.sort(key=lambda x: x[1], reverse=True)
        return [p[0] for p in scored_patterns]



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

        #约束3
        if any(c[0] == 3 for c in self.soft_constraints):
            # 获取该教师已使用的教室列表
            teacher_rooms = [
                entry[1]  # 教室ID
                for entry in solution
                if entry[2] == course.teacher_uid  # 教师ID匹配
            ]
            # 优先选择教师已用过的教室
            if teacher_rooms:
                candidates = sorted(
                    candidates,
                    key=lambda r: 100 if r.rid in teacher_rooms else 0,
                    reverse=True
                )
                self._log(f"教师 {course.teacher_uid} 已使用教室: {teacher_rooms}，优先匹配", "DEBUG")


        for room in candidates[:10]:  # 限制检查数量
            if self._check_availability(room, course, pattern, solution):
                return room
        return None

    def _check_availability(self, room, course, pattern, solution) -> bool:
        existing_slots = {e[3:6] for e in solution if e[0] == course.uid}
        new_slots = set(self._expand_pattern(course, pattern))
        if existing_slots & new_slots:
            return False

        required_slots = set(self._expand_pattern(course, pattern))
        course_weeks = self._get_course_weeks(course)

        for entry in solution:
            # 教室冲突检查
            if entry[1] == room.rid and entry[3] in course_weeks:
                if (entry[4], entry[5]) in {(p[0], p[1]) for p in pattern}:
                    return False

            # 教师冲突检查（修改点：使用teacher_uid）
            if hasattr(course, 'teacher_uid') and (entry[2] == course.teacher_uid):
                if (entry[3] in course_weeks) and (entry[4], entry[5]) in {(p[0], p[1]) for p in pattern}:
                    return False

            #体育课后是否上课？
            if course.is_pe and any(c[0] == 5 for c in self.soft_constraints):
                param = self._get_constraint_param(5)
                if param < 0:  # 禁止体育课后第一节课
                    # 获取体育课的时间段
                    pe_slots = self._expand_pattern(course, pattern)
                    for week, day, slot in pe_slots:
                        end_slot = slot + course.continuous - 1  # 体育课结束的节次
                        next_slot = end_slot + 1  # 课后第一节课的节次

                        # 检查同一周、同一天、下一节课是否被占用
                        if next_slot <= SLOTS_PER_DAY:
                            # 检查该时间段是否已有课程（教室或教师冲突）
                            key = (week, day, next_slot)
                            for entry in solution:
                                if (entry[3], entry[4], entry[5]) == key:
                                    self._log(
                                        f"⛔ 体育课 {course.uid} 后第{next_slot}节已安排课程 {entry[0]}，违反约束5",
                                        "DEBUG"
                                    )
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
        """将课程安排添加到解决方案（修改点：使用teacher_uid）"""
        slots = self._expand_pattern(course, pattern)
        solution.extend(
            (course, room.rid, getattr(course, 'teacher_uid', ''),  # 关键修改
             week, day, slot
             ) for week, day, slot in slots
        )
        self._log(
            f"✅ 安排课程 {course.uid} -> 教室 {room.rid} "
            f"教师: {getattr(course, 'teacher_uid', '未知')} "
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
        if hasattr(course, 'soft_scores'):
            score += sum(course.soft_scores.values()) * 0.1
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


