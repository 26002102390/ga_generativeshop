import cv2
import numpy as np
import random
from deap import base, creator, tools, algorithms

# 画像を読み込む
image_path = "./high_res_screenshot.jpg"  # アップロードした画像のパス
image = cv2.imread(image_path)

# BGR色空間で指定された色範囲を定義
# 黄色と青の境界線の色を指定
target_color_bgr = np.array([183,66,67])  # BGR形式で指定
threshold = 10  # 色の範囲の許容誤差

# 指定色の周辺の範囲を定義
lower_bound = target_color_bgr - threshold
upper_bound = target_color_bgr + threshold

# マスクを作成
mask = cv2.inRange(image, lower_bound, upper_bound)

# マスクから輪郭を検出
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 黒色の背景に輪郭を描画（デバッグ用）
boundary_image = np.zeros_like(image)
cv2.drawContours(boundary_image, contours, -1, (255, 255, 255), 2)
# 境界線のピクセル座標を取得
boundary_points = np.column_stack(np.where(boundary_image > 0))
# print(f"Number of boundary points: {len(boundary_points)}")
# cv2.imshow("Black Image with Contours", boundary_image)

# # ESCキーを押すまで画像を表示
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# GAの設定
NUM_ENTRIES = 10  # 入口の数
POP_SIZE = 50     # 個体数
GENS = 100        # 世代数

# 評価関数（入口から通路までの距離が短いほど良い）
def evaluate(individual):
    distance_sum = 0
    for entry in individual:
        x, y, _ = boundary_points[entry]
        distance_sum += np.sqrt((x - y) ** 2)  # 簡易な距離計算
    return distance_sum,

# 遺伝子表現：boundary_pointsのインデックスを使う
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("attr_int", random.randint, 0, len(boundary_points) - 1)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_int, n=NUM_ENTRIES)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("evaluate", evaluate)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutUniformInt, low=0, up=len(boundary_points) - 1, indpb=0.2)
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
best_entries = [boundary_points[entry] for entry in best_individual]

# 結果を画像に描画
cv2.drawContours(image, contours, -1, (0, 0, 0), 2)
for entry in best_entries:
    cv2.circle(image, (entry[1], entry[0]), 5, (0, 0, 255), -1)  # 赤色で入口を描画
cv2.imshow("Optimized Entrance Layout", image)
cv2.waitKey(0)
cv2.destroyAllWindows()

