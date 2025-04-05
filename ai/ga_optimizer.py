#GA
import random
from collections import defaultdict
from typing import List, Dict, Tuple
import time
from copy import deepcopy

class GAOptimizer:
    def __init__(self, courses, rooms, constraint_checker):
        """
        初始化GA优化器
        :param courses: 课程列表
        :param rooms: 教室列表
        :param constraint_checker: 约束检查器
        """
        self.courses = courses
        self.rooms = rooms
        self.constraint_checker = constraint_checker
        self.course_dict = {c.uid: c for c in courses}
        self.room_dict = {r.rid: r for r in rooms}

        # 遗传算法参数
        self.population_size = 30
        self.max_generations = 50
        self.mutation_rate = 0.15
        self.elitism_ratio = 0.2
        self.tournament_size = 5

        # 添加时间规则常量
        self.WEEKS_IN_SEMESTER = 20
        self.DAYS_PER_WEEK = 5
        self.SLOTS_PER_DAY = 8
        self.CONTINUOUS_SLOT_RULES = {
            2: [1, 3, 5, 7],  # 两节连排允许的开始节次
            4: [1, 3, 5],     # 四节连排允许的开始节次
        }

    def optimize(self, initial_solution):
        """
        基于初始解进行遗传算法优化
        :param initial_solution: CSP生成的初始解
        :return: 优化后的排课方案
        """
        print("\n=== 开始GA优化阶段 ===")

        # 初始化种群（包含初始解）
        population = self.initialize_population(initial_solution)

        # 记录最佳解
        best_individual = max(population, key=self.fitness)
        best_fitness = self.fitness(best_individual)

        # 遗传算法主循环
        for generation in range(self.max_generations):
            start_time = time.time()

            # 选择
            selected = self.tournament_selection(population)

            # 交叉
            offspring = []
            for i in range(0, len(selected), 2):
                if i+1 < len(selected):
                    child1, child2 = self.crossover(selected[i], selected[i+1])
                    offspring.extend([child1, child2])

            # 变异
            mutated_offspring = []
            for child in offspring:
                if random.random() < self.mutation_rate:
                    mutated_offspring.append(self.mutate(child))
                else:
                    mutated_offspring.append(child)

            # 精英保留
            elite_size = int(self.elitism_ratio * self.population_size)
            elites = sorted(population, key=self.fitness, reverse=True)[:elite_size]

            # 生成新一代种群
            population = elites + mutated_offspring
            population = population[:self.population_size]  # 保持种群大小

            # 更新最佳解
            current_best = max(population, key=self.fitness)
            current_fitness = self.fitness(current_best)

            if current_fitness > best_fitness:
                best_individual = deepcopy(current_best)
                best_fitness = current_fitness

            # 打印进度
            print(f"Generation {generation+1}: Best Fitness = {best_fitness:.1f} "
                  f"| Time = {time.time()-start_time:.2f}s")

            # 早停条件
            if generation > 10 and self.fitness(population[0]) - best_fitness < 1:
                break

        print("\n✅ GA优化完成!")
        return best_individual
    def _generate_time_slots(self, course):
        """
        与CSP一致的时间生成逻辑
        返回: [TimeSlot] 列表
        """
        slots = []
        continuous = getattr(course, 'continuous', 1)

        for start_week, end_week, lpw in course.time_slots:
            weeks = list(range(start_week, end_week + 1))
            lessons_per_week = lpw

            # 连排课程处理
            if continuous > 1:
                groups_per_week = lessons_per_week // continuous
                allowed_starts = self.CONTINUOUS_SLOT_RULES.get(continuous, [])

                for week in weeks:
                    # 随机打乱周几的顺序
                    days = list(range(1, self.DAYS_PER_WEEK + 1))
                    random.shuffle(days)

                    for day in days:
                        # 随机选择允许的起始节次
                        for start in random.sample(allowed_starts, len(allowed_starts)):
                            if start + continuous - 1 <= self.SLOTS_PER_DAY:
                                slots.extend([
                                    TimeSlot(week, day, start + i)
                                    for i in range(continuous)
                                ])
                                if len(slots) >= groups_per_week * len(weeks):
                                    return slots
            else:
                # 非连排课程处理
                for week in weeks:
                    # 随机选择不同的天
                    days = random.sample(
                        range(1, self.DAYS_PER_WEEK + 1),
                        min(lessons_per_week, self.DAYS_PER_WEEK)
                    )
                    for day in days:
                        slot = random.randint(1, self.SLOTS_PER_DAY)
                        slots.append(TimeSlot(week, day, slot))
        return slots

    def initialize_population(self, initial_solution):
        """初始化种群，基于初始解生成变体"""
        population = []

        # 确保初始解在种群中
        population.append(initial_solution)

        # 生成变体
        for _ in range(self.population_size - 1):
            # 对初始解进行随机扰动
            individual = self.mutate(initial_solution, mild=True)
            population.append(individual)

        return population

    def fitness(self, individual):
        """
        适应度函数（只考虑软约束，硬约束已在CSP阶段满足）
        分数越高表示解越好
        """
        score = 0

        # 1. 时间分布评分
        time_dist = defaultdict(list)
        for entry in individual:
            cid, _, _, week, day, slot = entry
            time_dist[cid].append((week, day, slot))

        for cid, slots in time_dist.items():
            course = self.course_dict.get(cid)
            if not course:
                continue

            # 周分散奖励
            unique_weeks = len({s[0] for s in slots})
            score += unique_weeks * 5

            # 同天多课惩罚（非连排课程）
            if not hasattr(course, 'continuous') or course.continuous == 1:
                day_counts = defaultdict(int)
                for _, day, _ in slots:
                    day_counts[day] += 1
                for cnt in day_counts.values():
                    if cnt > 1:
                        score -= 20 * (cnt - 1)

        # 2. 教室利用率评分
        for entry in individual:
            cid, rid, _, _, _, _ = entry
            course = self.course_dict.get(cid)
            room = self.room_dict.get(rid)

            if course and room:
                utilization = course.popularity / room.rcapacity
                if 0.7 <= utilization <= 0.9:
                    score += 30
                elif utilization > 0.9:
                    score += 10
                else:
                    score += max(0, 10 * utilization)

        # 3. 上午课奖励（1-4节）
        morning_slots = sum(1 for entry in individual if entry[5] <= 4)
        score += morning_slots * 3

        return score

    def tournament_selection(self, population):
        """锦标赛选择"""
        selected = []

        for _ in range(len(population)):
            # 随机选择参赛者
            contestants = random.sample(population, self.tournament_size)
            # 选择适应度最高的
            winner = max(contestants, key=self.fitness)
            selected.append(winner)

        return selected

    def crossover(self, parent1, parent2):
        """基于课程的分组交叉"""
        # 按课程分组
        p1_courses = defaultdict(list)
        p2_courses = defaultdict(list)

        for entry in parent1:
            p1_courses[entry[0]].append(entry)
        for entry in parent2:
            p2_courses[entry[0]].append(entry)

        child1, child2 = [], []
        all_cids = list(set(p1_courses.keys()).union(p2_courses.keys()))

        for cid in all_cids:
            # 随机选择从哪个父代继承
            if random.random() < 0.5:
                child1.extend(p1_courses.get(cid, []))
                child2.extend(p2_courses.get(cid, []))
            else:
                child1.extend(p2_courses.get(cid, []))
                child2.extend(p1_courses.get(cid, []))

        return child1, child2

    def mutate(self, individual, mild=False):
        """改进后的变异操作 (与CSP时间生成一致)"""
        mutated = deepcopy(individual)
        course_groups = defaultdict(list)

        # 按课程分组
        for i, entry in enumerate(mutated):
            if entry:
                course_groups[entry[0]].append((i, entry))

        # 随机选择要变异的课程
        for cid, entries in course_groups.items():
            if random.random() > self.mutation_rate and not mild:
                continue

            course = self.course_dict.get(cid)
            if not course:
                continue

            # 连排课程处理
            if hasattr(course, 'continuous') and course.continuous > 1:
                # 1. 删除原有安排
                for i, _ in entries:
                    mutated[i] = None

                # 2. 使用与CSP一致的时间生成
                new_slots = self._generate_continuous_slots(course)
                if not new_slots:
                    continue

                # 3. 选择教室 (优先原教室)
                original_room = entries[0][1][1] if entries else None
                room = self.room_dict.get(original_room) or \
                       self._select_room_for_course(course)

                if not room:
                    continue

                # 4. 添加新安排
                new_entries = [
                    (cid, room.rid, course.teacherid, ts.week, ts.day, ts.slot)
                    for ts in new_slots
                ]

                # 插入到空位
                empty_indices = [i for i, x in enumerate(mutated) if x is None]
                for i, entry in zip(empty_indices[:len(new_entries)], new_entries):
                    mutated[i] = entry

            # 非连排课程处理
            else:
                for i, entry in entries:
                    if mild:  # 温和变异只调整时间
                        new_slot = self._generate_single_slot(course)
                        if new_slot:
                            mutated[i] = (
                                cid, entry[1], entry[2],
                                new_slot.week, new_slot.day, new_slot.slot
                            )
                    else:  # 强力变异可能更换教室
                        if random.random() < 0.3:
                            room = self._select_room_for_course(course)
                            if room:
                                mutated[i] = (
                                    cid, room.rid, entry[2],
                                    entry[3], entry[4], entry[5]
                                )

        # 移除None并保持顺序
        mutated = [x for x in mutated if x is not None]

        # 确保满足硬约束
        if not self.constraint_checker.check_hard_constraints(mutated):
            return individual  # 变异失败则返回原个体

        return mutated

    def _generate_continuous_slots(self, course):
        """为连排课程生成时间槽 (与CSP一致)"""
        continuous = course.continuous
        allowed_starts = self.CONTINUOUS_SLOT_RULES.get(continuous, [])

        # 获取课程的教学周范围
        weeks = []
        for start, end, _ in course.time_slots:
            weeks.extend(range(start, end + 1))

        # 随机选择一周
        week = random.choice(weeks)

        # 随机选择一天和起始节次
        day = random.randint(1, self.DAYS_PER_WEEK)
        start = random.choice(allowed_starts)

        # 生成连续时间段
        if start + continuous - 1 <= self.SLOTS_PER_DAY:
            return [TimeSlot(week, day, start + i) for i in range(continuous)]
        return None


    def _generate_single_slot(self, course):
        """为单节课程生成时间槽 (与CSP一致)"""
        # 获取课程的教学周范围
        weeks = []
        for start, end, _ in course.time_slots:
            weeks.extend(range(start, end + 1))

        week = random.choice(weeks)
        day = random.randint(1, self.DAYS_PER_WEEK)

        # 优先上午时段 (1-4节)
        if random.random() < 0.7:  # 70%概率选择上午
            slot = random.randint(1, 4)
        else:
            slot = random.randint(5, self.SLOTS_PER_DAY)

        return TimeSlot(week, day, slot)


    def _select_room_for_course(self, course):
        """为课程选择教室"""
        # 固定教室优先
        if hasattr(course, 'fixedroom') and course.fixedroom:
            room = next((r for r in self.rooms if r.rname == course.fixedroom), None)
            if room:
                return room

        # 按类型匹配
        candidates = []
        if hasattr(course, 'fixedroomtype') and course.fixedroomtype:
            candidates = [r for r in self.rooms if r.rtype == course.fixedroomtype]

        # 如果没有匹配类型，选择容量足够的任意教室
        if not candidates:
            candidates = [r for r in self.rooms if r.rcapacity >= course.popularity]

        if candidates:
            # 按容量匹配度排序
            candidates.sort(key=lambda r: abs(r.rcapacity - course.popularity))
            return candidates[0]

        return None

class TimeSlot:
    """时间槽表示"""
    def __init__(self, week, day, slot):
        self.week = week
        self.day = day
        self.slot = slot