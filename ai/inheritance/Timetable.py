import random
from collections import defaultdict
from typing import List
from main import courses, rooms
import test
from sql.models import Schedule
import json
import deepseek
from collections import defaultdict
import time
from ConstraintSolver import ConstraintSolver
#连排开始规则
CONTINUOUS_SLOT_RULES = {
    2: [1, 3, 5, 7],  # 两节连排允许的开始节次
    4: [1, 3, 5],     # 四节连排允许的开始节次
    # 可以继续添加其他连排类型的规则
}

#这里完全对啦！
#总课程应该为66944
'''三维时间模型'''
WEEKS_IN_SEMESTER = 20  # 总教学周数
DAYS_PER_WEEK = 5       # 每周上课天数 (周一至周五)
SLOTS_PER_DAY = 8       # 每天节次数

class TimeSlot:
    """三维时间点表示 (周次, 周几, 节次)"""
    def __init__(self, week, day, slot):
        self.week = week    # 1-20教学周
        self.day = day      # 1-5 (周一至周五)
        self.slot = slot    # 1-8节

    def __str__(self):
        return f"第{self.week}周 周{self.day} 第{self.slot}节"

'''根据课程的time_slots生成所有有效时间点'''
def generate_course_slots(course):
    all_slots = []
    for start_week, end_week, lessons_per_week in course.time_slots:
        continuous = getattr(course, 'continuous', 1)
        groups_needed_per_week = lessons_per_week // continuous

        for week in range(start_week, end_week + 1):
            # 随机打乱周几的顺序，避免总是从周一开始
            days = list(range(1, DAYS_PER_WEEK + 1))
            random.shuffle(days)

            for day in days:
                if continuous > 1:
                    allowed_starts = CONTINUOUS_SLOT_RULES.get(continuous, [])
                    for start in allowed_starts:
                        if start + continuous - 1 <= SLOTS_PER_DAY:
                            group = [TimeSlot(week, day, start + i) for i in range(continuous)]
                            all_slots.append(group)
                else:
                    # 对于非连排课程，更均匀地分布在不同的天
                    slots = list(range(1, SLOTS_PER_DAY + 1))
                    random.shuffle(slots)
                    for slot in slots[:groups_needed_per_week]:
                        all_slots.append([TimeSlot(week, day, slot)])

                # 如果已经找到足够的组，就停止
                if len(all_slots) >= groups_needed_per_week * (end_week - start_week + 1):
                    break
    return all_slots

'''统计未被安排的课'''
def count_unscheduled_courses(timetable):
    scheduled_courses = {entry[0] for entry in timetable}
    unscheduled_courses = [c.cid for c in courses if c.cid not in scheduled_courses]
    return len(unscheduled_courses), unscheduled_courses

'''初始种群，贪心'''
'''初始种群，贪心'''
def initialize_population(size: int, courses, rooms):
    population = []
    constraint_solver = ConstraintSolver(courses, rooms)
    attempt=0
    # 课程排序逻辑（保留原有）
    sorted_courses = sorted(
        courses,
        key=lambda x: (
            -x.popularity if x.popularity is not None else 0,
            x.fixedroom is not None,
            random.random()
        )
    )
    while len(population) < size:
        attempt += 1
        individual=[]
        used_slots = {
            "teachers": set(),  # 直接使用set()而不是defaultdict
            "rooms": set()      # 直接使用set()而不是defaultdict
        }
        for course in sorted_courses:
            # 生成所有可能的时间槽组（按周分组）
            all_slot_groups = generate_course_slots(course)
            continuous = getattr(course, 'continuous', 1)

            # 按周和天两级分组
            weekly_slots = defaultdict(lambda: defaultdict(list))
            for group in all_slot_groups:
                week = group[0].week
                day = group[0].day
                weekly_slots[week][day].append(group)

            # 处理每个时间段
            for time_slot in course.time_slots:
                start_week, end_week, lessons_per_week = time_slot
                groups_needed_per_week = lessons_per_week // continuous

                for week in range(start_week, end_week + 1):
                    assigned_groups = 0

                    # 优先尝试固定教室
                    possible_rooms = [r for r in rooms if r.rtype == course.fixedroomtype]
                    if course.fixedroom:
                        fixed_room = next((r for r in rooms if r.rname == course.fixedroom), None)
                        if fixed_room:
                            possible_rooms.insert(0, fixed_room)

                    # 按天遍历，优先同一天分配多组
                    for day in range(1, DAYS_PER_WEEK + 1):
                        if assigned_groups >= groups_needed_per_week:
                            break

                        # 获取该天所有可用时间组
                        day_groups = weekly_slots[week].get(day, [])
                        random.shuffle(day_groups)

                        for group in day_groups:
                            if assigned_groups >= groups_needed_per_week:
                                break

                            # 检查整组是否可用
                            group_available = True
                            room_selected = None

                            for room in possible_rooms:
                                room_ok = True
                                for ts in group:
                                    teacher_key = (course.teacherid, ts.week, ts.day, ts.slot)
                                    room_key = (room.rid, ts.week, ts.day, ts.slot)
                                    if (teacher_key in used_slots["teachers"] or
                                            room_key in used_slots["rooms"]):
                                        room_ok = False
                                        break

                                if room_ok:
                                    room_selected = room
                                    break

                            if room_selected:
                                # 分配整组
                                for ts in group:
                                    entry = (
                                        course.cid,
                                        room_selected.rid,
                                        course.teacherid,
                                        ts.week, ts.day, ts.slot
                                    )
                                    individual.append(entry)
                                    used_slots["teachers"].add((course.teacherid, ts.week, ts.day, ts.slot))
                                    used_slots["rooms"].add((room_selected.rid, ts.week, ts.day, ts.slot))
                                assigned_groups += 1

                    if assigned_groups < groups_needed_per_week:
                        print(f"⚠️ 课程 {course.cid} 第{week}周需要 {groups_needed_per_week} 组，只安排了 {assigned_groups} 组")
        if constraint_solver.check_hard_constraints(individual):
            population.append(individual)
            print(f"✅ 成功生成个体 {len(population)}/{size}", end='\r')
        else:
            if attempt % 100 == 0:  # 每100次尝试输出警告
                print(f"⚠️ 已尝试 {attempt} 次，当前成功 {len(population)} 个")
        if attempt > size * 100:  # 安全阀
            raise RuntimeError("无法生成满足约束的初始种群，请检查约束条件")

    return population


'''冲突检查'''
"""
def check_conflict_3d(individual: list, index: int, courses: list, rooms: list) -> bool:
    if index >= len(individual) or individual[index] is None:
        return True  # 视为冲突，需重新安排

    target = individual[index]
    cid, rid, teacherid, week, day, slot = target

    # 获取当前课程信息
    course = next((c for c in courses if c.cid == cid), None)
    if not course:
        return True

    # ==================== 连排课程检查 ====================
    is_continuous = hasattr(course, 'continuous') and course.continuous > 1

    if is_continuous:
        # 1. 找出同一课程同周同天的所有安排
        course_entries = [e for e in individual if e[0] == cid
                          and e[3] == week and e[4] == day]

        # 2. 必须满足连排节数要求
        if len(course_entries) != course.continuous:
            return True

        # 3. 检查节次连续性
        course_entries.sort(key=lambda x: x[5])
        for i in range(len(course_entries) - 1):
            if course_entries[i+1][5] != course_entries[i][5] + 1:
                return True

        # 4. 检查开始节次是否符合规则
        start_slot = course_entries[0][5]
        allowed_starts = CONTINUOUS_SLOT_RULES.get(course.continuous, [])
        if allowed_starts and start_slot not in allowed_starts:
            return True

        # 5. 检查整组教室是否一致
        if len(set(e[1] for e in course_entries)) > 1:
            return True

    # ==================== 原有冲突检查 ====================
    # 教室类型检查
    room = next((r for r in rooms if r.rid == rid), None)
    room_type_mismatch = room and room.rtype != course.fixedroomtype

    # 固定教室检查（基于rname）
    fixed_room_mismatch = False
    if course.fixedroom:
        room = next((r for r in rooms if r.rid == rid), None)
        if not room or room.rname != course.fixedroom:
            fixed_room_mismatch = True

    # 教师时间冲突检查
    teacher_conflict = any(
        item[2] == teacherid and item[3] == week
        and item[4] == day and item[5] == slot
        for item in individual[:index] + individual[index+1:]
    )

    # 教室时间冲突检查
    room_conflict = any(
        item[1] == rid and item[3] == week
        and item[4] == day and item[5] == slot
        for item in individual[:index] + individual[index+1:]
    )

    # 综合所有冲突条件
    return (teacher_conflict or room_conflict
            or room_type_mismatch or fixed_room_mismatch)
"""
'''适应度函数'''
'''改进后的适应度函数（增加时间分布奖励）'''
def fitness(individual):
    """优化目标：只计算软约束得分（硬约束已由ConstraintSolver处理）"""
    score = 0
    course_time_distribution = defaultdict(list)
    room_utilization = defaultdict(int)

    # 数据收集阶段
    for cid, rid, _, week, day, slot in individual:
        course_time_distribution[cid].append((week, day, slot))
        room_utilization[rid] += 1

    # 1. 时间分布评分（周/天分散度）
    for cid, time_list in course_time_distribution.items():
        course = next((c for c in courses if c.cid == cid), None)
        if not course: continue

        # 周分散奖励
        unique_weeks = len({t[0] for t in time_list})
        score += unique_weeks * 5

        # 同天多课惩罚（非连排课程）
        if not hasattr(course, 'continuous') or course.continuous == 1:
            day_counts = defaultdict(int)
            for _, day, _ in time_list:
                day_counts[day] += 1
            for cnt in day_counts.values():
                if cnt > 1:
                    score -= 20 * (cnt - 1)

    # 2. 教室利用率评分（70%-90%最优）
    for cid, rid, _, _, _, _ in individual:
        course = next((c for c in courses if c.cid == cid), None)
        room = next((r for r in rooms if r.rid == rid), None)
        if course and room:
            utilization = course.popularity / room.rcapacity
            if 0.7 <= utilization <= 0.9:
                score += 30
            elif utilization > 0.9:
                score += 10
            else:
                score += max(0, 10 * utilization)

    # 3. 上午课奖励（1-4节）
    morning_slots = sum(1 for _, _, _, _, _, slot in individual if slot <= 4)
    score += morning_slots * 3

    # 4. 未排课惩罚（保留）
    scheduled_courses = {entry[0] for entry in individual}
    unscheduled_count = len([c for c in courses if c.cid not in scheduled_courses])
    score -= unscheduled_count * 1000

    return score


'''父辈选择，竞标赛'''
def selection(population: List[List[tuple]]) -> List[List[tuple]]:
    selected = []
    k = 5  # 增大锦标赛规模
    tournament_size = max(3, len(population)//10)  # 动态调整

    for _ in range(len(population)):
        # 确保选择不同的个体
        candidates = random.sample(population, min(tournament_size, len(population)))

        # 按适应度排序并加权选择
        candidates.sort(key=fitness, reverse=True)
        weights = [1/(i+1) for i in range(len(candidates))]  # 加权选择
        winner = random.choices(candidates, weights=weights, k=1)[0]

        selected.append(winner)
    return selected

'''基因重组'''
def crossover(parent1, parent2):
    """改进版交叉操作：按课程分组交叉，避免破坏连排课程"""
    # 1. 将父代按课程分组
    parent1_courses = defaultdict(list)
    parent2_courses = defaultdict(list)

    for entry in parent1:
        parent1_courses[entry[0]].append(entry)  # 按课程ID分组
    for entry in parent2:
        parent2_courses[entry[0]].append(entry)

    child = []

    # 2. 随机选择从哪个父代继承课程
    all_cids = list(set(parent1_courses.keys()).union(set(parent2_courses.keys())))
    random.shuffle(all_cids)  # 打乱顺序避免偏向某父代

    for cid in all_cids:
        # 随机选择继承父代1或父代2的该课程安排
        if random.random() < 0.5 and cid in parent1_courses:
            child.extend(parent1_courses[cid])
        elif cid in parent2_courses:
            child.extend(parent2_courses[cid])

    return child
'''基因变异'''
def mutate(individual):
    original_fitness=fitness(individual)
    """改进版变异函数，保留原有功能并确保满足硬约束"""
    constraint_solver = ConstraintSolver(courses, rooms)
    course_dict = {c.cid: c for c in courses}
    room_dict = {r.rid: r for r in rooms}

    # 最多尝试3次生成合法变异
    for _ in range(3):
        mutated = individual.copy()
        course_groups = defaultdict(list)

        # 按课程分组（保留原有分组逻辑）
        for i, entry in enumerate(mutated):
            if entry:
                course_groups[entry[0]].append((i, entry))

        # 随机选择要变异的课程（保留原有随机性）
        for cid, entries in course_groups.items():
            course = course_dict.get(cid)
            if not course or random.random() > 0.3:
                continue

            # === 连排课程处理（保留原有逻辑）===
            if hasattr(course, 'continuous') and course.continuous > 1:
                # 1. 删除原有连排段
                for i, _ in entries:
                    if i<len(mutated):
                        mutated[i] = None

                # 2. 生成新连排组（保持原有生成规则）
                valid_groups = [
                    group for group in generate_course_slots(course)
                    if len(group) == course.continuous
                       and all(ts.day == group[0].day for ts in group)
                       and group[0].slot in CONTINUOUS_SLOT_RULES.get(course.continuous, [])
                ]

                if not valid_groups:
                    continue

                new_group = random.choice(valid_groups)

                # 3. 教室选择（保留固定教室优先逻辑）
                if course.fixedroom:
                    room = next((r for r in rooms if r.rname == course.fixedroom), None)
                else:
                    original_room_id = next((e[1][1] for e in entries if e[1]), None)
                    room = room_dict.get(original_room_id) if original_room_id else None

                if not room:  # 备用选择
                    room = next((r for r in rooms if r.rtype == course.fixedroomtype), None)
                    if not room:
                        continue

                # 4. 插入新安排
                new_entries = [
                    (cid, room.rid, course.teacherid, ts.week, ts.day, ts.slot)
                    for ts in new_group
                ]

                # 找空位插入（保留原有位置优先策略）
                empty_indices = [i for i, x in enumerate(mutated) if x is None]
                for i, entry in zip(empty_indices[:len(new_entries)], new_entries):
                    mutated[i] = entry

            # === 非连排课程处理 ===
            else:
                for i, entry in entries:
                    # 保留原有教室选择策略
                    if course.fixedroom:
                        room = next((r for r in rooms if r.rname == course.fixedroom), None)
                    else:
                        room = room_dict.get(entry[1]) or \
                               next((r for r in rooms if r.rtype == course.fixedroomtype), None)

                    if not room:
                        continue

                    # 生成新时间（保留原有generate_course_slots逻辑）
                    for _ in range(3):  # 最多尝试3次
                        new_slot = random.choice(generate_course_slots(course)[0])
                        new_entry = (
                            cid, room.rid, course.teacherid,
                            new_slot.week, new_slot.day, new_slot.slot
                        )

                        # 临时替换并检查
                        original = mutated[i]
                        mutated[i] = new_entry
                        if constraint_solver.check_hard_constraints(mutated):
                            break
                        mutated[i] = original

        # 移除None并保持顺序
        mutated = [x for x in mutated if x is not None]
        new_fitness=fitness(mutated)
        if new_fitness > original_fitness:
            print(f"变异成功 Δ={new_fitness-original_fitness}")
        if constraint_solver.check_hard_constraints(mutated):
            return mutated

    # 如果无法生成合法变异，返回原个体（安全策略）
    return individual
'''遗传主算法'''
'''遗传主算法 - 添加可视化版本'''
def genetic_algorithm(iterations=100, population_size=50):
    """改进版遗传算法主函数，保留原有功能并整合ConstraintSolver"""
    print("🔄 开始初始化种群（强制满足硬约束）...")
    start_time = time.time()

    # 初始化种群
    population = initialize_population(population_size, courses, rooms)
    constraint_solver = ConstraintSolver(courses, rooms)  # 约束检查器

    best_fitness_history = []

    for gen in range(iterations):
        print(f"\n=== 第 {gen+1}/{iterations} 代 ===")

        # 计算适应度并排序
        population.sort(key=fitness, reverse=True)
        best_fitness = fitness(population[0])
        best_fitness_history.append(best_fitness)

        print(f"🏆 第 {gen+1} 代 | 最佳适应度: {best_fitness} | 种群多样性: {len(set(fitness(ind) for ind in population))}")

        # **精英保留 + 变异**
        elite_size = max(1, int(population_size * 0.2))
        elites = population[:elite_size]

        # 让部分精英个体进行变异（30% 概率）
        mutated_elites = [mutate(e) if random.random() < 0.3 else e for e in elites]

        # **生成新种群**
        new_population = mutated_elites.copy()
        mating_pool = selection(population)

        while len(new_population) < population_size:
            p1, p2 = random.sample(mating_pool, 2)

            # 交叉 & 变异
            child = crossover(p1, p2)
            mutated_child = mutate(child)

            # 硬约束检查
            if constraint_solver.check_hard_constraints(mutated_child):
                if fitness(mutated_child) > fitness(population[-1]):
                    new_population.append(mutated_child)

        # **确保适应度高的个体存活**
        population = sorted(new_population, key=fitness, reverse=True)[:population_size]

        print(f"✅ 第 {gen+1} 代完成 | 最佳适应度: {fitness(population[0])} | 变化 Δ={fitness(population[0]) - best_fitness_history[-2] if gen > 0 else 0}")

        # **早停机制**
        if gen > 10 and len(set(best_fitness_history[-5:])) == 1:
            print("🚀 适应度连续5代未提升，提前终止")
            break

    print(f"\n🎉 算法完成！最终适应度: {fitness(population[0])}")
    return population[0]  # 返回最佳个体



def print_schedule(timetable):
    print("\n📅 最终排课方案：")
    scheduled_courses = set()

    for i, (cid, rid, teacher, week, day, slot) in enumerate(timetable, 1):
        day_map = {1: "周一", 2: "周二", 3: "周三", 4: "周四", 5: "周五"}
        print(
            f"{i}. 课程 {cid} | "
            f"教室 {rid} | "
            f"教师 {teacher} | "
            f"时间：第{week}周 {day_map[day]} 第{slot}节"
        )
        scheduled_courses.add(cid)

    # 输出未被安排的课程
    unscheduled_courses = [c for c in courses if c.cid not in scheduled_courses]
    if unscheduled_courses:
        print("\n🚨 以下课程未被成功安排：")
        for c in unscheduled_courses:
            print(f"❌ 课程 {c.cid} (教师 {c.teacherid})")

# 在main中调用
'''main'''
if __name__ == "__main__":
    timetable = genetic_algorithm(iterations=50, population_size=30)
    print_schedule(timetable)

    # 数据格式转换
    schedule_list = [Schedule(scid, teacher, rid, f"{week}-{day}-{slot}")
                     for scid, teacher, rid, week, day, slot in timetable]
    schedule_json = json.dumps([s.to_dict() for s in schedule_list], ensure_ascii=False, indent=4)

    # 核查
    validation_report = test.validate_schedule(timetable, courses)
    if validation_report:
        print("\n发现以下冲突：")
        for line in validation_report:
            print(f"⚠️ {line}")
    else:
        print("\n✅ 排课方案无冲突")