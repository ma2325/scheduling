import random
import math

# 蚁群优化参数
PHEROMONE_DECAY = 0.1  # 信息素挥发系数
PHEROMONE_BOOST = 5.0  # 适应度对信息素的影响因子
ALPHA = 1.0  # 信息素影响力
BETA = 2.0   # 启发式信息影响力
EVAPORATION_RATE = 0.2  # 信息素衰减率

# 初始化信息素矩阵（教师、教室、时间段）
pheromones = {}

def initialize_pheromones(courses, rooms, teachers):
    """ 初始化信息素值 """
    global pheromones
    pheromones = {}
    for course in courses:
        for room in rooms:
            for teacher in teachers:
                for time_slot in range(21):  # 假设 0-20 共 21 个时间段
                    pheromones[(course.coid, room.rid, teacher.tid, time_slot)] = 1.0

def initialize_population(courses, rooms, teachers, population_size=100):
    """ 初始化种群，基于信息素选择教室和时间 """
    population = []
    for _ in range(population_size):
        schedule = []
        for course in courses:
            possible_rooms = [room.rid for room in rooms if room.rvolume >= course.covolume]
            possible_teachers = [teacher.tid for teacher in teachers]

            if not possible_rooms or not possible_teachers:
                continue

            # 计算蚁群优化选择概率
            choices = []
            for room in possible_rooms:
                for teacher in possible_teachers:
                    for time_slot in range(21):
                        pheromone = pheromones.get((course.coid, room, teacher, time_slot), 1.0)
                        heuristic = 1.0 / (1 + random.random())  # 启发式信息
                        probability = (pheromone ** ALPHA) * (heuristic ** BETA)
                        choices.append((probability, room, teacher, time_slot))

            choices.sort(reverse=True, key=lambda x: x[0])
            _, best_room, best_teacher, best_time = choices[0]  # 选择最高概率方案

            schedule.append({
                "course_id": course.coid,
                "room_id": best_room,
                "teacher_id": best_teacher,
                "time_slot": best_time
            })
        population.append(schedule)
    return population

def fitness(schedule):
    """ 计算适应度，考虑时间冲突、教师时间偏好等 """
    score = 0
    time_teacher_conflicts = set()
    time_room_conflicts = set()

    for entry in schedule:
        key_teacher = (entry['teacher_id'], entry['time_slot'])
        key_room = (entry['room_id'], entry['time_slot'])

        if key_teacher in time_teacher_conflicts:
            score -= 5  # 教师时间冲突
        else:
            time_teacher_conflicts.add(key_teacher)

        if key_room in time_room_conflicts:
            score -= 5  # 教室时间冲突
        else:
            time_room_conflicts.add(key_room)

        # 额外约束优化
        if entry["time_slot"] in [0, 20]:  # 避免极端早晚时间
            score -= 2
        if entry["time_slot"] in [10, 11]:  # 午休时间
            score -= 3

    return score

def update_pheromones(population):
    """ 信息素更新 """
    global pheromones
    # 挥发所有信息素
    for key in pheromones.keys():
        pheromones[key] *= (1 - PHEROMONE_DECAY)

    # 强化优良个体的信息素
    for schedule in population[:10]:  # 仅强化前 10 个解
        score = fitness(schedule)
        for entry in schedule:
            key = (entry['course_id'], entry['room_id'], entry['teacher_id'], entry['time_slot'])
            pheromones[key] += PHEROMONE_BOOST * max(0, score)

def select(population):
    """ 选择最优个体 """
    population.sort(key=lambda x: fitness(x), reverse=True)
    return population[: len(population) // 2]

def crossover(parent1, parent2):
    """ 交叉操作 """
    if not parent1 or not parent2:
        return parent1 or parent2
    point = random.randint(0, min(len(parent1), len(parent2)) - 1)
    return parent1[:point] + parent2[point:]

def mutate(schedule, mutation_rate=0.1):
    """ 变异操作，提高冲突排课的变异率 """
    for entry in schedule:
        if random.random() < mutation_rate:
            old_time = entry['time_slot']
            entry['time_slot'] = random.randint(0, 20)
            if fitness(schedule) < 0:  # 如果变异后适应度变差，回滚
                entry['time_slot'] = old_time
    return schedule

def genetic_algorithm(courses, rooms, teachers, generations=100):
    """ 遗传算法 + 蚁群优化 """
    initialize_pheromones(courses, rooms, teachers)
    population = initialize_population(courses, rooms, teachers)

    if not population or not population[0]:
        raise ValueError("无法生成有效初始种群，请检查教室容量是否满足课程需求")

    for _ in range(generations):
        selected = select(population)
        new_population = []

        while len(new_population) < len(population):
            p1, p2 = random.sample(selected, 2) if len(selected) >= 2 else (selected[0], selected[0])
            child = crossover(p1, p2)
            child = mutate(child)
            new_population.append(child)

        population = new_population
        update_pheromones(population)  # 更新信息素

    best_schedule = max(population, key=lambda x: fitness(x))
    return best_schedule

def result(courses, rooms, teachers):
    return genetic_algorithm(courses, rooms, teachers)
