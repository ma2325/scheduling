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
        # 生成每周的候选时间
        weekly_slots = [
            TimeSlot(week, day, slot)
            for week in range(start_week, end_week + 1)
            for day in range(1, DAYS_PER_WEEK + 1)
            for slot in range(1, SLOTS_PER_DAY + 1)
        ]

        # 随机选择每周需要的节数
        random.shuffle(weekly_slots)
        selected = weekly_slots[:lessons_per_week]
        all_slots.extend(selected)

    return all_slots

'''初始种群，贪心'''
def initialize_population(size: int) -> List[List[tuple]]:
    population = []
    sorted_courses = sorted(
        courses,
        key=lambda x: -x.popularity if x.popularity is not None else 0
    )
    for _ in range(size):
        individual = []
        used_slots = {"teachers": set(), "rooms": set()}
        for course in sorted_courses:
            valid_slots = generate_course_slots(course)
            for ts in valid_slots:  # 直接使用TimeSlot对象
                teacher_key = (course.teacherid, ts.week, ts.day, ts.slot)
                room = next((r for r in rooms if r.rcapacity >= course.popularity), None)
                if room:
                    room_key = (room.rid, ts.week, ts.day, ts.slot)
                    if teacher_key not in used_slots["teachers"] and room_key not in used_slots["rooms"]:
                        individual.append((course.cid, room.rid, course.teacherid, ts.week, ts.day, ts.slot))
                        used_slots["teachers"].add(teacher_key)
                        used_slots["rooms"].add(room_key)
                        break
        population.append(individual)
    return population

'''冲突检查'''
def check_conflict_3d(individual: list, index: int, courses: list, rooms: list) -> bool:
    target = individual[index]
    cid, rid, teacherid, week, day, slot = target

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

    return teacher_conflict or room_conflict
'''适应度函数'''
def fitness(individual):
    score = 0
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

    for count in teacher_day_count.values():
        if count > 4:
            score -= 50 * (count - 4)

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
    """交叉操作，交换部分课程安排"""
    split = len(parent1) // 2
    child = parent1[:split] + parent2[split:]
    return child

'''基因变异'''
def mutate(individual):
    print("🧬 开始变异操作...")
    mutated = individual.copy()
    total = len(mutated)

    for i in range(total):
        # 显示进度
        if i % 5 == 0 or i == total-1:
            print(f"🔄 变异进度: {i+1}/{total}", end="\r")

        if check_conflict_3d(mutated, i, courses, rooms):
            cid, _, teacher_id, _, _, _ = mutated[i]

            # 找到对应的课程对象
            course = next((c for c in courses if c.cid == cid), None)
            if not course:
                continue

            room = random.choice(rooms)
            new_slot = random.choice(generate_course_slots(course))
            mutated[i] = (cid, room.rid, teacher_id, new_slot.week, new_slot.day, new_slot.slot)

    print("\n✅ 变异完成！")
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

        # 评估种群
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

        # 创建新一代
        new_population = [population[0]]  # 精英保留

        while len(new_population) < population_size:
            # 显示进度
            if len(new_population) % 10 == 0:
                print(f"🧬 正在生成后代... {len(new_population)}/{population_size}", end="\r")

            p1, p2 = random.sample(population[:10], 2)
            child = crossover(p1, p2)
            new_population.append(mutate(child))

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
    for i, (cid, rid, teacher, week, day, slot) in enumerate(timetable, 1):
        day_map = {1: "周一", 2: "周二", 3: "周三", 4: "周四", 5: "周五"}
        print(
            f"{i}. 课程 {cid} | "
            f"教室 {rid} | "
            f"教师 {teacher} | "
            f"时间：第{week}周 {day_map[day]} 第{slot}节"
        )

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