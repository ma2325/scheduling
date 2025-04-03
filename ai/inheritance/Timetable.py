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


#这里有希望对
#两点前睡觉！

#this
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
    print(f"\n📝 开始生成课程 {course.cid} 的时间槽（总时间段数：{len(course.time_slots)}）")
    for start_week, end_week, lessons_per_week in course.time_slots:
        continuous = getattr(course, 'continuous', 1)
        groups_needed_per_week = lessons_per_week // continuous  # 计算每周需要的组数

        for week in range(start_week, end_week + 1):
            weekly_slots = []
            for day in range(1, DAYS_PER_WEEK + 1):
                # 连排课程逻辑
                if continuous > 1:
                    possible_starts = [s for s in range(1, SLOTS_PER_DAY + 1)
                                       if s + continuous - 1 <= SLOTS_PER_DAY]
                    for start in possible_starts:
                        slot_group = [
                            TimeSlot(week, day, start + i)
                            for i in range(continuous)
                        ]
                        weekly_slots.append(slot_group)
                else:
                    # 非连排课程逻辑
                    weekly_slots.extend([[TimeSlot(week, day, s)] for s in range(1, SLOTS_PER_DAY+1)])

            # 确保生成的组数不超过需求
            random.shuffle(weekly_slots)
            selected_groups = weekly_slots[:groups_needed_per_week]
            all_slots.extend(selected_groups)

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

    sorted_courses = sorted(
        courses,
        key=lambda x: -x.popularity if x.popularity is not None else 0 + random.uniform(-5, 5)
    )

    for _ in range(size):
        individual = []
        used_slots = {"teachers": defaultdict(list), "rooms": set()}

        for course in sorted_courses:
            # 获取课程的所有时间槽组（按周分组）
            all_slot_groups = generate_course_slots(course)

            # 按周分组时间槽
            weekly_slots = defaultdict(list)
            for slot_group in all_slot_groups:
                week = slot_group[0].week
                weekly_slots[week].append(slot_group)

            # 计算每周需要的课程组数（考虑连排）
            lessons_per_week = course.time_slots[0][2]  # 每周需要的课程数
            continuous = getattr(course, 'continuous', 1)  # 连排节数，默认为1
            groups_needed_per_week = lessons_per_week // continuous  # 每周需要的时间槽组数

            # 确保每周分配足够的课程组
            for week in range(course.time_slots[0][0], course.time_slots[0][1] + 1):
                available_groups = weekly_slots.get(week, [])
                random.shuffle(available_groups)

                # 分配该周需要的时间槽组
                assigned_groups = 0
                for slot_group in available_groups:
                    if assigned_groups >= groups_needed_per_week:
                        break

                    teacher_available = all(
                        (course.teacherid, ts.week, ts.day, ts.slot) not in used_slots["teachers"]
                        for ts in slot_group
                    )

                    possible_rooms = [r for r in rooms if r.rtype == course.fixedroomtype]
                    possible_rooms.sort(key=lambda r: abs(r.rcapacity - course.popularity))

                    for room in possible_rooms:
                        room_available = all(
                            (room.rid, ts.week, ts.day, ts.slot) not in used_slots["rooms"]
                            for ts in slot_group
                        )

                        if teacher_available and room_available:
                            for ts in slot_group:
                                individual.append((course.cid, room.rid, course.teacherid, ts.week, ts.day, ts.slot))
                                used_slots["teachers"][(course.teacherid, ts.week, ts.day, ts.slot)] = course.cid
                                used_slots["rooms"].add((room.rid, ts.week, ts.day, ts.slot))
                            assigned_groups += 1
                            break

                if assigned_groups < groups_needed_per_week:
                    print(f"⚠️ 课程 {course.cid} 在第 {week} 周安排不完全！需要 {groups_needed_per_week} 组，但只安排了 {assigned_groups} 组。")

        population.append(individual)

    return population


'''冲突检查'''
def check_conflict_3d(individual: list, index: int, courses: list, rooms: list) -> bool:
    if index >= len(individual) or individual[index] is None:
        return True  # 视为冲突，需重新安排
    target = individual[index]
    cid, rid, teacherid, week, day, slot = target

    # 获取当前课程信息
    course = next((c for c in courses if c.cid == cid), None)
    if not course:
        return True

    # 检查是否是连排课程的一部分
    is_continuous = hasattr(course, 'continuous') and course.continuous > 1
    continuous_slots = []

    if is_continuous:
        # 找出同一课程的所有连排安排
        course_entries = [e for e in individual if e[0] == cid and e[3] == week and e[4] == day]
        # 按节次排序
        course_entries.sort(key=lambda x: x[5])
        # 检查是否形成连续的节次块
        for i in range(len(course_entries) - 1):
            if course_entries[i+1][5] != course_entries[i][5] + 1:
                return True
        # 检查是否从正确的节次开始
        start_slot = course_entries[0][5]
        if course.continuous == 2 and start_slot not in [1, 3, 5, 7]:
            return True
        if course.continuous == 4 and start_slot not in [1, 3, 5]:
            return True

    # 检查教室类型是否匹配
    room = next((r for r in rooms if r.rid == rid), None)
    room_type_mismatch = room and room.rtype != course.fixedroomtype
    fixed_room_mismatch = course.fixedroom and rid != course.fixedroom

    # 检查教师冲突
    teacher_conflict = any(
        item[2] == teacherid and
        item[3] == week and
        item[4] == day and
        item[5] == slot
        for item in individual[:index] + individual[index+1:]
    )

    # 检查教室冲突
    room_conflict = any(
        item[1] == rid and
        item[3] == week and
        item[4] == day and
        item[5] == slot
        for item in individual[:index] + individual[index+1:]
    )

    return teacher_conflict or room_conflict or room_type_mismatch or fixed_room_mismatch
'''适应度函数'''
'''改进后的适应度函数（增加时间分布奖励）'''
def fitness(individual):
    score = 0
    # ----------------- 基础冲突检查 -----------------
    teacher_schedule = set()
    room_schedule = set()
    course_time_distribution = defaultdict(list)  # 记录每门课程的时间分布

    for cid, rid, teacher_id, week, day, slot in individual:
        # 基础冲突检查
        teacher_key = (teacher_id, week, day, slot)
        room_key = (rid, week, day, slot)

        if teacher_key in teacher_schedule:
            score -= 200  # 教师冲突惩罚
        else:
            teacher_schedule.add(teacher_key)

        if room_key in room_schedule:
            score -= 150  # 教室冲突惩罚
        else:
            room_schedule.add(room_key)

        # 记录课程时间分布
        course_time_distribution[cid].append( (week, day) )

    # ----------------- 新增时间分布评分项 -----------------
    time_distribution_reward = 0
    for cid, time_list in course_time_distribution.items():
        course = next((c for c in courses if c.cid == cid), None)
        if not course: continue

        # 奖励1：周次分散度（避免集中在某几周）
        weeks = [t[0] for t in time_list]
        unique_weeks = len(set(weeks))
        time_distribution_reward += unique_weeks * 5  # 每分散一周+5分

        # 奖励2：避免同一天多节课（特殊课程除外）
        if not hasattr(course, 'continuous') or course.continuous == 1:
            day_counts = defaultdict(int)
            for _, day in time_list:
                day_counts[day] += 1
            for cnt in day_counts.values():
                if cnt > 1:
                    time_distribution_reward -= 20 * (cnt-1)  # 同天多节惩罚

        # 奖励3：优先上午时段（1-4节）
        morning_slots = sum(1 for _, _, _,_, _, slot in individual
                            if cid == cid and slot <= 4)
        time_distribution_reward += morning_slots * 3

    score += time_distribution_reward

    # ----------------- 教室容量利用率 -----------------
    for cid, rid, _, _, _, _ in individual:
        course = next((c for c in courses if c.cid == cid), None)
        room = next((r for r in rooms if r.rid == rid), None)
        if course and room:
            # 容量匹配度奖励（70%-90%利用率最优）
            utilization = course.popularity / room.rcapacity
            if 0.7 <= utilization <= 0.9:
                score += 30
            elif utilization > 0.9:
                score += 10  # 过度拥挤
            else:
                score += max(0, 10 * utilization)  # 低利用率

    # ----------------- 未排课惩罚 -----------------
    scheduled_courses = {entry[0] for entry in individual}
    unscheduled_count = len([c for c in courses if c.cid not in scheduled_courses])
    score -= unscheduled_count * 1000

    return score


'''父辈选择，竞标赛'''
def selection(population: List[List[tuple]]) -> List[List[tuple]]:
    """锦标赛选择：随机选取k个个体，保留最优的"""
    selected = []
    k = 3  # 锦标赛规模
    for _ in range(len(population)):
        candidates = random.sample(population, k)
        winner = max(candidates, key=fitness)
        selected.append(winner)
    return selected

'''基因重组'''
def crossover(parent1, parent2):
    min_length = min(len(parent1), len(parent2))
    child = []
    for i in range(min_length):
        if random.random() < 0.5:
            child.append(parent1[i])
        else:
            child.append(parent2[i])
    return child
'''基因变异'''
def mutate(individual):
    mutated = individual.copy()
    total = len(mutated)

    course_teacher_map = {c.cid: c.teacherid for c in courses}
    course_dict = {c.cid: c for c in courses}

    # 按课程分组处理，特别是连排课程
    course_groups = defaultdict(list)
    for i, entry in enumerate(mutated):
        course_groups[entry[0]].append((i, entry))

    for cid, entries in course_groups.items():
        course = course_dict.get(cid)
        if not course:
            continue


        # 检查是否需要变异（随机决定）
        if random.random() > 0.5:  # 50%的概率保持不变
            continue

        # 处理连排课程
        if hasattr(course, 'continuous') and course.continuous > 1:
            # 获取该课程的所有安排
            entries.sort(key=lambda x: (x[1][3], x[1][4], x[1][5]))  # 按周、天、节次排序

            # 尝试生成新的时间组
            new_slot_groups = generate_course_slots(course)
            if not new_slot_groups:
                continue

            new_slot_group = random.choice(new_slot_groups)
            room = next((r for r in rooms if r.rid == entries[0][1][1]), None)
            if not room:
                continue

            # 删除原有安排
            for i, _ in entries:
                mutated[i] = None

            # 添加新安排
            new_entries = []
            for ts in new_slot_group:
                new_entry = (cid, room.rid, course.teacherid, ts.week, ts.day, ts.slot)
                new_entries.append(new_entry)

            # 找到空位插入
            empty_indices = [i for i, x in enumerate(mutated) if x is None]
            for i, entry in zip(empty_indices[:len(new_entries)], new_entries):
                mutated[i] = entry
        else:
            # 非连排课程的变异逻辑保持不变
            for i, entry in entries:
                if check_conflict_3d(mutated, i, courses, rooms):
                    teacher_id = course_teacher_map.get(cid)
                    if not teacher_id:
                        continue

                    if course.fixedroom:
                        room = next((r for r in rooms if r.rname == course.fixedroom), None)
                    else:
                        valid_rooms = [r for r in rooms if r.rtype == course.fixedroomtype]
                        room = random.choice(valid_rooms) if valid_rooms else None

                    if not room:
                        continue

                    new_slot = random.choice(generate_course_slots(course)[0])  # 取第一个时间组
                    mutated[i] = (cid, room.rid, teacher_id, new_slot.week, new_slot.day, new_slot.slot)

    # 移除None值
    mutated = [x for x in mutated if x is not None]
    return mutated
'''遗传主算法'''
'''遗传主算法 - 添加可视化版本'''
def genetic_algorithm(iterations=100, population_size=50):
    print("🔄 开始初始化种群...")
    start_time = time.time()
    population = initialize_population(population_size,courses,rooms)
    init_time = time.time() - start_time
    print(f"✅ 种群初始化完成，耗时 {init_time:.2f} 秒")

    best_fitness_history = []

    for gen in range(iterations):
        iter_start = time.time()
        print(f"\n=== 第 {gen+1}/{iterations} 代 ===")

        # 按适应度排序
        population.sort(key=fitness, reverse=True)
        current_best = fitness(population[0])
        best_fitness_history.append(current_best)

        # 修改精英保留策略：保留前10%
        elite_size = max(1, int(population_size * 0.1))  # 至少保留1个
        elites = population[:elite_size]

        new_population = elites.copy()  # 仅保留精英个体

        print(f"🏆 当前最佳适应度: {current_best}")
        print(f"🎖️ 保留精英数量: {elite_size}")

        # 显示种群多样性
        unique_fitness = len(set(fitness(ind) for ind in population))
        print(f"🧬 种群多样性（不同适应度数量）: {unique_fitness}")

        # 生成子代时观察
        while len(new_population) < population_size:
            p1, p2 = random.sample(population[:10], 2)

            # 交叉前打印父代信息
            print("\n👪 父代1课程安排:", [entry[0] for entry in p1])
            print("👪 父代2课程安排:", [entry[0] for entry in p2])

            child = crossover(p1, p2)
            mutated_child = mutate(child)

            # 打印子代详细信息
            print(f"👶 子代长度: {len(mutated_child)}")
            print("📋 子代课程安排详情:")
            for entry in mutated_child:
                cid, rid, tid, week, day, slot = entry
                print(f"课程{cid} -> 教室{rid} 教师{tid} 时间{week}-{day}-{slot}")

            new_population.append(mutated_child)
            print("----------------------------------")

        population = new_population
        iter_time = time.time() - iter_start
        print(f"⏱️ 本代耗时: {iter_time:.2f} 秒")

        # 早期终止条件
        if gen > 10 and len(set(best_fitness_history[-5:])) == 1:
            print("🚀 适应度连续5代未提升，提前终止")
            break


    total_time = time.time() - start_time
    print(f"\n🎉 遗传算法完成！总耗时: {total_time:.2f} 秒")
    print(f"📈 适应度变化: {best_fitness_history}")


    return max(population, key=fitness)

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