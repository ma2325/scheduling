#遗传算法
import random
import Class
# 模拟数据
teachers = ["T1", "T2", "T3"]
courses_names = ["C1", "C2", "C3", "C4"]
rooms = ["R1", "R2", "R3"]
time_slots = ["Mon-8AM", "Mon-10AM", "Tue-8AM", "Tue-10AM"]

# 生成初始种群
def generate_initial_population(size=10):
    population = []
    for _ in range(size):
        schedule = []
        for course_name in courses_names:
            course = Class.Course(
                name=course_name,
                teacher=random.choice(teachers),
                time=random.choice(time_slots),
                classroom=random.choice(rooms)
            )
            schedule.append(course)
        population.append(schedule)
    return population

# 适应度函数（简单版）
def fitness(schedule):
    score = 0
    seen = set()
    for course in schedule:
        key = (course.teacher, course.time)
        if key in seen:
            score -= 10  # 教师时间冲突
        seen.add(key)
    return score

# 交叉操作
def crossover(parent1, parent2):
    point = len(parent1) // 2
    child = parent1[:point] + parent2[point:]
    return child

# 变异操作
def mutate(schedule, mutation_rate=0.1):
    if random.random() < mutation_rate:
        course = random.choice(schedule)
        course.time = random.choice(time_slots)
    return schedule

# 遗传算法主循环
def genetic_algorithm(generations=100, population_size=10):
    population = generate_initial_population(population_size)

    for _ in range(generations):
        population = sorted(population, key=lambda s: fitness(s), reverse=True)
        next_gen = population[:2]  # 选择前两名直接进入下一代

        while len(next_gen) < population_size:
            parent1, parent2 = random.choices(population[:5], k=2)
            child = crossover(parent1, parent2)
            child = mutate(child)
            next_gen.append(child)

        population = next_gen

    return population[0]

# 运行遗传算法
best_schedule = genetic_algorithm()
for course in best_schedule:
    course.show_info()
