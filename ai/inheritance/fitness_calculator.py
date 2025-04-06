# fitness_calculator.py
from typing import List, Dict, Set, Tuple
from collections import defaultdict
import random
from functools import lru_cache
from typing import List, Dict, Set, Tuple
from collections import defaultdict
import random
from functools import lru_cache
import time
from typing import Any
import numpy as np

#试探
class FitnessCalculator:
    def __init__(self, weights: Dict[str, float], courses: List, rooms: List):
        """
        :param weights: 约束权重配置 {'teacher_gap': 0.1, ...}
        :param courses: 所有课程列表
        :param rooms: 所有教室列表
        """
        self.weights = weights
        self.courses = courses
        self.rooms = rooms
        print("[Fitness] 初始化FitnessCalculator...")
        start = time.time()
        self._build_lookups()
        print(f"[Fitness] 初始化完成 | 耗时: {time.time()-start:.2f}s | "
              f"课程数: {len(courses)} | 教室数: {len(rooms)}")
        # 在FitnessCalculator.__init__中添加
        self.continuous_courses = {
            c.uid for c in courses if getattr(c, 'continuous', 1) > 1
        }
        print(f"连排课程数量: {len(self.continuous_courses)}")
    def _build_lookups(self):
        """预构建加速查询的数据结构"""
        print("[Fitness] 构建查询索引...")
        start = time.time()
        self.course_dict = {c.uid: c for c in self.courses}
        self.room_dict = {r.rid: r for r in self.rooms}
        self.course_ids = [c.uid for c in self.courses]  # 用于快速抽样
        print(f"[Fitness] 索引构建完成 | 耗时: {time.time()-start:.2f}s")
    # 在 FitnessCalculator 类中
    # fitness_calculator.py
    def calculate(self, solution: List[Tuple]) -> Tuple[float, Dict[str, Any]]:
        """完整适应度计算（带诊断输出）"""
        print(f"[Fitness] 完整评估 | 解大小: {len(solution)}")
        start = time.time()

        # 计算各约束项
        unscheduled = self._calc_unscheduled(solution)
        teacher_conflicts = self._calc_teacher_conflicts(solution)
        room_utilization = self._calc_room_utilization(solution)
        #student_load = self._calc_student_load(solution)

        # 加权求和
        score = 100.0
        score -= unscheduled * self.weights['unscheduled']
        score -= teacher_conflicts * self.weights['teacher_gap']
        score -= room_utilization * self.weights['room_utilization']
        #score -= student_load * self.weights['student_load']

        # 创建 metrics 字典
        metrics = {
            'unscheduled': unscheduled,
            'teacher_conflicts': teacher_conflicts,
            'room_utilization': room_utilization,
            #'student_load': student_load,
        }

        print(f"[Fitness] 评估完成 | 耗时: {time.time()-start:.2f}s | "
              f"得分: {score:.2f} | 未排课: {unscheduled} | "
              f"教师冲突: {teacher_conflicts} | 教室利用: {room_utilization:.2f} | ")
             # f"学生负荷: {student_load:.2f}")
        return score, metrics  # 保持返回元组


    def _calc_continuity(self, solution: List[Tuple]) -> int:
        """优化版连排连续性检查"""
        print("    [连排连续] 开始检查连排课程...")
        start = time.time()

        # 按课程分组收集课时
        course_slots = defaultdict(list)
        for entry in solution:
            course_slots[entry[0]].append((entry[3], entry[4], entry[5]))  # (周,天,节)

        continuity_violations = 0
        continuous_courses = 0

        for course_id, slots in course_slots.items():
            course = self.course_dict[course_id]
            if getattr(course, 'continuous', 1) <= 1:
                continue

            continuous_courses += 1

            # 按周和天分组
            week_day_slots = defaultdict(list)
            for week, day, slot in slots:
                week_day_slots[(week, day)].append(slot)

            # 检查每天是否连续
            for day_slots in week_day_slots.values():
                if len(day_slots) < 2:
                    continue

                slots_sorted = sorted(day_slots)
                expected = list(range(slots_sorted[0], slots_sorted[0] + len(slots_sorted)))
                if slots_sorted != expected:
                    continuity_violations += 1
                    break  # 一门课程只要有一天不连续就算违规

        print(f"    [连排连续] 检查完成 | 耗时: {time.time()-start:.2f}s | "
              f"连排课程数: {continuous_courses} | 违规数: {continuity_violations}")
        return continuity_violations


    def quick_calculate(self,
                        solution: List[Tuple],
                        sample_size: int = 100) -> float:
        """
        快速适应度估算（带诊断输出）
        """
        print(f"[Fitness] 快速评估 | 解大小: {len(solution)}")
        start = time.time()

        # 未排课必须精确计算
        unscheduled = self._calc_unscheduled(solution)
        score = 100.0 - unscheduled * self.weights['unscheduled']

        # 教师冲突抽样检查
        if len(solution) > 0:
            sample_start = time.time()
            sample = random.sample(solution, min(sample_size, len(solution)))
            teacher_penalty = sum(
                len([e for e in solution if e[2] == entry[2]]) - 1
                for entry in sample
            ) * len(solution) / sample_size * 0.5
            score -= teacher_penalty * self.weights['teacher_gap']
            print(f"  [快速评估] 抽样耗时: {time.time()-sample_start:.2f}s")

        print(f"[Fitness] 快速评估完成 | 耗时: {time.time()-start:.2f}s | 估算得分: {score:.2f}")
        return score

    # ------------------- 各约束具体实现（添加详细日志） -------------------
    def _calc_unscheduled(self, solution: List[Tuple]) -> int:
        """计算未排课程数（带缓存）"""
        scheduled = {e[0] for e in solution}
        unscheduled = len([c for c in self.courses if c.uid not in scheduled])
        print(f"    [未排课] 已排: {len(scheduled)} | 未排: {unscheduled}")
        return unscheduled

    def _calc_teacher_conflicts(self, solution: List[Tuple]) -> float:
        """计算教师时间冲突（带详细统计）"""
        print("    [教师冲突] 开始分析教师时间表...")
        start = time.time()

        teacher_schedule = defaultdict(list)
        for entry in solution:
            teacher_schedule[entry[2]].append((entry[3], entry[4], entry[5]))

        total_penalty = 0
        teacher_stats = []

        for teacher, slots in teacher_schedule.items():
            day_slots = defaultdict(list)
            for week, day, slot in slots:
                day_slots[(week, day)].append(slot)

            day_penalty = 0
            for day, slots in day_slots.items():
                slots_sorted = sorted(slots)
                for i in range(1, len(slots_sorted)):
                    gap = slots_sorted[i] - slots_sorted[i-1] - 1
                    if gap > 0:
                        day_penalty += gap

            if day_penalty > 0:
                teacher_stats.append((teacher, day_penalty))
            total_penalty += day_penalty

        # 输出冲突最多的3个教师
        if teacher_stats:
            top3 = sorted(teacher_stats, key=lambda x: x[1], reverse=True)[:3]
            print(f"    [教师冲突] 最忙教师: {', '.join(f'{t[0]}({t[1]})' for t in top3)}")

        print(f"    [教师冲突] 分析完成 | 耗时: {time.time()-start:.2f}s | 总冲突值: {total_penalty}")
        return total_penalty

    def _calc_room_utilization(self, solution: List[Tuple]) -> float:
        """计算教室利用率方差（带统计）"""
        print("    [教室利用] 开始分析教室使用情况...")
        start = time.time()

        room_usage = defaultdict(int)
        for entry in solution:
            room_usage[entry[1]] += 1

        if not room_usage:
            return 0

        avg_usage = sum(room_usage.values()) / len(room_usage)
        penalty = sum((u - avg_usage)**2 for u in room_usage.values()) / len(room_usage)

        # 输出使用率最高和最低的教室
        if room_usage:
            sorted_rooms = sorted(room_usage.items(), key=lambda x: x[1])
            min_use = sorted_rooms[0]
            max_use = sorted_rooms[-1]
            print(f"    [教室利用] 最少使用: {min_use[0]}({min_use[1]}) | "
                  f"最多使用: {max_use[0]}({max_use[1]}) | 平均: {avg_usage:.1f}")

        print(f"    [教室利用] 分析完成 | 耗时: {time.time()-start:.2f}s | 不均衡值: {penalty:.2f}")
        return penalty

    def _calc_student_load(self, solution: List[Tuple]) -> float:

        """标准化学生负荷计算"""
        print("    [学生负荷] 开始分析学生课程负荷...")
        start = time.time()
        if not solution:
            return 0
        # 检查popularity值
        popularities = [getattr(self.course_dict[e[0]], 'popularity', 1) for e in solution]
        print(f"学生人数统计 - 平均: {np.mean(popularities):.1f}, 最大: {max(popularities)}")

        daily_load = defaultdict(int)
        for entry in solution:
            course = self.course_dict[entry[0]]
            daily_load[(entry[3], entry[4])] += getattr(course, 'popularity', 1)

        if not daily_load:
            return 0

        # 标准化处理（避免数值过大）
        loads = np.array(list(daily_load.values()))
        normalized_loads = (loads - np.min(loads)) / (np.max(loads) - np.min(loads) + 1e-6)
        penalty = float(np.var(normalized_loads))  # 计算标准化后的方差

        print(f"    [学生负荷] 分析完成 | 耗时: {time.time()-start:.2f}s | "
              f"标准化不均衡值: {penalty:.4f}")
        return penalty

    def _calc_continuity(self, solution: List[Tuple]) -> int:
        """检查连排课程连续性（带统计）"""
        print("    [连排连续] 开始检查连排课程...")
        start = time.time()

        continuity_violations = 0
        continuous_courses = 0

        for entry in solution:
            course = self.course_dict[entry[0]]
            if getattr(course, 'continuous', 1) > 1:
                continuous_courses += 1
                same_day = [
                    e for e in solution
                    if e[0] == entry[0] and e[3] == entry[3] and e[4] == entry[4]
                ]
                slots = sorted([e[5] for e in same_day])
                expected = list(range(slots[0], slots[0] + len(slots)))
                if slots != expected:
                    continuity_violations += 1

        print(f"    [连排连续] 检查完成 | 耗时: {time.time()-start:.2f}s | "
              f"连排课程数: {continuous_courses} | 违规数: {continuity_violations}")
        return continuity_violations