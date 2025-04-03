import random
from  ConstraintSolver import ConstraintSolver
#需要参考Timetable调整

class GeneticAdjuster:
    def __init__(self, schedule, rooms, courses, population_size=20, generations=100, mutation_rate=0.1):
        self.schedule = schedule  # 初始课表
        self.rooms = rooms
        self.courses = courses
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate

    def initialize_population(self):
        population = []
        for _ in range(self.population_size):
            new_schedule = self.mutate_schedule(self.schedule.copy())
            solver = ConstraintSolver(new_schedule, self.rooms, self.courses)
            if solver.is_valid_schedule():
                population.append(new_schedule)
        return population

    def fitness_function(self, schedule):
        solver = ConstraintSolver(schedule, self.rooms, self.courses)
        if not solver.is_valid_schedule():
            return -1  # 无效解

        # 计算教室利用率（简单示例，可扩展）
        used_rooms = len(set((r for _, r, _, _ in schedule.values())))
        utilization_score = used_rooms / len(self.rooms)

        return utilization_score

    def select_parents(self, population):
        return random.choices(population, weights=[self.fitness_function(s) for s in population], k=2)

    def crossover(self, parent1, parent2):
        child = parent1.copy()
        for course_id in random.sample(list(parent1.keys()), len(parent1) // 2):
            child[course_id] = parent2[course_id]
        return child if ConstraintSolver(child, self.rooms, self.courses).is_valid_schedule() else parent1

    def mutate_schedule(self, schedule):
        new_schedule = schedule.copy()
        for course_id in schedule:
            if random.random() < self.mutation_rate:
                new_time = random.randint(0, 40)  # 假设一周有40个时间段
                new_room = random.choice(list(self.rooms.keys()))
                course_info = new_schedule[course_id]
                new_schedule[course_id] = (new_time, new_room, course_info[2], course_info[3])
        return new_schedule

    def optimize_schedule(self):
        population = self.initialize_population()
        for _ in range(self.generations):
            new_population = []
            for _ in range(self.population_size // 2):
                parent1, parent2 = self.select_parents(population)
                child = self.crossover(parent1, parent2)
                child = self.mutate_schedule(child)
                if ConstraintSolver(child, self.rooms, self.courses).is_valid_schedule():
                    new_population.append(child)
            population = new_population if new_population else population
        return max(population, key=self.fitness_function)

# 用法示例
# adjuster = GeneticAdjuster(schedule, rooms, courses)
# new_schedule = adjuster.optimize_schedule()
