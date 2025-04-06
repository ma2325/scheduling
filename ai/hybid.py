import traceback
import random
import time
from csp_solver import CSPScheduler
from collections import defaultdict
# 文件顶部添加
CONTINUOUS_SLOT_RULES = {
    2: [1, 3, 5, 7],  # 两节连排
    4: [1, 3, 5]       # 四节连排
}
DAYS_PER_WEEK = 5
SLOTS_PER_DAY = 8
WEEKS_IN_SEMESTER = 20

class HybridScheduler(CSPScheduler):
    def __init__(self, courses, rooms):
        super().__init__(courses, rooms)
        # GA参数优化
        self.population_size = 30    # 减少种群规模
        self.generations = 50        # 减少迭代次数
        self.mutation_rate = 0.25
        self.elitism_count = 2
        self.batch_size = 25        # 每次处理课程数

    def solve(self):
        """分批次处理未排课程"""
        scheduled, unscheduled = super().solve()
        total_unscheduled = len(unscheduled)
        print(f"\n=== 开始混合优化 ===")
        print(f"初始未排课程: {total_unscheduled} 门")

        # 分批次处理
        for batch_idx in range(0, len(unscheduled), self.batch_size):
            batch = unscheduled[batch_idx:batch_idx+self.batch_size]
            print(f"\n=== 处理批次 {batch_idx//self.batch_size+1} ==="
                  f" | 课程数: {len(batch)} ===")

            scheduled = self.process_batch(scheduled, batch)

        return scheduled, []

    def process_batch(self, base_schedule, batch):
        base = list(base_schedule)
        print(f"\n=== 开始处理批次 | 待排课程: {len(batch)}门 ===")
        print(f"初始课表长度: {len(base)}条记录")

        # 初始化种群
        population = self.initialize_population(base, batch)

        for gen in range(self.generations):
            start_time = time.time()
            print(f"\n▶▶ 第 {gen+1}/{self.generations} 代 ▶▶")

            # ------------------- 评估阶段 -------------------
            # 评估所有个体并更新属性
            evaluated_pop = []
            for idx, ind in enumerate(population):
                # 执行评估并合并结果到个体
                eval_result = self.evaluate(ind)
                ind.update(eval_result)  # 关键点：将评估结果合并到原始个体

                # 打印个体状态
                print(f"个体{idx+1}: "
                      f"适应度={ind.get('fitness', 'N/A')} | "
                      f"排入课程={ind.get('scheduled_count', 0)} | "
                      f"冲突={ind.get('total_conflicts', 0)}")

                evaluated_pop.append(ind)

            # 按适应度排序
            evaluated_pop.sort(key=lambda x: x['fitness'], reverse=True)
            elites = evaluated_pop[:self.elitism_count]

            # 打印精英信息
            avg_fitness = sum(ind['fitness'] for ind in evaluated_pop) / len(evaluated_pop)
            print(f"\n★ 精英个体 | 最高适应度: {elites[0]['fitness']} | 平均适应度: {avg_fitness:.1f}")

            # ------------------- 生成新一代 -------------------
            new_pop = elites.copy()
            while len(new_pop) < self.population_size:
                # 选择父代
                p1, p2 = self.select_parents(evaluated_pop)  # 注意此处使用 evaluated_pop

                # 交叉操作
                child = self.crossover(p1, p2)

                # 变异操作
                if random.random() < self.mutation_rate:
                    print(f"\n⚡ 对个体{len(new_pop)+1}进行变异...")
                    child = self.mutate(child)

                new_pop.append(child)

            population = new_pop
            time_cost = time.time() - start_time
            print(f"└── 本代耗时: {time_cost:.2f}s")

            # ------------------- 提前终止检测 -------------------
            if elites[0]['fitness'] >= 200 * len(batch):
                print(f"\n🔥 在第{gen+1}代达成完美解，终止优化")
                break

        # 返回最佳解
        best = max(population, key=lambda x: x.get('fitness', -float('inf')))
        print(f"\n✔ 批次处理完成 | 最终适应度: {best['fitness']} | 新增课程: {best['scheduled_count']}")
        return best['full_schedule']

    def initialize_population(self, base, batch):


        population = []
        total_courses = len(batch)

        print(f"\n🌀 初始化种群（{self.population_size}个个体）| 待排课程: {total_courses}门")

        # 遍历每个个体
        for idx in range(self.population_size):
            print(f"\n▹ 生成个体 {idx+1}/{self.population_size}")

            # 初始化个体数据结构
            individual = {
                'base': list(base),  # 基础课表副本
                'full_schedule': list(base),  # 完整课表（初始为基础课表）
                'attempts': [],  # 排课尝试记录
                'scheduled_count': 0,  # 成功排课数计数器
                'total_conflicts': 0  ,# 冲突计数器
                'fitness': -float('inf')  # 新增初始化字段
            }

            # 按课程优先级排序（高优先级先处理）
            sorted_courses = sorted(batch, key=self.calculate_priority, reverse=True)

            # 遍历每个待排课程
            for course_idx, course in enumerate(sorted_courses):
                # 显示进度条
                progress = (course_idx + 1) / total_courses * 100
                print(f"\r  进度: [{ '▊' * int(progress//5) }{ ' ' * (20 - int(progress//5))}] {progress:.1f}%", end='', flush=True)

                # 尝试插入课程
                success, new_slots = self.try_insert(course, individual['full_schedule'])

                # 记录尝试结果
                individual['attempts'].append({
                    'course': course,
                    'scheduled': success,
                    'slots': new_slots if success else []
                })

                # 更新课表和计数器
                if success:
                    individual['full_schedule'].extend(new_slots)
                    individual['scheduled_count'] += 1

            # 统计冲突（用于调试）
            individual['total_conflicts'] = self.count_conflicts(individual['full_schedule'])
            print(f"\n  初始状态 | 排入课程: {individual['scheduled_count']} | 冲突数: {individual['total_conflicts']}")

            population.append(individual)

        return population

    def _generate_all_patterns(self, course):
        """放宽时间模式生成规则"""
        patterns = []
        continuous = getattr(course, 'continuous', 1)

        # 允许所有可能的连排开始时间
        allowed_starts = list(range(1, SLOTS_PER_DAY - continuous + 2))

        # 每天最多尝试3种模式（提高生成效率）
        for day in random.sample(range(1, DAYS_PER_WEEK+1), 3):
            for start in random.sample(allowed_starts, 3):
                if start + continuous - 1 <= SLOTS_PER_DAY:
                    patterns.append([(day, start, continuous)])

        # 补充单节模式
        if continuous == 1:
            for _ in range(5):
                patterns.append([(random.randint(1, DAYS_PER_WEEK),
                                  random.randint(1, SLOTS_PER_DAY), 1)])

        return patterns
    def _find_room_candidates(self, course):
        """放宽教室匹配条件"""
        candidates = []
        min_cap = max(10, int(course.popularity * 0.8))  # 允许容量稍小的教室

        # 1. 优先固定教室（不检查容量）
        if hasattr(course, 'fixedroom'):
            candidates += [r for r in self.rooms if r.rname == course.fixedroom]

        # 2. 匹配类型时放宽容量要求
        room_type = getattr(course, 'fixedroomtype', '普通教室')
        candidates += [r for r in self.rooms
                       if  r.rcapacity >= min_cap]

        # 3. 任意可用教室（容量>=最小要求）
        candidates += [r for r in self.rooms if r.rcapacity >= min_cap]

        # 去重并随机排序
        seen = set()
        return [r for r in candidates if not (r.rid in seen or seen.add(r.rid))]
    def _expand_pattern(self, course, pattern):
        """继承自CSP的周次展开方法"""
        return super()._expand_pattern(course, pattern)
    def try_insert(self, course, existing):
        """改进的插入逻辑：增加随机性"""
        # 随机打乱时间模式和候选教室顺序
        patterns = self._generate_all_patterns(course)
        random.shuffle(patterns)  # 增加随机性

        for pattern in patterns:
            slots = self._expand_pattern(course, pattern)
            rooms = self._find_room_candidates(course)
            random.shuffle(rooms)  # 增加随机性

            for room in rooms:
                if self.is_valid_insertion(course, room, slots, existing):
                    print("OK")
                    return True, [(course.uid, room.rid, course.teacherid, *s) for s in slots]
        return False, []

    def is_valid_insertion(self, course, room, slots, existing):
        """简化冲突检查：仅检查教室硬冲突"""
        occupied = defaultdict(set)
        for entry in existing:
            key = (entry[3], entry[4], entry[5])  # (周,天,节)
            occupied[entry[1]].add(key)  # 教室占用记录

        # 只检查教室时间冲突
        for slot in slots:
            week, day, time = slot
            if (week, day, time) in occupied.get(room.rid, set()):
                return False
        return True

    def evaluate(self, individual):
        """优化适应度函数：优先排课数"""
        scheduled_count = len(set(
            entry[0] for entry in individual['full_schedule']
            if entry[0] in {c.uid for c in self.courses}
        ))

        # 基础分数 = 排课数 * 200（提高权重）
        fitness = scheduled_count * 200

        # 轻度冲突惩罚（原惩罚的1/10）
        fitness -= self.count_conflicts(individual['full_schedule']) * 10

        # 未排课惩罚（仅当完全失败时）
        failed = len([a for a in individual['attempts'] if not a['scheduled']])
        fitness -= failed * 5

        return {
            'fitness': max(fitness, 0),  # 防止负值
            'scheduled_count': scheduled_count,
            'total_conflicts': self.count_conflicts(individual['full_schedule'])}

    def count_conflicts(self, schedule):
        """精确冲突检测：仅检查不同课程间的冲突"""
        conflict_count = 0
        time_slot_map = defaultdict(set)

        for entry in schedule:
            key = (entry[3], entry[4], entry[5])  # (周, 天, 节)
            course_id = entry[0]

            # 同一时间点的不同课程
            if key in time_slot_map:
                # 检查教室冲突
                if entry[1] in {e[1] for e in time_slot_map[key]}:
                    conflict_count += 1
                # 检查教师冲突
                if entry[2] in {e[2] for e in time_slot_map[key]}:
                    conflict_count += 1
            time_slot_map[key].add(entry)

        return conflict_count

    # 遗传操作保持不变，但增加调试输出
    # 在 HybridScheduler 类中添加/替换以下方法
    def select_parents(self, population):
        """改进的轮盘赌选择（增加调试输出）"""
        print(f"\n[选择] 种群适应度范围: {min(p['fitness'] for p in population if 'fitness' in p)}"
              f" ~ {max(p['fitness'] for p in population if 'fitness' in p)}")

        # 以下是原始代码逻辑（保持原有实现）
        valid_pop = [ind for ind in population if 'attempts' in ind and 'fitness' in ind]
        if not valid_pop:
            return random.choice(population), random.choice(population)

        total_fitness = sum(max(ind['fitness'], 0) for ind in valid_pop)
        if total_fitness <= 0:
            return random.choice(valid_pop), random.choice(valid_pop)

        pick1 = random.uniform(0, total_fitness)
        pick2 = random.uniform(0, total_fitness)
        current, parent1, parent2 = 0, None, None

        for ind in valid_pop:
            current += max(ind['fitness'], 0)
            if parent1 is None and current >= pick1:
                parent1 = ind
            if parent2 is None and current >= pick2:
                parent2 = ind
            if parent1 and parent2:
                break

        parent1 = parent1 or valid_pop[0]
        parent2 = parent2 or valid_pop[-1]
        return parent1, parent2

    def mutate(self, individual):
        """变异操作（增加适应度输出）"""
        print(f"[变异] 当前适应度: {individual.get('fitness', '未评估')}")

        # 以下是原始代码逻辑（保持原有实现）
        try:
            mutated = {
                'base': individual.get('base', []).copy(),
                'full_schedule': individual.get('full_schedule', []).copy(),
                'attempts': [a.copy() for a in individual.get('attempts', [])],
                'scheduled_count': individual.get('scheduled_count', 0),
                'total_conflicts': individual.get('total_conflicts', 0),
                'fitness': individual.get('fitness', -float('inf'))
            }

            if not mutated['attempts']:
                return mutated

            idx = random.randint(0, len(mutated['attempts'])-1)
            course = mutated['attempts'][idx]['course']
            new_attempt = self.try_insert(course, mutated['base'])

            if isinstance(new_attempt, dict):
                mutated['attempts'][idx] = new_attempt
            return mutated

        except Exception as e:
            traceback.print_exc()
            return individual
    def crossover(self, parent1, parent2):
        """修复后的交叉操作，确保字段完整性"""
        try:
            # 获取父代数据
            p1_attempts = parent1.get('attempts', [])
            p2_attempts = parent2.get('attempts', [])

            min_len = min(len(p1_attempts), len(p2_attempts))
            if min_len < 2:
                # 均匀交叉策略（当无法生成有效交叉点时）
                child_attempts = []
                for a1, a2 in zip(p1_attempts, p2_attempts):
                    child_attempts.append(random.choice([a1, a2]))
                print("⚠️ 课程数不足，改用均匀交叉")
                crossover_point = 0  # 标记无效交叉点
            else:
                # 生成合法交叉点（范围：1 <= point <= min_len-1）
                crossover_point = random.randint(1, min_len - 1)
                child_attempts = p1_attempts[:crossover_point] + p2_attempts[crossover_point:]

            # 生成子代
            child = {
                'base': parent1.get('base', []).copy(),
                'full_schedule': parent1.get('full_schedule', []).copy(),
                'attempts': p1_attempts[:crossover_point] + p2_attempts[crossover_point:],
                'scheduled_count': 0,  # 需要重新计算
                'total_conflicts': 0,  # 需要重新计算
                'fitness': -float('inf')  # 初始化为无效值
            }
            # 重新计算子代的统计信息
            child['scheduled_count'] = sum(1 for a in child['attempts'] if a['scheduled'])
            child['total_conflicts'] = self.count_conflicts(child['full_schedule'])
            return child
        except Exception as e:
            print(f"交叉失败: {str(e)}")
            return parent1.copy()