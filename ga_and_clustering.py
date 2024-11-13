import random
from deap import base, creator, tools, algorithms
import numpy as np
import cv2
from scipy.spatial import Voronoi
from PIL import Image, ImageDraw, ImageFont

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

# 画像の読み込み
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

# 各フロアのレイアウトを描画
for floor_index, floor_shops_list in enumerate(floor_assignments):
    print(floor_index)
    # 各フロアの店舗の仮想的な重心をキャパシティに基づき拡張して生成
    expanded_centroids = []
    for shop in floor_shops_list:
        centroid = boundary_points[np.random.choice(len(boundary_points))]  # 任意のポイントを取得
        capacity_factor = shop_types[shop] / max(shop_types.values())  # キャパシティに基づく重み
        expansion_offset = np.random.normal(scale=50 * capacity_factor, size=centroid.shape)  # 偏移
        expanded_centroids.append(centroid + expansion_offset)

    expanded_centroids = np.array(expanded_centroids)

    # Voronoi領域の計算
    vor = Voronoi(expanded_centroids)

    # 描画用に各クラスタに対して色をランダムに割り当て
    colors = np.random.randint(0, 255, size=(len(floor_shops_list), 3))

    # Voronoi領域に基づき、boundary_pointsを色分けして描画
    for i, point in enumerate(boundary_points):
        distances = np.linalg.norm(expanded_centroids - point, axis=1)
        closest_cluster = np.argmin(distances)
        cv2.circle(image, (point[1], point[0]), 1, colors[closest_cluster].tolist(), -1)

    # OpenCVの画像をPillowに変換
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(image_pil)

    # 日本語フォントの読み込み（必要に応じてパスを変更してください）
    font_path = "/Users/cdl/Downloads/Noto_Sans_JP/NotoSansJP-VariableFont_wght.ttf"  # Mac用の例
    font = ImageFont.truetype(font_path, 20)

    # 各クラスタの重心（代表点）に店舗名を描画
    for i, (centroid, shop) in enumerate(zip(expanded_centroids, floor_shops_list)):
        # 各店舗に名前を描画
        draw.text((centroid[1], centroid[0]), shop, fill=(0, 0, 0), font=font, background=(255, 255, 255))

    # 最終結果を保存
    output_image_path = "./floors/final_result" + str(floor_index) + ".png"  # 保存するファイル名
    image_pil.save(output_image_path)
    # 最終結果を表示
    image_pil.show()

#     # 画像のサイズを取得（同じサイズであることが前提）
#     width, height = image_pil.width, image_pil.height

#     if floor_index == 0:
#         # 3つの画像を縦に並べるための新しい画像を作成
#         combined_image = Image.new('RGB', (width, height * 3))
#     # 各フロアの画像を貼り付け
#     combined_image.paste(image_pil, (0, height*floor_index))  # 1階の画像

# # 結合された画像を表示
# combined_image.show()
