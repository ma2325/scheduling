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
        weekly_slots = []

        for week in range(start_week, end_week + 1):
            for day in range(1, DAYS_PER_WEEK + 1):
                # 处理连排课程
                if hasattr(course, 'continuous') and course.continuous > 1:
                    # 根据连排次数确定可选的开始节次
                    if course.continuous == 2:
                        possible_start_slots = [1, 3, 5, 7]
                    elif course.continuous == 4:
                        possible_start_slots = [1, 3, 5]
                    else:
                        possible_start_slots = list(range(1, SLOTS_PER_DAY + 1))

                    # 确保连排课程不会超出当天节次限制
                    possible_start_slots = [
                        s for s in possible_start_slots
                        if s + course.continuous - 1 <= SLOTS_PER_DAY
                    ]

                    # 为连排课程生成时间点
                    for start_slot in possible_start_slots:
                        # 生成连续的节次
                        continuous_slots = [
                            TimeSlot(week, day, slot)
                            for slot in range(start_slot, start_slot + course.continuous)
                        ]
                        weekly_slots.append(continuous_slots)
                else:
                    # 非连排课程按原方式处理
                    weekly_slots.extend([
                        [TimeSlot(week, day, slot)]
                        for slot in range(1, SLOTS_PER_DAY + 1)
                    ])

        # 随机选择足够的课程安排
        random.shuffle(weekly_slots)
        selected = weekly_slots[:lessons_per_week]
        all_slots.extend(selected)

    return all_slots
'''统计未被安排的课'''
def count_unscheduled_courses(timetable):
    scheduled_courses = {entry[0] for entry in timetable}
    unscheduled_courses = [c.cid for c in courses if c.cid not in scheduled_courses]
    return len(unscheduled_courses), unscheduled_courses

'''初始种群，贪心'''
'''初始种群，贪心'''
def initialize_population(size: int) -> List[List[tuple]]:
    population = []
    sorted_courses = sorted(
        courses,
        key=lambda x: -x.popularity if x.popularity is not None else 0
    )

    for _ in range(size):
        individual = []
        used_slots = {"teachers": defaultdict(list), "rooms": set()}

        for course in sorted_courses:
            valid_slot_groups = generate_course_slots(course)
            assigned = False

            for slot_group in valid_slot_groups:
                # 检查教师和教室在所有连排时间段是否可用
                teacher_available = True
                room_available = True

                # 尝试多个教室
                possible_rooms = [r for r in rooms if r.rtype == course.fixedroomtype]
                possible_rooms.sort(key=lambda r: abs(r.rcapacity - course.popularity))

                for room in possible_rooms:
                    teacher_available = all(
                        (course.teacherid, ts.week, ts.day, ts.slot) not in used_slots["teachers"]
                        for ts in slot_group
                    )

                    room_available = all(
                        (room.rid, ts.week, ts.day, ts.slot) not in used_slots["rooms"]
                        for ts in slot_group
                    )

                    if teacher_available and room_available:
                        # 安排所有连排课程
                        for ts in slot_group:
                            individual.append((course.cid, room.rid, course.teacherid, ts.week, ts.day, ts.slot))
                            used_slots["teachers"][(course.teacherid, ts.week, ts.day, ts.slot)] = course.cid
                            used_slots["rooms"].add((room.rid, ts.week, ts.day, ts.slot))
                        assigned = True
                        break

                if assigned:
                    break

            if not assigned:
                print(f"⚠️ 课程 {course.cid} (教师 {course.teacherid}) 无法安排！可能是教师冲突或教室不足。")

        population.append(individual)
    return population
'''冲突检查'''
def check_conflict_3d(individual: list, index: int, courses: list, rooms: list) -> bool:
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
def fitness(individual):
    score = 0
    teacher_hours = defaultdict(int)  # 教师课时统计
    room_utilization = defaultdict(int)  # 教室使用率
    teacher_schedule = set()
    room_schedule = set()
    teacher_day_count = defaultdict(int)

    for cid, rid, teacher_id, week, day, slot in individual:
        teacher_key = (teacher_id, week, day, slot)
        room_key = (rid, week, day, slot)

        if teacher_key in teacher_schedule:
            score -= 200
        else:
            teacher_schedule.add(teacher_key)

        if room_key in room_schedule:
            score -= 150
        else:
            room_schedule.add(room_key)

        teacher_day_count[(teacher_id, week, day)] += 1
    for cid, rid, tid, week, day, slot in individual:
        course = next((c for c in courses if c.cid == cid), None)
        if not course:
            continue

        # 奖励教室容量匹配度（避免大教室排小课）
        room = next((r for r in rooms if r.rid == rid), None)
        if room and course.popularity:
            utilization = min(1.0, course.popularity / room.rcapacity)
            score += 10 * utilization  # 正向奖励

        # 惩罚教师单日课时过多
        teacher_hours[(tid, week, day)] += 1

    # 教师每日课时均衡性惩罚
    for hours in teacher_hours.values():
        if hours > 4:
            score -= 20 * (hours - 4)  # 超过4节/天则惩罚
    for count in teacher_day_count.values():
        if count > 4:
            score -= 50 * (count - 4)

    scheduled_courses ={entry[0] for entry in individual}
    unscheduled_count=len([c for c in courses if c.cid not in scheduled_courses])
    score-= unscheduled_count*1000
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
def crossover(parent1: List[tuple], parent2: List[tuple]) -> List[tuple]:
    min_length = min(len(parent1), len(parent2))
    parent1, parent2 = parent1[:min_length], parent2[:min_length]

   # print(f"📏 parent1 长度: {len(parent1)}, parent2 长度: {len(parent2)}")

    # 创建课程ID到教师ID的映射字典
    course_teacher_map = {c.cid: c.teacherid for c in courses}

    split = len(parent1) // 2
    child = []

    for i in range(len(parent1)):
        if i < split:
            cid, rid, _, week, day, slot = parent1[i]  # 忽略原teacher_id
        else:
            cid, rid, _, week, day, slot = parent2[i]  # 忽略原teacher_id

        # 直接从映射字典获取正确的教师ID
        teacher_id = course_teacher_map.get(cid)
        if teacher_id is None:
            continue  # 或者处理找不到课程的情况

        child.append((cid, rid, teacher_id, week, day, slot))

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
        if random.random() > 0.3:  # 70%的概率保持不变
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
    population = initialize_population(population_size)
    init_time = time.time() - start_time
    print(f"✅ 种群初始化完成，耗时 {init_time:.2f} 秒")

    best_fitness_history = []  # 记录每代最佳适应度

    for gen in range(iterations):
        iter_start = time.time()
        print(f"\n=== 第 {gen+1}/{iterations} 代 ===")
        population.sort(key=fitness, reverse=True)
        current_best = fitness(population[0])
        best_fitness_history.append(current_best)
        print(f"🏆 当前最佳适应度: {current_best}")

        # 显示冲突情况
        conflict_count = sum(
            1 for i in range(len(population[0]))
            if check_conflict_3d(population[0], i, courses, rooms)
        )
        print(f"⚠️ 当前最佳个体冲突数: {conflict_count}")
        best_individual = population[0]
        unscheduled_count, unscheduled_courses = count_unscheduled_courses(best_individual)
        print(f"🚨 未被安排课程数: {unscheduled_count}, 课程ID: {unscheduled_courses}")

        new_population = [best_individual]
        while len(new_population) < population_size:
            # 显示进度
            if len(new_population) % 10 == 0:
                print(f"🧬 正在生成后代... {len(new_population)}/{population_size}", end="\r")
            p1, p2 = random.sample(population[:10], 2)
            child = crossover(p1, p2)
            mutated_child = mutate(child)

            new_population.append(mutated_child)

        population = new_population
        iter_time = time.time() - iter_start
        print(f"⏱️ 本代耗时: {iter_time:.2f} 秒")

        # 早期终止条件（可选）
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