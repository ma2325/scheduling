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
    def __init__(self, courses, rooms, soft_constraints=None):
        super().__init__(courses, rooms,soft_constraints=soft_constraints)
        # GA参数优化
        self.population_size = 3    # 减少种群规模
        self.generations = 10        # 减少迭代次数
        self.mutation_rate = 0.3
        self.elitism_count = 3
        self.batch_size = 50        # 每次处理课程数

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
        best_fitness = -float('inf')
        no_improve_count = 0

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
            current_best = elites[0]['fitness']
            if current_best > best_fitness:
                best_fitness = current_best
                no_improve_count = 0
            else:
                no_improve_count += 1

            # 新终止条件：连续3代无改进 或 达到95%排课率
            terminate_conditions = [
                no_improve_count >= 3,
                (elites[0]['scheduled_count'] / len(batch)) >= 0.95
            ]

            if any(terminate_conditions):
                print(f"\n🔥 在第{gen+1}代终止优化（连续无改进：{no_improve_count}代，排课率：{(elites[0]['scheduled_count']/len(batch)):.1%}）")
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
                    # 在 individual['full_schedule'].extend(new_slots) 后添加
                    print(f"当前课表长度: {len(individual['full_schedule'])}, 最新插入: {new_slots[0] if new_slots else '无'}")
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

        # 1. 优先固定教室（不检查容量）
        if hasattr(course, 'fixedroom'):
            candidates += [r for r in self.rooms if r.rname == course.fixedroom]

        # 2. 匹配类型时放宽容量要求
        room_type = getattr(course, 'fixedroomtype', '普通教室')
        candidates += [r for r in self.rooms
                       if  r.rcapacity >= course.popularity and r.rtype == room_type]

        # 去重并随机排序
        seen = set()
        return [r for r in candidates if not (r.rid in seen or seen.add(r.rid))]
    def _expand_pattern(self, course, pattern):
        """继承自CSP的周次展开方法"""
        return super()._expand_pattern(course, pattern)
    def try_insert(self, course, existing):
        """尝试插入课程（返回的记录中使用 teacher_uid）"""
        patterns = self._generate_all_patterns(course)
        random.shuffle(patterns)

        for pattern in patterns:
            slots = self._expand_pattern(course, pattern)
            rooms = self._find_room_candidates(course)
            random.shuffle(rooms)

            for room in rooms:
                if self.is_valid_insertion(course, room, slots, existing):
                    # 使用 teacher_uid 替代 teacherid
                    print(f"即将插入: 课程={course.uid}, 教师={course.teacher_uid}, 教室={room.rid}, 时间={slots}")
                    return True, [(
                        course.uid,      # 课程唯一ID
                        room.rid,        # 教室ID
                        course.teacher_uid,  # 教师唯一ID（原为 teacherid）
                        *slot            # 时间槽 (周, 天, 节)
                    ) for slot in slots]

        return False, []  # 插入失败

    def is_valid_insertion(self, course, room, slots, existing):
        """检查插入是否有效（使用 teacher_uid）"""
        occupied = defaultdict(lambda: {'rooms': set(), 'teachers': set()})

        # 统计已有占用的时间槽
        for entry in existing:
            key = (entry[3], entry[4], entry[5])  # (周, 天, 节)
            occupied[key]['rooms'].add(entry[1])    # 教室占用
            occupied[key]['teachers'].add(entry[2]) # 教师占用（使用 teacher_uid）

        # 检查新插入的槽位
        for slot in slots:
            week, day, time = slot
            key = (week, day, time)

            # 检查教室冲突
            if room.rid in occupied[key]['rooms']:
                return False

            # 检查教师冲突（使用 teacher_uid）
            if course.teacher_uid in occupied[key]['teachers']:
                return False

        return True  # 无冲突


    def evaluate(self, individual):
        """优化后的适应度函数：区分冲突类型并加权"""
        # 统计详细冲突类型
        conflicts = self.count_conflicts(individual['full_schedule'])

        # 计算基础排课分数（保持高权重）
        scheduled_count = individual['scheduled_count']
        base_score = scheduled_count * 200

        # 冲突惩罚（教师冲突 ×10，教室冲突 ×5）
        penalty = (
                conflicts['teacher'] * 10 +
                conflicts['room'] * 5 +
                conflicts['continuous'] * 1  # 时间不连排惩罚
        )

        # 未排课程惩罚（适度降低）
        failed = len([a for a in individual['attempts'] if not a['scheduled']])

        # 最终适应度计算
        fitness = base_score - penalty - failed * 3
        return {
            'fitness': max(fitness, 0),
            'scheduled_count': scheduled_count,
            'total_conflicts': sum(conflicts.values()),
            'conflict_details': conflicts
        }


    def count_conflicts(self, schedule):
        conflict_types = {'teacher': 0, 'room': 0, 'continuous': 0}
        time_slot_map = defaultdict(lambda: {'rooms': set(), 'teachers': set()})

        print("\n=== 冲突检查开始 ===")  # 调试日志
        for entry in schedule:
            key = (entry[3], entry[4], entry[5])
            #print(f"检查记录: 课程={entry[0]}, 教室={entry[1]}, 教师={entry[2]}, 时间={key}")

            # 教室冲突检查
            if entry[1] in time_slot_map[key]['rooms']:
                print(f"⚠️ 教室冲突: {entry[1]} 在时间 {key} 被重复使用")
                conflict_types['room'] += 1
            time_slot_map[key]['rooms'].add(entry[1])

            # 教师冲突检查
            if entry[2] in time_slot_map[key]['teachers']:
                print(f"⚠️ 教师冲突: {entry[2]} 在时间 {key} 有多个课程")
                conflict_types['teacher'] += 1
            time_slot_map[key]['teachers'].add(entry[2])

        print(f"=== 冲突统计: {conflict_types} ===\n")
        return conflict_types
    def check_continuity(self, schedule, entry):
        """检查课程时间连续性"""
        course_id = entry[0]
        same_course = [e for e in schedule if e[0] == course_id]

        # 按周、天、时间排序
        sorted_slots = sorted(same_course, key=lambda x: (x[3], x[4], x[5]))

        # 计算最大连续时间段
        max_continuous = 1
        current = 1
        for i in range(1, len(sorted_slots)):
            prev = sorted_slots[i-1]
            curr = sorted_slots[i]
            if (curr[3] == prev[3] and  # 同一周
                    curr[4] == prev[4] and  # 同一天
                    curr[5] == prev[5] + 1):  # 连续时间
                current += 1
                max_continuous = max(max_continuous, current)
            else:
                current = 1

        return max_continuous



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
        """变异操作（修复适应度显示问题）"""
        try:
            # 复制个体时重置关键字段
            mutated = {
                'base': individual.get('base', []).copy(),
                'full_schedule': individual.get('full_schedule', []).copy(),
                'attempts': [a.copy() for a in individual.get('attempts', [])],
                'scheduled_count': 0,  # 重置成功计数
                'total_conflicts': 0,   # 重置冲突计数
                'fitness': 0           # 初始化为0，而非 -inf
            }

            if not mutated['attempts']:
                return mutated

            # 随机选择一个课程尝试重新插入
            idx = random.randint(0, len(mutated['attempts'])-1)
            course = mutated['attempts'][idx]['course']
            success, new_slots = self.try_insert(course, mutated['base'])

            # 更新排课记录
            if success:
                mutated['full_schedule'].extend(new_slots)
                mutated['scheduled_count'] += 1
                mutated['attempts'][idx]['scheduled'] = True
                mutated['attempts'][idx]['slots'] = new_slots
            else:
                mutated['attempts'][idx]['scheduled'] = False
                mutated['attempts'][idx]['slots'] = []

            # 关键修复：变异后立即重新计算适应度
            eval_result = self.evaluate(mutated)
            mutated.update(eval_result)

            print(f"[变异] 新适应度: {mutated['fitness']}")  # 调试输出
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
def test_conflict_detection():
    # 创建两个同一时间同一教师的课程
    course1 = type('Course', (), {'uid': 'MATH101', 'teacher_uid': 'T001-张三'})
    course2 = type('Course', (), {'uid': 'PHY101', 'teacher_uid': 'T001-张三'})
    room = type('Room', (), {'rid': 'R101'})

    # 相同时间槽
    slots = [(1, 1, 1)]  # 第1周周1第1节

    # 创建有冲突的课表
    schedule = [
        (course1.uid, room.rid, course1.teacher_uid, 1, 1, 1),  # 已存在的课程
    ]

    # 测试插入第二个课程
    scheduler = HybridScheduler([], [])
    print("教师冲突应被检测到:",
          not scheduler.is_valid_insertion(course2, room, slots, schedule))

    # 测试冲突统计
    conflict_schedule = schedule + [
        (course2.uid, room.rid, course2.teacher_uid, 1, 1, 1)
    ]
    print("冲突统计结果:",
          scheduler.count_conflicts(conflict_schedule))

test_conflict_detection()