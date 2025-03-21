import random
from typing import List
from main import courses,rooms,teachers

def initialize_population(size: int) -> List[List[tuple]]:
    """生成初始种群，每个个体是一个排课方案"""
    population = []
    for _ in range(size):
        individual = []
        for course in courses:
            teacher = random.choice(teachers)  # 随机选择教师
            room = random.choice(rooms)  # 随机选择教室
            time_slot = random.randint(1, 40)  # 40个时间段（5天×8节课）
            individual.append((course.coid, teacher.tcode, room.rid, time_slot))
        population.append(individual)
    print("初始生成种群成功")
    return population

def fitness(individual: List[tuple]) -> int:
    """适应度函数，计算排课方案的合理性"""
    score = 0
    teacher_schedule = {}
    room_schedule = {}
    teacher_rooms = {}

    for course_id, teacher_id, room_id, time_slot in individual:
        # 硬约束：教师时间冲突
        if (teacher_id, time_slot) in teacher_schedule:
            score -= 100  # 严重冲突
        else:
            teacher_schedule[(teacher_id, time_slot)] = course_id

        # 硬约束：教室不能同时安排两门课
        if (room_id, time_slot) in room_schedule:
            score -= 50
        else:
            room_schedule[(room_id, time_slot)] = course_id

    # 软约束：教师授课地点尽量不超过2个教学楼

    for teacher_id,assigned_rooms in teacher_rooms.items():
        if len(assigned_rooms) > 2:
            score -= 10 * (len(assigned_rooms) - 2)

    print(score)

    return score

def selection(population: List[List[tuple]]) -> List[List[tuple]]:
    """选择适应度最高的个体"""
    sorted_population = sorted(population, key=fitness, reverse=True)
    return sorted_population[:len(population) // 2]  # 选择前50%作为父代

def crossover(parent1: List[tuple], parent2: List[tuple]) -> List[tuple]:
    """交叉操作，交换部分课程安排"""
    split = len(parent1) // 2
    child = parent1[:split] + parent2[split:]
    return child

def mutate(individual: List[tuple], mutation_rate: float = 0.1):
    """变异操作，随机调整部分课程安排"""
    for i in range(len(individual)):
        if random.random() < mutation_rate:
            course_id, teacher_id, room_id, time_slot = individual[i]
            individual[i] = (course_id, random.choice(teachers).tcode, random.choice(rooms).rid, random.randint(1, 40))
    return individual

def genetic_algorithm(courses, rooms, teachers, iterations: int, population_size: int):
    """主流程：运行GA进行排课"""
    population = initialize_population(population_size)
    for _ in range(iterations):
        population = selection(population)
        next_gen = []
        while len(next_gen) < population_size:
            p1, p2 = random.sample(population, 2)
            child = crossover(p1, p2)
            child = mutate(child)
            next_gen.append(child)
        population = next_gen

    best_schedule = max(population, key=fitness)
    return best_schedule  # 返回最优解

# 运行遗传算法
timetable = genetic_algorithm(courses, rooms, teachers, iterations=100, population_size=50)
print("最佳排课方案：", timetable)