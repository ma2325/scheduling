import random
from collections import defaultdict
from typing import List
from main import courses,rooms
import test
from sql.models import Schedule
import json
import deepseek


def initialize_population(size: int) -> List[List[tuple]]:
    """80%贪心初始化 + 20%随机初始化"""
    population = []

    # 贪心生成优质个体（优先安排大课）
    sorted_courses = sorted(courses, key=lambda x: (- (x.popularity if x.popularity is not None else 0), x.teacherid if x.teacherid is not None else -1))

    for _ in range(int(size * 0.8)):
        individual = []
        used_slots = {"teachers": set(), "rooms": set()}
        for course in sorted_courses:
            # 寻找第一个可用时间段
            for ts in range(1, 41):
                teacher_key = (course.teacherid, ts)
                room = next(r for r in rooms if r.rcapacity >= course.popularity)
                room_key = (room.rid, ts)
                if teacher_key not in used_slots["teachers"] and room_key not in used_slots["rooms"]:
                    individual.append( (course.cid, room.rid, course.teacherid, ts) )
                    used_slots["teachers"].add(teacher_key)
                    used_slots["rooms"].add(room_key)
                    break
        population.append(individual)

    # 补充随机个体
    for _ in range(size - len(population)):
        individual = [ (c.cid, random.choice(rooms).rid, c.teacherid, random.randint(1,40)) for c in courses ]
        population.append(individual)

    return population
def check_conflict(individual: List[tuple], index: int) -> bool:
    """
    检查某个课程安排是否与当前排课方案中的其他课程存在冲突
    :param individual: 当前排课方案
    :param index: 需要检查的课程索引
    :return: 如果存在冲突返回True，否则返回False
    """
    target_course = individual[index]
    target_cid, target_rid, target_teacher_id, target_ts = target_course

    for i, (cid, rid, teacher_id, ts) in enumerate(individual):
        if i == index:
            continue  # 跳过自身

        # 检查教师冲突
        if teacher_id == target_teacher_id and ts == target_ts:
            return True  # 教师在同一时间有冲突

        # 检查教室冲突
        if rid == target_rid and ts == target_ts:
            return True  # 教室在同一时间有冲突

    return False  # 无冲突


def fitness(individual: List[tuple]) -> int:
    """优化后的适应度函数，减少冗余计算"""
    score = 0
    teacher_schedule = set()  # 使用集合代替字典，仅记录冲突
    room_schedule = set()
    teacher_day_count = defaultdict(int)  # 使用默认字典简化计数

    for cid, rid, teacher_id, ts in individual:
        # 教师冲突检测（O(1) 复杂度）
        teacher_key = (teacher_id, ts)
        if teacher_key in teacher_schedule:
            score -= 200
        else:
            teacher_schedule.add(teacher_key)

        # 教室冲突检测
        room_key = (rid, ts)
        if room_key in room_schedule:
            score -= 150
        else:
            room_schedule.add(room_key)

        # 教师单日课时统计（直接使用字典累加）
        day = (ts - 1) // 8
        teacher_day_count[(teacher_id, day)] += 1

    # 统一处理教师单日课时过多惩罚（减少循环次数）
    for count in teacher_day_count.values():
        if count > 4:
            score -= 50 * (count - 4)  # 超限越多惩罚越重

    return score
def selection(population: List[List[tuple]]) -> List[List[tuple]]:
    """锦标赛选择：随机选取k个个体，保留最优的"""
    selected = []
    k = 3  # 锦标赛规模
    for _ in range(len(population)):
        candidates = random.sample(population, k)
        winner = max(candidates, key=fitness)
        selected.append(winner)
    return selected

def crossover(parent1: List[tuple], parent2: List[tuple]) -> List[tuple]:
    """交叉操作，交换部分课程安排"""
    split = len(parent1) // 2
    child = parent1[:split] + parent2[split:]
    return child

def mutate(individual: List[tuple], gen: int = 0) -> List[tuple]:
    """动态变异率 + 冲突优先调整"""
    mutated = individual.copy()
    effective_rate = 0.3 * (0.5 ** (gen // 20))  # 初始变异率0.3，每20代减半

    # 第一步：强制修复所有冲突（优先级最高）
    for i in range(len(mutated)):
        if check_conflict(mutated, i):
            # 强制调整冲突课程的时间和教室
            mutated[i] = (
                mutated[i][0],
                random.choice(rooms).rid,
                mutated[i][2],
                random.randint(1, 40)
            )

    # 第二步：随机变异（概率降低）
    for i in range(len(mutated)):
        if not check_conflict(mutated, i) and random.random() < effective_rate:
            mutated[i] = (
                mutated[i][0],
                random.choice(rooms).rid,
                mutated[i][2],
                random.randint(1, 40)
            )

    return mutated
def genetic_algorithm(iterations=300, population_size=200):
    population = initialize_population(population_size)
    best_individual = None
    mutation_rate = 0.2  # 初始变异率

    for gen in range(iterations):
        # 动态调整变异率（指数衰减）
        mutation_rate = 0.2 * (0.95 ** gen)

        # 精英保留（保留前5%）
        population = sorted(population, key=fitness, reverse=True)
        elites = population[:int(0.05 * population_size)]

        # 选择（锦标赛选择）
        selected = []
        for _ in range(population_size - len(elites)):
            candidates = random.sample(population, k=3)
            selected.append(max(candidates, key=fitness))

        # 交叉和变异
        new_population = elites.copy()
        while len(new_population) < population_size:
            p1, p2 = random.sample(selected, 2)
            child = crossover(p1, p2)
            child = mutate(child, mutation_rate)
            new_population.append(child)

        population = new_population

    return max(population, key=fitness)# 运行遗传算法
# 测试冲突修复逻辑
test_individual = [
    ("C1", "R1", "T1", 10),
    ("C2", "R1", "T2", 10),  # 教室冲突（R1在时间片10被占用）
    ("C3", "R2", "T1", 10),  # 教师冲突（T1在时间片10被占用）
]

print("修复前冲突检查：", [check_conflict(test_individual, i) for i in range(3)])
# 应输出 [True, True, True]

fixed_individual = mutate(test_individual)
print("修复后冲突检查：", [check_conflict(fixed_individual, i) for i in range(3)])
# 应输出 [False, False, False]

timetable = genetic_algorithm( iterations=100, population_size=50)
print("最佳排课方案：", timetable)

#课表列表
schedule_list = [Schedule(scid,teacher,rid,time)for scid,teacher,rid,time in timetable]
#schedule_json = json.dumps([s.to_dict() for s in schedule_list], ensure_ascii=False, indent=4)

'''
deepseek

constraints="教师号为130的教师希望在JXL5#517这个教室上课，请尽量满足要求"
api_key="" deepseek要钱^ _ ^
scheduler=deepseek.DeepSeekScheduler(api_key)
optimized_schedule = scheduler.optimize_schedule(schedule_json, constraints)
print("优化后的课表：", optimized_schedule)
'''

validation_report = test.validate_schedule(timetable,courses)
if validation_report:
    print("\n发现以下冲突：")
    for line in validation_report:
        print(f"⚠️ {line}")
else:
    print("\n✅ 排课方案无冲突")

