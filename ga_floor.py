import random
from deap import base, creator, tools, algorithms
import numpy as np

# 各フロアのキャパシティ
floor_capacities = [30, 30, 30]  # 1階, 2階, 3階のキャパシティ

# 店舗の種類とそれぞれが占めるキャパシティ
shop_types = {
    "映画館": 15,
    "服屋": 2,
    "食事": 5,
    "雑貨": 3,
    "書店": 4,
    "スポーツ用品店": 6,
    "家電店": 10,
    "美容・化粧品店": 4,
    "子供向けエリア": 8,
    "カー用品店": 7
}

# 各店舗タイプに対する最小・最大数
shop_constraints = {
    "映画館": (0, 1),
    "服屋": (3, 30),
    "食事": (2, 20),
    "雑貨": (2, 10),
    "書店": (0, 2),
    "スポーツ用品店": (0, 1),
    "家電店": (0, 2),
    "美容・化粧品店": (1, 3),
    "子供向けエリア": (1, 2),
    "カー用品店": (0, 1)
}

# 店舗の種類と優先フロア
preferred_floor = {
    "映画館": 3, # 映画館は3階に優先で配置
    "服屋": 2,
    "食事": 1,
    "雑貨": 1,
    "書店": 1,
    "スポーツ用品店": 2,
    "家電店": 3,
    "美容・化粧品店": 2,
    "子供向けエリア": 1,
    "カー用品店": 3,
}

# GA設定
NUM_FLOORS = 3
POP_SIZE = 50
GENS = 100

# 個体を初期化する関数：店舗の種類と数の制約を満たすようにランダムに生成
def create_individual():
    individual = []
    for shop, (min_count, max_count) in shop_constraints.items():
        count = random.randint(min_count, max_count)
        individual.extend([shop] * count)
    random.shuffle(individual)
    return individual

# 評価関数
def evaluate(individual):
    total_score = 0
    floor_usage = [0] * NUM_FLOORS
    shop_count = {shop: 0 for shop in shop_types}

    for floor in range(NUM_FLOORS):
        floor_shops = individual[floor::NUM_FLOORS]
        for shop in floor_shops:
            shop_capacity = shop_types[shop]
            shop_count[shop] += 1
            if floor_usage[floor] + shop_capacity <= floor_capacities[floor]:
                floor_usage[floor] += shop_capacity
                if preferred_floor[shop] == floor + 1:
                    total_score += 5
                else:
                    total_score += 1
            else:
                total_score -= 10

    for shop, count in shop_count.items():
        min_count, max_count = shop_constraints[shop]
        if count < min_count:
            total_score -= 10 * (min_count - count)
        elif count > max_count:
            total_score -= 10 * (count - max_count)

    return total_score,

# 遺伝子表現を設定
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("individual", tools.initIterate, creator.Individual, create_individual)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("evaluate", evaluate)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.2)
toolbox.register("select", tools.selTournament, tournsize=3)

# GAの実行
population = toolbox.population(n=POP_SIZE)
for gen in range(GENS):
    offspring = algorithms.varAnd(population, toolbox, cxpb=0.5, mutpb=0.2)
    fits = map(toolbox.evaluate, offspring)
    for fit, ind in zip(fits, offspring):
        ind.fitness.values = fit
    population = toolbox.select(offspring, k=len(population))

# 最適な配置の取得
best_individual = tools.selBest(population, k=1)[0]
print(f"Generation {gen}, Best fitness: {best_individual.fitness.values[0]}")
print(f"Best individual: {best_individual}")

# 結果を表示
floor_assignments = [best_individual[i::NUM_FLOORS] for i in range(NUM_FLOORS)]
for floor, shops in enumerate(floor_assignments):
    print(f"Floor {floor + 1}: {shops}")
