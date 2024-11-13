import cv2
import numpy as np
import random
from deap import base, creator, tools, algorithms
from sklearn.cluster import KMeans

# 画像を読み込む
image_path = "./high_res_screenshot.jpg"  # アップロードした画像のパス
image = cv2.imread(image_path)

# BGR色空間で指定された色範囲を定義
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

# 店の数
NUM_SHOPS = 10

# KMeansクラスタリングを使ってboundary_pointsをNUM_SHOPS個に分割
kmeans = KMeans(n_clusters=NUM_SHOPS, random_state=42)
kmeans.fit(boundary_points)
labels = kmeans.labels_

# 各クラスタに対して色をランダムに割り当て
colors = np.random.randint(0, 255, size=(NUM_SHOPS, 3))

# GAの設定
POP_SIZE = 50     # 個体数
GENS = 100        # 世代数

# 評価関数（店舗の入口とクラスタの重心との距離が短いほど良い）
def evaluate(individual):
    distance_sum = 0
    for shop_id, shop_entry in enumerate(individual):
        # クラスタに属する全ての点の重心を計算
        cluster_points = boundary_points[labels == shop_id]
        cluster_center = np.mean(cluster_points, axis=0)

        # 入口とクラスタの重心との距離を計算
        distance_sum += np.sqrt(np.sum((shop_entry - cluster_center) ** 2))

    print(f"Individual: {individual}, Fitness: {distance_sum}")  # 評価の詳細を表示
    return distance_sum,

# 遺伝子表現：各店舗の入口位置を選ぶ
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("attr_int", random.randint, 0, len(boundary_points) - 1)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_int, n=NUM_SHOPS)
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
print(f"Generation {gen}, Best fitness: {best_individual.fitness.values[0]}")
best_entries = [boundary_points[entry] for entry in best_individual]

# 結果を画像に描画
for shop_id, shop_entry in enumerate(best_entries):
    cluster_points = boundary_points[labels == shop_id]
    # クラスタのポイントをその店に対応する色で描画
    for point in cluster_points:
        cv2.circle(image, (point[1], point[0]), 1, colors[shop_id].tolist(), -1)

    # 店の入口（GAで選ばれた位置）を赤で描画
    cv2.circle(image, (shop_entry[1], shop_entry[0]), 5, (0, 0, 255), -1)

# 結果を表示
cv2.imshow("Optimized Store Layout", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
