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

    def _build_lookups(self):
        """预构建加速查询的数据结构"""
        print("[Fitness] 构建查询索引...")
        start = time.time()
        self.course_dict = {c.uid: c for c in self.courses}
        self.room_dict = {r.rid: r for r in self.rooms}
        self.course_ids = [c.uid for c in self.courses]  # 用于快速抽样
        print(f"[Fitness] 索引构建完成 | 耗时: {time.time()-start:.2f}s")

    def calculate(self,
                  solution: List[Tuple],
                  active_constraints: Set[str] = None) -> Tuple[float, Dict]:
        """
        完整适应度计算（带详细诊断输出）
        :return: (适应度得分, 各分项得分详情)
        """
        print(f"\n[Fitness] 开始适应度计算 | 解大小: {len(solution)}")
        total_start = time.time()

        if active_constraints is None:
            active_constraints = set(self.weights.keys())

        metrics = {}
        score = 100.0  # 基础分
        calc_details = []  # 记录各约束计算耗时

        # 1. 未排课惩罚（必须精确计算）
        if 'unscheduled' in active_constraints:
            start = time.time()
            unscheduled = self._calc_unscheduled(solution)
            elapsed = time.time() - start
            calc_details.append(f"未排课: {elapsed:.2f}s")
            metrics['unscheduled'] = unscheduled
            score -= unscheduled * self.weights['unscheduled']
            print(f"  [未排课] 耗时: {elapsed:.2f}s | 未排课程数: {unscheduled}")

        # 2. 教师冲突检查
        if 'teacher_gap' in active_constraints:
            start = time.time()
            teacher_gap = self._calc_teacher_conflicts(solution)
            elapsed = time.time() - start
            calc_details.append(f"教师冲突: {elapsed:.2f}s")
            metrics['teacher_gap'] = teacher_gap
            score -= teacher_gap * self.weights['teacher_gap']
            print(f"  [教师冲突] 耗时: {elapsed:.2f}s | 冲突值: {teacher_gap}")

        # 3. 教室利用率
        if 'room_utilization' in active_constraints:
            start = time.time()
            room_penalty = self._calc_room_utilization(solution)
            elapsed = time.time() - start
            calc_details.append(f"教室利用: {elapsed:.2f}s")
            metrics['room_utilization'] = room_penalty
            score -= room_penalty * self.weights['room_utilization']
            print(f"  [教室利用] 耗时: {elapsed:.2f}s | 不均衡值: {room_penalty:.2f}")

        # 4. 学生负荷
        if 'student_load' in active_constraints:
            start = time.time()
            student_penalty = self._calc_student_load(solution)
            elapsed = time.time() - start
            calc_details.append(f"学生负荷: {elapsed:.2f}s")
            metrics['student_load'] = student_penalty
            score -= student_penalty * self.weights['student_load']
            print(f"  [学生负荷] 耗时: {elapsed:.2f}s | 不均衡值: {student_penalty:.2f}")

        # 5. 连排连续性
        if 'continuity' in active_constraints:
            start = time.time()
            continuity_penalty = self._calc_continuity(solution)
            elapsed = time.time() - start
            calc_details.append(f"连排连续: {elapsed:.2f}s")
            metrics['continuity'] = continuity_penalty
            score -= continuity_penalty * self.weights['continuity']
            print(f"  [连排连续] 耗时: {elapsed:.2f}s | 违规数: {continuity_penalty}")

        total_time = time.time() - total_start
        print(f"[Fitness] 计算完成 | 总耗时: {total_time:.2f}s | 最终得分: {score:.2f}")
        print(f"  各分项耗时: {', '.join(calc_details)}")

        return score, metrics

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
        """计算学生每日负荷方差（带统计）"""
        print("    [学生负荷] 开始分析学生课程负荷...")
        start = time.time()

        daily_load = defaultdict(int)
        for entry in solution:
            course = self.course_dict[entry[0]]
            daily_load[(entry[3], entry[4])] += getattr(course, 'popularity', 1)

        if not daily_load:
            return 0

        avg_load = sum(daily_load.values()) / len(daily_load)
        penalty = sum((l - avg_load)**2 for l in daily_load.values()) / len(daily_load)

        # 输出负荷最高和最低的天
        if daily_load:
            sorted_days = sorted(daily_load.items(), key=lambda x: x[1])
            min_day = sorted_days[0]
            max_day = sorted_days[-1]
            print(f"    [学生负荷] 最轻松: 第{min_day[0][0]}周周{min_day[0][1]}({min_day[1]}) | "
                  f"最繁忙: 第{max_day[0][0]}周周{max_day[0][1]}({max_day[1]})")

        print(f"    [学生负荷] 分析完成 | 耗时: {time.time()-start:.2f}s | 不均衡值: {penalty:.2f}")
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