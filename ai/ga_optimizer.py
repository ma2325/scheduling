import concurrent
import random
import math
from typing import List, Dict, Tuple, Set, Any
from collections import defaultdict
import time
import copy
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from inheritance.fitness_calculator import FitnessCalculator
#初始化约10s
#评估种群太慢
class GeneticCourseScheduler:
    """基于遗传算法的排课优化器（完整方法版）"""

    def __init__(self, initial_solution: List[Tuple], unscheduled: List, courses: List, rooms: List):
        """
        初始化遗传算法优化器
        :param initial_solution: CSP求解器的初始解
        :param unscheduled: 未安排的课程列表
        :param courses: 所有课程列表
        :param rooms: 所有教室列表
        """
        self.initial_solution = initial_solution
        self.unscheduled = unscheduled
        self.courses = courses
        self.rooms = rooms
        self.course_dict = {c.uid: c for c in courses}
        self.room_dict = {r.rid: r for r in rooms}
        self.log = []

        # 遗传算法参数
        self.population_size = 50
        self.elite_size = 5
        self.mutation_rate = 0.2
        self.generations = 100
        self.tournament_size = 3

        # 软约束权重
        self.weights = {
            'teacher_gap': 0.0,      # 教师课程间隔
            'room_utilization': 0.0, # 教室利用率均衡
            'student_load': 0.00,     # 学生每日课程负荷
            'continuity': 0.0,       # 连排课程连续性
            'unscheduled': 100.0      # 未安排课程的惩罚
        }

        # 排课规则常量
        self.CONTINUOUS_SLOT_RULES = {
            2: [1, 3, 5, 7],  # 两节连排允许的开始节次
            4: [1, 3, 5],     # 四节连排允许的开始节次
        }
        self.WEEKS_IN_SEMESTER = 20
        self.DAYS_PER_WEEK = 5
        self.SLOTS_PER_DAY = 8
        self.fitness_calc = FitnessCalculator(
            weights=self.weights,
            courses=courses,
            rooms=rooms
        )
        self.active_constraints = set(self.weights.keys())
        self.current_generation = 0  # 初始化当前代数
        self.best_solution = None    # 记录最优解
        self.best_fitness = -float('inf')  # 记录最佳适应度

    def set_active_constraints(self, constraints: List[str]):
        """设置当前启用的约束"""
        self.active_constraints = set(constraints)
#
    def _get_unscheduled(self, solution: List[Tuple]) -> List[Any]:
        """获取未安排的课程"""
        scheduled_courses = {e[0] for e in solution}
        return [c for c in self.courses if c.uid not in scheduled_courses]
#
    def _generate_domains(self, course) -> List[List[Tuple[int, int, int]]]:
        """生成课程的有效时间模式候选域"""
        patterns = []
        continuous = getattr(course, 'continuous', 1)
        total_lessons = course.total_hours
        total_weeks = sum(end - start + 1 for start, end, _ in course.time_slots)
        lessons_per_week = total_lessons / total_weeks

        # 连排课程模式生成
        if continuous > 1:
            allowed_starts = self.CONTINUOUS_SLOT_RULES.get(continuous, [])
            groups_per_week = int(lessons_per_week / continuous)

            for day in random.sample(range(1, self.DAYS_PER_WEEK + 1), groups_per_week):
                for start in allowed_starts:
                    if start + continuous - 1 <= self.SLOTS_PER_DAY:
                        patterns.append([(day, start, continuous)])
        # 非连排课程模式生成
        else:
            days = random.sample(range(1, self.DAYS_PER_WEEK + 1), int(lessons_per_week))
            patterns.append([(day, 1, 1) for day in days])

        return patterns
#
    def _find_compatible_room(self, course, pattern, solution) -> Any:
        """三级教室匹配策略"""
        # 策略1: 固定教室优先
        if getattr(course, 'fixedroom', None):
            fixed_room = next((r for r in self.rooms if r.rname == course.fixedroom), None)
            if fixed_room and self._check_availability(fixed_room, course, pattern, solution):
                return fixed_room

        # 策略2: 按类型匹配
        room_type = getattr(course, 'fixedroomtype', '教室')
        candidates = [r for r in self.rooms
                      if r.rtype == room_type and r.rcapacity >= getattr(course, 'popularity', 0)]

        # 策略3: 若无匹配类型，选择容量足够的任意教室
        if not candidates:
            candidates = [r for r in self.rooms
                          if r.rcapacity >= getattr(course, 'popularity', 0)]

        candidates.sort(key=lambda r: abs(r.rcapacity - getattr(course, 'popularity', 0)))

        for room in candidates[:10]:  # 限制检查数量
            if self._check_availability(room, course, pattern, solution):
                return room
        return None
#
    def _assign_course(self, solution, course, pattern, room):
        """将课程安排添加到解决方案"""
        slots = self._expand_pattern(course, pattern)
        solution.extend(
            (course.uid, room.rid, getattr(course, 'teacherid', ''),
             week, day, slot
             ) for week, day, slot in slots
        )

    def _expand_pattern(self, course, pattern) -> List[Tuple[int, int, int]]:
        """将周模式扩展到具体的(周, 天, 节)时间点"""
        slots = []
        for start_week, end_week, _ in getattr(course, 'time_slots', [(1, self.WEEKS_IN_SEMESTER, 1)]):
            for week in range(start_week, end_week + 1):
                for day, start, length in pattern:
                    slots.extend((week, day, start + offset) for offset in range(length))
        return slots

    def _check_availability(self, room, course, pattern, solution) -> bool:
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

    def _get_course_weeks(self, course) -> Set[int]:
        """获取课程的所有教学周"""
        weeks = set()
        for start, end, _ in getattr(course, 'time_slots', [(1, self.WEEKS_IN_SEMESTER, 1)]):
            weeks.update(range(start, end + 1))
        return weeks

    def _initialize_population(self) -> List[List[Tuple]]:
        """初始化种群（优化版）"""
        population = []
        total = self.population_size

        # 策略1：添加初始解
        self._log(f"初始化个体 1/{total}")
        population.append(copy.deepcopy(self.initial_solution))

        # 策略2：随机安排未排课程
        for i in range(1, total):
            self._log(f"初始化个体 {i+1}/{total}")
            individual = self._create_individual()
            population.append(individual)

        return population



    def _tournament_selection(self, population: List[List[Tuple]]) -> List[Tuple]:
        """锦标赛选择"""
        tournament = random.sample(population, self.tournament_size)
        best = max(tournament, key=lambda x: self._fitness(x))
        return best
#
    def _crossover(self, parent1: List[Tuple], parent2: List[Tuple]) -> List[Tuple]:
        """交叉操作"""
        child = []
        courses1 = {e[0] for e in parent1}
        courses2 = {e[0] for e in parent2}
        common_courses = courses1 & courses2

        # 对于共同课程，随机选择一个父代的安排
        for course_uid in common_courses:
            if random.random() < 0.5:
                child.extend([e for e in parent1 if e[0] == course_uid])
        else:
            child.extend([e for e in parent2 if e[0] == course_uid])

        # 添加非共同课程
        for course_uid in (courses1 - common_courses):
            child.extend([e for e in parent1 if e[0] == course_uid])

        for course_uid in (courses2 - common_courses):
            child.extend([e for e in parent2 if e[0] == course_uid])

        return child
#
    def _repair(self, individual):
        """专门修复未排课问题的算子"""
        repaired = copy.deepcopy(individual)
        scheduled_courses = {e[0] for e in repaired}

        # 按课程优先级排序（课时多的优先）
        unscheduled = sorted(
            [c for c in self.courses if c.uid not in scheduled_courses],
            key=lambda x: x.total_hours,
            reverse=True
        )

        for course in unscheduled[:10]:  # 每次尝试修复10门
            domains = self._generate_domains(course)
            for pattern in domains:
                room = self._find_compatible_room(course, pattern, repaired)
                if room:
                    self._assign_course(repaired, course, pattern, room)
                    break

        return repaired
#
    def _mutate(self, individual: List[Tuple]) -> List[Tuple]:
        # 选择未排课程中优先级最高的5门
        unscheduled = sorted(
            self._get_unscheduled(individual),
            key=lambda c: c.total_hours,
            reverse=True
        )[:10]
        for course in unscheduled:
            domains = self._generate_domains(course)
            for pattern in domains:
                room = self._find_compatible_room(course, pattern, individual)
                if room:
                    self._assign_course(individual, course, pattern, room)
                    break
        return individual
#
    def _fitness(self, solution: List[Tuple]) -> float:
        """完整适应度计算"""
        score, _ = self.fitness_calc.calculate(solution)
        return score
#
    def _quick_fitness(self, solution):
        """适配原有快速评估接口"""
        return self.fitness_calc.quick_calculate(solution)
    def _print_progress(self, current, total, prefix=""):
        """进度条显示"""
        bar_len = 50
        filled_len = int(round(bar_len * current / float(total)))
        bar = '█' * filled_len + '-' * (bar_len - filled_len)
        print(f'\r{prefix} |{bar}| {current}/{total}', end="", flush=True)
        if current == total:
            print()
    def _print_population_stats(self, population: List[List[Tuple]], title: str):
        """最终优化版种群统计"""
        print(f"\n[{title} 统计]")
        total = len(population)
        stats = []

        # 并行计算（可选）
        for i in range(0, total, 5):  # 分批处理减少内存压力
            batch = population[i:i+5]
            self._print_progress(i, total, "计算中")

            for ind in batch:
                # 使用集合加速查询
                scheduled = {e[0] for e in ind}
                unscheduled = [c.uid for c in self.courses if c.uid not in scheduled]

                # 关键优化：并行计算
                fitness = self._quick_fitness(ind, len(scheduled), unscheduled)
                stats.append({
                    'individual': ind,
                    'fitness': fitness,
                    'scheduled': len(scheduled),
                    'unscheduled': len(unscheduled)
                })

        # 统计结果
        fitnesses = [s['fitness'] for s in stats]
        unscheduled_counts = [s['unscheduled'] for s in stats]

        print(f"适应度范围: {min(fitnesses):.1f}-{max(fitnesses):.1f}")
        print(f"未安排课程: {min(unscheduled_counts)}-{max(unscheduled_counts)}")

        # Top3展示
        top3 = sorted(stats, key=lambda x: x['fitness'], reverse=True)[:3]
        for i, stat in enumerate(top3):
            print(f"Top {i+1}: 适应度={stat['fitness']:.1f} | "
                  f"安排={stat['scheduled']} | "
                  f"未安排={stat['unscheduled']}")

        return stats  # 返回详细数据供后续使用

    def _report_stats(self, solution, unscheduled, elapsed):
        """输出统计报告"""
        scheduled_courses = len({e[0] for e in solution})
        total_courses = len(self.courses)
        fitness = self._fitness(solution)

        print("\n=== 优化结果 ===")
        print(f"优化用时: {elapsed:.2f}秒")
        print(f"适应度得分: {fitness:.2f}")
        print(f"已安排课程: {scheduled_courses}/{total_courses}")
        print(f"未安排课程: {len(unscheduled)}")

        if unscheduled:
            print("未安排课程列表:")
            for course in unscheduled:
                print(f"  - {course.uid} (周数: {self._get_course_weeks(course)})")
#
    def optimize(self) -> Tuple[List[Tuple], List[Any]]:
        """主优化流程"""
        self.current_generation = 0
        self.best_solution = None
        self.best_fitness = -float('inf')

        self._log("=== 优化开始 ===")
        start_time = time.time()

        # 初始化种群
        self._log("开始初始化种群...")
        population = self._initialize_population()
        self._log(f"种群初始化完成，共{len(population)}个个体")

        self._evaluate_population(population)
        self._log("初始种群评估完成")

        # 进化循环
        for gen in range(self.generations):
            self.current_generation = gen + 1
            self._log(f"开始第{gen+1}代进化...")

            population = self._run_generation(population)
            self._log(f"第{gen+1}代进化完成")

            # 每10代输出详细统计
            if gen % 10 == 0 or gen == self.generations - 1:
                self._report_generation_stats(population, gen)

        return self.best_solution, self._get_unscheduled(self.best_solution)
    def _run_generation(self, population: List[List[Tuple]]) -> List[List[Tuple]]:
        """执行单代进化（带详细诊断输出）"""
        print(f"\n[Gen {self.current_generation}] 开始执行单代进化...")
        start_time = time.time()

        # 1. 选择
        print("  [阶段1] 选择父代...")
        select_start = time.time()
        parents = self._select_parents(population)
        print(f"  选择完成 | 耗时: {time.time()-select_start:.2f}s | 父代数量: {len(parents)}")

        # 2. 交叉
        print("  [阶段2] 交叉操作...")
        crossover_start = time.time()
        offspring = self._crossover_parents(parents)
        print(f"  交叉完成 | 耗时: {time.time()-crossover_start:.2f}s | 后代数量: {len(offspring)}")

        # 3. 变异
        print("  [阶段3] 变异操作...")
        mutate_start = time.time()
        offspring = [self._mutate_with_debug(ind, i) for i, ind in enumerate(offspring)]  # 使用带调试的变异方法
        print(f"  变异完成 | 耗时: {time.time()-mutate_start:.2f}s")

        # 4. 精英保留
        print("  [阶段4] 精英保留...")
        elitism_start = time.time()
        new_pop = self._apply_elitism(population, offspring)
        print(f"  精英保留完成 | 耗时: {time.time()-elitism_start:.2f}s")

        # 5. 修复
        print("  [阶段5] 修复个体...")
        repair_start = time.time()
        new_pop = [self._repair_with_debug(ind, i) for i, ind in enumerate(new_pop)]  # 使用带调试的修复方法
        print(f"  修复完成 | 耗时: {time.time()-repair_start:.2f}s")

        # 6. 评估
        print("  [阶段6] 评估新种群...")
        evaluate_start = time.time()
        self._evaluate_population(new_pop)
        print(f"  评估完成 | 总耗时: {time.time()-start_time:.2f}s")

        return new_pop
    def _initialize_population(self) -> List[List[Tuple]]:
        """初始化种群（优化版）"""
        population = []

        # 策略1：添加初始解
        population.append(copy.deepcopy(self.initial_solution))

        # 策略2：随机安排未排课程
        for _ in range(1, self.population_size):
            individual = self._create_individual()
            population.append(individual)

        return population

    def _create_individual(self) -> List[Tuple]:
        new_ind = copy.deepcopy(self.initial_solution)
        # 按课程优先级（如课时数）降序尝试安排未排课程
        unscheduled_sorted = sorted(
            self.unscheduled,
            key=lambda c: c.total_hours,
            reverse=True
        )
        for course in unscheduled_sorted[:30]:  # 增加尝试数量
            self._try_schedule_course(new_ind, course)
        return new_ind

    def _try_schedule_course(self,
                             solution: List[Tuple],
                             course: Any) -> bool:
        """尝试安排单个课程"""
        domains = self._generate_domains(course)
        for pattern in domains:
            room = self._find_compatible_room(course, pattern, solution)
            if room:
                self._assign_course(solution, course, pattern, room)
                return True
        return False
    def _select_parents(self, population: List[List[Tuple]]) -> List[List[Tuple]]:
        """锦标赛选择"""
        parents = []
        for _ in range(self.population_size - self.elite_size):
            tournament = random.sample(population, self.tournament_size)
            best = max(tournament, key=lambda x: self._quick_fitness(x))
            parents.append(best)
        return parents
    def _mutate_with_debug(self, individual: List[Tuple], idx: int) -> List[Tuple]:
        """带调试输出的变异操作"""
        print(f"\n  开始变异个体 {idx}...")
        original_size = len(individual)
        original_unscheduled = len(self._get_unscheduled(individual))

        try:
            mutated = self._mutate(individual)
            new_size = len(mutated)
            new_unscheduled = len(self._get_unscheduled(mutated))

            print(f"  变异结果 | 原大小: {original_size} | 新大小: {new_size} | "
                  f"原未排课: {original_unscheduled} | 新未排课: {new_unscheduled}")
            return mutated
        except Exception as e:
            print(f"  ⚠️ 变异个体 {idx} 时出错: {str(e)}")
            return individual
    def _repair_with_debug(self, individual: List[Tuple], idx: int) -> List[Tuple]:
        """带调试输出的修复操作"""
        print(f"\n  开始修复个体 {idx}...")
        original_unscheduled = len(self._get_unscheduled(individual))
        start_time = time.time()

        try:
            repaired = self._repair(individual)
            new_unscheduled = len(self._get_unscheduled(repaired))
            elapsed = time.time() - start_time

            print(f"  修复结果 | 耗时: {elapsed:.2f}s | "
                  f"未排课变化: {original_unscheduled} -> {new_unscheduled}")
            return repaired
        except Exception as e:
            print(f"  ⚠️ 修复个体 {idx} 时出错: {str(e)}")
            return individual
    def _crossover_parents(self, parents: List[List[Tuple]]) -> List[List[Tuple]]:
        """生成后代种群"""
        offspring = []
        for i in range(0, len(parents), 2):
            if i+1 < len(parents):
                child = self._crossover(parents[i], parents[i+1])
                offspring.append(child)
        return offspring
    def _apply_elitism(self,
                       old_pop: List[List[Tuple]],
                       new_pop: List[List[Tuple]]) -> List[List[Tuple]]:
        """精英保留策略"""
        combined = old_pop + new_pop
        elites = sorted(
            combined,
            key=lambda x: self._fitness(x),
            reverse=True
        )[:self.elite_size]
        return elites + new_pop[:self.population_size - self.elite_size]
    # ga_optimizer.py
    def _evaluate_population(self, population: List[List[Tuple]]):
        """单线程评估版本"""
        print(f"\n[评估] 开始单线程评估种群（{len(population)}个个体）...")
        start_time = time.time()

        results = []
        for i, ind in enumerate(population):
            print(f"  评估个体 {i+1}/{len(population)}...", end="\r")
            try:
                score, _ = self.fitness_calc.calculate(ind)  # 确保只获取分数部分
                results.append(score)  # 现在只存储分数，而不是元组
            except Exception as e:
                print(f"评估个体 {i} 出错: {str(e)}")
                results.append(-float('inf'))

        # 更新最优解
        best_idx = np.argmax(results)  # 现在results是纯分数列表
        self.best_fitness = results[best_idx]
        self.best_solution = copy.deepcopy(population[best_idx])

        print(f"[评估] 完成 | 最佳分数: {self.best_fitness:.1f} | "
              f"总耗时: {time.time()-start_time:.2f}s")
    def _report_generation_stats(self,
                                 population: List[List[Tuple]],
                                 gen: int):
        """输出代统计信息"""
        # 快速评估全种群
        with ThreadPoolExecutor() as executor:
            quick_scores = list(executor.map(
                self._quick_fitness,
                population
            ))

        # 精确评估最优个体
        best_idx = np.argmax(quick_scores)
        best_score, metrics = self.fitness_calc.calculate(population[best_idx])

        print(f"\n=== 代 {gen} 统计 ===")
        print(f"适应度范围: {min(quick_scores):.1f}-{max(quick_scores):.1f}")
        print(f"最优解详情:")
        print(f"  - 未排课: {metrics.get('unscheduled', 0)}")
        print(f"  - 教师冲突: {metrics.get('teacher_gap', 0):.1f}")
        print(f"  - 教室利用率: {metrics.get('room_utilization', 0):.2f}")
    def _log(self, message: str):
        """带时间戳的日志"""
        print(f"[Gen {self.current_generation}] {message}")
